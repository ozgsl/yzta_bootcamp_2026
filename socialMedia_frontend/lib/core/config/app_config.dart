/// Uygulama yapılandırması — Platform bağımsız, ortam değişkeni destekli.
///
/// Kullanım:
///   flutter run --dart-define=API_HOST=192.168.1.100
///   flutter run --dart-define=API_HOST=10.5.5.11
///   flutter run --dart-define=API_HOST=localhost   (emülatör için)
///
/// Varsayılan: Android emülatör için 10.0.2.2, iOS/fiziksel cihaz için localhost
library app_config;

import 'dart:io';

class AppConfig {
  AppConfig._();

  /// --dart-define=API_HOST=... ile override edilebilir.
  /// Belirtilmezse platforma göre otomatik seçilir.
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

    // Use local machine IP for physical device testing
    return '192.168.1.101';
  }

  static int get apiPort => _definedPort;

  /// Tam backend URL'si
  static String get baseUrl {
    if (_definedHost.startsWith('http://') ||
        _definedHost.startsWith('https://')) {
      return _definedHost;
    }
    return 'http://$apiHost:$apiPort';
  }
}
