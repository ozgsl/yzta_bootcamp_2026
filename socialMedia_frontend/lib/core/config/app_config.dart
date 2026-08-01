/// Uygulama yapılandırması — Platform bağımsız, ortam değişkeni destekli.
library app_config;

import 'dart:io';
import 'package:flutter/foundation.dart';

class AppConfig {
  AppConfig._();

  /// --dart-define=API_HOST=... ile override edilebilir.
  static const String _definedHost = String.fromEnvironment(
    'API_HOST',
    defaultValue: '',
  );

  static const int _definedPort = int.fromEnvironment(
    'API_PORT',
    defaultValue: 8000,
  );

  /// Backend'in çalıştığı host
  static String get apiHost {
    if (_definedHost.isNotEmpty) return _definedHost;

    if (kIsWeb) return 'localhost';
    try {
      if (Platform.isWindows || Platform.isMacOS || Platform.isLinux) {
        return '127.0.0.1';
      }
    } catch (_) {}

    // Fiziksel cihaz için USB Tünelleme (adb reverse) ile doğrudan PC'ye erişim
    return '127.0.0.1';
  }

  static int get apiPort => _definedPort;

  /// Tam backend URL'si (Canlı Google Cloud Run Sunucusu)
  static String get baseUrl {
    if (_definedHost.isNotEmpty) {
      if (_definedHost.startsWith('http://') ||
          _definedHost.startsWith('https://')) {
        return _definedHost;
      }
      return 'http://$_definedHost:$apiPort';
    }
    // Google Cloud Run Canlı Sunucu Adresi (Kablosuz, USB'siz Her Yerden Bağlan!)
    return 'https://dijital-gardrop-api-127622765965.europe-west1.run.app';
  }
}
