import 'dart:io';
import 'dart:convert';
import 'package:image_picker/image_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:country_picker/country_picker.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/localization/locale_provider.dart';
import '../../../../services/api_service.dart';
import '../providers/profile_provider.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';

class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _displayNameController = TextEditingController();
  final _bioController = TextEditingController();
  final _cityController = TextEditingController();
  final _countryController = TextEditingController();
  final _avatarUrlController = TextEditingController();
  final _picker = ImagePicker();
  File? _selectedImage;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    final user = ref.read(profileProvider).user;
    if (user != null) {
      _displayNameController.text = user.displayName;
      _bioController.text = user.bio;
      _avatarUrlController.text = user.avatarUrl;

      final locParts = user.location.split(',');
      if (locParts.length > 1) {
        _cityController.text = locParts[0].trim();
        _countryController.text = locParts.sublist(1).join(',').trim();
      } else {
        _cityController.text = user.location.trim();
        _countryController.text = '';
      }
    }
  }

  Future<String?> _uploadImage(File file) async {
    final uri = Uri.parse('${ApiService.baseUrl}/captions/upload');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('file', file.path));
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['url'] as String?;
    }
    return null;
  }

  Future<void> _pickImage() async {
    final xfile = await _picker.pickImage(
        source: ImageSource.gallery, imageQuality: 75, maxWidth: 1024);
    if (xfile != null) {
      setState(() => _selectedImage = File(xfile.path));
    }
  }

  Future<void> _saveProfile() async {
    setState(() => _isLoading = true);
    try {
      final userId = ref.read(authProvider).currentUserId;
      if (userId == null) return;

      String avatarUrl = _avatarUrlController.text;
      if (_selectedImage != null) {
        final uploadedUrl = await _uploadImage(_selectedImage!);
        if (uploadedUrl != null) avatarUrl = uploadedUrl;
      }

      String locationStr = '';
      final city = _cityController.text.trim();
      final country = _countryController.text.trim();
      if (city.isNotEmpty && country.isNotEmpty) {
        locationStr = '$city, $country';
      } else if (city.isNotEmpty) {
        locationStr = city;
      } else if (country.isNotEmpty) {
        locationStr = country;
      }

      await ApiService().updateProfile(
        userId: userId,
        displayName: _displayNameController.text,
        bio: _bioController.text,
        location: locationStr,
        avatarUrl: avatarUrl,
      );

      // Refresh profile data
      await ref.read(profileProvider).loadProfile(userId, userId);

      if (mounted) {
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to update profile: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(stringsProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(s.isTr ? 'Profili Düzenle' : 'Edit Profile',
            style: TextStyle(
                color: Theme.of(context).textTheme.bodyLarge?.color ??
                    Colors.white)),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        elevation: 0,
        iconTheme: IconThemeData(
            color:
                Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveProfile,
            child: _isLoading
                ? SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Theme.of(context).colorScheme.primary))
                : Text(s.isTr ? 'Kaydet' : 'Save',
                    style: TextStyle(
                        color: Theme.of(context).colorScheme.primary,
                        fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Center(
              child: GestureDetector(
                onTap: _pickImage,
                child: Stack(
                  children: [
                    CircleAvatar(
                      radius: 50,
                      backgroundColor: Theme.of(context).colorScheme.surface,
                      backgroundImage: _selectedImage != null
                          ? FileImage(_selectedImage!) as ImageProvider
                          : (_avatarUrlController.text.isNotEmpty
                              ? NetworkImage(_avatarUrlController.text)
                              : null),
                      child: (_selectedImage == null &&
                              _avatarUrlController.text.isEmpty)
                          ? Icon(Icons.person,
                              size: 50,
                              color: Theme.of(context)
                                      .textTheme
                                      .bodyMedium
                                      ?.color ??
                                  Colors.grey)
                          : null,
                    ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.primary,
                          shape: BoxShape.circle,
                        ),
                        padding: const EdgeInsets.all(8),
                        child: const Icon(Icons.camera_alt,
                            color: Colors.white, size: 20),
                      ),
                    )
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),
            TextField(
              controller: _displayNameController,
              style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ??
                      Colors.white),
              decoration: InputDecoration(
                labelText: s.isTr ? 'Görünen Ad' : 'Display Name',
                labelStyle: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey),
                enabledBorder: UnderlineInputBorder(
                    borderSide:
                        BorderSide(color: Theme.of(context).dividerColor)),
                focusedBorder: UnderlineInputBorder(
                    borderSide: BorderSide(
                        color: Theme.of(context).colorScheme.primary)),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: GestureDetector(
                    onTap: () {
                      showCountryPicker(
                        context: context,
                        showPhoneCode: false,
                        countryListTheme: CountryListThemeData(
                          backgroundColor: Theme.of(context).scaffoldBackgroundColor,
                          textStyle: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
                          searchTextStyle: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white),
                          bottomSheetHeight: 500,
                          borderRadius: const BorderRadius.only(
                            topLeft: Radius.circular(20.0),
                            topRight: Radius.circular(20.0),
                          ),
                        ),
                        onSelect: (Country country) {
                          setState(() {
                            _countryController.text = country.name;
                          });
                        },
                      );
                    },
                    child: AbsorbPointer(
                      child: TextField(
                        controller: _countryController,
                        style: TextStyle(
                            color: Theme.of(context).textTheme.bodyLarge?.color ??
                                Colors.white),
                        decoration: InputDecoration(
                          labelText: s.isTr ? 'Ülke' : 'Country',
                          hintText: s.isTr ? 'Örn: Türkiye' : 'e.g. Turkey',
                          labelStyle: TextStyle(
                              color: Theme.of(context).textTheme.bodySmall?.color ??
                                  Colors.grey),
                          enabledBorder: UnderlineInputBorder(
                              borderSide:
                                  BorderSide(color: Theme.of(context).dividerColor)),
                          focusedBorder: UnderlineInputBorder(
                              borderSide: BorderSide(
                                  color: Theme.of(context).colorScheme.primary)),
                          suffixIcon: Icon(Icons.arrow_drop_down,
                              color: Theme.of(context).textTheme.bodySmall?.color ?? Colors.grey),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: _cityController,
                    enabled: _countryController.text.isNotEmpty,
                    style: TextStyle(
                        color: _countryController.text.isNotEmpty
                            ? (Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white)
                            : Colors.grey),
                    decoration: InputDecoration(
                      labelText: s.isTr ? 'Şehir (Hava Durumu)' : 'City (Weather)',
                      hintText: s.isTr ? 'Örn: Antalya' : 'e.g. London',
                      labelStyle: TextStyle(
                          color: Theme.of(context).textTheme.bodySmall?.color ??
                              Colors.grey),
                      enabledBorder: UnderlineInputBorder(
                          borderSide:
                              BorderSide(color: Theme.of(context).dividerColor)),
                      focusedBorder: UnderlineInputBorder(
                          borderSide: BorderSide(
                              color: Theme.of(context).colorScheme.primary)),
                      disabledBorder: UnderlineInputBorder(
                          borderSide:
                              BorderSide(color: Theme.of(context).dividerColor.withOpacity(0.5))),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _bioController,
              style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ??
                      Colors.white),
              maxLines: 3,
              decoration: InputDecoration(
                labelText: s.isTr ? 'Biyografi' : 'Bio',
                labelStyle: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey),
                enabledBorder: UnderlineInputBorder(
                    borderSide:
                        BorderSide(color: Theme.of(context).dividerColor)),
                focusedBorder: UnderlineInputBorder(
                    borderSide: BorderSide(
                        color: Theme.of(context).colorScheme.primary)),
              ),
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _avatarUrlController,
              style: TextStyle(
                  color: Theme.of(context).textTheme.bodyLarge?.color ??
                      Colors.white),
              decoration: InputDecoration(
                labelText: s.isTr ? 'Profil Fotoğrafı URL' : 'Avatar URL',
                labelStyle: TextStyle(
                    color: Theme.of(context).textTheme.bodySmall?.color ??
                        Colors.grey),
                enabledBorder: UnderlineInputBorder(
                    borderSide:
                        BorderSide(color: Theme.of(context).dividerColor)),
                focusedBorder: UnderlineInputBorder(
                    borderSide: BorderSide(
                        color: Theme.of(context).colorScheme.primary)),
              ),
              onChanged: (val) => setState(() {}),
            ),
          ],
        ),
      ),
    );
  }
}
