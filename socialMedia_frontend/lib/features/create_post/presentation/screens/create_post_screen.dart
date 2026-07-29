import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/create_post/presentation/providers/create_post_provider.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../../features/create_post/presentation/widgets/visibility_selector.dart';
import '../../../../features/create_post/presentation/widgets/outfit_picker.dart';
import '../../../../features/feed/presentation/providers/feed_provider.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/navigation/app_navigator.dart';
import '../../../../features/profile/presentation/providers/profile_provider.dart';
import '../../../../services/api_service.dart';
import '../../../../features/feed/domain/models/outfit_item_model.dart';

class CreatePostScreen extends ConsumerStatefulWidget {
  const CreatePostScreen({super.key});

  @override
  ConsumerState<CreatePostScreen> createState() => _CreatePostScreenState();
}

class _CreatePostScreenState extends ConsumerState<CreatePostScreen> {
  late TextEditingController _captionController;
  CreatePostProvider? _provider;

  @override
  void initState() {
    super.initState();
    _captionController = TextEditingController();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _provider = ref.read(createPostProvider);
      _provider!.addListener(_syncCaption);
    });
  }

  void _syncCaption() {
    final provider = ref.read(createPostProvider);
    if (_captionController.text != provider.caption) {
      _captionController.text = provider.caption;
      _captionController.selection = TextSelection.fromPosition(
        TextPosition(offset: provider.caption.length),
      );
    }
  }

  @override
  void dispose() {
    _provider?.removeListener(_syncCaption);
    _captionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Yeni Paylaşım',
          semanticsLabel: 'Yeni paylaşım oluştur',
        ),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        leading: IconButton(
          icon: const Icon(Icons.close_rounded),
          onPressed: () {
            ref.read(createPostProvider).clearForm();
            Navigator.of(context).pop();
          },
          tooltip: 'Kapat',
        ),
      ),
      body: Consumer(
        builder: (context, ref, _) {
          final provider = ref.watch(createPostProvider);
          return SingleChildScrollView(
            padding: const EdgeInsets.symmetric(
              horizontal: AppTheme.spacingL,
              vertical: AppTheme.spacingL,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ─── Section 1: Görsel Seçimi ─────────────────
                _buildSectionTitle('📸 Görsel'),
                const SizedBox(height: AppTheme.spacingM),
                _buildImagePicker(provider),

                const SizedBox(height: AppTheme.spacingXL),

                // ─── Section 2: Kombin Parçaları ──────────────
                _buildSectionTitle('👗 Kombin Parçaları'),
                const SizedBox(height: AppTheme.spacingM),
                OutfitPicker(
                  items: provider.mockOutfitItems,
                  selectedItems: provider.selectedOutfitItems,
                  onToggle: (item) => provider.toggleOutfitItem(item),
                ),

                const SizedBox(height: AppTheme.spacingXL),

                // ─── Section 3: Caption ───────────────────────
                _buildSectionTitle('✏️ Açıklama'),
                const SizedBox(height: AppTheme.spacingM),
                _buildCaptionField(provider),

                const SizedBox(height: AppTheme.spacingXL),

                // ─── Section 4: Gizlilik ──────────────────────
                _buildSectionTitle('🔐 Gizlilik'),
                const SizedBox(height: AppTheme.spacingM),
                VisibilitySelector(
                  currentValue: provider.visibility,
                  onChanged: (value) => provider.setVisibility(value),
                ),

                const SizedBox(height: AppTheme.spacingXL),

                // ─── Section 5: AI Eğitim İzni ───────────────
                _buildAiConsentRow(provider),

                const SizedBox(height: AppTheme.spacingXL),

                // ─── Error Message ────────────────────────────
                if (provider.errorMessage != null)
                  _buildErrorMessage(provider.errorMessage!),

                // ─── Section 6: Paylaş Butonu ─────────────────
                _buildSubmitButton(provider),

                const SizedBox(height: AppTheme.spacingXXL),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: TextStyle(
        color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
        fontSize: 18,
        fontWeight: FontWeight.w600,
      ),
    );
  }

  Widget _buildImagePicker(CreatePostProvider provider) {
    if (provider.selectedImage != null) {
      return _buildSelectedImage(provider);
    }
    if (provider.isCollage && provider.selectedOutfitItems.isNotEmpty) {
      return _buildCollageGrid(provider);
    }
    return _buildImagePlaceholder(provider);
  }

  Widget _buildImagePlaceholder(CreatePostProvider provider) {
    return Column(
      children: [
        GestureDetector(
          onTap: () => provider.pickImage(),
          child: Semantics(
            label: 'Galeriden görsel seç',
            child: Container(
              height: 140,
              width: double.infinity,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
                color:
                    Theme.of(context).colorScheme.primary.withValues(alpha: 0.05),
              ),
              child: CustomPaint(
                painter: _DashedBorderPainter(
                  color:
                      Theme.of(context).colorScheme.primary.withValues(alpha: 0.3),
                  borderRadius: AppTheme.radiusLarge,
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.add_photo_alternate_rounded,
                      size: 36,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: AppTheme.spacingM),
                    const Text(
                      'Galeriden Seç',
                      style: TextStyle(
                        color: AppTheme.accentPurple,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: AppTheme.spacingM),
        GestureDetector(
          onTap: () => _showOutfitSelection(provider),
          child: Semantics(
            label: 'Kombinlerimden Seç',
            child: Container(
              height: 80,
              width: double.infinity,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
                color: Theme.of(context).colorScheme.secondary.withValues(alpha: 0.1),
                border: Border.all(
                  color: Theme.of(context).colorScheme.secondary.withValues(alpha: 0.3),
                )
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.style_rounded,
                    size: 28,
                    color: Theme.of(context).colorScheme.secondary,
                  ),
                  const SizedBox(width: AppTheme.spacingM),
                  Text(
                    'Kombinlerimden Seç',
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.secondary,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCollageGrid(CreatePostProvider provider) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppTheme.spacingM),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
        color: Theme.of(context).colorScheme.surface,
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Kombin Kolajı',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
              TextButton.icon(
                onPressed: () {
                  provider.setCollage(false);
                },
                icon: const Icon(Icons.close, size: 16, color: Colors.grey),
                label: const Text('İptal', style: TextStyle(color: Colors.grey)),
              )
            ],
          ),
          const SizedBox(height: AppTheme.spacingS),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: provider.selectedOutfitItems.map((item) {
              return Container(
                width: 80,
                height: 100,
                decoration: BoxDecoration(
                  color: Colors.grey[800],
                  borderRadius: BorderRadius.circular(8),
                  image: item.imageUrl.isNotEmpty
                      ? DecorationImage(
                          image: NetworkImage(item.imageUrl),
                          fit: BoxFit.cover,
                        )
                      : null,
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  void _showOutfitSelection(CreatePostProvider provider) async {
    final userId = ref.read(authProvider).currentUserId ?? '';
    if (userId.isEmpty) return;

    showModalBottomSheet(
      context: context,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return FutureBuilder<List<dynamic>>(
          future: ApiService().getOutfits(userId),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(
                child: Text('Hata oluştu', style: TextStyle(color: Theme.of(context).colorScheme.error)),
              );
            }
            final outfits = snapshot.data ?? [];
            if (outfits.isEmpty) {
              return const Center(
                child: Text('Kayıtlı kombininiz bulunmuyor.', style: TextStyle(color: Colors.grey)),
              );
            }
            return ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: outfits.length,
              itemBuilder: (context, index) {
                final outfit = outfits[index];
                final kiyafetler = outfit['kiyafetler'] as List<dynamic>? ?? [];
                
                return ListTile(
                  title: const Text('Kombin Önerisi'),
                  subtitle: Text(outfit['aciklama']?.toString() ?? '', maxLines: 1, overflow: TextOverflow.ellipsis),
                  leading: const Icon(Icons.style_rounded, color: AppTheme.accentPurple),
                  onTap: () {
                    // Kıyafetleri OutfitItem modeline çevir
                    final outfitItems = kiyafetler.map((k) {
                      return OutfitItem(
                        itemId: k['id'].toString(),
                        category: k['tur'] ?? 'diğer',
                        imageUrl: ApiService.fixImageUrl(k['foto_url']?.toString() ?? ''),
                      );
                    }).toList();
                    
                    provider.setCollage(true);
                    provider.setSelectedOutfitItems(outfitItems);
                    Navigator.pop(context);
                  },
                );
              },
            );
          },
        );
      },
    );
  }

  Widget _buildSelectedImage(CreatePostProvider provider) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
      child: Stack(
        children: [
          AspectRatio(
            aspectRatio: 4 / 5,
            child: Image.file(
              provider.selectedImage!,
              fit: BoxFit.cover,
              semanticLabel: 'Seçilen görsel',
            ),
          ),
          // ─── Change Button Overlay ──────────────────────────
          Positioned(
            top: AppTheme.spacingM,
            right: AppTheme.spacingM,
            child: GestureDetector(
              onTap: () => provider.pickImage(),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppTheme.spacingM,
                  vertical: AppTheme.spacingS,
                ),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.6),
                  borderRadius: BorderRadius.circular(AppTheme.radiusRound),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.swap_horiz_rounded,
                      color: Colors.white,
                      size: 18,
                    ),
                    SizedBox(width: AppTheme.spacingXS),
                    Text(
                      'Değiştir',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCaptionField(CreatePostProvider provider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ─── LLaVA Tespit Chip'leri ──────────────────────────────
        if (provider.detectedItems.isNotEmpty) ..._buildDetectedItemChips(provider),

        // ─── Metin Alanı ────────────────────────────────────────
        TextFormField(
          controller: _captionController,
          maxLines: 5,
          maxLength: 1500,
          onChanged: (value) => provider.setCaption(value),
          style: TextStyle(
            color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
            fontSize: 14,
          ),
          decoration: InputDecoration(
            hintText: provider.selectedImage != null
                ? 'Kombin hikayeni yazın ya da AI\'a oluşturmasını bırakın...'
                : 'Kombinin hakkında bir şeyler yaz...',
            counterStyle: TextStyle(
              color:
                  Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey,
              fontSize: 11,
            ),
            filled: true,
            fillColor: Theme.of(context).colorScheme.surface,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
              borderSide: BorderSide(color: Theme.of(context).dividerColor),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
              borderSide: BorderSide(color: Theme.of(context).dividerColor),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
              borderSide: BorderSide(
                  color: Theme.of(context).colorScheme.primary, width: 1.5),
            ),
          ),
        ),
        const SizedBox(height: AppTheme.spacingS),

        // ─── AI Buton ────────────────────────────────────────
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: provider.isSuggestingCaption
                ? null
                : () => provider.suggestCaption(),
            icon: provider.isSuggestingCaption
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: AppTheme.accentPurple,
                    ),
                  )
                : Text(
                    provider.selectedImage != null ? '🧥' : '✨',
                    style: const TextStyle(fontSize: 16),
                  ),
            label: Text(
              provider.isSuggestingCaption
                  ? (provider.selectedImage != null
                      ? 'Kıyafetler analiz ediliyor...'
                      : 'Öneri alınıyor...')
                  : (provider.selectedImage != null
                      ? 'Kombini Analiz Et (Moondream + AI)'
                      : 'AI Öneri Al'),
            ),
            style: OutlinedButton.styleFrom(
              foregroundColor: AppTheme.accentPurple,
              side: BorderSide(
                color: AppTheme.accentPurple.withValues(alpha: 0.5),
              ),
              padding: const EdgeInsets.symmetric(
                vertical: AppTheme.spacingM,
              ),
            ),
          ),
        ),

        // ─── Pipeline bilgi notu ──────────────────────────────
        if (provider.selectedImage != null)
          Padding(
            padding: const EdgeInsets.only(top: AppTheme.spacingXS),
            child: Text(
              'LLaVA ile kıyafet tespiti → Ollama ile kombin açıklaması',
              style: TextStyle(
                color: (Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey)
                    .withValues(alpha: 0.6),
                fontSize: 10,
              ),
              textAlign: TextAlign.center,
            ),
          ),
      ],
    );
  }

  /// LLaVA tarafından tespit edilen kıyafetleri chip olarak gösterir
  List<Widget> _buildDetectedItemChips(CreatePostProvider provider) {
    final colors = [
      const Color(0xFF6C63FF),
      const Color(0xFF00B4D8),
      const Color(0xFFFF6B9D),
      const Color(0xFF43AA8B),
      const Color(0xFFF9844A),
      const Color(0xFF90BE6D),
    ];

    return [
      const SizedBox(height: AppTheme.spacingXS),
      Text(
        'LLaVA ile Tespit Edilen Kıyafetler:',
        style: TextStyle(
          color: (Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey)
              .withValues(alpha: 0.8),
          fontSize: 11,
          fontWeight: FontWeight.w600,
        ),
      ),
      const SizedBox(height: AppTheme.spacingXS),
      Wrap(
        spacing: 6,
        runSpacing: 4,
        children: provider.detectedItems.asMap().entries.map((entry) {
          final idx = entry.key;
          final item = entry.value;
          final color = colors[idx % colors.length];
          final label = [
            item['tur'] ?? '',
            if ((item['renk'] as String?)?.isNotEmpty == true) item['renk'],
            if ((item['stil'] as String?)?.isNotEmpty == true) item['stil'],
          ].join(' • ');
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: color.withValues(alpha: 0.4)),
            ),
            child: Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: 11,
                fontWeight: FontWeight.w500,
              ),
            ),
          );
        }).toList(),
      ),
      const SizedBox(height: AppTheme.spacingS),
    ];
  }

  Widget _buildAiConsentRow(CreatePostProvider provider) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingM),
      decoration: AppTheme.glassDecoration(opacity: 0.05),
      child: Row(
        children: [
          Checkbox(
            value: provider.aiTrainingConsent,
            onChanged: (value) => provider.setAiTrainingConsent(value ?? false),
          ),
          const SizedBox(width: AppTheme.spacingS),
          Expanded(
            child: Semantics(
              label: 'AI eğitim izni',
              child: GestureDetector(
                onTap: () =>
                    provider.setAiTrainingConsent(!provider.aiTrainingConsent),
                child: Text(
                  'Bu görsel, modelin gelişmesi için kullanılabilir',
                  style: TextStyle(
                    color: Theme.of(context).textTheme.bodyMedium?.color ??
                        Colors.grey,
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorMessage(String message) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingM),
      child: Row(
        children: [
          Icon(
            Icons.error_outline_rounded,
            color: Theme.of(context).colorScheme.error,
            size: 16,
          ),
          const SizedBox(width: AppTheme.spacingS),
          Expanded(
            child: Text(
              message,
              style: TextStyle(
                color: Theme.of(context).colorScheme.error,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSubmitButton(CreatePostProvider provider) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 200),
        opacity: provider.isFormValid ? 1.0 : 0.5,
        child: Container(
          decoration: AppTheme.gradientButtonDecoration(),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: provider.isFormValid && !provider.isSubmitting
                  ? () => _handleSubmit(provider)
                  : null,
              borderRadius: BorderRadius.circular(AppTheme.radiusRound),
              child: Center(
                child: provider.isSubmitting
                    ? const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: Colors.white,
                        ),
                      )
                    : const Text(
                        'Paylaş',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.5,
                        ),
                      ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _handleSubmit(CreatePostProvider provider) async {
    final authProv = ref.read(authProvider);
    final userId = authProv.currentUserId ?? '';
    if (userId.isEmpty) return;

    final result = await provider.submitPost(userId);
    if (result != null && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Row(
            children: [
              Icon(Icons.check_circle_rounded, color: Colors.green, size: 20),
              SizedBox(width: AppTheme.spacingS),
              Text('Paylaşım başarıyla oluşturuldu! 🎉'),
            ],
          ),
          backgroundColor: Theme.of(context).cardColor,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
          ),
          duration: const Duration(seconds: 2),
        ),
      );
      provider.clearForm();
      // Feed'i ve Profil'i güncelle
      ref.read(feedProvider).loadFeed();
      // Profil Provider'ı da güncelle ki anında podyuma düşsün
      final currentUserId = ref.read(authProvider).currentUserId;
      if (currentUserId != null) {
        ref.read(profileProvider.notifier).loadProfile(currentUserId, currentUserId);
      }
      
      // Ekranı kapat
      Navigator.of(context).pop(true);
    }
  }
}

/// Dashed border painter for image placeholder
class _DashedBorderPainter extends CustomPainter {
  final Color color;
  final double borderRadius;

  _DashedBorderPainter({
    required this.color,
    required this.borderRadius,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // No-op: using container border instead for simplicity
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
