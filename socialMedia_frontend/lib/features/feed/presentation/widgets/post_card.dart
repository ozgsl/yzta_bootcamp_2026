import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../../features/feed/domain/models/post_model.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../../services/api_service.dart';
import '../providers/feed_provider.dart';
import 'like_button.dart';

class PostCard extends ConsumerWidget {
  final PostModel post;
  final ValueChanged<String> onLike;
  final ValueChanged<String>? onSave;
  final VoidCallback? onComment;
  final ValueChanged<String>? onUserTap;

  const PostCard({
    super.key,
    required this.post,
    required this.onLike,
    this.onSave,
    this.onComment,
    this.onUserTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingL,
        vertical: AppTheme.spacingS,
      ),
      decoration: AppTheme.glassDecoration(),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ─── Header: Avatar + Username + Time ─────────────────
          _buildHeader(context, ref),
          // ─── Post Image ───────────────────────────────────────          // 📸 Post Image
          _buildImage(context),
          // ✨ Actions & Caption ────────────────────────────────
          _buildFooter(context),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context, WidgetRef ref) {
    final currentUserId = ref.read(authProvider).currentUserId;
    final isMine = post.userId == currentUserId;

    return Padding(
      padding: const EdgeInsets.all(AppTheme.spacingM),
      child: Row(
        children: [
          // Avatar
          GestureDetector(
            onTap: () => onUserTap?.call(post.userId),
            onLongPress: () {
              if (post.avatarUrl.isNotEmpty) {
                showDialog(
                  context: context,
                  builder: (_) => Dialog(
                    backgroundColor: Colors.transparent,
                    insetPadding: const EdgeInsets.all(16),
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        InteractiveViewer(
                          minScale: 0.8,
                          maxScale: 3.0,
                          clipBehavior: Clip.none,
                          child: Container(
                            width: 250,
                            height: 250,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(color: Theme.of(context).colorScheme.primary, width: 2),
                              image: DecorationImage(
                                image: CachedNetworkImageProvider(post.avatarUrl),
                                fit: BoxFit.cover,
                              ),
                            ),
                          ),
                        ),
                        Positioned(
                          top: -20,
                          right: -20,
                          child: IconButton(
                            icon: const Icon(Icons.close,
                                color: Colors.white, size: 30),
                            onPressed: () => Navigator.pop(context),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }
            },
            child: Container(
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: AppTheme.primaryGradient,
                boxShadow: [
                  BoxShadow(
                    color: Theme.of(context)
                        .colorScheme
                        .primary
                        .withValues(alpha: 0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              padding: const EdgeInsets.all(2),
              child: Semantics(
                label: '${post.username} profil fotoğrafı',
                child: CircleAvatar(
                  radius: 18,
                  backgroundColor: Theme.of(context).cardColor,
                  backgroundImage: post.avatarUrl.isNotEmpty
                      ? CachedNetworkImageProvider(post.avatarUrl)
                      : null,
                  child: post.avatarUrl.isEmpty
                      ? Text(
                          post.username.isNotEmpty
                              ? post.username[0].toUpperCase()
                              : '?',
                          style: TextStyle(
                            color:
                                Theme.of(context).textTheme.bodyLarge?.color ??
                                    Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        )
                      : null,
                ),
              ),
            ),
          ),
          const SizedBox(width: AppTheme.spacingM),
          // Username + Time
          Expanded(
            child: GestureDetector(
              onTap: () => onUserTap?.call(post.userId),
              behavior: HitTestBehavior.opaque,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      if (post.activeTitle != null && post.activeTitle!.isNotEmpty) ...[
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [Color(0xFFD4AF37), Color(0xFFF5D060)],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                            borderRadius: BorderRadius.circular(8),
                            boxShadow: [
                              BoxShadow(
                                color: Color(0xFFD4AF37).withValues(alpha: 0.3),
                                blurRadius: 4,
                                offset: const Offset(0, 1),
                              ),
                            ],
                          ),
                          child: Text(
                            post.activeTitle!,
                            style: const TextStyle(
                              color: Color(0xFF2D1B00),
                              fontSize: 9,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.3,
                            ),
                          ),
                        ),
                        const SizedBox(width: 6),
                      ],
                      Flexible(
                        child: Text(
                          post.username,
                          style: TextStyle(
                            color: Theme.of(context).textTheme.bodyLarge?.color ??
                                Colors.white,
                            fontWeight: FontWeight.w600,
                            fontSize: 14,
                          ),
                          overflow: TextOverflow.ellipsis,
                          semanticsLabel: 'Kullanıcı: ${post.username}',
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    post.timeAgo,
                    style: TextStyle(
                      color: Theme.of(context).textTheme.bodySmall?.color ??
                          Colors.grey,
                      fontSize: 12,
                    ),
                    semanticsLabel: 'Paylaşım zamanı: ${post.timeAgo}',
                  ),
                ],
              ),
            ),
          ),
          // More options
          IconButton(
            icon: Icon(
              Icons.more_horiz_rounded,
              color:
                  Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey,
              size: 20,
            ),
            onPressed: () {
              showModalBottomSheet(
                context: context,
                backgroundColor: Theme.of(context).colorScheme.surface,
                shape: const RoundedRectangleBorder(
                  borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
                ),
                builder: (context) => SafeArea(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const SizedBox(height: 8),
                      Container(
                        width: 40,
                        height: 4,
                        decoration: BoxDecoration(
                          color: Theme.of(context).dividerColor,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      const SizedBox(height: 16),
                      if (isMine) ...[
                        ListTile(
                          leading: Icon(Icons.edit_rounded,
                              color: Theme.of(context)
                                      .textTheme
                                      .bodyLarge
                                      ?.color ??
                                  Colors.white),
                          title: Text('Düzenle',
                              style: TextStyle(
                                  color: Theme.of(context)
                                          .textTheme
                                          .bodyLarge
                                          ?.color ??
                                      Colors.white)),
                          onTap: () {
                            Navigator.pop(context);
                            _showEditDialog(context, ref);
                          },
                        ),
                        ListTile(
                          leading: Icon(Icons.delete_outline_rounded,
                              color: Theme.of(context).colorScheme.error),
                          title: Text('Sil',
                              style: TextStyle(
                                  color: Theme.of(context).colorScheme.error)),
                          onTap: () {
                            Navigator.pop(context);
                            _showDeleteConfirm(context, ref);
                          },
                        ),
                      ] else ...[
                        ListTile(
                          leading: const Icon(Icons.favorite,
                              color: Colors.pinkAccent),
                          title: Text('İlgileniyorum',
                              style: TextStyle(
                                  color: Theme.of(context)
                                          .textTheme
                                          .bodyLarge
                                          ?.color ??
                                      Colors.white)),
                          onTap: () {
                            Navigator.pop(context);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('İlgi alanlarınıza eklendi! ✨'),
                                backgroundColor: Colors.pinkAccent,
                              ),
                            );
                          },
                        ),
                        ListTile(
                          leading: Icon(Icons.visibility_off_outlined,
                              color: Theme.of(context)
                                      .textTheme
                                      .bodySmall
                                      ?.color ??
                                  Colors.grey),
                          title: Text('İlgilenmiyorum',
                              style: TextStyle(
                                  color: Theme.of(context)
                                          .textTheme
                                          .bodyLarge
                                          ?.color ??
                                      Colors.white)),
                          onTap: () {
                            Navigator.pop(context);
                            ref.read(feedProvider).hidePost(post.postId);
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(
                                    'Bu tarz gönderiler daha az gösterilecek.'),
                                backgroundColor:
                                    Theme.of(context).colorScheme.surface,
                              ),
                            );
                          },
                        ),
                      ],
                      const SizedBox(height: 16),
                    ],
                  ),
                ),
              );
            },
            tooltip: 'Daha fazla',
          ),
        ],
      ),
    );
  }

