import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../../services/api_service.dart';
import '../../../../core/localization/locale_provider.dart';
import '../../domain/models/color_model.dart';
import '../widgets/clothing_color_picker.dart';
class AddItemScreen extends ConsumerStatefulWidget {
  const AddItemScreen({super.key});

  @override
  ConsumerState<AddItemScreen> createState() => _AddItemScreenState();
}

class _AddItemScreenState extends ConsumerState<AddItemScreen> {
  final _picker = ImagePicker();
  File? _selectedImage;
  bool _isLoading = false;
  bool _isAnalyzing = false;
  String? _uploadedImageUrl;         // Yükleme sonrası backend URL'si
  Map<String, dynamic>? _aiAnalysis; // FashionSigLIP analiz sonucu

  // Form state
  String _tur = 'Tişört';
  SelectedColor? _selectedColor;
  String _mevsim = 'Tüm Sezon';
  final _markaCtrl = TextEditingController();
  final _bedenCtrl = TextEditingController();

  static const _turler = [
    'Tişört',
    'Gömlek',
    'Bluz',
    'Kazak',
    'Sweatshirt',
    'Pantolon',
    'Şort',
    'Etek',
    'Elbise',
    'Ceket',
    'Mont',
    'Kaban',
    'Ayakkabı',
    'Bot',
    'Sneaker',
    'Çanta',
    'Aksesuar',
    'Diğer',
  ];  static const _mevsimler = ['Yaz', 'Kış', 'İlkbahar', 'Sonbahar', 'Tüm Sezon'];

