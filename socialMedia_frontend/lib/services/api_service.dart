import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../features/feed/domain/models/post_model.dart';
import '../features/feed/domain/models/comment_model.dart';
import '../features/feed/domain/models/outfit_item_model.dart';
import '../features/profile/domain/models/user_model.dart';
import '../core/config/app_config.dart';

class ApiService {
  ApiService._internal();
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  /// Base URL — AppConfig üzerinden platform-bağımsız olarak belirlenir.
  /// Override için: flutter run --dart-define=API_HOST=192.168.1.100
  static String get baseUrl => AppConfig.baseUrl;

  /// Veritabanında kayıtlı localhost/127.0.0.1/eski-IP URL'lerini
  /// güncel sunucu adresiyle değiştirir. iOS/Android/Windows uyumlu.
  static String fixImageUrl(String? url) {
    if (url == null || url.isEmpty) return '';
    // Bilinen tüm local adres varyantlarını AppConfig.baseUrl ile değiştir
    return url.replaceAllMapped(
      RegExp(
          r'https?://(localhost|127\.0\.0\.1|10\.0\.2\.2|10\.5\.5\.\d+|192\.168\.\d+\.\d+):8000'),
      (_) => AppConfig.baseUrl,
    );
  }

  final http.Client _client = http.Client();
  static const Duration _timeout =
      Duration(seconds: 120); // Ollama AI çağrıları ve büyük istekler için uzatıldı

