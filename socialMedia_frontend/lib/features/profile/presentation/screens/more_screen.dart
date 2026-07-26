import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/theme/theme_provider.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/locale_provider.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import 'local_profile_screen.dart';
import 'body_measurement_screen.dart';
import 'location_timezone_screen.dart';

class MoreScreen extends ConsumerWidget {
  const MoreScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = ref.watch(stringsProvider);
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                strings.navMore,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 28,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 24),

              // Profile Card
              GestureDetector(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => LocalProfileScreen()),
                  );
                },
                child: Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              strings.accountSettings,
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              strings.manageAccount,
                              style: TextStyle(
                                color: Theme.of(context)
                                        .textTheme
                                        .bodySmall
                                        ?.color ??
                                    Colors.grey,
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Icon(Icons.chevron_right_rounded,
                          color: Theme.of(context).textTheme.bodySmall?.color ??
                              Colors.grey),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 32),

              Text(
                strings.settings,
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ??
                      Colors.white,
                  fontSize: 16,
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
                    _SettingsTile(
                        title: strings.stylePreferences,
                        icon: Icons.palette_rounded,
                        onTap: () {}),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    _SettingsTile(
                        title: strings.locationTimezone,
                        icon: Icons.location_on_rounded,
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (_) => const LocationTimezoneScreen()),
                          );
                        }),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    _SettingsTile(
                        title: strings.outfitSchedule,
                        icon: Icons.calendar_today_rounded,
                        onTap: () {}),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    _SettingsTile(
                        title: strings.language,
                        icon: Icons.language_rounded,
                        onTap: () {
                          _showLanguageDialog(context, ref);
                        }),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    _SettingsTile(
                        title: strings.bodyMeasurements,
                        icon: Icons.straighten_rounded,
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (_) => const BodyMeasurementScreen()),
                          );
                        }),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    _SettingsTile(
                        title: strings.subscription,
                        icon: Icons.credit_card_rounded,
                        onTap: () {}),
                  ],
                ),
              ),

              Container(
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    _SettingsTile(
                        title: strings.termsOfUse,
                        icon: Icons.description_rounded,
                        hasExternalIcon: true,
                        onTap: () {}),
                    Divider(height: 1, color: Theme.of(context).dividerColor),
                    _SettingsTile(
                        title: strings.privacyPolicy,
                        icon: Icons.security_rounded,
                        hasExternalIcon: true,
                        onTap: () {}),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Container(
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: _SettingsAppearance(
                    title: strings.theme,
                    icon: Icons.brightness_medium_rounded),
              ),
              const SizedBox(height: 100), // padding for bottom nav
            ],
          ),
        ),
      ),
    );
  }

  void _showLanguageDialog(BuildContext context, WidgetRef ref) {
    final languages = [
      {'name': 'Türkçe', 'locale': AppLocale.tr},
      {'name': 'English', 'locale': AppLocale.en},
      {'name': 'Deutsch', 'locale': AppLocale.de},
      {'name': 'Français', 'locale': AppLocale.fr},
      {'name': '日本語', 'locale': AppLocale.ja},
      {'name': '한국어', 'locale': AppLocale.ko},
      {'name': '中文', 'locale': AppLocale.zh},
    ];
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Theme.of(context).cardColor,
        title: Text(ref.watch(stringsProvider).languageTitle,
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white)),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: languages.length,
            itemBuilder: (context, index) {
              final lang = languages[index];
              return ListTile(
                title: Text(lang['name'] as String,
                    style: TextStyle(
                        color: Theme.of(context).textTheme.bodyMedium?.color ??
                            Colors.grey)),
                onTap: () {
                  ref
                      .read(localeProvider.notifier)
                      .setLocale(lang['locale'] as AppLocale);
                  Navigator.pop(context);
                },
              );
            },
          ),
        ),
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final String title;
  final IconData icon;
  final VoidCallback onTap;
  final bool isDestructive;
  final bool isCenter;
  final bool hasExternalIcon;

  const _SettingsTile({
    required this.title,
    required this.icon,
    required this.onTap,
    this.isDestructive = false,
    this.isCenter = false,
    this.hasExternalIcon = false,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        child: Row(
          mainAxisAlignment:
              isCenter ? MainAxisAlignment.center : MainAxisAlignment.start,
          children: [
            Icon(
              icon,
              size: 20,
              color: isDestructive
                  ? Theme.of(context).colorScheme.error
                  : Theme.of(context).textTheme.bodyMedium?.color ??
                      Colors.grey,
            ),
            const SizedBox(width: 16),
            Text(
              title,
              style: TextStyle(
                color: isDestructive
                    ? Theme.of(context).colorScheme.error
                    : Theme.of(context).textTheme.bodyLarge?.color ??
                        Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.w500,
              ),
            ),
            if (!isCenter) const Spacer(),
            if (!isCenter)
              Icon(
                hasExternalIcon
                    ? Icons.open_in_new_rounded
                    : Icons.chevron_right_rounded,
                color:
                    Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey,
                size: 18,
              ),
          ],
        ),
      ),
    );
  }
}

class _SettingsAppearance extends ConsumerWidget {
  final String title;
  final IconData icon;

  const _SettingsAppearance({required this.title, required this.icon});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = ref.watch(stringsProvider);
    final currentTheme = ref.watch(themeProvider);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon,
                  size: 20,
                  color: Theme.of(context).textTheme.bodyMedium?.color ??
                      Colors.grey),
              SizedBox(width: 16),
              Text(
                title,
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ??
                      Colors.white,
                  fontSize: 15,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                  child: GestureDetector(
                onTap: () =>
                    ref.read(themeProvider.notifier).setTheme(ThemeMode.system),
                child: _SegmentItem(
                    label: strings.systemTheme,
                    isSelected: currentTheme == ThemeMode.system),
              )),
              const SizedBox(width: 8),
              Expanded(
                  child: GestureDetector(
                onTap: () =>
                    ref.read(themeProvider.notifier).setTheme(ThemeMode.light),
                child: _SegmentItem(
                    label: strings.lightTheme,
                    isSelected: currentTheme == ThemeMode.light),
              )),
              const SizedBox(width: 8),
              Expanded(
                  child: GestureDetector(
                onTap: () =>
                    ref.read(themeProvider.notifier).setTheme(ThemeMode.dark),
                child: _SegmentItem(
                    label: strings.darkTheme,
                    isSelected: currentTheme == ThemeMode.dark),
              )),
            ],
          ),
        ],
      ),
    );
  }
}

class _SegmentItem extends StatelessWidget {
  final String label;
  final bool isSelected;

  const _SegmentItem({required this.label, required this.isSelected});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        color: isSelected ? Theme.of(context).colorScheme.primary : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Center(
        child: Text(
          label,
          style: TextStyle(
            color: isSelected
                ? Colors.white
                : Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey,
            fontSize: 13,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
          ),
        ),
      ),
    );
  }
}
