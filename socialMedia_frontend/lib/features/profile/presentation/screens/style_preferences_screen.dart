import 'package:flutter/material.dart';

class StylePreferencesScreen extends StatefulWidget {
  const StylePreferencesScreen({super.key});

  @override
  State<StylePreferencesScreen> createState() => _StylePreferencesScreenState();
}

class _StylePreferencesScreenState extends State<StylePreferencesScreen> {
  final List<String> _vibes = [
    'Casual', 'Formal', 'Streetwear', 'Vintage', 
    'Minimalist', 'Bohemian', 'Sporty', 'Chic'
  ];
  final List<String> _colors = [
    'Black', 'White', 'Navy', 'Red', 'Earth Tones', 'Pastels'
  ];
  
  final Set<String> _selectedVibes = {'Casual', 'Minimalist'};
  final Set<String> _selectedColors = {'Black', 'Earth Tones'};

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          'Style Preferences',
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
                'Help AI Stylist Know You Better',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.black,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Select your preferred styles and colors to get better outfit recommendations.',
                style: TextStyle(
                  fontSize: 14,
                  color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey,
                ),
              ),
              const SizedBox(height: 32),

              Text(
                'Favorite Vibes',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).textTheme.bodyLarge?.color,
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8.0,
                runSpacing: 8.0,
                children: _vibes.map((vibe) {
                  final isSelected = _selectedVibes.contains(vibe);
                  return FilterChip(
                    label: Text(vibe),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        if (selected) {
                          _selectedVibes.add(vibe);
                        } else {
                          _selectedVibes.remove(vibe);
                        }
                      });
                    },
                    selectedColor: Theme.of(context).colorScheme.primary,
                    checkmarkColor: Colors.white,
                    labelStyle: TextStyle(
                      color: isSelected 
                          ? Colors.white 
                          : Theme.of(context).textTheme.bodyLarge?.color,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 32),

              Text(
                'Go-To Colors',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).textTheme.bodyLarge?.color,
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8.0,
                runSpacing: 8.0,
                children: _colors.map((color) {
                  final isSelected = _selectedColors.contains(color);
                  return FilterChip(
                    label: Text(color),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        if (selected) {
                          _selectedColors.add(color);
                        } else {
                          _selectedColors.remove(color);
                        }
                      });
                    },
                    selectedColor: Theme.of(context).colorScheme.secondary,
                    checkmarkColor: Colors.white,
                    labelStyle: TextStyle(
                      color: isSelected 
                          ? Colors.white 
                          : Theme.of(context).textTheme.bodyLarge?.color,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 48),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Preferences saved!')),
                    );
                    Navigator.pop(context);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text('Save Preferences', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
