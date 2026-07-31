import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import '../../../../features/feed/domain/models/outfit_item_model.dart';
import '../../../../services/api_service.dart';

final createPostProvider =
    ChangeNotifierProvider((ref) => CreatePostProvider());

class CreatePostProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  final ImagePicker _picker = ImagePicker();

  File? _selectedImage;
  File? get selectedImage => _selectedImage;

  String _caption = '';
  String get caption => _caption;

  String _visibility = 'public';
  String get visibility => _visibility;

  bool _aiTrainingConsent = false;
  bool get aiTrainingConsent => _aiTrainingConsent;

  List<OutfitItem> _selectedOutfitItems = [];
  List<OutfitItem> get selectedOutfitItems => _selectedOutfitItems;

  bool _isSubmitting = false;
  bool get isSubmitting => _isSubmitting;

  bool _isSuggestingCaption = false;
  bool get isSuggestingCaption => _isSuggestingCaption;

  String _suggestedCaption = '';
  String get suggestedCaption => _suggestedCaption;

  /// Moondream tarafından tespit edilen kıyafetler
  List<Map<String, dynamic>> _detectedItems = [];
  List<Map<String, dynamic>> get detectedItems => _detectedItems;

  /// Ollama tarafından üretilen kombin açıklaması
  String _outfitStory = '';
  String get outfitStory => _outfitStory;

  /// Yüklenen görselin backend URL'si (outfit-story için)
  String? _uploadedImageUrl;
  String? get uploadedImageUrl => _uploadedImageUrl;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  // isFormValid is now defined later in the file.

  // ─── Mock Outfit Items (UI'da gösterim için) ───────────────
  List<OutfitItem> get mockOutfitItems => [
        OutfitItem(
          itemId: 'item-001',
          category: 'üst giyim',
          imageUrl: '${ApiService.baseUrl}/static/categories/miyazaki_top.png',
        ),
        OutfitItem(
          itemId: 'item-002',
          category: 'alt giyim',
          imageUrl:
              '${ApiService.baseUrl}/static/categories/miyazaki_bottom.png',
        ),
        OutfitItem(
          itemId: 'item-003',
          category: 'ayakkabı',
          imageUrl:
              '${ApiService.baseUrl}/static/categories/miyazaki_shoes.png',
        ),
        OutfitItem(
          itemId: 'item-004',
          category: 'aksesuar',
          imageUrl:
              '${ApiService.baseUrl}/static/categories/miyazaki_accessory.png',
        ),
        OutfitItem(
          itemId: 'item-005',
          category: 'dış giyim',
          imageUrl:
              '${ApiService.baseUrl}/static/categories/miyazaki_jacket.png',
        ),
        OutfitItem(
          itemId: 'item-006',
          category: 'diğer',
          imageUrl: '${ApiService.baseUrl}/static/categories/miyazaki_bag.png',
        ),
      ];

  // ─── Görsel Seçimi ──────────────────────────────────────────
  Future<void> pickImage() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );
      if (image != null) {
        _selectedImage = File(image.path);
        _errorMessage = null;
        notifyListeners();
      }
    } catch (e) {
      _errorMessage = 'Görsel seçilirken bir hata oluştu.';
      debugPrint('Görsel seçme hatası: $e');
      notifyListeners();
    }
  }

  /// Seçili görseli backend'e yükler ve URL + ai_analysis döndürür.
  Future<Map<String, dynamic>?> _uploadImageWithAnalysis(File file) async {
    try {
      final result = await _api.uploadImageForAnalysis(file);
      return result;
    } catch (e) {
      debugPrint('Upload exception: $e');
      return null;
    }
  }

  // ─── Caption Ayarla ─────────────────────────────────────────
  void setCaption(String value) {
    _caption = value;
    notifyListeners();
  }

  // ─── Gizlilik Ayarla ───────────────────────────────────────
  void setVisibility(String value) {
    _visibility = value;
    notifyListeners();
  }

  // ─── AI Eğitim İzni ────────────────────────────────────────
  void setAiTrainingConsent(bool value) {
    _aiTrainingConsent = value;
    notifyListeners();
  }

  // ─── Outfit Item Seç/Kaldır ─────────────────────────────────
  void toggleOutfitItem(OutfitItem item) {
    if (_selectedOutfitItems.contains(item)) {
      _selectedOutfitItems.remove(item);
    } else {
      _selectedOutfitItems.add(item);
    }
    notifyListeners();
  }

  // ─── AI Caption Önerisi ───────────────────────────────────────
  /// Görsel seçilmişse: LLaVA+Ollama pipeline çalıştırır
  /// Görsel yoksa: Eski llama3.2 metin fallback'ını kullanır
  Future<void> suggestCaption() async {
    _isSuggestingCaption = true;
    _errorMessage = null;
    _detectedItems = [];
    _outfitStory = '';
    notifyListeners();

    try {
      if (_selectedImage != null) {
        // ─── LLaVA + Ollama Pipeline ──────────────────────────────
        // Adım 1: Görseli yükle, FashionSigLIP analizi al
        final uploadResult = await _uploadImageWithAnalysis(_selectedImage!);
        if (uploadResult == null) {
          _errorMessage = 'Görsel yüklenemedi. Bağlantınızı kontrol edin.';
          _isSuggestingCaption = false;
          notifyListeners();
          return;
        }

        final imageUrl = uploadResult['url'] as String? ?? '';
        _uploadedImageUrl = imageUrl;
        final aiAnalysis = uploadResult['ai_analysis'] as Map<String, dynamic>?;

        // Adım 2: LLaVA tespit + Ollama hikaye pipeline
        final storyResult = await _api.generateOutfitStory(
          imageUrl: imageUrl,
          aiAnalysis: aiAnalysis,
        );

        final detectedRaw = storyResult['detected_items'];
        if (detectedRaw is List) {
          _detectedItems = detectedRaw
              .whereType<Map<String, dynamic>>()
              .toList();
        }

        final story = storyResult['outfit_story'] as String? ?? '';
        if (story.isNotEmpty) {
          _outfitStory = story;
          _caption = story;
          _suggestedCaption = story;
        } else {
          _errorMessage = 'AI açıklama üretemedi, lütfen manuel yazın.';
        }
      } else {
        // ─── Görsel yoksa eski fallback ──────────────────────────────
        final items = _selectedOutfitItems.isNotEmpty
            ? _selectedOutfitItems
            : <OutfitItem>[
                const OutfitItem(itemId: '', category: 'diğer', imageUrl: ''),
              ];
        final caption = await _api.suggestCaption(outfitItems: items);
        if (caption.isNotEmpty) {
          _suggestedCaption = caption;
          _caption = caption;
        } else {
          _errorMessage = 'AI caption üretemedi, lütfen manuel yazın.';
        }
      }
    } on ApiException catch (e) {
      _errorMessage = e.message;
      debugPrint('Caption önerisi hatası: ${e.message}');
    } catch (e) {
      _errorMessage = 'Caption önerisi alınamadı.';
      debugPrint('Caption önerisi hatası: $e');
    }

    _isSuggestingCaption = false;
    notifyListeners();
  }

  bool _isCollage = false;
  bool get isCollage => _isCollage;

  void setCollage(bool value) {
    _isCollage = value;
    if (value) {
      _selectedImage = null; // Clear image if collage selected
    }
    notifyListeners();
  }

  void setSelectedOutfitItems(List<OutfitItem> items) {
    _selectedOutfitItems = List.from(items);
    notifyListeners();
  }

  /// Form geçerliliği: Görsel seçili olmalı VEYA kolaj modu aktif olmalı, VE en az 1 parça olmalı
  bool get isFormValid =>
      (_selectedImage != null || _isCollage) && _selectedOutfitItems.isNotEmpty;

  // ─── Gönderi Paylaş ─────────────────────────────────────────
  Future<String?> submitPost(String userId) async {
    if (!isFormValid) {
      if (_selectedImage == null && !_isCollage) {
        _errorMessage = 'Lütfen bir görsel seçin veya kombin kolajı oluşturun.';
      } else if (_selectedOutfitItems.isEmpty) {
        _errorMessage = 'Lütfen en az 1 kombin parçası seçin.';
      }
      notifyListeners();
      return null;
    }

    _isSubmitting = true;
    _errorMessage = null;
    notifyListeners();

    try {
      String? imageUrl;
      
      if (_isCollage) {
        imageUrl = 'collage';
      } else {
        // 1. Görseli backend'e yükle
        // AI öneri sırasında zaten yüklendiyse URL'yi yeniden kullan
        if (_uploadedImageUrl != null && _uploadedImageUrl!.isNotEmpty) {
          imageUrl = _uploadedImageUrl;
        } else {
          final uploadResult = await _uploadImageWithAnalysis(selectedImage!);
          imageUrl = uploadResult?['url'] as String?;
        }

        // Upload başarısız olursa hata göster
        if (imageUrl == null || imageUrl.isEmpty) {
          _isSubmitting = false;
          _errorMessage = 'Görsel yüklenemedi. Bağlantınızı kontrol edin.';
          notifyListeners();
          return null;
        }
      }

      // 2. Post oluştur
      final postId = await _api.createPost(
        userId: userId,
        imageUrl: imageUrl,
        caption: _caption,
        outfitItems: _selectedOutfitItems,
        visibility: _visibility,
        aiTrainingConsent: _aiTrainingConsent,
      );

      _isSubmitting = false;
      notifyListeners();
      return postId.isNotEmpty ? postId : null;
    } on ApiException catch (e) {
      _isSubmitting = false;
      _errorMessage = e.message;
      notifyListeners();
      debugPrint('Paylaşım hatası: ${e.message}');
      return null;
    } catch (e) {
      _isSubmitting = false;
      _errorMessage = 'Paylaşım sırasında bir hata oluştu.';
      notifyListeners();
      debugPrint('Paylaşım hatası: $e');
      return null;
    }
  }

  // ─── Formu Temizle ───────────────────────────────────────────
  void clearForm() {
    _selectedImage = null;
    _caption = '';
    _visibility = 'public';
    _aiTrainingConsent = false;
    _selectedOutfitItems = [];
    _isSubmitting = false;
    _isSuggestingCaption = false;
    _suggestedCaption = '';
    _detectedItems = [];
    _outfitStory = '';
    _uploadedImageUrl = null;
    _errorMessage = null;
    _isCollage = false;
    notifyListeners();
  }
}
