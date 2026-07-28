import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';

class WeatherInfo {
  final double temp;
  final int code;
  final String description;
  final String cityName;

  WeatherInfo({
    required this.temp,
    required this.code,
    required this.description,
    required this.cityName,
  });

  String get recommendation {
    if (code >= 95 && code <= 99) {
      return '⚠️ Fırtına var! Evde kalmanı veya korunaklı kalın kıyafetler giymen önerilir.';
    }
    if (code >= 71 && code <= 77) {
      return '❄️ Hava karlı! Kalın kaban, bere, eldiven ve kar botu tercih etmelisin.';
    }
    if ((code >= 61 && code <= 67) || (code >= 80 && code <= 82)) {
      return '🌧️ Şemsiyeni ve su geçirmez montunu almayı unutma, hava yağmurlu!';
    }
    if (code >= 51 && code <= 57) {
      return '🌦️ Çiseleyen yağmur var, hafif bir yağmurluk veya ceket giyebilirsin.';
    }
    if (temp < 10) {
      return '🧥 Hava soğuk! Kalın kabanını ve kazağını giymeyi unutma.';
    }
    if (temp < 18) {
      return '🧥 Hava serin. Üzerine tarz bir ceket, trençkot veya hırka alabilirsin.';
    }
    if (temp < 25) {
      return '👕 Hava ılık ve harika! Rahat bir tişört veya gömlek tercih edebilirsin.';
    }
    return '☀️ Hava sıcak ve güneşli! İnce kıyafetler giy, şapkanı ve güneş gözlüğünü unutma 🕶️';
  }
}

class WeatherService {
  static final WeatherService _instance = WeatherService._internal();
  factory WeatherService() => _instance;
  WeatherService._internal();

  /// GPS Konumunu güvenli zaman aşımı ile alır
  Future<Position?> _getCurrentLocation() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled().timeout(const Duration(seconds: 2));
      if (!serviceEnabled) return null;

      LocationPermission permission = await Geolocator.checkPermission().timeout(const Duration(seconds: 2));
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission().timeout(const Duration(seconds: 3));
        if (permission == LocationPermission.denied) return null;
      }

      if (permission == LocationPermission.deniedForever) return null;

      return await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.low,
      ).timeout(const Duration(seconds: 3));
    } catch (e) {
      print('[WeatherService] GPS konum hatası/timeout: $e');
      return null;
    }
  }

  /// Şehir adından koordinat bulma (Open-Meteo Geocoding API)
  Future<Map<String, dynamic>?> _getCoordsFromCityName(String cityName) async {
    try {
      final cleanCity = cityName.trim();
      if (cleanCity.isEmpty) return null;

      final url = Uri.parse(
        'https://geocoding-api.open-meteo.com/v1/search?name=${Uri.encodeComponent(cleanCity)}&count=1&language=tr',
      );
      final response = await http.get(url).timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['results'] != null && (data['results'] as List).isNotEmpty) {
          final first = data['results'][0];
          return {
            'lat': (first['latitude'] as num).toDouble(),
            'lon': (first['longitude'] as num).toDouble(),
            'name': first['name'] as String? ?? cleanCity,
          };
        }
      }
    } catch (e) {
      print('[WeatherService] Geocoding hatası ($cityName): $e');
    }
    return null;
  }

  /// AI Stylist bağlamı için hava durumu metni
  Future<String?> getCurrentWeatherContext({String? manualLocation}) async {
    final info = await getDashboardWeather(manualLocation: manualLocation);
    if (info != null) {
      return '${info.cityName}: ${info.temp.round()}°C, ${info.description}';
    }
    return null;
  }

  /// Dashboard Hava Durumunu Getirir
  Future<WeatherInfo?> getDashboardWeather({String? manualLocation}) async {
    try {
      double latitude = 41.0082;
      double longitude = 28.9784;
      String cityName = 'İstanbul';

      // 1. Önce GPS konumunu dene
      final position = await _getCurrentLocation();
      if (position != null) {
        latitude = position.latitude;
        longitude = position.longitude;
        cityName = 'Konumun (GPS)';
      } else if (manualLocation != null && manualLocation.trim().isNotEmpty) {
        // 2. GPS yoksa kullanıcının profildeki manuel konumunu kullan
        final geo = await _getCoordsFromCityName(manualLocation);
        if (geo != null) {
          latitude = geo['lat'];
          longitude = geo['lon'];
          cityName = geo['name'];
        } else {
          cityName = manualLocation.trim();
        }
      }

      final url = Uri.parse(
        'https://api.open-meteo.com/v1/forecast?latitude=$latitude&longitude=$longitude&current_weather=true',
      );

      final response = await http.get(url).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final current = data['current_weather'];
        final temp = (current['temperature'] as num).toDouble();
        final code = current['weathercode'] as int;
        final description = _getWeatherDescription(code);

        return WeatherInfo(
          temp: temp,
          code: code,
          description: description,
          cityName: cityName,
        );
      }
    } catch (e) {
      print('[WeatherService] Weather fetch failed: $e');
    }

    // Varsayılan Güvenli Fallback (Kartın yok olmaması için)
    return WeatherInfo(
      temp: 22.0,
      code: 0,
      description: 'Güneşli / Açık',
      cityName: (manualLocation?.isNotEmpty == true) ? manualLocation! : 'İstanbul',
    );
  }

  String _getWeatherDescription(int code) {
    if (code == 0) return 'Güneşli / Açık';
    if (code >= 1 && code <= 3) return 'Parçalı Bulutlu';
    if (code == 45 || code == 48) return 'Sisli';
    if (code >= 51 && code <= 57) return 'Çiseleyen Yağmur';
    if (code >= 61 && code <= 67) return 'Yağmurlu';
    if (code >= 71 && code <= 77) return 'Karlı';
    if (code >= 80 && code <= 82) return 'Sağanak Yağışlı';
    if (code >= 95 && code <= 99) return 'Fırtınalı';
    return 'Açık';
  }
}
