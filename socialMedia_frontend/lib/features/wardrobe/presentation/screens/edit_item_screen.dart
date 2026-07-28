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
  ];

  static const _mevsimler = ['Yaz', 'Kış', 'İlkbahar', 'Sonbahar', 'Tüm Sezon'];

  @override
  void initState() {
    super.initState();
    final rawTur = widget.initialItem['tur']?.toString() ?? '';
    _tur = _matchInitialValue(rawTur, _turler);

    final renk = widget.initialItem['renk'] as String?;
    final renkHex = widget.initialItem['renk_hex'] as String?;
    final renkCatId = widget.initialItem['renk_kategori_id'] as String?;
    if (renk != null && renk.isNotEmpty) {
      _selectedColor = SelectedColor(
        name: renk,
        hexCode: renkHex ?? '#000000',
        parentCategoryId: renkCatId ?? 'siyah',
      );
    }

    final rawMevsim = widget.initialItem['mevsim']?.toString() ?? '';
    _mevsim = _matchInitialValue(rawMevsim, _mevsimler);

    _markaCtrl.text = widget.initialItem['marka'] ?? '';
    _bedenCtrl.text = widget.initialItem['beden'] ?? '';

    _isFavorite = widget.initialItem['is_favorite'] == 1 || widget.initialItem['is_favorite'] == true;
    _isDirty = widget.initialItem['temiz'] == 0 || widget.initialItem['temiz'] == false || widget.initialItem['is_dirty'] == 1 || widget.initialItem['is_dirty'] == true;
  }

  String _matchInitialValue(String raw, List<String> items) {
    if (raw.isEmpty) return items.first;
    final r = raw.trim().toLowerCase();

    for (var item in items) {
      if (item.toLowerCase() == r) return item;
    }

    if (r == 'tişört' || r == 't-shirt' || r == 'tshirt') return 'Tişört';
    if (r == 'gömlek' || r == 'shirt') return 'Gömlek';
    if (r == 'bluz' || r == 'blouse') return 'Bluz';
    if (r == 'kazak' || r == 'sweater' || r == 'hırka' || r == 'cardigan') return 'Kazak';
    if (r == 'sweatshirt' || r == 'hoodie') return 'Sweatshirt';
    if (r == 'pantolon' || r == 'jean' || r == 'jeans' || r == 'trousers' || r == 'eşofman altı' || r == 'tayt' || r == 'alt giyim') return 'Pantolon';
    if (r == 'şort' || r == 'shorts') return 'Şort';
    if (r == 'etek' || r == 'skirt') return 'Etek';
    if (r == 'elbise' || r == 'dress' || r == 'tulum' || r == 'jumpsuit') return 'Elbise';
    if (r == 'ceket' || r == 'jacket' || r == 'blazer' || r == 'yelek' || r == 'dış giyim') return 'Ceket';
    if (r == 'mont' || r == 'coat' || r == 'kaban' || r == 'parka') return 'Mont';
    if (r == 'sneaker' || r == 'sneakers' || r == 'spor ayakkabı') return 'Sneaker';
    if (r == 'bot' || r == 'boots') return 'Bot';
    if (r == 'ayakkabı' || r == 'topuklu ayakkabı' || r == 'heels' || r == 'loafer' || r == 'sandalet') return 'Ayakkabı';
    if (r == 'çanta' || r == 'bag' || r == 'backpack' || r == 'handbag') return 'Çanta';
    if (r == 'aksesuar' || r == 'accessory' || r == 'şapka' || r == 'bere' || r == 'eşarp' || r == 'kemer' || r == 'kravat') return 'Aksesuar';

    if (r.contains('yaz') || r == 'summer') return 'Yaz';
    if (r.contains('kış') || r.contains('kis') || r == 'winter') return 'Kış';
    if (r.contains('ilkbahar') || r == 'spring') return 'İlkbahar';
    if (r.contains('sonbahar') || r == 'autumn') return 'Sonbahar';
    if (r.contains('tüm') || r.contains('tum') || r.contains('all')) return 'Tüm Sezon';

    return items.firstWhere(
      (item) => item.toLowerCase().contains(r) || r.contains(item.toLowerCase()),
      orElse: () => items.first,
    );
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
        'tur': _tur.toLowerCase(),
        'renk': _selectedColor?.name ?? 'Belirsiz',
        'renk_hex': _selectedColor?.hexCode,
        'renk_kategori_id': _selectedColor?.parentCategoryId,
        'marka': _markaCtrl.text.isEmpty ? null : _markaCtrl.text,
        'beden': _bedenCtrl.text.isEmpty ? null : _bedenCtrl.text,
        'mevsim': _mevsim.toLowerCase(),
        'temiz': !_isDirty,
        'foto_url': imageUrl,
        'is_favorite': _isFavorite,
      });

      if (mounted) {
        Navigator.pop(context, true);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(s.isTr ? '✅ Kıyafet güncellendi!' : '✅ Clothing updated!')),
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

  Future<void> _deleteItem() async {
    final s = ref.read(stringsProvider);
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Theme.of(context).cardColor,
        title: Text(s.isTr ? 'Kıyafeti Sil' : 'Delete Clothing',
            style: TextStyle(color: Theme.of(context).colorScheme.error)),
        content: Text(
            s.isTr 
              ? 'Bu kıyafeti gardırobunuzdan silmek istediğinize emin misiniz?'
              : 'Are you sure you want to delete this clothing from your wardrobe?',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(s.isTr ? 'İptal' : 'Cancel',
                style: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(s.isTr ? 'Sil' : 'Delete',
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
            SnackBar(content: Text(s.isTr ? 'Kıyafet silindi.' : 'Clothing deleted.')),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('${s.isTr ? "Silme hatası" : "Delete error"}: $e')),
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
                color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey,
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
            color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
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
                  padding: const EdgeInsets.all(16),
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

            // ── Kategori ────────────────────────────────
            const _SectionLabel(text: 'Type *'),
            _DropdownField(
              value: _tur,
              items: _turler,
              onChanged: (v) => setState(() => _tur = v!),
              displayTranslator: (val) => s.translateWardrobe(val),
            ),

            const SizedBox(height: 16),

            // ── Renk ────────────────────────────────────
            const _SectionLabel(text: 'Color *'),
            ClothingColorPicker(
              initialColor: _selectedColor,
              onColorSelected: (color) {
                setState(() => _selectedColor = color);
              },
            ),

            const SizedBox(height: 16),

            // ── Mevsim ──────────────────────────────────
            const _SectionLabel(text: 'Season'),
            _DropdownField(
              value: _mevsim,
              items: _mevsimler,
              onChanged: (v) => setState(() => _mevsim = v!),
              displayTranslator: (val) => s.translateWardrobe(val),
            ),

            const SizedBox(height: 16),

            // ── Marka ───────────────────────────────────
            const _SectionLabel(text: 'Brand (optional)'),
            _TextField(controller: _markaCtrl, hint: 'Nike, Zara, H&M...'),

            const SizedBox(height: 16),

            // ── Beden ───────────────────────────────────
            const _SectionLabel(text: 'Size (optional)'),
            _TextField(
                controller: _bedenCtrl, hint: 'XS, S, M, L, XL, 36, 38...'),

            const SizedBox(height: 24),

            // ── Kirli Sepeti Toggle ──────────────────────
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(12),
              ),
              child: SwitchListTile(
                title: Text(
                  _isDirty 
                    ? (s.isTr ? 'Kirli Sepetinde' : 'Laundry Basket')
                    : (s.isTr ? 'Dolapta (Temiz)' : 'In Closet (Clean)'),
                  style: TextStyle(
                    color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                subtitle: Text(
                  s.isTr ? 'Bu kıyafet kirli sepetinde mi?' : 'Is this clothing in the laundry basket?',
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

            // ── Sil Butonu ──────────────────────────────
            SizedBox(
              width: double.infinity,
              height: 50,
              child: OutlinedButton.icon(
                onPressed: _isDeleting ? null : _deleteItem,
                icon: _isDeleting
                    ? SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                            color: Theme.of(context).colorScheme.error,
                            strokeWidth: 2))
                    : Icon(Icons.delete_outline_rounded,
                        color: Theme.of(context).colorScheme.error),
                label: Text(
                  s.isTr ? 'Kıyafeti Sil' : 'Delete Clothing',
                  style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                      fontWeight: FontWeight.bold),
                ),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: Theme.of(context).colorScheme.error),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),

            const SizedBox(height: 40),
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
              color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey,
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
