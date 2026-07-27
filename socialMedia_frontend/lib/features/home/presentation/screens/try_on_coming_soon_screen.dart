import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';

class TryOnComingSoonScreen extends StatelessWidget {
  const TryOnComingSoonScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surface,
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.auto_awesome_rounded,
                    color: Theme.of(context).colorScheme.secondary, size: 48),
              ),
              const SizedBox(height: 32),
              Text(
                'Try-On Photo',
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'See how clothes fit on you virtually!\nThis feature is coming very soon.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodySmall?.color ??
                      Colors.grey,
                  fontSize: 16,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 48),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Text(
                  'Stay Tuned 👀',
                  style: TextStyle(
                    color: Theme.of(context).textTheme.bodyMedium?.color ??
                        Colors.grey,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
