import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

import '../../../../core/theme/app_theme.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../../services/api_service.dart';
import '../../../../core/localization/locale_provider.dart';
import '../../domain/models/color_model.dart';
import '../widgets/clothing_color_picker.dart';

class EditItemScreen extends ConsumerStatefulWidget {
  final Map<String, dynamic> initialItem;

  const EditItemScreen({super.key, required this.initialItem});

  @override
  ConsumerState<EditItemScreen> createState() => _EditItemScreenState();
}

class _EditItemScreenState extends ConsumerState<EditItemScreen> {
  final _picker = ImagePicker();
  File? _selectedImage;
  bool _isLoading = false;
  bool _isDeleting = false;
  bool _isFavorite = false;
  bool _isDirty = false;

  late String _tur;
  SelectedColor? _selectedColor;
  late String _mevsim;

  final _markaCtrl = TextEditingController();
  final _bedenCtrl = TextEditingController();

  final List<String> _turler = [
    'Üst Giyim',
    'Alt Giyim',
    'Dış Giyim',
    'Elbise',
    'Ayakkabı',
    'Aksesuar',
    'Çanta'
  ];
  final List<String> _mevsimler = [
    'İlkbahar',
    'Yaz',
    'Sonbahar',
    'Kış',
    'Tüm Sezon'
  ];

  @override
  void initState() {
    super.initState();
    _tur = _ensureValidDropdownValue(widget.initialItem['tur'], _turler);
    
    final renk = widget.initialItem['renk'] as String?;
    final renkHex = widget.initialItem['renk_hex'] as String?;
    final renkCatId = widget.initialItem['renk_kategori_id'] as String?;
    if (renk != null) {
      _selectedColor = SelectedColor(
        name: renk,
        hexCode: renkHex ?? '#000000',
        parentCategoryId: renkCatId ?? 'siyah',
      );
    }

    _mevsim =
        _ensureValidDropdownValue(widget.initialItem['mevsim'], _mevsimler);

    _markaCtrl.text = widget.initialItem['marka'] ?? '';
    _bedenCtrl.text = widget.initialItem['beden'] ?? '';

    _isFavorite = widget.initialItem['is_favorite'] == 1 || widget.initialItem['is_favorite'] == true;
    _isDirty = widget.initialItem['is_dirty'] == 1 || widget.initialItem['is_dirty'] == true;
  }

  String _ensureValidDropdownValue(dynamic val, List<String> items) {
    if (val == null || !items.contains(val)) return items.first;
    return val as String;
  }

  Future<void> _pickImage(ImageSource source) async {
    final xfile = await _picker.pickImage(source: source, imageQuality: 70);
    if (xfile != null) {
      setState(() => _selectedImage = File(xfile.path));
    }
  }

