import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../services/api_service.dart';
import '../../../../services/notification_service.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/localization/locale_provider.dart';
import 'add_item_screen.dart';
import 'edit_item_screen.dart';
import 'outfits_screen.dart';

class WardrobeScreen extends ConsumerStatefulWidget {
  const WardrobeScreen({super.key});

  @override
  ConsumerState<WardrobeScreen> createState() => _WardrobeScreenState();
}

class _WardrobeScreenState extends ConsumerState<WardrobeScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<dynamic>> _clothesFuture;
  String? _selectedCategory;
  bool _isLaundryMode = false;
  String _searchQuery = '';
  int _refreshKey = 0; // Bu değer değişince FutureBuilder zorunlu yenilenir

  @override
  void initState() {
    super.initState();
    _loadClothes();
  }

  void _loadClothes() {
    if (!mounted) return; // Widget ağacından kaldırıldıysa çık
    final userId = ref.read(authProvider).currentUserId ?? '';
    setState(() {
      _refreshKey++; // Her çağrıda key artar — FutureBuilder kesinlikle yenilenir
      if (userId.isEmpty) {
        _clothesFuture = Future.value([]);
      } else {
        _clothesFuture = _apiService.getClothes(userId).then((clothes) {
          NotificationService().checkLowClothesCount(clothes);
          return clothes;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(stringsProvider);
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _isLaundryMode 
                        ? (s.isTr ? 'Kirli Sepeti' : 'Laundry Basket') 
                        : (s.isTr ? 'Gardırobum' : 'My Wardrobe'),
                    style: TextStyle(
                      color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.w700,
                      letterSpacing: -0.5,
                    ),
                  ),
                  Row(
                    children: [
                      IconButton(
                        icon: Icon(
                          _isLaundryMode ? Icons.local_laundry_service : Icons.local_laundry_service_outlined,
                          color: _isLaundryMode ? Theme.of(context).colorScheme.primary : (Theme.of(context).iconTheme.color ?? Colors.white),
                          size: 28,
                        ),
                        tooltip: s.isTr ? 'Kirli Sepeti' : 'Laundry Basket',
                        onPressed: () {
                          setState(() {
                            _isLaundryMode = !_isLaundryMode;
                            _selectedCategory = null; // Clear standard filters when toggling mode
                          });
                        },
                      ),
                      IconButton(
                        icon: Icon(Icons.style_rounded, color: Theme.of(context).iconTheme.color ?? Colors.white, size: 28),
                        tooltip: s.isTr ? 'Kombinlerim' : 'My Outfits',
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => const OutfitsScreen()),
                          );
                        },
                      ),
                      IconButton(
                        icon: Icon(Icons.add_circle_outline_rounded,
                            color: Theme.of(context).iconTheme.color ?? Colors.white, size: 28),
                        onPressed: () async {
                          final refreshed = await Navigator.push<bool>(
                            context,
                            MaterialPageRoute(
                                builder: (_) => const AddItemScreen()),
                          );
                          // true dönürse (başarılı ekleme) gardrıobu yenile
                          if (refreshed == true && mounted) {
                            _loadClothes();
                          }
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Search Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Container(
                height: 40,
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const SizedBox(width: 12),
                    Icon(Icons.search_rounded,
                        color: Theme.of(context).textTheme.bodySmall?.color ??
                            Colors.grey,
                        size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: TextField(
                        onChanged: (val) {
                          setState(() {
                            _searchQuery = val.toLowerCase();
                          });
                        },
                        style:
                            TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white, fontSize: 14),
                        decoration: InputDecoration(
                          hintText: s.isTr ? 'Kıyafet ara...' : 'Search items...',
                          hintStyle: TextStyle(
                              color: Theme.of(context)
                                      .textTheme
                                      .bodySmall
                                      ?.color ??
                                  Colors.grey),
                          border: InputBorder.none,
                          isDense: true,
                          contentPadding:
                              const EdgeInsets.symmetric(vertical: 10),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Category Chips
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                children: [
                  _FilterChip(
                    label: s.isTr ? 'Favoriler' : 'Favorites',
                    isSelected: _selectedCategory == 'Favorites',
                    onTap: () => setState(() => _selectedCategory =
                        _selectedCategory == 'Favorites' ? null : 'Favorites'),
                  ),

                  _FilterChip(
                    label: 'Shirt',
                    isSelected: _selectedCategory == 'Shirt',
                    onTap: () => setState(() => _selectedCategory =
                        _selectedCategory == 'Shirt' ? null : 'Shirt'),
                  ),
                  _FilterChip(
                    label: 'T-Shirt',
                    isSelected: _selectedCategory == 'T-Shirt',
                    onTap: () => setState(() => _selectedCategory =
                        _selectedCategory == 'T-Shirt' ? null : 'T-Shirt'),
                  ),
                  _FilterChip(
                    label: 'Pants',
                    isSelected: _selectedCategory == 'Pants',
                    onTap: () => setState(() => _selectedCategory =
                        _selectedCategory == 'Pants' ? null : 'Pants'),
                  ),
                  _FilterChip(
                    label: 'Jeans',
                    isSelected: _selectedCategory == 'Jeans',
                    onTap: () => setState(() => _selectedCategory =
                        _selectedCategory == 'Jeans' ? null : 'Jeans'),
                  ),
                  _FilterChip(
                    label: 'Shoes',
                    isSelected: _selectedCategory == 'Shoes',
                    onTap: () => setState(() => _selectedCategory =
                        _selectedCategory == 'Shoes' ? null : 'Shoes'),
                  ),
                  _FilterChip(
                    label: 'Accessories',
                    isSelected: _selectedCategory == 'Accessories',
                    onTap: () => setState(() => _selectedCategory =
                        _selectedCategory == 'Accessories'
                            ? null
                            : 'Accessories'),
                  ),
                  _FilterChip(
                    label: s.isTr ? 'Eşarp' : 'Hijab',
                    isSelected: _selectedCategory == 'Hijab',
                    onTap: () => setState(() => _selectedCategory =
                        _selectedCategory == 'Hijab' ? null : 'Hijab'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            Expanded(
              child: FutureBuilder<List<dynamic>>(
                key: ValueKey(_refreshKey), // key değişince Flutter tamamen yeniden build eder
                future: _clothesFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(
                      child: CircularProgressIndicator(color: Colors.white),
                    );
                  }
                  if (snapshot.hasError) {
                    return Center(
                      child: Text(
                        'Error: ${snapshot.error}',
                        style: TextStyle(
                            color: Theme.of(context).colorScheme.error),
                      ),
                    );
                  }

                  var clothes = snapshot.data ?? [];
                  
                  // 1. Base Filter (Laundry Mode)
                  if (_isLaundryMode) {
                    clothes = clothes.where((c) => c['temiz'] == 0 || c['temiz'] == false || c['is_dirty'] == 1 || c['is_dirty'] == true).toList();
                  } else {
                    clothes = clothes.where((c) => c['temiz'] == 1 || c['temiz'] == true).toList();
                  }
                  
                  // 2. Apply Category Filter
                  if (_selectedCategory != null) {
                    if (_selectedCategory == 'Favorites') {
                      clothes = clothes.where((c) => (c['is_favorite'] == 1 || c['is_favorite'] == true)).toList();
                    } else {
                      clothes = clothes.where((c) {
                        final type = c['tur']?.toString().toLowerCase() ?? '';
                        final category = c['kategori']?.toString().toLowerCase() ?? '';
                        final tags = c['stil_etiketi']?.toString().toLowerCase() ?? '';
                        
                        String searchTarget = _selectedCategory!.toLowerCase();
                        // Map English chips to Turkish db values
                        if (searchTarget == 'shirt') searchTarget = 'gömlek';
                        if (searchTarget == 't-shirt') searchTarget = 'tişört';
                        if (searchTarget == 'pants') searchTarget = 'pantolon';
                        if (searchTarget == 'jeans') searchTarget = 'kot';
                        if (searchTarget == 'shoes') searchTarget = 'ayakkabı';
                        if (searchTarget == 'accessories') searchTarget = 'aksesuar';
                        if (searchTarget == 'hijab') searchTarget = 'eşarp';

                        return (type.contains(searchTarget) || tags.contains(searchTarget) || category.contains(searchTarget));
                      }).toList();
                    }
                  }

                  // Apply Search Query Filter
                  if (_searchQuery.isNotEmpty) {
                    clothes = clothes.where((c) {
                        final type = c['tur']?.toString().toLowerCase() ?? '';
                        final color = c['renk']?.toString().toLowerCase() ?? '';
                        final style = c['stil']?.toString().toLowerCase() ?? '';
                        final tags = c['stil_etiketi']?.toString().toLowerCase() ?? '';
                        final brand = c['marka']?.toString().toLowerCase() ?? '';
                        return type.contains(_searchQuery) || 
                               color.contains(_searchQuery) || 
                               style.contains(_searchQuery) ||
                               tags.contains(_searchQuery) ||
                               brand.contains(_searchQuery);
                    }).toList();
                  }

                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16.0, vertical: 4.0),
                        child: Text(
                          '${clothes.length} items',
                          style: TextStyle(
                            color:
                                Theme.of(context).textTheme.bodySmall?.color ??
                                    Colors.grey,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      if (clothes.isEmpty)
                        Expanded(
                          child: Center(
                            child: Text(
                              'No clothes found',
                              style: TextStyle(
                                  color: Theme.of(context)
                                          .textTheme
                                          .bodyMedium
                                          ?.color ??
                                      Colors.grey),
                            ),
                          ),
                        )
                      else
                        Expanded(
                          child: GridView.builder(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 16.0, vertical: 8.0),
                            gridDelegate:
                                const SliverGridDelegateWithFixedCrossAxisCount(
                              crossAxisCount: 2,
                              childAspectRatio: 0.8,
                              crossAxisSpacing: 12,
                              mainAxisSpacing: 12,
                            ),
                            itemCount: clothes.length,
                            itemBuilder: (context, index) {
                              final cloth =
                                  clothes[index] as Map<String, dynamic>;
                              final rawImageUrl =
                                  cloth['foto_url']?.toString() ??
                                      cloth['image_url']?.toString() ??
                                      '';
                              final imageUrl =
                                  ApiService.fixImageUrl(rawImageUrl);

                              final parts = <String>[];
                              if (cloth['renk'] != null &&
                                  cloth['renk'].toString().isNotEmpty)
                                parts.add(s.translateWardrobe(cloth['renk'].toString()));
                              if (cloth['tur'] != null &&
                                  cloth['tur'].toString().isNotEmpty)
                                parts.add(s.translateWardrobe(cloth['tur'].toString()));
                              if (cloth['beden'] != null &&
                                  cloth['beden'].toString().isNotEmpty)
                                parts.add(cloth['beden'].toString());
                              final label = parts.join(', ');

                              return GestureDetector(
                                onTap: () async {
                                  final refreshed = await Navigator.push<bool>(
                                    context,
                                    MaterialPageRoute(
                                      builder: (_) =>
                                          EditItemScreen(initialItem: cloth),
                                    ),
                                  );
                                  if (refreshed == true && mounted) {
                                    _loadClothes();
                                  }
                                },
                                child: Container(
                                  decoration: BoxDecoration(
                                    color: Theme.of(context).cardColor,
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  clipBehavior: Clip.antiAlias,
                                  child: Stack(
                                    fit: StackFit.expand,
                                    children: [
                                      imageUrl.isNotEmpty
                                          ? Image.network(
                                              imageUrl,
                                              fit: BoxFit.cover,
                                              errorBuilder: (_, __, ___) =>
                                                  const _EmptyClothIcon(),
                                            )
                                          : const _EmptyClothIcon(),
                                      if (label.isNotEmpty)
                                        Positioned(
                                          bottom: 0,
                                          left: 0,
                                          right: 0,
                                          child: Container(
                                            padding: const EdgeInsets.symmetric(
                                                vertical: 8, horizontal: 8),
                                            decoration: BoxDecoration(
                                              gradient: LinearGradient(
                                                begin: Alignment.bottomCenter,
                                                end: Alignment.topCenter,
                                                colors: [
                                                  Colors.black.withOpacity(0.8),
                                                  Colors.transparent,
                                                ],
                                              ),
                                            ),
                                            child: Text(
                                              label,
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontSize: 12,
                                                fontWeight: FontWeight.w600,
                                                shadows: [
                                                  Shadow(
                                                      color: Colors.black54,
                                                      blurRadius: 2)
                                                ],
                                              ),
                                              maxLines: 2,
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          ),
                                        ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                    ],
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyClothIcon extends StatelessWidget {
  const _EmptyClothIcon();

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Theme.of(context).colorScheme.surface,
      child: Center(
        child: Icon(Icons.checkroom_rounded,
            size: 52,
            color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey),
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _FilterChip({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(right: 8.0),
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
        decoration: BoxDecoration(
          color: isSelected ? Theme.of(context).colorScheme.primary : Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? Theme.of(context).colorScheme.primary : Theme.of(context).dividerColor,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected 
                ? (Theme.of(context).brightness == Brightness.dark ? Colors.white : Colors.black)
                : Theme.of(context).textTheme.bodyMedium?.color ?? Colors.white,
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }
}
