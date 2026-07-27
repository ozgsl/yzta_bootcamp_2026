import 'package:flutter/material.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  const PrivacyPolicyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          'Privacy Policy',
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
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Digital Wardrobe Privacy Policy',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.black,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Your privacy is our priority. Here is how we handle your data:\n\n'
              '1. Data Collection\n'
              'We collect the information you provide when creating an account, as well as the photos you upload to your digital wardrobe.\n\n'
              '2. How We Use Data\n'
              'Your data is used to provide the service: displaying your wardrobe, generating AI outfit recommendations, and enabling social sharing on your feed.\n\n'
              '3. Artificial Intelligence\n'
              'We use local AI models (like LLaMA and FashionSigLIP) to process your data. This means your outfit images and chat logs with the AI Stylist are processed securely and are not used to train global commercial models without your consent.\n\n'
              '4. Data Security\n'
              'We implement standard security practices to protect your data. You can delete your account and all associated data at any time from the account settings.',
              style: TextStyle(
                fontSize: 15,
                height: 1.5,
                color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey[800],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
