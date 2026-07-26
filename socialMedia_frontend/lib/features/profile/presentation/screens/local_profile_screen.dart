import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../providers/profile_provider.dart';
import '../../../../services/api_service.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/locale_provider.dart';

class LocalProfileScreen extends ConsumerStatefulWidget {
  const LocalProfileScreen({super.key});

  @override
  ConsumerState<LocalProfileScreen> createState() => _LocalProfileScreenState();
}

class _LocalProfileScreenState extends ConsumerState<LocalProfileScreen> {
  final ApiService _api = ApiService();

  Future<void> _updateUsername(String currentUsername) async {
    final ctrl = TextEditingController(text: currentUsername);
    final newUsername = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Change Username'),
        content: TextField(
          controller: ctrl,
          decoration: const InputDecoration(labelText: 'New Username'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, ctrl.text),
            child: const Text('Save'),
          ),
        ],
      ),
    );

    if (newUsername != null && newUsername.isNotEmpty && newUsername != currentUsername) {
      try {
        await ref.read(profileProvider).updateProfile(username: newUsername);
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Username updated successfully!')));
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final userId = authState.currentUserId ?? "Unknown ID";
    final profile = ref.watch(profileProvider).user;

    final username = profile?.username ?? 'Loading...';
    final email = profile?.email ?? 'Loading...';
    final strings = ref.watch(stringsProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          strings.accountSettings,
          style: TextStyle(
              color: Colors.white, fontSize: 18, fontWeight: FontWeight.w600),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              Text(
                'Personal Information',
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodyMedium?.color ??
                      Colors.grey,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),
              Container(
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    _InfoRow(
                      label: 'Username', 
                      value: username,
                      onTap: () => _updateUsername(username),
                    ),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    _InfoRow(
                      label: 'Email', 
                      value: email,
                      onTap: () => _showEmailChangeDialog(email),
                    ),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    _InfoRow(
                      label: 'Password', 
                      value: '********',
                      onTap: () => _showPasswordChangeDialog(),
                    ),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('User ID', style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white, fontSize: 15, fontWeight: FontWeight.w500)),
                          Text(userId, style: TextStyle(color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey, fontSize: 13)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
              
              // Sign Out & Delete Account
              Container(
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    InkWell(
                      onTap: () {
                        ref.read(authProvider.notifier).logout();
                      },
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                        child: Row(
                          children: [
                            Icon(Icons.logout_rounded, color: Theme.of(context).textTheme.bodyLarge?.color),
                            const SizedBox(width: 16),
                            Text(
                              strings.logout,
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500),
                            ),
                          ],
                        ),
                      ),
                    ),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    InkWell(
                      onTap: () {
                        // TODO: Implement delete account logic
                      },
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                        child: Row(
                          children: [
                            Icon(Icons.delete_outline_rounded, color: Colors.redAccent),
                            const SizedBox(width: 16),
                            Text(
                              strings.deleteAccount,
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Colors.redAccent),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _showEmailChangeDialog(String currentEmail) async {
    final newEmailCtrl = TextEditingController();
    final newEmail = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Change Email'),
        content: TextField(
          controller: newEmailCtrl,
          decoration: const InputDecoration(labelText: 'New Email Address'),
          keyboardType: TextInputType.emailAddress,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(onPressed: () => Navigator.pop(ctx, newEmailCtrl.text), child: const Text('Next')),
        ],
      ),
    );

    if (newEmail != null && newEmail.isNotEmpty && newEmail != currentEmail) {
      if (!mounted) return;
      try {
        await _api.requestEmailChange(newEmail);
        if (!mounted) return;
        _showOTPDialog(
          title: 'Verify Email',
          message: 'An OTP has been sent to your NEW email ($newEmail).',
          onVerify: (code) async {
            final userId = ref.read(authProvider).currentUserId;
            if (userId != null) {
              await _api.verifyEmailChange(userId, newEmail, code);
              ref.read(profileProvider).loadProfile(userId, userId);
            }
          },
        );
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  Future<void> _showPasswordChangeDialog() async {
    final userId = ref.read(authProvider).currentUserId;
    if (userId == null) return;

    try {
      await _api.requestPasswordChange(userId);
      if (!mounted) return;
      _showOTPDialog(
        title: 'Verify Password Change',
        message: 'An OTP has been sent to your current email.',
        requiresNewPassword: true,
        onVerifyPassword: (code, newPassword) async {
          await _api.verifyPasswordChange(userId, newPassword!, code);
        },
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
  }

  void _showOTPDialog({
    required String title,
    required String message,
    bool requiresNewPassword = false,
    Future<void> Function(String)? onVerify,
    Future<void> Function(String, String?)? onVerifyPassword,
  }) {
    final codeCtrl = TextEditingController();
    final passCtrl = TextEditingController();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) {
        bool isLoading = false;
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: Text(title),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(message, style: const TextStyle(fontSize: 13, color: Colors.grey)),
                  const SizedBox(height: 16),
                  TextField(
                    controller: codeCtrl,
                    decoration: const InputDecoration(labelText: '6-digit Code'),
                    keyboardType: TextInputType.number,
                  ),
                  if (requiresNewPassword) ...[
                    const SizedBox(height: 16),
                    TextField(
                      controller: passCtrl,
                      decoration: const InputDecoration(labelText: 'New Password'),
                      obscureText: true,
                    ),
                  ],
                ],
              ),
              actions: [
                TextButton(
                  onPressed: isLoading ? null : () => Navigator.pop(ctx),
                  child: const Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: isLoading
                      ? null
                      : () async {
                          setState(() => isLoading = true);
                          try {
                            if (onVerifyPassword != null) {
                              await onVerifyPassword(codeCtrl.text, passCtrl.text);
                            } else if (onVerify != null) {
                              await onVerify(codeCtrl.text);
                            }
                            if (!mounted) return;
                            Navigator.pop(ctx);
                            ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Update successful!')));
                          } catch (e) {
                            ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text(e.toString())));
                          } finally {
                            if (mounted) setState(() => isLoading = false);
                          }
                        },
                  child: isLoading ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Text('Verify & Save'),
                ),
              ],
            );
          }
        );
      },
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  final VoidCallback? onTap;

  const _InfoRow({required this.label, required this.value, this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: TextStyle(
                color:
                    Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.w500,
              ),
            ),
            Row(
              children: [
                Text(
                  value,
                  style: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey,
                    fontSize: 15,
                  ),
                ),
                if (onTap != null) ...[
                  const SizedBox(width: 8),
                  Icon(Icons.edit_rounded, size: 16, color: AppTheme.accentViolet),
                ]
              ],
            ),
          ],
        ),
      ),
    );
  }
}
