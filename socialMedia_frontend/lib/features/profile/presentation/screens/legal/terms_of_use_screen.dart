import 'package:flutter/material.dart';

class TermsOfUseScreen extends StatelessWidget {
  const TermsOfUseScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          'Terms of Use',
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
              'Digital Wardrobe Terms of Use',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.black,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Welcome to Digital Wardrobe. By using our application, you agree to these terms.\n\n'
              '1. Purpose of the Application\n'
              'Digital Wardrobe is a social media and AI-powered fashion platform. It helps you digitize your clothes, receive AI-generated outfit recommendations, and share them with your followers.\n\n'
              '2. User Content\n'
              'You are responsible for the photos and content you upload. Please respect copyright and do not upload inappropriate material.\n\n'
              '3. AI Services\n'
              'Our AI Stylist (powered by local Ollama/LLaMA and FashionSigLIP models) provides recommendations based on your digital wardrobe. The AI\'s suggestions are for entertainment and convenience.\n\n'
              '4. Privacy and Data\n'
              'We prioritize your privacy. The AI analysis is primarily processed using our secure backend systems, and we do not sell your personal wardrobe data to third parties. Please refer to our Privacy Policy for more details.',
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
