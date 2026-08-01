import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../services/api_service.dart';
import '../../../../services/google_auth_service.dart';

final authProvider = ChangeNotifierProvider((ref) => AuthProvider());

const _kUserIdKey = 'saved_user_id';

class AuthProvider extends ChangeNotifier {
  String? _currentUserId;
  bool _isLoading = false;
  bool _isInitializing = true;

  String? get currentUserId => _currentUserId;
  bool get isLoading => _isLoading;
  bool get isInitializing => _isInitializing;
  bool get isLoggedIn => _currentUserId != null && _currentUserId!.isNotEmpty;

  AuthProvider() {
    _loadSavedSession();
  }

  /// Uygulama açıldığında kayıtlı oturumu yükle
  Future<void> _loadSavedSession() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedId = prefs.getString(_kUserIdKey);
      if (savedId != null && savedId.isNotEmpty) {
        if (savedId.startsWith('user-')) {
          await _clearSession();
        } else {
          _currentUserId = savedId;
        }
      }
    } catch (e) {
      debugPrint('Session yükleme hatası: $e');
    } finally {
      _isInitializing = false;
      notifyListeners();
    }
  }

  Future<void> _saveSession(String userId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_kUserIdKey, userId);
    } catch (e) {
      debugPrint('Session kaydetme hatası: $e');
    }
  }

  Future<void> _clearSession() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_kUserIdKey);
    } catch (e) {
      debugPrint('Session silme hatası: $e');
    }
  }

  Future<void> login(String email, String password) async {
    _setLoading(true);
    try {
      final userId = await ApiService().login(email, password);
      _currentUserId = userId;
      await _saveSession(userId);
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> register(String email, String password) async {
    _setLoading(true);
    try {
      final userId = await ApiService().register(email, password);
      _currentUserId = userId;
      await _saveSession(userId);
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  /// Google ile giriş yap / kayıt ol
  /// null döner: kullanıcı dialogu kapattı
  /// exception: gerçek hata
  Future<bool> loginWithGoogle() async {
    _setLoading(true);
    try {
      final userId = await GoogleAuthService().signIn();
      if (userId == null) {
        // Kullanıcı iptal etti
        return false;
      }
      _currentUserId = userId;
      await _saveSession(userId);
      notifyListeners();
      return true;
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  /// 2FA doğrulaması sonrası oturumu kaydet
  Future<void> finalizeLogin(String userId) async {
    _currentUserId = userId;
    await _saveSession(userId);
    notifyListeners();
  }

  Future<void> logout() async {
    _currentUserId = null;
    await _clearSession();
    // Google oturumunu da kapat
    try {
      await GoogleAuthService().signOut();
    } catch (_) {}
    notifyListeners();
  }
}