  Future<void> _pickImage(ImageSource source) async {
    final xfile = await _picker.pickImage(
      source: source,
      imageQuality: 75,
      maxWidth: 1024,
    );
    if (xfile == null) return;

    setState(() {
      _selectedImage = File(xfile.path);
      _isAnalyzing = true;
      _uploadedImageUrl = null;
      _aiAnalysis = null;
    });

    try {
      // Tek istekte yükle + FashionSigLIP analizi al
      final result = await ApiService().uploadImageForAnalysis(_selectedImage!);
      final url = result['url'] as String?;
      final analysis = result['ai_analysis'] as Map<String, dynamic>?;

      if (mounted) {
        setState(() {
          _uploadedImageUrl = url;
          _aiAnalysis = analysis;

          if (analysis != null) {
            // 1. Kıyafet Türü (Type) Matching
            final turRaw = (analysis['tur'] as String? ?? '').trim().toLowerCase();
            String matchedTur = '';
            
            if (turRaw == 'tişört' || turRaw == 't-shirt' || turRaw == 'tshirt') {
              matchedTur = 'Tişört';
            } else if (turRaw == 'gömlek' || turRaw == 'shirt') {
              matchedTur = 'Gömlek';
            } else if (turRaw == 'bluz' || turRaw == 'blouse') {
              matchedTur = 'Bluz';
            } else if (turRaw == 'kazak' || turRaw == 'sweater' || turRaw == 'hırka' || turRaw == 'cardigan') {
              matchedTur = 'Kazak';
            } else if (turRaw == 'sweatshirt' || turRaw == 'hoodie') {
              matchedTur = 'Sweatshirt';
            } else if (turRaw == 'pantolon' || turRaw == 'jean' || turRaw == 'jeans' || turRaw == 'trousers' || turRaw == 'eşofman altı' || turRaw == 'tayt' || turRaw == 'leggings' || turRaw == 'sweatpants') {
              matchedTur = 'Pantolon';
            } else if (turRaw == 'şort' || turRaw == 'shorts') {
              matchedTur = 'Şort';
            } else if (turRaw == 'etek' || turRaw == 'skirt') {
              matchedTur = 'Etek';
            } else if (turRaw == 'elbise' || turRaw == 'dress' || turRaw == 'tulum' || turRaw == 'jumpsuit') {
              matchedTur = 'Elbise';
            } else if (turRaw == 'ceket' || turRaw == 'jacket' || turRaw == 'blazer' || turRaw == 'yelek' || turRaw == 'vest') {
              matchedTur = 'Ceket';
            } else if (turRaw == 'mont' || turRaw == 'coat' || turRaw == 'kaban' || turRaw == 'parka') {
              matchedTur = 'Mont';
            } else if (turRaw == 'sneaker' || turRaw == 'sneakers' || turRaw == 'spor ayakkabı') {
              matchedTur = 'Sneaker';
            } else if (turRaw == 'bot' || turRaw == 'boots') {
              matchedTur = 'Bot';
            } else if (turRaw == 'ayakkabı' || turRaw == 'topuklu ayakkabı' || turRaw == 'heels' || turRaw == 'loafer' || turRaw == 'loafers' || turRaw == 'sandalet' || turRaw == 'sandals') {
              matchedTur = 'Ayakkabı';
            } else if (turRaw == 'çanta' || turRaw == 'bag' || turRaw == 'backpack' || turRaw == 'handbag' || turRaw == 'sırt çantası' || turRaw == 'el çantası') {
              matchedTur = 'Çanta';
            } else if (turRaw == 'aksesuar' || turRaw == 'accessory' || turRaw == 'şapka' || turRaw == 'hat' || turRaw == 'bere' || turRaw == 'beanie' || turRaw == 'eşarp' || turRaw == 'scarf' || turRaw == 'kemer' || turRaw == 'belt' || turRaw == 'kravat' || turRaw == 'tie') {
              matchedTur = 'Aksesuar';
            } else {
              matchedTur = _turler.firstWhere(
                (t) => t.toLowerCase() == turRaw || turRaw.contains(t.toLowerCase()) || t.toLowerCase().contains(turRaw),
                orElse: () => '',
              );
            }
            if (matchedTur.isNotEmpty) _tur = matchedTur;

            // 2. Renk (Color) Matching
            final renkRaw = (analysis['renk'] as String? ?? '').trim().toLowerCase();
            if (renkRaw.isNotEmpty) {
              for (var mc in clothingColors) {
                final mcName = mc.name.toLowerCase();
                if (mcName == renkRaw || renkRaw.contains(mcName) || mcName.contains(renkRaw)) {
                  _selectedColor = SelectedColor(
                    name: mc.name,
                    hexCode: mc.primaryHex,
                    parentCategoryId: mc.id,
                  );
                  break;
                }
                for (var sc in mc.subColors) {
                  final scName = sc.name.toLowerCase();
                  if (scName == renkRaw || renkRaw.contains(scName) || scName.contains(renkRaw)) {
                    _selectedColor = SelectedColor(
                      name: sc.name,
                      hexCode: sc.hex,
                      parentCategoryId: mc.id,
                    );
                    break;
                  }
                }
              }
            }

            // 3. Mevsim (Season) Matching
            final mevsimRaw = (analysis['mevsim'] as String? ?? '').trim().toLowerCase();
            String matchedMevsim = '';
            if (mevsimRaw.contains('yaz') || mevsimRaw == 'summer') {
              matchedMevsim = 'Yaz';
            } else if (mevsimRaw.contains('kış') || mevsimRaw.contains('kis') || mevsimRaw == 'winter') {
              matchedMevsim = 'Kış';
            } else if (mevsimRaw.contains('ilkbahar') || mevsimRaw == 'spring') {
              matchedMevsim = 'İlkbahar';
            } else if (mevsimRaw.contains('sonbahar') || mevsimRaw == 'autumn') {
              matchedMevsim = 'Sonbahar';
            } else if (mevsimRaw.contains('tüm') || mevsimRaw.contains('tum') || mevsimRaw.contains('all')) {
              matchedMevsim = 'Tüm Sezon';
            } else {
              matchedMevsim = _mevsimler.firstWhere(
                (m) => m.toLowerCase() == mevsimRaw,
                orElse: () => '',
              );
            }
            if (matchedMevsim.isNotEmpty) _mevsim = matchedMevsim;
          }
        });

        if (analysis != null) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text(
              s.isTr 
                ? '✨ AI analiz: ${analysis['tur'] ?? ''} (${analysis['renk'] ?? ''}, ${analysis['stil_etiketi'] ?? ''})'
                : '✨ AI Analysis: ${s.translateWardrobe(analysis['tur']?.toString() ?? '')} (${analysis['renk'] ?? ''}, ${analysis['stil_etiketi'] ?? ''})',
            ),
            backgroundColor: Theme.of(context).colorScheme.primary,
            duration: const Duration(seconds: 3),
          ));
        } else if (url != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(s.isTr ? 'Görsel yüklendi' : 'Image uploaded')),
          );
        }
      }
    } catch (e) {
      debugPrint('Upload/Analyze error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${s.isTr ? "Yükleme hatası" : "Upload error"}: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isAnalyzing = false);
    }
  }

  Future<void> _submit() async {
    final s = ref.read(stringsProvider);
    final userId = ref.read(authProvider).currentUserId;
    if (userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(s.isTr ? 'Giriş yapmanız gerekiyor.' : 'Please log in first.')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      // Görsel zaten _pickImage'da yüklendi; yoksa şimdi yükle
      String? imageUrl = _uploadedImageUrl;
      if (_selectedImage != null && imageUrl == null) {
        final uploadResult =
            await ApiService().uploadImageForAnalysis(_selectedImage!);
        imageUrl = uploadResult['url'] as String?;
      }

      final itemData = <String, dynamic>{
        'tur': _tur.toLowerCase(),
        'renk': _selectedColor?.name ?? 'Belirsiz',
        'renk_hex': _selectedColor?.hexCode,
        'renk_kategori_id': _selectedColor?.parentCategoryId,
        'marka': _markaCtrl.text.isEmpty ? null : _markaCtrl.text,
        'beden': _bedenCtrl.text.isEmpty ? null : _bedenCtrl.text,
        'mevsim': _mevsim.toLowerCase(),
        'temiz': true,
        if (imageUrl != null) 'foto_url': imageUrl,
        if (_aiAnalysis?['stil_etiketi'] != null)
          'stil_etiketi': _aiAnalysis!['stil_etiketi'],
      };

      await ApiService().addCloth(userId, itemData);

      if (mounted) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(s.isTr ? '✅ Kıyafet başarıyla eklendi!' : '✅ Clothing added successfully!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${s.isTr ? "Hata" : "Error"}: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }


  void _showImageSourceSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Theme.of(context).cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 8),
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color:
                    Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),
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
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(stringsProvider);
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text('Add Clothing',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white)),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        elevation: 0,
        iconTheme: IconThemeData(
            color:
                Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
        actions: [
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
                  child: Text('Save',
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
            // ── Fotoğraf Seçimi ─────────────────────────
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
                    ? Stack(
                        fit: StackFit.expand,
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(14),
                            child:
                                Image.file(_selectedImage!, fit: BoxFit.cover),
                          ),
                          if (_isAnalyzing)
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.black.withOpacity(0.5),
                                borderRadius: BorderRadius.circular(14),
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  CircularProgressIndicator(
                                      color: Theme.of(context)
                                          .colorScheme
                                          .primary),
                                  SizedBox(height: 12),
                                  Text(
                                    'AI Analyzing...',
                                    style: TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold),
                                  ),
                                ],
                              ),
                            ),
                        ],
                      )
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
                          Text('Add photo',
                              style: TextStyle(
                                  color: Theme.of(context)
                                          .textTheme
                                          .bodySmall
                                          ?.color ??
                                      Colors.grey,
                                  fontSize: 15)),
                          const SizedBox(height: 4),
                          Text('Select from camera or library',
                              style: TextStyle(
                                  color: Theme.of(context)
                                          .textTheme
                                          .bodySmall
                                          ?.color ??
                                      Colors.grey,
                                  fontSize: 12)),
                        ],
                      ),
              ),
            ),

            const SizedBox(height: 24),

            // ── Kategori ────────────────────────────────
            _SectionLabel(text: 'Type *'),
            _DropdownField(
              value: _tur,
              items: _turler,
              onChanged: (v) => setState(() => _tur = v!),
              displayTranslator: (val) =>
                  s.translateWardrobe(val), // Force translate to English
            ),

            const SizedBox(height: 16),

            // ── Renk ────────────────────────────────────
            _SectionLabel(text: 'Color *'),
            ClothingColorPicker(
              initialColor: _selectedColor,
              onColorSelected: (color) {
                setState(() => _selectedColor = color);
              },
            ),

            const SizedBox(height: 16),

            // ── Mevsim ──────────────────────────────────
            _SectionLabel(text: 'Season'),
            _DropdownField(
              value: _mevsim,
              items: _mevsimler,
              onChanged: (v) => setState(() => _mevsim = v!),
              displayTranslator: (val) =>
                  s.translateWardrobe(val), // Force translate to English
            ),

            const SizedBox(height: 16),

            // ── Marka ───────────────────────────────────
            _SectionLabel(text: 'Brand (optional)'),
            _TextField(controller: _markaCtrl, hint: 'Nike, Zara, H&M...'),

            const SizedBox(height: 16),

            // ── Beden ───────────────────────────────────
            _SectionLabel(text: 'Size (optional)'),
            _TextField(
                controller: _bedenCtrl, hint: 'XS, S, M, L, XL, 36, 38...'),

            const SizedBox(height: 40),

            // ── Kaydet Butonu ───────────────────────────
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _submit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14)),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(
                        color: Colors.white, strokeWidth: 2)
                    : const Text('Add Clothing',
                        style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white)),
              ),
            ),

            const SizedBox(height: 20),
          ],
        ),
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
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(text,
          style: TextStyle(
              color:
                  Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey,
              fontSize: 13,
              fontWeight: FontWeight.w500)),
    );
  }
}

class _DropdownField extends StatelessWidget {
  final String value;
  final List<String> items;
  final void Function(String?) onChanged;
  final String Function(String)? displayTranslator;

  const _DropdownField({
    required this.value,
    required this.items,
    required this.onChanged,
    this.displayTranslator,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
      ),
      child: DropdownButton<String>(
        value: value,
        isExpanded: true,
        underline: const SizedBox(),
        dropdownColor: Theme.of(context).cardColor,
        style: TextStyle(
            color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
            fontSize: 15),
        items: items
            .map((e) => DropdownMenuItem(
                value: e,
                child: Text(
                    displayTranslator != null ? displayTranslator!(e) : e)))
            .toList(),
        onChanged: onChanged,
      ),
    );
  }
}

class _TextField extends StatelessWidget {
  final TextEditingController controller;
  final String hint;

  const _TextField({required this.controller, required this.hint});

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      style: TextStyle(
          color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: TextStyle(
            color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey),
        filled: true,
        fillColor: Theme.of(context).colorScheme.surface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Theme.of(context).dividerColor),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Theme.of(context).dividerColor),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Theme.of(context).colorScheme.primary),
        ),
      ),
    );
  }
}