  Future<String?> _uploadImage(File file) async {
    final uri = Uri.parse('${ApiService.baseUrl}/captions/upload');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('file', file.path));
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['url'] as String?;
    }
    return null;
  }

  Future<void> _submit() async {
    final userId = ref.read(authProvider).currentUserId;
    if (userId == null) return;

    setState(() => _isLoading = true);
    try {
      String? imageUrl = widget.initialItem['foto_url'];
      if (_selectedImage != null) {
        final uploaded = await _uploadImage(_selectedImage!);
        if (uploaded != null) imageUrl = uploaded;
      }

      await ApiService().updateCloth(widget.initialItem['id'], {
        'tur': _tur,
        'renk': _selectedColor?.name ?? 'Belirsiz',
        'renk_hex': _selectedColor?.hexCode,
        'renk_kategori_id': _selectedColor?.parentCategoryId,
        'marka': _markaCtrl.text.isEmpty ? null : _markaCtrl.text,
        'beden': _bedenCtrl.text.isEmpty ? null : _bedenCtrl.text,
        'mevsim': _mevsim,
        'foto_url': imageUrl,
        'is_favorite': _isFavorite,
        'is_dirty': _isDirty,
      });

      if (mounted) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Clothing updated!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _deleteItem() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Theme.of(context).cardColor,
        title: Text('Delete Clothing',
            style: TextStyle(color: Theme.of(context).colorScheme.error)),
        content: Text(
            'Are you sure you want to delete this clothing from your wardrobe?',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text('Cancel',
                style: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text('Delete',
                style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      setState(() => _isDeleting = true);
      try {
        await ApiService().deleteCloth(widget.initialItem['id']);
        if (mounted) {
          Navigator.pop(context, true);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Clothing deleted.')),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error during deletion: $e')),
          );
        }
      } finally {
        if (mounted) setState(() => _isDeleting = false);
      }
    }
  }

  void _showImageSourceSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Theme.of(context).cardColor,
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: Icon(Icons.camera_alt_rounded,
                  color: Theme.of(context).colorScheme.primary),
              title: Text('Camera',
                  style: TextStyle(
                      color: Theme.of(context).textTheme.bodyLarge?.color ??
                          Colors.white)),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: Icon(Icons.photo_library_rounded,
                  color: Theme.of(context).colorScheme.secondary),
              title: Text('Photo Library',
                  style: TextStyle(
                      color: Theme.of(context).textTheme.bodyLarge?.color ??
                          Colors.white)),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(stringsProvider);
    final rawFotoUrl = widget.initialItem['foto_url']?.toString() ?? widget.initialItem['image_url']?.toString() ?? '';
    final fotoUrl = rawFotoUrl.isNotEmpty ? ApiService.fixImageUrl(rawFotoUrl) : null;
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(s.isTr ? 'Kıyafeti Düzenle' : 'Edit Clothing',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white)),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        elevation: 0,
        iconTheme: IconThemeData(
            color:
                Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
        actions: [
          IconButton(
            icon: Icon(
              _isFavorite ? Icons.favorite_rounded : Icons.favorite_border_rounded,
              color: _isFavorite ? Colors.redAccent : (Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
            ),
            onPressed: () {
              setState(() {
                _isFavorite = !_isFavorite;
              });
            },
          ),
          _isLoading
              ? Padding(
                  padding: EdgeInsets.all(16),
                  child: SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Theme.of(context).colorScheme.primary),
                  ),
                )
              : TextButton(
                  onPressed: _submit,
                  child: Text(s.isTr ? 'Kaydet' : 'Save',
                      style: TextStyle(
                          color: Theme.of(context).colorScheme.primary,
                          fontWeight: FontWeight.bold)),
                ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            GestureDetector(
              onTap: _showImageSourceSheet,
              child: Container(
                width: double.infinity,
                height: 200,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surface,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: _selectedImage != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(14),
                        child: Image.file(_selectedImage!, fit: BoxFit.cover))
                    : (fotoUrl != null && fotoUrl.isNotEmpty)
                        ? ClipRRect(
                            borderRadius: BorderRadius.circular(14),
                            child: Image.network(fotoUrl, fit: BoxFit.cover))
                        : Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.add_photo_alternate_rounded,
                                  size: 52,
                                  color: Theme.of(context)
                                      .colorScheme
                                      .primary
                                      .withValues(alpha: 0.7)),
                              const SizedBox(height: 12),
                              Text(
                                  s.isTr ? 'Fotoğraf değiştir' : 'Change photo',
                                  style: TextStyle(
                                      color: Theme.of(context)
                                              .textTheme
                                              .bodySmall
                                              ?.color ??
                                          Colors.grey,
                                      fontSize: 15)),
                            ],
                          ),
              ),
            ),
            const SizedBox(height: 24),
            const _SectionLabel(text: 'Type *'),
            _ChipsField(
                value: _tur,
                items: _turler,
                onChanged: (v) => setState(() => _tur = v),
                displayTranslator: (val) => s.translateWardrobe(val)),
            const SizedBox(height: 16),
            const _SectionLabel(text: 'Color *'),
            ClothingColorPicker(
              initialColor: _selectedColor,
              onColorSelected: (color) {
                setState(() => _selectedColor = color);
              },
            ),
            const SizedBox(height: 16),
            const _SectionLabel(text: 'Season'),
            _ChipsField(
                value: _mevsim,
                items: _mevsimler,
                onChanged: (v) => setState(() => _mevsim = v),
                displayTranslator: (val) => s.translateWardrobe(val)),
            const SizedBox(height: 16),
            const _SectionLabel(text: 'Brand'),
            TextField(
              controller: _markaCtrl,
              style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ??
                      Colors.white),
              decoration: _inputDeco('Enter brand'),
            ),
            const SizedBox(height: 16),
            const _SectionLabel(text: 'Size'),
            TextField(
              controller: _bedenCtrl,
              style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ??
                      Colors.white),
              decoration: _inputDeco('Size (e.g. M, 38)'),
            ),
            const SizedBox(height: 32),
            
            // Laundry Basket / Clean Toggle
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(12),
              ),
              child: SwitchListTile(
                title: Text(
                  _isDirty ? 'Kirli Sepetinde' : 'Dolapta (Temiz)',
                  style: TextStyle(
                    color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                subtitle: Text(
                  'Bu kıyafet kirli sepetinde mi?',
                  style: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey,
                  ),
                ),
                value: _isDirty,
                activeColor: Theme.of(context).colorScheme.primary,
                secondary: Icon(
                  _isDirty ? Icons.local_laundry_service_rounded : Icons.checkroom_rounded,
                  color: _isDirty ? Colors.orangeAccent : Colors.green,
                ),
                onChanged: (val) {
                  setState(() {
                    _isDirty = val;
                  });
                },
              ),
            ),

            const SizedBox(height: 32),
            
            // Delete Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: OutlinedButton.icon(
                onPressed: _isDeleting ? null : _deleteItem,
                icon: _isDeleting 
                    ? SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Theme.of(context).colorScheme.error, strokeWidth: 2)) 
                    : Icon(Icons.delete_outline_rounded, color: Theme.of(context).colorScheme.error),
                label: Text(
                  'Kıyafeti Sil',
                  style: TextStyle(color: Theme.of(context).colorScheme.error, fontWeight: FontWeight.bold),
                ),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: Theme.of(context).colorScheme.error),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  InputDecoration _inputDeco(String hint) {
    return InputDecoration(
      hintText: hint,
      hintStyle: TextStyle(
          color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey),
      filled: true,
      fillColor: Theme.of(context).colorScheme.surface,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String text;
  const _SectionLabel({required this.text});
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, left: 4),
      child: Text(text,
          style: TextStyle(
              color:
                  Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
              fontWeight: FontWeight.bold)),
    );
  }
}

class _ChipsField extends StatelessWidget {
  final String value;
  final List<String> items;
  final void Function(String) onChanged;
  final String Function(String)? displayTranslator;

  const _ChipsField({
    required this.value,
    required this.items,
    required this.onChanged,
    this.displayTranslator,
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: items.map((item) {
        final isSelected = item == value;
        return GestureDetector(
          onTap: () => onChanged(item),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: isSelected
                  ? Theme.of(context).colorScheme.primary
                  : Theme.of(context).colorScheme.surface,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              displayTranslator != null ? displayTranslator!(item) : item,
              style: TextStyle(
                color: isSelected
                    ? Theme.of(context).textTheme.bodyLarge?.color ??
                        Colors.white
                    : Theme.of(context).textTheme.bodyLarge?.color ??
                        Colors.white,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                fontSize: 13,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
