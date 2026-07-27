import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../../features/profile/presentation/providers/profile_provider.dart';
import '../../../../features/feed/domain/models/post_model.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/localization/locale_provider.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../features/feed/presentation/widgets/shimmer_loading.dart';
import '../../../../core/widgets/custom_shimmer.dart';
import 'follow_list_screen.dart';
import 'edit_profile_screen.dart';
import '../../../../features/create_post/presentation/screens/create_post_screen.dart';
import '../../../../features/feed/presentation/providers/feed_provider.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  final String? userId;
  const ProfileScreen({super.key, this.userId});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  @override
  Future<void> _loadProfile() async {
    final currentUserId = ref.read(authProvider).currentUserId;
    final targetUserId = widget.userId ?? currentUserId;
    if (targetUserId != null && targetUserId.isNotEmpty) {
      await ref
          .read(profileProvider)
          .loadProfile(targetUserId, currentUserId ?? targetUserId);
    }
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadProfile();
    });
  }

  @override
  Widget build(BuildContext context) {
    final currentUserId = ref.watch(authProvider).currentUserId;
    final targetUserId = widget.userId ?? currentUserId;
    if (targetUserId == null) return const SizedBox.shrink();

    final provider = ref.watch(profileProvider);
    final s = ref.watch(stringsProvider);

    if (provider.isLoading && provider.user == null) {
      return Scaffold(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        body: SafeArea(
          child: Column(
            children: [
              const SizedBox(height: 32),
              const CustomShimmer(width: 100, height: 100, isCircle: true),
              const SizedBox(height: 16),
              const CustomShimmer(width: 150, height: 24, borderRadius: 8),
              const SizedBox(height: 32),
              Expanded(child: const ProfileGridShimmer()),
            ],
          ),
        ),
      );
    }

    if (provider.hasError || provider.user == null) {
      return Scaffold(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        body: Center(
          child: Text(
            provider.errorMessage.isNotEmpty
                ? provider.errorMessage
                : 'Profile could not be loaded',
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ),
      );
    }

    final user = provider.user!;

    return DefaultTabController(
        length: provider.isOwnProfile ? 2 : 1,
        child: Scaffold(
          backgroundColor: Theme.of(context).scaffoldBackgroundColor,
          appBar: AppBar(
            title: Text(
              user.username,
              style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            backgroundColor: Theme.of(context).scaffoldBackgroundColor,
            elevation: 0,
          ),
          floatingActionButton: provider.isOwnProfile
              ? FloatingActionButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (_) => const CreatePostScreen()),
                    );
                  },
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  child: Icon(Icons.add,
                      color: Theme.of(context).scaffoldBackgroundColor),
                )
              : null,
          body: RefreshIndicator(
            onRefresh: _loadProfile,
            color: Theme.of(context).colorScheme.primary,
            backgroundColor: Theme.of(context).colorScheme.surface,
            child: NestedScrollView(
              headerSliverBuilder: (context, innerBoxIsScrolled) => [
                SliverToBoxAdapter(child: _buildHeader(user, provider, s)),
                SliverPersistentHeader(
                  pinned: true,
                  delegate: _TabBarDelegate(
                    TabBar(
                      indicatorColor: Theme.of(context).colorScheme.primary,
                      labelColor:
                          Theme.of(context).textTheme.bodyLarge?.color ??
                              Colors.white,
                      unselectedLabelColor:
                          Theme.of(context).textTheme.bodySmall?.color ??
                              Colors.grey,
                      tabs: [
                        const Tab(icon: Icon(Icons.style_rounded)),
                        if (provider.isOwnProfile)
                          const Tab(
                              icon: Icon(Icons.auto_awesome_rounded,
                                  color: Color(0xFFFFD700))),
                      ],
                    ),
                  ),
                ),
              ],
              body: TabBarView(
                children: [
                  _buildPostGrid(
                    provider.userPosts,
                    s,
                    targetUserId,
                    isLocked: !provider.isOwnProfile && !user.isFollowing,
                  ),
                  if (provider.isOwnProfile)
                    _buildPostGrid(
                      provider.savedPosts,
                      s,
                      targetUserId,
                      isSavedTab: true,
                      emptyMessage: s.isTr
                          ? 'Henüz kaydedilmiş gönderi yok'
                          : 'No saved posts yet',
                    ),
                ],
              ),
            ),
          ),
        ));
  }

  Widget _buildHeader(dynamic user, ProfileProvider provider, AppStrings s) {
    return Padding(
      padding: const EdgeInsets.all(AppTheme.spacingL),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Glassmorphism Profile Card
          Container(
            padding: const EdgeInsets.all(AppTheme.spacingL),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Theme.of(context).colorScheme.surface.withValues(alpha: 0.8),
                  Theme.of(context).cardColor.withValues(alpha: 0.9),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: Theme.of(context)
                      .colorScheme
                      .primary
                      .withValues(alpha: 0.1),
                  blurRadius: 20,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Avatar with gradient ring
                Container(
                  width: 96,
                  height: 96,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: AppTheme.primaryGradient,
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.accentPurple.withValues(alpha: 0.4),
                        blurRadius: 15,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.all(3),
                  child: Container(
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Theme.of(context).colorScheme.surface,
                    ),
                    child: GestureDetector(
                      onTap: user.avatarUrl.isNotEmpty
                          ? () {
                              showDialog(
                                context: context,
                                builder: (_) => Dialog(
                                  backgroundColor: Colors.transparent,
                                  insetPadding: const EdgeInsets.all(16),
                                  child: Stack(
                                    alignment: Alignment.center,
                                    children: [
                                      InteractiveViewer(
                                        clipBehavior: Clip.none,
                                        child: Image.network(user.avatarUrl),
                                      ),
                                      Positioned(
                                        top: 10,
                                        right: 10,
                                        child: IconButton(
                                          icon: const Icon(Icons.close,
                                              color: Colors.white, size: 30),
                                          onPressed: () =>
                                              Navigator.pop(context),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            }
                          : null,
                      child: CircleAvatar(
                        radius: 44,
                        backgroundColor: Theme.of(context).cardColor,
                        backgroundImage: user.avatarUrl.isNotEmpty
                            ? NetworkImage(user.avatarUrl)
                            : null,
                        child: user.avatarUrl.isEmpty
                            ? Icon(Icons.person,
                                size: 44,
                                color: Theme.of(context)
                                        .textTheme
                                        .bodyMedium
                                        ?.color ??
                                    Colors.grey)
                            : null,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: AppTheme.spacingM),
                // Display name
                Text(
                  user.displayName.isNotEmpty
                      ? user.displayName
                      : user.username,
                  style: TextStyle(
                    color: Theme.of(context).textTheme.bodyLarge?.color ??
                        Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 4),
                if (user.bio.isNotEmpty) ...[
                  const SizedBox(height: AppTheme.spacingM),
                  Text(
                    user.bio,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Theme.of(context).textTheme.bodyLarge?.color ??
                          Colors.white,
                      fontSize: 15,
                      height: 1.4,
                    ),
                  ),
                ],
                const SizedBox(height: AppTheme.spacingL),
                // Stats
                Container(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  decoration: BoxDecoration(
                    color: Theme.of(context)
                        .scaffoldBackgroundColor
                        .withValues(alpha: 0.5),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _buildStatColumn(provider.postCount, s.posts),
                      _buildStatColumn(
                        user.followersCount,
                        s.followers,
                        onTap: () => FollowListBottomSheet.show(
                          context,
                          userId: user.userId,
                          initialTabIndex: 0,
                        ),
                      ),
                      _buildStatColumn(
                        user.followingCount,
                        s.following,
                        onTap: () => FollowListBottomSheet.show(
                          context,
                          userId: user.userId,
                          initialTabIndex: 1,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: AppTheme.spacingL),
                // Action buttons
                if (provider.isOwnProfile)
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                  builder: (_) => const EditProfileScreen()),
                            );
                          },
                          style: OutlinedButton.styleFrom(
                            foregroundColor:
                                Theme.of(context).textTheme.bodyLarge?.color ??
                                    Colors.white,
                            side: BorderSide(
                                color: Theme.of(context).dividerColor),
                            padding: const EdgeInsets.symmetric(
                                vertical: AppTheme.spacingS),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          child: Text(s.editProfile,
                              style: const TextStyle(
                                  fontSize: 13, fontWeight: FontWeight.bold)),
                        ),
                      ),
                      const SizedBox(width: AppTheme.spacingS),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {},
                          style: OutlinedButton.styleFrom(
                            foregroundColor:
                                Theme.of(context).textTheme.bodyLarge?.color ??
                                    Colors.white,
                            side: BorderSide(
                                color: Theme.of(context).dividerColor),
                            padding: const EdgeInsets.symmetric(
                                vertical: AppTheme.spacingS),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          child: Text(s.shareProfile,
                              style: const TextStyle(
                                  fontSize: 13, fontWeight: FontWeight.bold)),
                        ),
                      ),
                    ],
                  )
                else
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () => provider.toggleFollow(),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: user.isFollowing
                                ? Theme.of(context).colorScheme.surface
                                : Theme.of(context).colorScheme.primary,
                            foregroundColor:
                                Theme.of(context).textTheme.bodyLarge?.color ??
                                    Colors.white,
                            padding: const EdgeInsets.symmetric(
                                vertical: AppTheme.spacingS),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                              side: user.isFollowing
                                  ? BorderSide(
                                      color: Theme.of(context).dividerColor)
                                  : BorderSide.none,
                            ),
                            elevation: user.isFollowing ? 0 : 2,
                          ),
                          child: Text(
                              user.isFollowing ? 'Takibi Bırak' : 'Takip Et',
                              style: const TextStyle(
                                  fontSize: 13, fontWeight: FontWeight.bold)),
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPostGrid(
      List<PostModel> posts, AppStrings s, String targetUserId,
      {String? emptyMessage, bool isLocked = false, bool isSavedTab = false}) {
    if (isLocked) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.lock_outline_rounded,
                size: 48,
                color: Theme.of(context).textTheme.bodySmall?.color ??
                    Colors.grey),
            const SizedBox(height: 12),
            Text(
              s.isTr ? 'Bu profil gizlidir' : 'This profile is private',
              style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ??
                      Colors.white,
                  fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              s.isTr
                  ? 'Gönderilerini görmek için takip et.'
                  : 'Follow to see their posts.',
              style: TextStyle(
                  color: Theme.of(context).textTheme.bodyMedium?.color ??
                      Colors.grey,
                  fontSize: 13),
            ),
          ],
        ),
      );
    }

    if (posts.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.photo_library_outlined,
                size: 48,
                color: Theme.of(context).textTheme.bodySmall?.color ??
                    Colors.grey.withValues(alpha: 0.4)),
            const SizedBox(height: 12),
            Text(
              emptyMessage ?? s.noPostsYet,
              style: TextStyle(
                  color: Theme.of(context).textTheme.bodyMedium?.color ??
                      Colors.grey),
            ),
          ],
        ),
      );
    }

    return GridView.builder(
      padding: const EdgeInsets.all(2),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 2,
        mainAxisSpacing: 2,
      ),
      itemCount: posts.length,
      itemBuilder: (context, index) {
        final post = posts[index];
        final provider = ref.read(profileProvider);
        return GestureDetector(
          onTap: () {
            showDialog(
              context: context,
              builder: (ctx) => Dialog(
                backgroundColor: Colors.transparent,
                insetPadding: const EdgeInsets.all(16),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Flexible(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: post.imageUrl == 'collage'
                            ? Container(
                                color: Theme.of(context).colorScheme.surface,
                                padding: const EdgeInsets.all(24),
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.style_rounded, size: 64, color: AppTheme.accentPurple),
                                    const SizedBox(height: 16),
                                    const Text('Kombin Kolajı', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                                  ],
                                ),
                              )
                            : post.imageUrl.startsWith('http')
                                ? Image.network(
                                    post.imageUrl,
                                    fit: BoxFit.contain,
                                  )
                                : Image.file(
                                    File(post.imageUrl),
                                    fit: BoxFit.contain,
                                  ),
                      ),
                    ),
                    Container(
                      width: double.infinity,
                      margin: const EdgeInsets.only(top: 12),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.surface,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '@${post.username}',
                            style: TextStyle(
                              color: Theme.of(context)
                                      .textTheme
                                      .bodyLarge
                                      ?.color ??
                                  Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            post.caption.isNotEmpty
                                ? post.caption
                                : (s.isTr ? 'Açıklama yok' : 'No caption'),
                            style: TextStyle(
                              color: Theme.of(context)
                                      .textTheme
                                      .bodyMedium
                                      ?.color ??
                                  Colors.grey,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (isSavedTab) ...[
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 10),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8)),
                        ),
                        icon: const Icon(Icons.bookmark_remove,
                            color: Colors.white, size: 18),
                        label: Text(s.isTr ? 'Kaydedilenlerden Çıkar' : 'Unsave',
                            style: const TextStyle(color: Colors.white)),
                        onPressed: () async {
                          Navigator.pop(ctx);
                          await ref.read(feedProvider.notifier).toggleSave(post.id);
                          ref.read(profileProvider.notifier).loadProfile(targetUserId, ref.read(authProvider).currentUserId ?? targetUserId);
                        },
                      ),
                    ] else if (provider.isOwnProfile) ...[
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  Theme.of(context).colorScheme.primary,
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 16, vertical: 10),
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8)),
                            ),
                            icon: Icon(Icons.edit_rounded,
                                color: Theme.of(context)
                                        .textTheme
                                        .bodyLarge
                                        ?.color ??
                                    Colors.white,
                                size: 18),
                            label: Text(s.isTr ? 'Düzenle' : 'Edit',
                                style: TextStyle(
                                    color: Theme.of(context)
                                            .textTheme
                                            .bodyLarge
                                            ?.color ??
                                        Colors.white)),
                            onPressed: () {
                              Navigator.pop(ctx);
                              _showProfileEditDialog(context, post);
                            },
                          ),
                          const SizedBox(width: 16),
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  Theme.of(context).colorScheme.error,
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 16, vertical: 10),
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8)),
                            ),
                            icon: Icon(Icons.delete_rounded,
                                color: Theme.of(context)
                                        .textTheme
                                        .bodyLarge
                                        ?.color ??
                                    Colors.white,
                                size: 18),
                            label: Text(s.isTr ? 'Sil' : 'Delete',
                                style: TextStyle(
                                    color: Theme.of(context)
                                            .textTheme
                                            .bodyLarge
                                            ?.color ??
                                        Colors.white)),
                            onPressed: () {
                              Navigator.pop(ctx);
                              _showProfileDeleteConfirm(context, post);
                            },
                          ),
                        ],
                      ),
                    ]
                  ],
                ),
              ),
            );
          },
          child: Container(
            color: Theme.of(context).colorScheme.surface,
            child: post.imageUrl == 'collage'
                ? Center(
                    child: Icon(Icons.style_rounded,
                        size: 40,
                        color: Theme.of(context).textTheme.bodySmall?.color ??
                            Colors.grey),
                  )
                : post.imageUrl.startsWith('http')
                    ? Image.network(
                        post.imageUrl,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) => Center(
                          child: Icon(Icons.error_outline,
                              color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey),
                        ),
                      )
                    : Image.file(
                        File(post.imageUrl),
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) => Center(
                          child: Icon(Icons.error_outline,
                              color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey),
                        ),
                      ),
          ),
        );
      },
    );
  }

  Widget _buildStatColumn(int count, String label, {VoidCallback? onTap}) {
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            count.toString(),
            style: TextStyle(
              color:
                  Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              color:
                  Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showProfileEditDialog(
      BuildContext context, PostModel post) async {
    final controller = TextEditingController(text: post.caption);
    final isTr = ref.read(localeProvider) == AppLocale.tr;
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Theme.of(context).colorScheme.surface,
        title: Text(isTr ? 'Gönderiyi Düzenle' : 'Edit Post',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white)),
        content: TextField(
          controller: controller,
          maxLines: 3,
          style: TextStyle(
              color:
                  Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
          decoration: InputDecoration(
            hintText: isTr ? 'Yeni açıklama...' : 'New caption...',
            hintStyle: TextStyle(
                color: Theme.of(context).textTheme.bodySmall?.color ??
                    Colors.grey),
            enabledBorder: OutlineInputBorder(
              borderSide: BorderSide(color: Theme.of(context).dividerColor),
              borderRadius: BorderRadius.circular(8),
            ),
            focusedBorder: OutlineInputBorder(
              borderSide:
                  BorderSide(color: Theme.of(context).colorScheme.primary),
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(isTr ? 'İptal' : 'Cancel',
                style: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(isTr ? 'Kaydet' : 'Save',
                style: TextStyle(color: Theme.of(context).colorScheme.primary)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      final newCaption = controller.text.trim();
      final userId = ref.read(authProvider).currentUserId;
      if (userId == null) return;
      try {
        await ref
            .read(profileProvider)
            .updatePost(post.postId, userId, newCaption);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content: Text(isTr ? 'Gönderi güncellendi.' : 'Post updated.')),
          );
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content:
                    Text('${isTr ? "Güncelleme hatası" : "Update error"}: $e')),
          );
        }
      }
    }
  }

  Future<void> _showProfileDeleteConfirm(
      BuildContext context, PostModel post) async {
    final isTr = ref.read(localeProvider) == AppLocale.tr;
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Theme.of(context).colorScheme.surface,
        title: Text(isTr ? 'Gönderiyi Sil' : 'Delete Post',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white)),
        content: Text(
            isTr
                ? 'Bu gönderiyi kalıcı olarak silmek istediğinize emin misiniz?'
                : 'Are you sure you want to permanently delete this post?',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyMedium?.color ??
                    Colors.grey)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(isTr ? 'İptal' : 'Cancel',
                style: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(isTr ? 'Sil' : 'Delete',
                style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      final userId = ref.read(authProvider).currentUserId;
      if (userId == null) return;
      try {
        await ref.read(profileProvider).deletePost(post.postId, userId);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content: Text(isTr ? 'Gönderi silindi.' : 'Post deleted.')),
          );
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content: Text('${isTr ? "Silme hatası" : "Delete error"}: $e')),
          );
        }
      }
    }
  }
}

// ── Tab Bar Delegate ───────────────────────────────────────────
class _TabBarDelegate extends SliverPersistentHeaderDelegate {
  final TabBar tabBar;
  _TabBarDelegate(this.tabBar);

  @override
  double get minExtent => tabBar.preferredSize.height;
  @override
  double get maxExtent => tabBar.preferredSize.height;

  @override
  Widget build(
      BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
        color: Theme.of(context).scaffoldBackgroundColor, child: tabBar);
  }

  @override
  bool shouldRebuild(covariant _TabBarDelegate oldDelegate) => false;
}
