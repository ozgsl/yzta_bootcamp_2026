import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/localization/locale_provider.dart';
import '../../../../services/api_service.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../profile/presentation/screens/profile_screen.dart';
import 'package:timeago/timeago.dart' as timeago;

class NotificationsScreen extends ConsumerStatefulWidget {
  const NotificationsScreen({super.key});

  @override
  ConsumerState<NotificationsScreen> createState() =>
      _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen> {
  List<Map<String, dynamic>> _notifications = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }

  Future<void> _loadNotifications() async {
    final userId = ref.read(authProvider).currentUserId;
    if (userId == null) return;

    setState(() => _isLoading = true);
    try {
      final data = await ApiService().getNotifications(userId);
      if (mounted) {
        setState(() {
          _notifications = List<Map<String, dynamic>>.from(data);
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _markAllRead() async {
    final userId = ref.read(authProvider).currentUserId;
    if (userId == null) return;
    try {
      await ApiService().markAllNotificationsRead(userId);
      await _loadNotifications();
    } catch (_) {}
  }

  IconData _getNotifIcon(String type) {
    switch (type) {
      case 'like':
        return Icons.favorite_rounded;
      case 'comment':
        return Icons.chat_bubble_rounded;
      case 'follow':
        return Icons.person_add_rounded;
      case 'mention':
        return Icons.alternate_email_rounded;
      default:
        return Icons.notifications_rounded;
    }
  }

  Color _getNotifColor(String type) {
    switch (type) {
      case 'like':
        return Colors.redAccent;
      case 'comment':
        return Theme.of(context).colorScheme.primary;
      case 'follow':
        return Colors.blueAccent;
      case 'mention':
        return Colors.orangeAccent;
      default:
        return Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey;
    }
  }

  String _timeAgo(String? dateStr) {
    if (dateStr == null) return '';
    try {
      final date = DateTime.parse(dateStr);
      return timeago.format(date, locale: 'tr');
    } catch (_) {
      return dateStr;
    }
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(stringsProvider);
    final hasUnread = _notifications.any((n) => n['is_read'] == false);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          s.isTr ? 'Bildirimler' : 'Notifications',
          style: TextStyle(
              color:
                  Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
              fontWeight: FontWeight.bold),
        ),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        elevation: 0,
        iconTheme: IconThemeData(
            color:
                Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
        actions: [
          if (hasUnread)
            TextButton(
              onPressed: _markAllRead,
              child: Text(
                s.isTr ? 'Tümünü Oku' : 'Read All',
                style: TextStyle(
                    color: Theme.of(context).colorScheme.primary, fontSize: 13),
              ),
            ),
        ],
      ),
      body: _isLoading
          ? Center(
              child: CircularProgressIndicator(
                  color: Theme.of(context).colorScheme.primary))
          : _notifications.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.notifications_off_rounded,
                          size: 64,
                          color: Theme.of(context).textTheme.bodySmall?.color ??
                              Colors.grey),
                      const SizedBox(height: 16),
                      Text(
                        s.isTr
                            ? 'Henüz bildiriminiz yok'
                            : 'No notifications yet',
                        style: TextStyle(
                            color:
                                Theme.of(context).textTheme.bodySmall?.color ??
                                    Colors.grey,
                            fontSize: 16),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  color: Theme.of(context).colorScheme.primary,
                  onRefresh: _loadNotifications,
                  child: ListView.builder(
                    itemCount: _notifications.length,
                    itemBuilder: (context, index) {
                      final notif = _notifications[index];
                      final isRead = notif['is_read'] == true;
                      final type = notif['type'] as String? ?? '';
                      final message = notif['message'] as String? ?? '';
                      final actorAvatar = notif['actor_avatar_url'] as String?;
                      final postImageUrl = notif['post_image_url'] as String?;

                      return Container(
                        color: isRead
                            ? Colors.transparent
                            : Theme.of(context)
                                .colorScheme
                                .primary
                                .withValues(alpha: 0.05),
                        child: ListTile(
                          leading: Stack(
                            clipBehavior: Clip.none,
                            children: [
                              CircleAvatar(
                                radius: 22,
                                backgroundColor:
                                    Theme.of(context).colorScheme.surface,
                                backgroundImage: actorAvatar != null &&
                                        actorAvatar.isNotEmpty
                                    ? NetworkImage(actorAvatar)
                                    : null,
                                child:
                                    actorAvatar == null || actorAvatar.isEmpty
                                        ? Icon(Icons.person,
                                            color: Theme.of(context)
                                                    .textTheme
                                                    .bodyMedium
                                                    ?.color ??
                                                Colors.grey)
                                        : null,
                              ),
                              Positioned(
                                bottom: -2,
                                right: -2,
                                child: Container(
                                  padding: const EdgeInsets.all(2),
                                  decoration: BoxDecoration(
                                    color: Theme.of(context)
                                        .scaffoldBackgroundColor,
                                    shape: BoxShape.circle,
                                  ),
                                  child: Icon(
                                    _getNotifIcon(type),
                                    size: 14,
                                    color: _getNotifColor(type),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          title: Text(
                            message,
                            style: TextStyle(
                              color: Theme.of(context)
                                      .textTheme
                                      .bodyLarge
                                      ?.color ??
                                  Colors.white,
                              fontSize: 14,
                              fontWeight:
                                  isRead ? FontWeight.normal : FontWeight.w600,
                            ),
                          ),
                          subtitle: Text(
                            _timeAgo(notif['created_at'] as String?),
                            style: TextStyle(
                                color: Theme.of(context)
                                        .textTheme
                                        .bodySmall
                                        ?.color ??
                                    Colors.grey,
                                fontSize: 12),
                          ),
                          trailing:
                              postImageUrl != null && postImageUrl.isNotEmpty
                                  ? ClipRRect(
                                      borderRadius: BorderRadius.circular(8),
                                      child: Image.network(
                                        postImageUrl,
                                        width: 44,
                                        height: 44,
                                        fit: BoxFit.cover,
                                        errorBuilder: (_, __, ___) =>
                                            const SizedBox.shrink(),
                                      ),
                                    )
                                  : null,
                          onTap: () async {
                            if (!isRead) {
                              try {
                                await ApiService().markNotificationRead(
                                    notif['notification_id'] as String);
                                await _loadNotifications();
                              } catch (_) {}
                            }

                            if (type == 'follow') {
                              if (!context.mounted) return;
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => ProfileScreen(
                                      userId: notif['actor_id'] as String),
                                ),
                              );
                            } else if (type == 'like' || type == 'comment') {
                              final currentUserId =
                                  ref.read(authProvider).currentUserId;
                              if (currentUserId != null) {
                                if (!context.mounted) return;
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) =>
                                        ProfileScreen(userId: currentUserId),
                                  ),
                                );
                              }
                            }
                          },
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
