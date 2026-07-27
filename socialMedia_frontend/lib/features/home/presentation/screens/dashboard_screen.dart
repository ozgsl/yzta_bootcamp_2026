import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../profile/presentation/providers/profile_provider.dart';
import '../../../feed/presentation/screens/feed_screen.dart';
import '../../../feed/presentation/widgets/post_card.dart';
import '../../../feed/presentation/widgets/comments_bottom_sheet.dart';
import '../../../feed/presentation/providers/feed_provider.dart';
import '../../../wardrobe/presentation/screens/ai_stylist_screen.dart';
import '../../../wardrobe/presentation/screens/add_item_screen.dart';
import 'analytics_screen.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/locale_provider.dart';

class DashboardScreen extends ConsumerWidget {
  DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = ref.watch(stringsProvider);
    final user = ref.watch(profileProvider).user;
    final name = user?.displayName.isNotEmpty == true ? user!.displayName : 'Demo';
    
    final hour = DateTime.now().hour;
    String greeting;
    if (hour >= 5 && hour < 12) {
      greeting = strings.goodMorning;
    } else if (hour >= 12 && hour < 17) {
      greeting = strings.goodAfternoon;
    } else if (hour >= 17 && hour < 21) {
      greeting = strings.goodEvening;
    } else {
      greeting = strings.goodNight;
    }

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () => ref.read(feedProvider).refresh(),
          child: CustomScrollView(
            slivers: [
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Greeting
              Text(
                '$greeting, $name',
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                  fontSize: 26,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.5,
                ),
              ),
              SizedBox(height: 4),
              Text(
                strings.whatToWear,
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodySmall?.color ??
                      Colors.grey,
                  fontSize: 14,
                ),
              ),

              SizedBox(height: 24),

              // AI Stylist Banner
              GestureDetector(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => AiStylistScreen()),
                  );
                },
                child: Container(
                  width: double.infinity,
                  padding: EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Color(0xFF7C3AED), Color(0xFFDB2777)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Color(0xFF7C3AED).withValues(alpha: 0.3),
                        blurRadius: 12,
                        offset: Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(Icons.auto_awesome_rounded,
                            color: Colors.white, size: 24),
                      ),
                      SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'AI Stylist',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            Text(
                              'Get an instant outfit recommendation',
                              style: TextStyle(
                                color: Colors.white70,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Icon(Icons.chevron_right_rounded, color: Colors.white),
                    ],
                  ),
                ),
              ),

              SizedBox(height: 24),

              // Weather Card
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    Icon(Icons.wb_sunny_rounded, color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white, size: 28),
                    SizedBox(width: 16),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '32°C',
                          style: TextStyle(
                            color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        Text(
                          'Mostly Sunny',
                          style: TextStyle(
                            color:
                                Theme.of(context).textTheme.bodySmall?.color ??
                                    Colors.grey,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                    Spacer(),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          'feels 31°',
                          style: TextStyle(
                            color:
                                Theme.of(context).textTheme.bodyMedium?.color ??
                                    Colors.grey,
                            fontSize: 12,
                          ),
                        ),
                        Text(
                          '2% chance of rain',
                          style: TextStyle(
                            color:
                                Theme.of(context).textTheme.bodySmall?.color ??
                                    Colors.grey,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 32),

              // Pending Outfits Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Pending Outfits',
                    style: TextStyle(
                      color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    '0 total',
                    style: TextStyle(
                      color: Theme.of(context).textTheme.bodySmall?.color ??
                          Colors.grey,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 16),

              // Placeholder for empty outfits
              Container(
                width: double.infinity,
                padding: EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    Icon(Icons.checkroom_rounded,
                        color: Theme.of(context).textTheme.bodySmall?.color ??
                            Colors.grey,
                        size: 40),
                    SizedBox(height: 12),
                    Text(
                      "No pending outfits",
                      style: TextStyle(
                          color:
                              Theme.of(context).textTheme.bodyMedium?.color ??
                                  Colors.grey,
                          fontSize: 14),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 32),

              // Explore / Social Feed
              Text(
                'Explore',
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              SizedBox(height: 16),

              Row(
                children: [
                  Expanded(
                    child: _ExploreCard(
                      icon: Icons.add_circle_outline_rounded,
                      title: 'Add Item',
                      subtitle: 'Add clothes to wardrobe',
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => AddItemScreen()),
                        );
                      },
                    ),
                  ),
                  SizedBox(width: 16),
                  Expanded(
                    child: _ExploreCard(
                      icon: Icons.bar_chart_rounded,
                      title: 'Analytics',
                      subtitle: 'Your style stats',
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const AnalyticsScreen()),
                        );
                      },
                    ),
                  ),
                ],
              ),

                    ],
                  ),
                ),
              ),
              
              // Feed Section
              SliverPadding(
                padding: const EdgeInsets.only(left: 24, right: 24, top: 16, bottom: 8),
                sliver: SliverToBoxAdapter(
                  child: Text(
                    'Social Feed',
                    style: TextStyle(
                      color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
              
              _buildFeedSliver(context, ref),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeedSliver(BuildContext context, WidgetRef ref) {
    final provider = ref.watch(feedProvider);
    final currentUserId = ref.watch(authProvider).currentUserId ?? '';

    if (provider.isLoading) {
      return const SliverToBoxAdapter(
        child: Center(
          child: Padding(
            padding: EdgeInsets.all(32.0),
            child: CircularProgressIndicator(),
          ),
        ),
      );
    }

    if (provider.posts.isEmpty) {
      return SliverToBoxAdapter(
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 24),
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            children: [
              Icon(Icons.explore_rounded, color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey, size: 40),
              const SizedBox(height: 12),
              Text(
                "No posts yet. Follow users to see their posts here!",
                textAlign: TextAlign.center,
                style: TextStyle(color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey, fontSize: 14),
              ),
            ],
          ),
        ),
      );
    }

    return SliverPadding(
      padding: const EdgeInsets.only(bottom: 100),
      sliver: SliverList(
        delegate: SliverChildBuilderDelegate(
          (context, index) {
            if (index == provider.posts.length) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: SizedBox(
                    width: 24, height: 24, 
                    child: CircularProgressIndicator(strokeWidth: 2, color: Theme.of(context).colorScheme.primary)
                  ),
                ),
              );
            }
            final post = provider.posts[index];
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: PostCard(
                post: post,
                onLike: (postId) => provider.toggleLike(postId),
                onSave: (postId) => provider.toggleSave(postId),
                onComment: () {
                  CommentsBottomSheet.show(
                    context,
                    postId: post.postId,
                    currentUserId: currentUserId,
                    initialCommentsCount: post.commentsCount,
                    onCommentsCountChanged: (count) =>
                        provider.updateCommentsCount(post.postId, count),
                  );
                },
                onUserTap: (userId) {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => ProfileScreen(userId: userId),
                    ),
                  );
                },
              ),
            );
          },
          childCount: provider.posts.length + (provider.hasMore ? 1 : 0),
        ),
      ),
    );
  }
}

class _ExploreCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  _ExploreCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 120,
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white, size: 24),
            Spacer(),
            Text(
              title,
              style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 2),
            Text(
              subtitle,
              style: TextStyle(
                color:
                    Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