  // ─── Headers ────────────────────────────────────────────────
  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Bypass-Tunnel-Reminder': 'true',
      };

  // ─── Generic Request Handler ────────────────────────────────
  Future<Map<String, dynamic>> _get(String endpoint,
      {Map<String, String>? queryParams}) async {
    final decoded = await _getDecoded(endpoint, queryParams: queryParams);
    if (decoded is Map<String, dynamic>) {
      return decoded;
    }
    throw ApiException('Beklenmeyen yanıt formatı.');
  }

  Future<dynamic> _getDecoded(String endpoint,
      {Map<String, String>? queryParams}) async {
    try {
      final uri =
          Uri.parse('$baseUrl$endpoint').replace(queryParameters: queryParams);
      final response =
          await _client.get(uri, headers: _headers).timeout(_timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        _throwError(response);
      }
    } on SocketException {
      throw ApiException(
          'Bağlantı hatası. İnternet bağlantınızı kontrol edin.');
    } on TimeoutException {
      throw ApiException('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Beklenmeyen bir hata oluştu: $e');
    }
  }

  Future<List<dynamic>> _getList(String endpoint,
      {Map<String, String>? queryParams}) async {
    final decoded = await _getDecoded(endpoint, queryParams: queryParams);
    if (decoded is List) {
      return decoded;
    }
    throw ApiException('Beklenmeyen yanıt formatı.');
  }

  Future<Map<String, dynamic>> _post(
      String endpoint, Map<String, dynamic> body) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final response = await _client
          .post(uri, headers: _headers, body: jsonEncode(body))
          .timeout(_timeout);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        _throwError(response);
      }
    } on SocketException {
      throw ApiException(
          'Bağlantı hatası. İnternet bağlantınızı kontrol edin.');
    } on TimeoutException {
      throw ApiException('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Beklenmeyen bir hata oluştu: $e');
    }
  }

  Future<Map<String, dynamic>> _put(String endpoint, Map<String, dynamic> body,
      {Map<String, String>? headers}) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final reqHeaders = Map<String, String>.from(_headers);
      if (headers != null) {
        reqHeaders.addAll(headers);
      }
      final response = await _client
          .put(uri, headers: reqHeaders, body: jsonEncode(body))
          .timeout(_timeout);

      if (response.statusCode == 200 ||
          response.statusCode == 201 ||
          response.statusCode == 204) {
        if (response.body.isNotEmpty) {
          return jsonDecode(response.body) as Map<String, dynamic>;
        }
        return {};
      } else {
        _throwError(response);
      }
    } on SocketException {
      throw ApiException(
          'Bağlantı hatası. İnternet bağlantınızı kontrol edin.');
    } on TimeoutException {
      throw ApiException('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Beklenmeyen bir hata oluştu: $e');
    }
  }

  Future<Map<String, dynamic>> _delete(
      String endpoint, Map<String, dynamic>? body,
      {Map<String, String>? headers}) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final reqHeaders = Map<String, String>.from(_headers);
      if (headers != null) {
        reqHeaders.addAll(headers);
      }
      final request = http.Request('DELETE', uri)..headers.addAll(reqHeaders);
      if (body != null) {
        request.body = jsonEncode(body);
      }
      final streamed = await _client.send(request).timeout(_timeout);
      final response = await http.Response.fromStream(streamed);

      if (response.statusCode == 200 ||
          response.statusCode == 201 ||
          response.statusCode == 204) {
        if (response.body.isNotEmpty) {
          return jsonDecode(response.body) as Map<String, dynamic>;
        }
        return {};
      } else {
        _throwError(response);
      }
    } on SocketException {
      throw ApiException(
          'Bağlantı hatası. İnternet bağlantınızı kontrol edin.');
    } on TimeoutException {
      throw ApiException('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Beklenmeyen bir hata oluştu: $e');
    }
  }

  Future<Map<String, dynamic>> _patch(
      String endpoint, Map<String, dynamic> body) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final response = await _client
          .patch(uri, headers: _headers, body: jsonEncode(body))
          .timeout(_timeout);

      if (response.statusCode == 200 ||
          response.statusCode == 201 ||
          response.statusCode == 204) {
        if (response.body.isNotEmpty) {
          return jsonDecode(response.body) as Map<String, dynamic>;
        }
        return {};
      } else {
        _throwError(response);
      }
    } on SocketException {
      throw ApiException(
          'Bağlantı hatası. İnternet bağlantınızı kontrol edin.');
    } on TimeoutException {
      throw ApiException('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Beklenmeyen bir hata oluştu: $e');
    }
  }

  // ─── Error Handler ──────────────────────────────────────────
  Never _throwError(http.Response response) {
    String message = 'İstek başarısız: ${response.statusCode}';
    try {
      final body = jsonDecode(response.body);
      if (body is Map && body.containsKey('detail')) {
        final detail = body['detail'];
        if (detail is String) {
          message = detail;
        } else if (detail is List && detail.isNotEmpty) {
          final first = detail.first;
          if (first is Map && first['msg'] != null) {
            message = first['msg'].toString();
          } else {
            message = detail.toString();
          }
        }
      }
    } catch (_) {}
    throw ApiException(message, statusCode: response.statusCode);
  }

  // ─── Auth ───────────────────────────────────────────────────
  Future<String> register(String email, String password) async {
    final body = {
      'email': email,
      'password': password,
    };
    final data = await _post('/auth/register', body);
    return data['user_id'] as String;
  }

  Future<String> login(String email, String password) async {
    final body = {
      'email': email,
      'password': password,
    };
    final data = await _post('/auth/login', body);
    return data['user_id'] as String;
  }

  Future<void> requestPasswordResetCode(String email) async {
    final body = {'email': email};
    await _post('/auth/request-password-reset', body);
  }

  Future<void> verifyResetCode(String email, String code) async {
    final body = {'email': email, 'code': code};
    await _post('/auth/verify-reset-code', body);
  }

  Future<void> resetPassword(String email, String newPassword) async {
    final body = {
      'email': email,
      'new_password': newPassword,
    };
    await _post('/auth/reset-password', body);
  }

  Future<String> loginWithGoogle({
    required String idToken,
    required String email,
    required String displayName,
    String? avatarUrl,
  }) async {
    final body = {
      'id_token': idToken,
      'email': email,
      'display_name': displayName,
      if (avatarUrl != null) 'avatar_url': avatarUrl,
    };
    final data = await _post('/auth/google', body);
    return data['user_id'] as String;
  }

  // ─── Feed ───────────────────────────────────────────────────
  Future<({List<PostModel> posts, String? nextCursor})> getFeed({
    required String userId,
    String? cursor,
    int limit = 20,
  }) async {
    final queryParams = <String, String>{
      'user_id': userId,
      'limit': limit.toString(),
    };
    if (cursor != null) queryParams['cursor'] = cursor;

    final data = await _get('/feed', queryParams: queryParams);
    final posts = (data['posts'] as List<dynamic>?)
            ?.map((p) => PostModel.fromJson(p as Map<String, dynamic>))
            .toList() ??
        [];
    final nextCursor = data['next_cursor'] as String?;
    return (posts: posts, nextCursor: nextCursor);
  }

  // ─── Create Post ───────────────────────────────────────────
  Future<String> createPost({
    required String userId,
    required String imageUrl,
    String? caption,
    required List<OutfitItem> outfitItems,
    required String visibility,
    required bool aiTrainingConsent,
  }) async {
    final body = {
      'user_id': userId,
      'image_url': imageUrl,
      'caption': caption ?? '',
      'outfit_items': outfitItems.map((item) => item.itemId).toList(),
      'visibility': visibility,
      'ai_training_consent': aiTrainingConsent,
    };
    final data = await _post('/posts', body);
    // Backend MessageResponse döndürüyor: {success, message, data: {post_id}}
    final postId = data['data']?['post_id'] as String? ?? '';
    return postId;
  }

  // ─── User Posts ─────────────────────────────────────────────
  Future<List<PostModel>> getUserPosts({
    required String userId,
    String? viewerId,
  }) async {
    final queryParams = <String, String>{};
    if (viewerId != null) queryParams['viewer_id'] = viewerId;

    final data =
        await _getList('/posts/users/$userId/posts', queryParams: queryParams);
    return data
        .map((p) => PostModel.fromJson(p as Map<String, dynamic>))
        .toList();
  }

  Future<List<PostModel>> getSavedPosts({required String userId}) async {
    final data = await _getList('/posts/users/$userId/saved_posts');
    return data
        .map((p) => PostModel.fromJson(p as Map<String, dynamic>))
        .toList();
  }

  Future<void> deletePost(
      {required String postId, required String userId}) async {
    await _delete('/posts/$postId?user_id=$userId', null);
  }

  Future<void> updatePost(
      {required String postId,
      required String userId,
      required String caption}) async {
    await _patch('/posts/$postId?user_id=$userId', {
      'caption': caption,
    });
  }

  // ─── User Profile ──────────────────────────────────────────
  Future<UserModel> getUser(String userId) async {
    final data = await _get('/users/$userId');
    return UserModel.fromJson(data);
  }

  Future<UserModel> getMyProfile(String userId) async {
    // /users/me endpoint'i yok — doğrudan /users/{id} kullan
    final data = await _get('/users/$userId');
    return UserModel.fromJson(data);
  }

  Future<void> updateProfile({
    required String userId,
    String? username,
    String? displayName,
    String? bio,
    String? avatarUrl,
    String? height,
    String? weight,
    String? chest,
    String? waist,
    String? hips,
    String? location,
    String? timezone,
  }) async {
    final body = {
      if (username != null) 'username': username,
      if (displayName != null) 'display_name': displayName,
      if (bio != null) 'bio': bio,
      if (avatarUrl != null) 'avatar_url': avatarUrl,
      if (height != null) 'height': height,
      if (weight != null) 'weight': weight,
      if (chest != null) 'chest': chest,
      if (waist != null) 'waist': waist,
      if (hips != null) 'hips': hips,
      if (location != null) 'location': location,
      if (timezone != null) 'timezone': timezone,
    };
    await _put('/users/me', body, headers: {'Authorization': 'Bearer $userId'});
  }

  Future<void> updatePrivacy(String userId, bool isPrivate) async {
    final body = {
      'profile_visibility': isPrivate ? 'private' : 'public',
    };
    await _put('/users/me/privacy', body,
        headers: {'Authorization': 'Bearer $userId'});
  }

  Future<void> deleteAccount(String userId) async {
    await _delete('/users/me', null,
        headers: {'Authorization': 'Bearer $userId'});
  }

  // ─── Profile Security (Email & Password) ──────────────────────
  Future<void> requestEmailChange(String newEmail) async {
    await _post('/auth/request-email-change', {'new_email': newEmail});
  }

  Future<void> verifyEmailChange(String userId, String newEmail, String code) async {
    final uri = Uri.parse('$baseUrl/auth/verify-email-change').replace(
      queryParameters: {'user_id': userId},
    );
    final response = await _client.post(uri, headers: _headers, body: jsonEncode({
      'new_email': newEmail,
      'code': code
    })).timeout(_timeout);
    if (response.statusCode != 200) {
      _throwError(response);
    }
  }

  Future<void> requestPasswordChange(String userId) async {
    final uri = Uri.parse('$baseUrl/auth/request-password-change').replace(
      queryParameters: {'user_id': userId},
    );
    final response = await _client.post(uri, headers: _headers, body: jsonEncode({})).timeout(_timeout);
    if (response.statusCode != 200) {
      _throwError(response);
    }
  }

  Future<void> verifyPasswordChange(String userId, String newPassword, String code) async {
    final uri = Uri.parse('$baseUrl/auth/verify-password-change').replace(
      queryParameters: {'user_id': userId},
    );
    final response = await _client.post(uri, headers: _headers, body: jsonEncode({
      'new_password': newPassword,
      'code': code
    })).timeout(_timeout);
    if (response.statusCode != 200) {
      _throwError(response);
    }
  }

  // ─── Follow ─────────────────────────────────────────────────
  Future<void> follow({
    required String followerId,
    required String followingId,
  }) async {
    await _post('/follow', {
      'follower_id': followerId,
      'following_id': followingId,
    });
  }

  Future<void> unfollow({
    required String followerId,
    required String followingId,
  }) async {
    await _delete('/follow', {
      'follower_id': followerId,
      'following_id': followingId,
    });
  }

  Future<void> likePost({
    required String postId,
    required String userId,
  }) async {
    await _post('/posts/$postId/like', {'user_id': userId});
  }

  Future<void> unlikePost({
    required String postId,
    required String userId,
  }) async {
    await _delete('/posts/$postId/like?user_id=$userId', {});
  }

  // ─── Save ───────────────────────────────────────────────────
  Future<void> savePost({
    required String postId,
    required String userId,
  }) async {
    // Backend: POST /posts/{post_id}/save?user_id=...
    final uri = Uri.parse('$baseUrl/posts/$postId/save').replace(
      queryParameters: {'user_id': userId},
    );
    final response =
        await _client.post(uri, headers: _headers).timeout(_timeout);
    if (response.statusCode != 200 && response.statusCode != 201) {
      _throwError(response);
    }
  }

  Future<void> unsavePost({
    required String postId,
    required String userId,
  }) async {
    // Backend: DELETE /posts/{post_id}/save?user_id=...
    final uri = Uri.parse('$baseUrl/posts/$postId/save').replace(
      queryParameters: {'user_id': userId},
    );
    final request = http.Request('DELETE', uri)..headers.addAll(_headers);
    final streamed = await _client.send(request).timeout(_timeout);
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode != 200) {
      _throwError(response);
    }
  }

  // ─── Comments ───────────────────────────────────────────────
  Future<String> addComment({
    required String postId,
    required String userId,
    required String content,
    String? parentId,
  }) async {
    final body = <String, dynamic>{
      'user_id': userId,
      'content': content,
    };
    if (parentId != null) {
      body['parent_id'] = parentId;
    }
    final data = await _post('/posts/$postId/comments', body);
    return data['data']?['comment_id'] as String? ?? '';
  }

  Future<void> deleteComment({
    required String commentId,
    required String userId,
  }) async {
    await _delete('/comments/$commentId?user_id=$userId', null);
  }

  Future<List<CommentModel>> getComments(String postId) async {
    final data = await _getList('/posts/$postId/comments');
    return data
        .map((e) => CommentModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  // ─── Caption Suggestion ────────────────────────────────────
  Future<String> suggestCaption({
    required List<OutfitItem> outfitItems,
    String? styleHint,
    String? imageUrl,
    Map<String, dynamic>? aiAnalysis, // FashionSigLIP sonucu (opsiyonel)
  }) async {
    final body = <String, dynamic>{
      'outfit_items': outfitItems.map((item) => item.toJson()).toList(),
    };
    if (styleHint != null && styleHint.isNotEmpty) body['style_hint'] = styleHint;
    if (imageUrl != null && imageUrl.isNotEmpty) body['image_url'] = imageUrl;
    if (aiAnalysis != null) body['ai_analysis'] = aiAnalysis;
    final data = await _post('/captions/suggest', body);
    // Backend MessageResponse: {success, message, data: {caption: "..."}}
    final nested = data['data'] as Map<String, dynamic>?;
    return nested?['caption'] as String? ?? '';
  }

  // ─── Outfit Story (LLaVA + Ollama Pipeline) ───────────────
  /// Görsel yükleyip iki aşamalı pipeline çalıştırır:
  /// 1. LLaVA → Kıyafetleri JSON olarak tespit eder
  /// 2. llama3.2 → Kombinin neden seçildiğini açıklar
  ///
  /// Dönen map: {
  ///   'detected_items': List<Map>,  // Tespit edilen kıyafetler
  ///   'outfit_story': String,       // Detaylı açıklama metni
  ///   'fashion_analysis': Map?      // FashionSigLIP verisi
  /// }
  Future<Map<String, dynamic>> generateOutfitStory({
    String? imageUrl,
    String? styleHint,
    Map<String, dynamic>? aiAnalysis,
  }) async {
    final body = <String, dynamic>{};
    if (imageUrl != null && imageUrl.isNotEmpty) body['image_url'] = imageUrl;
    if (styleHint != null && styleHint.isNotEmpty) body['style_hint'] = styleHint;
    if (aiAnalysis != null) body['ai_analysis'] = aiAnalysis;
    return await _post('/captions/outfit-story', body);
  }


  // --- Epic 3: Wardrobe & AI Stylist ---
  Future<List<dynamic>> getClothes(String userId) async {
    return await _getList('/wardrobe/items/$userId');
  }

  Future<dynamic> addCloth(String userId, Map<String, dynamic> itemData) async {
    return await _post('/wardrobe/items?user_id=$userId', itemData);
  }

  /// Görsel yükler ve FashionSigLIP ile otomatik analiz döner.
  /// Dönen map: { 'url': String, 'filename': String, 'ai_analysis': Map? }
  Future<Map<String, dynamic>> uploadImageForAnalysis(File file) async {
    final uri = Uri.parse('$baseUrl/captions/upload');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('file', file.path));
    final streamed = await request.send().timeout(_timeout);
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    throw ApiException('Görsel yüklenemedi', statusCode: response.statusCode);
  }

  /// Var olan bir görsel URL'si ile FashionSigLIP analizi çalıştırır.
  Future<Map<String, dynamic>> analyzeClothingItem(String imageUrl) async {
    return await _post('/wardrobe/items/analyze', {'image_url': imageUrl});
  }


  Future<dynamic> updateCloth(int itemId, Map<String, dynamic> itemData) async {
    return await _put('/wardrobe/items/$itemId', itemData);
  }

  /// Quickly toggle laundry (dirty) status without a full PUT.
  Future<void> setLaundryStatus(int itemId, {required bool isDirty}) async {
    await _patch('/wardrobe/items/$itemId/laundry', {'is_dirty': isDirty});
  }

  /// Quickly toggle favorite status without a full PUT.
  Future<void> setFavoriteStatus(int itemId, {required bool isFavorite}) async {
    await _patch('/wardrobe/items/$itemId/favorite', {'is_favorite': isFavorite});
  }

  Future<dynamic> deleteCloth(int itemId) async {
    return await _delete('/wardrobe/items/$itemId', null);
  }

  Future<dynamic> chat(String userId, String message, {String? weather, String? sessionId}) async {
    final body = {'user_id': userId, 'mesaj': message};
    if (weather != null) body['hava_durumu'] = weather;
    if (sessionId != null) body['session_id'] = sessionId;
    return await _post('/wardrobe/chat', body);
  }

  Future<List<Map<String, dynamic>>> getChatHistory(String userId, {String? sessionId}) async {
    try {
      final query = sessionId != null ? '?session_id=$sessionId' : '';
      final data = await _getList('/wardrobe/chat/history/$userId$query');
      return data
          .map((e) => {
                'role': (e as Map)['rol']?.toString() ?? 'user',
                'text': e['mesaj']?.toString() ?? '',
                'outfit_items': e['outfit_items'] ?? [],
              })
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<List<Map<String, dynamic>>> getChatSessions(String userId) async {
    try {
      final data = await _getList('/wardrobe/chat/sessions/$userId');
      return data.cast<Map<String, dynamic>>();
    } catch (_) {
      return [];
    }
  }

  Future<dynamic> getOutfit(
      String userId, String event, String weather, String style) async {
    return await _post('/wardrobe/outfit/suggest', {
      'user_id': userId,
      'etkinlik': event,
      'hava_durumu': weather,
      'stil_tercihi': style
    });
  }

  Future<List<dynamic>> getOutfits(String userId) async {
    return await _getList('/wardrobe/outfits/$userId');
  }

  Future<dynamic> createManualOutfit(String userId, List<int> itemIds, String aciklama) async {
    return await _post('/wardrobe/outfit/manual', {
      'user_id': userId,
      'item_ids': itemIds,
      'aciklama': aciklama,
    });
  }

  // ─── 2FA Yardımcı Metodları ────────────────────────────────
  /// 2FA setup/verify için POST isteği — Map döner
  Future<Map<String, dynamic>> post2FA(
      String endpoint, Map<String, dynamic> body) async {
    return await _post(endpoint, body);
  }

  /// 2FA disable için DELETE isteği
  Future<void> delete2FA(String endpoint) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      final request = http.Request('DELETE', uri)..headers.addAll(_headers);
      final streamed = await _client.send(request).timeout(_timeout);
      final response = await http.Response.fromStream(streamed);
      if (response.statusCode != 200) {
        _throwError(response);
      }
    } on SocketException {
      throw ApiException(
          'Bağlantı hatası. İnternet bağlantınızı kontrol edin.');
    } on TimeoutException {
      throw ApiException('İstek zaman aşımına uğradı.');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Beklenmeyen hata: $e');
    }
  }

  /// 2FA status için GET isteği — Map döner
  Future<Map<String, dynamic>> get2FAStatus(String endpoint) async {
    return await _get(endpoint);
  }

  // ─── 2FA Metotları ──────────────────────────────────────────
  Future<Map<String, dynamic>> setup2FA(String userId) async {
    return await _post('/auth/2fa/setup', {'user_id': userId});
  }

  Future<Map<String, dynamic>> verify2FASetup(
      String userId, String code) async {
    return await _post(
        '/auth/2fa/verify-setup', {'user_id': userId, 'code': code});
  }

  Future<Map<String, dynamic>> login2FA(String userId, String code) async {
    return await _post('/auth/2fa/verify', {'user_id': userId, 'code': code});
  }

  // ─── E-posta Doğrulama ─────────────────────────────────────
  Future<Map<String, dynamic>> verifyEmail(String userId, String code) async {
    return await _post('/auth/verify-email', {'user_id': userId, 'code': code});
  }

  // ─── Arama ─────────────────────────────────────────────────
  Future<List<dynamic>> searchUsers(String query, {String? viewerId}) async {
    final viewerParam = viewerId != null ? '&viewer_id=$viewerId' : '';
    return await _getList('/search?query=$query$viewerParam');
  }

  // ─── Beğeni Listesi ────────────────────────────────────────
  Future<List<dynamic>> getPostLikers(String postId) async {
    return await _getList('/posts/$postId/likers');
  }

  // --- Takip İşlemleri ----------------------------------------------------
  Future<List<dynamic>> getFollowers(String userId) async {
    return await _getList('/follows/$userId/followers');
  }

  Future<List<dynamic>> getFollowing(String userId) async {
    return await _getList('/follows/$userId/following');
  }

  // ─── Bildirimler ───────────────────────────────────────────
  Future<List<dynamic>> getNotifications(String userId) async {
    return await _getList('/notifications?user_id=$userId');
  }

  Future<Map<String, dynamic>> markAllNotificationsRead(String userId) async {
    return await _put('/notifications/read-all?user_id=$userId', {});
  }

  Future<Map<String, dynamic>> markNotificationRead(
      String notificationId) async {
    return await _put('/notifications/$notificationId/read', {});
  }

  // ─── Wardrobe Outfits ──────────────────────────────────────────
  Future<void> deleteOutfit(int outfitId) async {
    await _delete('/wardrobe/outfits/$outfitId', null);
  }

  // ─── Analytics ─────────────────────────────────────────────
  Future<Map<String, dynamic>> getAnalytics(String userId) async {
    return await _get('/analytics/$userId');
  }

  // ─── Title (Ünvan) ────────────────────────────────────────
  Future<void> setActiveTitle(String userId, String? title) async {
    final queryParams = title != null ? '?title=${Uri.encodeComponent(title)}' : '?title=';
    final url = Uri.parse('$baseUrl/users/$userId/title$queryParams');
    final response = await _client.put(url, headers: _headers).timeout(_timeout);
    if (response.statusCode != 200) {
      throw ApiException('Ünvan güncellenemedi', statusCode: response.statusCode);
    }
  }

  // ─── Dispose ───────────────────────────────────────────────
  void dispose() {
    _client.close();
  }
}

// ─── Custom Exception ──────────────────────────────────────────
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  const ApiException(this.message, {this.statusCode});

  @override
  String toString() => 'ApiException: $message (status: $statusCode)';
}
