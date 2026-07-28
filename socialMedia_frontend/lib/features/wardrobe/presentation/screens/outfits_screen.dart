import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../services/api_service.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../../core/theme/app_theme.dart';
import 'dart:convert';
import 'ai_stylist_screen.dart';
import 'create_outfit_screen.dart';

class OutfitsScreen extends ConsumerStatefulWidget {
  const OutfitsScreen({super.key});

  @override
  ConsumerState<OutfitsScreen> createState() => _OutfitsScreenState();
}

class _OutfitsScreenState extends ConsumerState<OutfitsScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<dynamic>> _outfitsFuture;

  @override
  void initState() {
    super.initState();
    _loadOutfits();
  }

  void _loadOutfits() {
    final userId = ref.read(authProvider).currentUserId ?? '';
    setState(() {
      _outfitsFuture = _apiService.getOutfits(userId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Kombinlerim'),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.add_box_outlined, color: AppTheme.accentPurple),
            tooltip: 'Manuel Kombin Oluştur',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const CreateOutfitScreen()),
              ).then((saved) {
                if (saved == true) {
                  _loadOutfits();
                }
              });
            },
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const AiStylistScreen()),
          ).then((_) => _loadOutfits());
        },
        backgroundColor: Theme.of(context).colorScheme.primary,
        icon: const Icon(Icons.auto_awesome, color: Colors.white),
        label: const Text('Yeni Kombin Oluştur', style: TextStyle(color: Colors.white)),
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _outfitsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(
              child: CircularProgressIndicator(color: Theme.of(context).colorScheme.primary),
            );
          }
          if (snapshot.hasError) {
            return Center(
              child: Text(
                'Bir hata oluştu.',
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            );
          }

          final outfits = snapshot.data ?? [];

          if (outfits.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.style_rounded, size: 64, color: Colors.grey.withOpacity(0.5)),
                  const SizedBox(height: 16),
                  const Text(
                    'Henüz hiç kombin oluşturmadın.',
                    style: TextStyle(color: Colors.grey, fontSize: 16),
                  ),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: outfits.length,
            itemBuilder: (context, index) {
              final outfit = outfits[index] as Map<String, dynamic>;
              final kiyafetler = outfit['kiyafetler'] as List<dynamic>? ?? [];
              final aciklama = outfit['aciklama'] as String? ?? 'Açıklama yok';
              
              String baglam = '';
              try {
                final baglamMap = jsonDecode(outfit['baglam_json']);
                baglam = '${baglamMap['etkinlik'] ?? ''} - ${baglamMap['hava_durumu'] ?? ''}';
              } catch (_) {}

              return Card(
                color: Theme.of(context).cardColor,
                margin: const EdgeInsets.only(bottom: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              baglam.isNotEmpty ? baglam : 'Kombin Önerisi',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          Icon(Icons.check_circle_outline, color: Theme.of(context).colorScheme.primary, size: 20),
                          const SizedBox(width: 8),
                          IconButton(
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(),
                            icon: Icon(Icons.delete_outline, color: Theme.of(context).colorScheme.error, size: 20),
                            onPressed: () {
                              showDialog(
                                context: context,
                                builder: (ctx) => AlertDialog(
                                  backgroundColor: Theme.of(context).cardColor,
                                  title: Text('Kombini Sil', style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white)),
                                  content: Text('Bu kombini silmek istediğinize emin misiniz?', style: TextStyle(color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey[300])),
                                  actions: [
                                    TextButton(
                                      onPressed: () => Navigator.pop(ctx),
                                      child: const Text('İptal', style: TextStyle(color: Colors.grey)),
                                    ),
                                    TextButton(
                                      onPressed: () async {
                                        Navigator.pop(ctx);
                                        try {
                                          await ApiService().deleteOutfit(outfit['id']);
                                          _loadOutfits();
                                        } catch (e) {
                                          if (mounted) {
                                            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Hata: $e')));
                                          }
                                        }
                                      },
                                      child: Text('Sil', style: TextStyle(color: Theme.of(context).colorScheme.error)),
                                    ),
                                  ],
                                ),
                              );
                            },
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        aciklama,
                        style: const TextStyle(color: Colors.grey, fontSize: 13),
                      ),
                      const SizedBox(height: 16),
                      // Image grid
                      if (kiyafetler.isNotEmpty)
                        SizedBox(
                          height: 80,
                          child: ListView.builder(
                            scrollDirection: Axis.horizontal,
                            itemCount: kiyafetler.length,
                            itemBuilder: (context, i) {
                              final item = kiyafetler[i] as Map<String, dynamic>;
                              final url = ApiService.fixImageUrl(item['foto_url']?.toString() ?? '');
                              return Container(
                                width: 60,
                                height: 80,
                                margin: const EdgeInsets.only(right: 8),
                                decoration: BoxDecoration(
                                  color: Colors.grey[800],
                                  borderRadius: BorderRadius.circular(8),
                                  image: url.isNotEmpty
                                      ? DecorationImage(
                                          image: NetworkImage(url),
                                          fit: BoxFit.cover,
                                        )
                                      : null,
                                ),
                                child: url.isEmpty ? const Icon(Icons.image_not_supported, color: Colors.grey) : null,
                              );
                            },
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
