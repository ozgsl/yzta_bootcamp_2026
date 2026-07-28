import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:country_picker/country_picker.dart';
import 'package:timezone/data/latest.dart' as tz;
import 'package:timezone/timezone.dart' as tz;
import '../../../../core/theme/app_theme.dart';
import '../providers/profile_provider.dart';

class LocationTimezoneScreen extends ConsumerStatefulWidget {
  const LocationTimezoneScreen({super.key});

  @override
  ConsumerState<LocationTimezoneScreen> createState() => _LocationTimezoneScreenState();
}

class _LocationTimezoneScreenState extends ConsumerState<LocationTimezoneScreen> {
  String _selectedCountry = '';
  String _selectedCity = '';
  String _selectedTimezone = '';
  final _cityController = TextEditingController();

  @override
  void initState() {
    super.initState();
    tz.initializeTimeZones();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final user = ref.read(profileProvider).user;
      if (user != null) {
        final parts = user.location.split(',');
        if (parts.length >= 2) {
          setState(() {
            _selectedCity = parts[0].trim();
            _selectedCountry = parts.sublist(1).join(',').trim();
          });
        } else {
          setState(() {
            _selectedCountry = user.location.trim();
            _selectedCity = '';
          });
        }
        _cityController.text = _selectedCity;
        setState(() => _selectedTimezone = user.timezone);
      }
    });
  }

  @override
  void dispose() {
    _cityController.dispose();
    super.dispose();
  }

  void _pickCountry() {
    showCountryPicker(
      context: context,
      showPhoneCode: false,
      countryListTheme: CountryListThemeData(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        textStyle: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
        searchTextStyle: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
        bottomSheetHeight: MediaQuery.of(context).size.height * 0.8,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
      ),
      onSelect: (Country country) {
        setState(() {
          _selectedCountry = country.name;
          // Reset city when country changes
          _selectedCity = '';
          _cityController.clear();
        });
      },
    );
  }

  void _pickTimezone() {
    final timezones = tz.timeZoneDatabase.locations.keys.toList();
    timezones.sort();

    showModalBottomSheet(
      context: context,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                'Select Timezone',
                style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: timezones.length,
                itemBuilder: (context, index) {
                  final t = timezones[index];
                  return ListTile(
                    title: Text(
                      t,
                      style: TextStyle(
                        color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey,
                      ),
                    ),
                    onTap: () {
                      setState(() => _selectedTimezone = t);
                      _save();
                      Navigator.pop(context);
                    },
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }

  Future<void> _save() async {
    // Build location string: "City, Country" if both present, else just country
    final city = _cityController.text.trim();
    final country = _selectedCountry.trim();
    String locationStr;
    if (city.isNotEmpty && country.isNotEmpty) {
      locationStr = '$city, $country';
    } else if (city.isNotEmpty) {
      locationStr = city;
    } else {
      locationStr = country;
    }

    try {
      await ref.read(profileProvider).updateProfile(
            location: locationStr,
            timezone: _selectedTimezone,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Preferences saved successfully.'),
          backgroundColor: AppTheme.successColor,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error saving: $e'),
          backgroundColor: AppTheme.errorColor,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final countrySelected = _selectedCountry.isNotEmpty;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Location & Timezone'),
        actions: [
          TextButton(
            onPressed: _save,
            child: Text(
              'Save',
              style: TextStyle(
                color: Theme.of(context).colorScheme.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Help us tailor your experience by setting your location and timezone.',
              style: TextStyle(color: Colors.grey, fontSize: 14),
            ),
            const SizedBox(height: 32),

            // Country picker tile
            _buildSelectionTile(
              label: 'Country',
              value: _selectedCountry.isEmpty ? 'Select Country' : _selectedCountry,
              icon: Icons.public_rounded,
              onTap: _pickCountry,
            ),

            const SizedBox(height: 16),

            // City text field — enabled only after country is selected
            AnimatedOpacity(
              opacity: countrySelected ? 1.0 : 0.4,
              duration: const Duration(milliseconds: 300),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardColor,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: countrySelected
                        ? Theme.of(context).colorScheme.primary.withOpacity(0.5)
                        : Colors.transparent,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.location_city_rounded,
                      color: countrySelected ? AppTheme.accentViolet : Colors.grey,
                      size: 28,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'City (for weather)',
                            style: const TextStyle(color: Colors.grey, fontSize: 12),
                          ),
                          TextField(
                            controller: _cityController,
                            enabled: countrySelected,
                            style: TextStyle(
                              color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.w500,
                            ),
                            decoration: InputDecoration(
                              hintText: countrySelected
                                  ? 'e.g. Antalya, Istanbul, London'
                                  : 'Select a country first',
                              hintStyle: const TextStyle(color: Colors.grey, fontSize: 14),
                              border: InputBorder.none,
                              isDense: true,
                              contentPadding: const EdgeInsets.symmetric(vertical: 4),
                            ),
                            onChanged: (val) => setState(() => _selectedCity = val),
                            onSubmitted: (_) => _save(),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Timezone picker tile
            _buildSelectionTile(
              label: 'Timezone',
              value: _selectedTimezone.isEmpty ? 'Select Timezone' : _selectedTimezone,
              icon: Icons.access_time_rounded,
              onTap: _pickTimezone,
            ),

            const SizedBox(height: 8),
            if (countrySelected && _cityController.text.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, color: Colors.grey, size: 14),
                    const SizedBox(width: 6),
                    Text(
                      'Weather will be fetched for: ${_cityController.text.trim()}, $_selectedCountry',
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSelectionTile({
    required String label,
    required String value,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          children: [
            Icon(icon, color: AppTheme.accentViolet, size: 28),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
               crossAxisAlignment: CrossAxisAlignment.start,
               children: [
                 Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                 const SizedBox(height: 4),
                 Text(
                   value,
                   style: TextStyle(
                     color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white,
                     fontSize: 16,
                     fontWeight: FontWeight.w500,
                   ),
                 ),
               ],
              ),
            ),
            const Icon(Icons.chevron_right_rounded, color: Colors.grey),
          ],
        ),
      ),
    );
  }
}
