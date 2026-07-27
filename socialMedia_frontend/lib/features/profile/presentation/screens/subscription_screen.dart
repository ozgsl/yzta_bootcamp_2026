import 'package:flutter/material.dart';
import '../../../../../core/theme/app_theme.dart';

class SubscriptionScreen extends StatelessWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          'Subscription',
          style: TextStyle(
            color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.black,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: IconThemeData(
            color: Theme.of(context).iconTheme.color ?? Colors.black),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Unlock Your Full Style Potential',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.black,
                  height: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Choose a plan that fits your fashion journey.',
                style: TextStyle(
                  fontSize: 16,
                  color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey,
                ),
              ),
              const SizedBox(height: 32),
              
              _SubscriptionCard(
                title: 'Free',
                price: '\$0 / month',
                features: const [
                  'Up to 50 wardrobe items',
                  'Basic AI Outfit suggestions',
                  'Social Feed access',
                ],
                isCurrentPlan: true,
              ),
              const SizedBox(height: 16),
              
              _SubscriptionCard(
                title: 'Premium',
                price: '\$4.99 / month',
                features: const [
                  'Unlimited wardrobe items',
                  'Advanced AI Stylist chat',
                  'Weather-based scheduling',
                  'Ad-free experience',
                ],
                isPopular: true,
              ),
              const SizedBox(height: 16),

              _SubscriptionCard(
                title: 'Pro',
                price: '\$9.99 / month',
                features: const [
                  'Everything in Premium',
                  'Virtual Try-On (Coming Soon)',
                  'Early access to new features',
                  'Priority support',
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SubscriptionCard extends StatelessWidget {
  final String title;
  final String price;
  final List<String> features;
  final bool isPopular;
  final bool isCurrentPlan;

  const _SubscriptionCard({
    required this.title,
    required this.price,
    required this.features,
    this.isPopular = false,
    this.isCurrentPlan = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24.0),
      decoration: BoxDecoration(
        color: isPopular ? Theme.of(context).colorScheme.surface : Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(20),
        border: isPopular
            ? Border.all(color: Theme.of(context).colorScheme.primary, width: 2)
            : Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).textTheme.bodyLarge?.color,
                ),
              ),
              if (isPopular)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primary,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text(
                    'POPULAR',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              if (isCurrentPlan)
                const Text(
                  'Current Plan',
                  style: TextStyle(
                    color: Colors.grey,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            price,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w800,
              color: Theme.of(context).textTheme.bodyLarge?.color,
            ),
          ),
          const SizedBox(height: 16),
          ...features.map((f) => Padding(
                padding: const EdgeInsets.only(bottom: 8.0),
                child: Row(
                  children: [
                    Icon(Icons.check_circle_rounded,
                        color: Theme.of(context).colorScheme.primary, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        f,
                        style: TextStyle(
                          color: Theme.of(context).textTheme.bodyMedium?.color,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ],
                ),
              )),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: isCurrentPlan ? null : () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: isPopular
                    ? Theme.of(context).colorScheme.primary
                    : Theme.of(context).cardColor,
                foregroundColor: isPopular
                    ? Colors.white
                    : Theme.of(context).textTheme.bodyLarge?.color,
                elevation: 0,
                side: isPopular
                    ? null
                    : BorderSide(color: Theme.of(context).dividerColor),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: Text(
                isCurrentPlan ? 'Active' : 'Upgrade to $title',
                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
