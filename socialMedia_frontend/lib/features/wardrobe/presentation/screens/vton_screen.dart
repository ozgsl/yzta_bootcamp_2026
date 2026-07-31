import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../../services/api_service.dart';

class VtonScreen extends StatefulWidget {
  final Map<String, dynamic> clothItem;

  const VtonScreen({super.key, required this.clothItem});

  @override
  State<VtonScreen> createState() => _VtonScreenState();
}

class _VtonScreenState extends State<VtonScreen> {
  File? _modelImage;
  bool _isLoading = false;
  String? _resultImageUrl;
  String? _errorMessage;
  final _picker = ImagePicker();

  Future<void> _pickImage(ImageSource source) async {
    try {
      final pickedFile = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );
      if (pickedFile != null) {
        setState(() {
          _modelImage = File(pickedFile.path);
          _resultImageUrl = null;
          _errorMessage = null;
        });
      }
    } catch (e) {
      debugPrint("Resim seçme hatası: $e");
    }
  }

  Future<void> _tryOn() async {
    if (_modelImage == null) return;
    
    final garmentUrl = widget.clothItem['foto_url']?.toString() ?? widget.clothItem['image_url']?.toString() ?? '';
    if (garmentUrl.isEmpty) {
      setState(() => _errorMessage = "Kıyafet resmi bulunamadı.");
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _resultImageUrl = null;
    });

    try {
      // Base64 encode model image
      final bytes = await _modelImage!.readAsBytes();
      final String base64Image = "data:image/jpeg;base64," + base64Encode(bytes);
      
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token') ?? '';

      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/wardrobe/vton/tryon'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'garment_url': ApiService.fixImageUrl(garmentUrl),
          'model_image_b64': base64Image,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['image_url'] != null) {
          setState(() {
            _resultImageUrl = data['image_url'];
          });
        } else {
          setState(() {
            _errorMessage = data['message'] ?? "Bilinmeyen bir hata oluştu.";
          });
        }
      } else {
        setState(() {
          _errorMessage = "API Hatası: ${response.statusCode} - ${response.body}";
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Bağlantı hatası: $e";
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final rawGarmentUrl = widget.clothItem['foto_url']?.toString() ?? widget.clothItem['image_url']?.toString() ?? '';
    final garmentUrl = ApiService.fixImageUrl(rawGarmentUrl);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text("Sanal Deneme (VTON)"),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Bu özellik deneyseldir. Fashn.ai modelini kullanarak kıyafeti üzerinizde görebilirsiniz.",
              style: TextStyle(color: Colors.grey, fontSize: 13),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            
            // Garment Image
            const Text("Kıyafet", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            Container(
              height: 150,
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(12),
                image: garmentUrl.isNotEmpty
                    ? DecorationImage(
                        image: NetworkImage(garmentUrl),
                        fit: BoxFit.contain,
                      )
                    : null,
              ),
              child: garmentUrl.isEmpty
                  ? const Center(child: Icon(Icons.checkroom, size: 50, color: Colors.grey))
                  : null,
            ),
            
            const SizedBox(height: 24),
            
            // Model Image Selection
            const Text("Sizin Fotoğrafınız", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () {
                showModalBottomSheet(
                  context: context,
                  backgroundColor: Theme.of(context).cardColor,
                  builder: (_) => SafeArea(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        ListTile(
                          leading: const Icon(Icons.camera_alt),
                          title: const Text('Kamera'),
                          onTap: () {
                            Navigator.pop(context);
                            _pickImage(ImageSource.camera);
                          },
                        ),
                        ListTile(
                          leading: const Icon(Icons.photo_library),
                          title: const Text('Galeri'),
                          onTap: () {
                            Navigator.pop(context);
                            _pickImage(ImageSource.gallery);
                          },
                        ),
                      ],
                    ),
                  ),
                );
              },
              child: Container(
                height: 200,
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(12),
                  image: _modelImage != null
                      ? DecorationImage(
                          image: FileImage(_modelImage!),
                          fit: BoxFit.cover,
                        )
                      : null,
                  border: Border.all(color: AppTheme.accentViolet.withOpacity(0.5), width: 1, style: BorderStyle.solid),
                ),
                child: _modelImage == null
                    ? const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.add_a_photo, size: 40, color: Colors.grey),
                            SizedBox(height: 8),
                            Text("Fotoğraf Yükle", style: TextStyle(color: Colors.grey)),
                          ],
                        ),
                      )
                    : null,
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Result Image
            if (_resultImageUrl != null) ...[
              const Text("Sonuç", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 8),
              Container(
                height: 350,
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(12),
                  image: DecorationImage(
                    image: NetworkImage(_resultImageUrl!),
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              const SizedBox(height: 24),
            ],
            
            if (_errorMessage != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withOpacity(0.5)),
                ),
                child: Text(
                  _errorMessage!,
                  style: const TextStyle(color: Colors.red, fontSize: 13),
                  textAlign: TextAlign.center,
                ),
              ),
              const SizedBox(height: 24),
            ],
            
            ElevatedButton(
              onPressed: _isLoading || _modelImage == null ? null : _tryOn,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.accentViolet,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _isLoading
                  ? const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Text("Üzerimde Dene 🪄", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