  Widget _buildImage(BuildContext context) {
    return GestureDetector(
      onTap: () {
        showDialog(
          context: context,
          barrierColor: Colors.black87,
          builder: (_) => Dialog(
            backgroundColor: Colors.transparent,
            insetPadding: const EdgeInsets.all(16),
            child: Stack(
              alignment: Alignment.center,
              children: [
                InteractiveViewer(
                  clipBehavior: Clip.none,
                  minScale: 0.5,
                  maxScale: 4.0,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(24),
                    child: post.imageUrl == 'collage'
                        ? _buildCollageGrid(context)
                        : post.imageUrl.startsWith('http')
                            ? CachedNetworkImage(
                                imageUrl: post.imageUrl,
                                fit: BoxFit.contain,
                                placeholder: (context, url) =>
                                    CircularProgressIndicator(
                                        color: Theme.of(context).colorScheme.primary),
                              )
                            : Image.file(File(post.imageUrl), fit: BoxFit.contain),
                  ),
                ),
                Positioned(
                  top: 10,
                  right: 10,
                  child: IconButton(
                    icon:
                        const Icon(Icons.close, color: Colors.white, size: 30),
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
              ],
            ),
          ),
        );
      },
      child: AspectRatio(
        aspectRatio: 4 / 5,
        child: post.imageUrl == 'collage'
            ? _buildCollageGrid(context)
            : post.imageUrl.startsWith('http')
                ? CachedNetworkImage(
                    imageUrl: post.imageUrl,
                    fit: BoxFit.cover,
                    placeholder: (context, url) => Container(
                      color: Theme.of(context).colorScheme.surface,
                      child: Center(
                        child: CircularProgressIndicator(
                          color: Theme.of(context).colorScheme.primary,
                          strokeWidth: 2,
                        ),
                      ),
                    ),
                errorWidget: (context, url, error) => Container(
                  color: Theme.of(context).colorScheme.surface,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.broken_image_rounded,
                        color: Theme.of(context).textTheme.bodySmall?.color ??
                            Colors.grey,
                        size: 48,
                      ),
                      SizedBox(height: AppTheme.spacingS),
                      Text(
                        'Görsel yüklenemedi',
                        style: TextStyle(
                          color: Theme.of(context).textTheme.bodySmall?.color ??
                              Colors.grey,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              )
            : Image.file(
                File(post.imageUrl),
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => Container(
                  color: Theme.of(context).colorScheme.surface,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.broken_image_rounded,
                        color: Theme.of(context).textTheme.bodySmall?.color ??
                            Colors.grey,
                        size: 48,
                      ),
                      SizedBox(height: AppTheme.spacingS),
                      Text(
                        'Görsel bulunamadı',
                        style: TextStyle(
                          color: Theme.of(context).textTheme.bodySmall?.color ??
                              Colors.grey,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
      ),
    );
  }

  Widget _buildFooter(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(AppTheme.spacingM),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Actions Row (Like, Comment, Save)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  LikeButton(
                    isLiked: post.isLiked,
                    likesCount: post.likesCount,
                    onToggle: () => onLike(post.postId),
                  ),
                  const SizedBox(width: AppTheme.spacingM),
                  GestureDetector(
                    onTap: onComment,
                    child: Row(
                      children: [
                        Icon(
                          Icons.chat_bubble_outline_rounded,
                          color: Theme.of(context).textTheme.bodyLarge?.color ??
                              Colors.white,
                          size: 24,
                        ),
                        if (post.commentsCount > 0) ...[
                          const SizedBox(width: 4),
                          Text(
                            '${post.commentsCount}',
                            style: TextStyle(
                              color: Theme.of(context)
                                      .textTheme
                                      .bodyLarge
                                      ?.color ??
                                  Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ],
              ),
              IconButton(
                icon: Icon(
                  post.isSaved ? Icons.bookmark : Icons.bookmark_outline,
                  color: post.isSaved ? AppTheme.accentPurple : (Theme.of(context).textTheme.bodySmall?.color ?? Colors.white),
                  size: 26,
                ),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
                onPressed: () => onSave?.call(post.postId),
                tooltip: post.isSaved ? 'Kaydedilenlerden Çıkar' : 'Kaydet',
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingS),
          // Caption
          if (post.caption.isNotEmpty) ...[
            RichText(
              text: TextSpan(
                children: [
                  TextSpan(
                    text: '${post.username} ',
                    style: TextStyle(
                      color: Theme.of(context).textTheme.bodyLarge?.color ??
                          Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  TextSpan(
                    text: post.caption,
                    style: TextStyle(
                      color: Theme.of(context).textTheme.bodyMedium?.color ??
                          Colors.grey,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ],
          // View all comments hint
          if (post.commentsCount > 0) ...[
            const SizedBox(height: 4),
            GestureDetector(
              onTap: onComment,
              child: Text(
                '${post.commentsCount} yorumun tümünü gör',
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodySmall?.color ??
                      Colors.grey,
                  fontSize: 13,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Future<void> _showEditDialog(BuildContext context, WidgetRef ref) async {
    final controller = TextEditingController(text: post.caption);
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Theme.of(context).colorScheme.surface,
        title: Text('Gönderiyi Düzenle',
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
            hintText: 'Yeni açıklama...',
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
            child: Text('İptal',
                style: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Kaydet',
                style: TextStyle(color: Theme.of(context).colorScheme.primary)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      final newCaption = controller.text.trim();
      try {
        await ref.read(feedProvider).updatePost(post.postId, newCaption);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Gönderi güncellendi.')),
          );
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Güncelleme hatası: $e')),
          );
        }
      }
    }
  }

  Future<void> _showDeleteConfirm(BuildContext context, WidgetRef ref) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Theme.of(context).colorScheme.surface,
        title: Text('Gönderiyi Sil',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white)),
        content: Text(
            'Bu gönderiyi kalıcı olarak silmek istediğinize emin misiniz?',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyMedium?.color ??
                    Colors.grey)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('İptal',
                style: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Sil',
                style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await ref.read(feedProvider).deletePost(post.postId);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Gönderi silindi.')),
          );
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Silme hatası: $e')),
          );
        }
      }
    }
  }

  Widget _buildCollageGrid(BuildContext context) {
    if (post.outfitItems.isEmpty) return Container(color: Colors.grey[900]);
    return Container(
      color: Theme.of(context).colorScheme.surface,
      padding: const EdgeInsets.all(8),
      child: Center(
        child: Wrap(
          spacing: 4,
          runSpacing: 4,
          alignment: WrapAlignment.center,
          runAlignment: WrapAlignment.center,
          children: post.outfitItems.map((item) {
            final url = ApiService.fixImageUrl(item.imageUrl);
            return GestureDetector(
              onTap: () {
                showDialog(
                  context: context,
                  barrierColor: Colors.black87,
                  builder: (_) => Dialog(
                    backgroundColor: Colors.transparent,
                    insetPadding: const EdgeInsets.all(16),
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        Container(
                          decoration: BoxDecoration(
                            color: Theme.of(context).cardColor,
                            borderRadius: BorderRadius.circular(24),
                          ),
                          clipBehavior: Clip.antiAlias,
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              url.isNotEmpty 
                                  ? InteractiveViewer(
                                      minScale: 0.5,
                                      maxScale: 4.0,
                                      child: CachedNetworkImage(
                                        imageUrl: url,
                                        fit: BoxFit.contain,
                                        placeholder: (context, url) => CircularProgressIndicator(color: Theme.of(context).colorScheme.primary),
                                      ),
                                    )
                                  : Container(height: 200, color: Colors.grey[800]),
                              Padding(
                                padding: const EdgeInsets.all(16.0),
                                child: Text(
                                  'Outfit Item',
                                  style: TextStyle(
                                    color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        Positioned(
                          top: 10,
                          right: 10,
                          child: IconButton(
                            icon: const Icon(Icons.close, color: Colors.white, size: 30),
                            onPressed: () => Navigator.pop(context),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
              child: Container(
                width: 150,
                height: 200,
                clipBehavior: Clip.antiAlias,
                decoration: BoxDecoration(
                  color: Colors.grey[800],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: url.isNotEmpty
                    ? CachedNetworkImage(
                        imageUrl: url,
                        fit: BoxFit.cover,
                        placeholder: (context, url) => Center(
                          child: CircularProgressIndicator(
                            color: Theme.of(context).colorScheme.primary,
                            strokeWidth: 2,
                          ),
                        ),
                        errorWidget: (context, url, error) => const Center(
                          child: Icon(Icons.broken_image, color: Colors.grey, size: 40),
                        ),
                      )
                    : null,
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
}
