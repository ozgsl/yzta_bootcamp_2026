import '../../../../services/api_service.dart';

class UserModel {
  final String userId;
  final String email;
  final String username;
  final String displayName;
  final String avatarUrl;
  final String bio;
  final int followersCount;
  final int followingCount;
  final bool isFollowing;
  final String height;
  final String weight;
  final String chest;
  final String waist;
  final String hips;
  final String location;
  final String timezone;
  final String? activeTitle;

  const UserModel({
    required this.userId,
    required this.email,
    required this.username,
    required this.displayName,
    required this.avatarUrl,
    required this.bio,
    required this.followersCount,
    required this.followingCount,
    required this.isFollowing,
    this.height = '',
    this.weight = '',
    this.chest = '',
    this.waist = '',
    this.hips = '',
    this.location = '',
    this.timezone = '',
    this.activeTitle,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      userId: json['user_id'] as String? ?? '',
      email: json['email'] as String? ?? '',
      username: json['username'] as String? ?? '',
      displayName: json['display_name'] as String? ?? '',
      avatarUrl: ApiService.fixImageUrl(json['avatar_url'] as String?),
      bio: json['bio'] as String? ?? '',
      followersCount: json['followers_count'] as int? ?? 0,
      followingCount: json['following_count'] as int? ?? 0,
      isFollowing: json['is_following'] as bool? ?? false,
      height: json['height'] as String? ?? '',
      weight: json['weight'] as String? ?? '',
      chest: json['chest'] as String? ?? '',
      waist: json['waist'] as String? ?? '',
      hips: json['hips'] as String? ?? '',
      location: json['location'] as String? ?? '',
      timezone: json['timezone'] as String? ?? '',
      activeTitle: json['active_title'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'email': email,
      'username': username,
      'display_name': displayName,
      'avatar_url': avatarUrl,
      'bio': bio,
      'followers_count': followersCount,
      'following_count': followingCount,
      'is_following': isFollowing,
      'height': height,
      'weight': weight,
      'chest': chest,
      'waist': waist,
      'hips': hips,
      'location': location,
      'timezone': timezone,
      'active_title': activeTitle,
    };
  }

  UserModel copyWith({
    String? userId,
    String? email,
    String? username,
    String? displayName,
    String? avatarUrl,
    String? bio,
    int? followersCount,
    int? followingCount,
    bool? isFollowing,
    String? height,
    String? weight,
    String? chest,
    String? waist,
    String? hips,
    String? location,
    String? timezone,
    String? activeTitle,
  }) {
    return UserModel(
      userId: userId ?? this.userId,
      email: email ?? this.email,
      username: username ?? this.username,
      displayName: displayName ?? this.displayName,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      bio: bio ?? this.bio,
      followersCount: followersCount ?? this.followersCount,
      followingCount: followingCount ?? this.followingCount,
      isFollowing: isFollowing ?? this.isFollowing,
      height: height ?? this.height,
      weight: weight ?? this.weight,
      chest: chest ?? this.chest,
      waist: waist ?? this.waist,
      hips: hips ?? this.hips,
      location: location ?? this.location,
      timezone: timezone ?? this.timezone,
      activeTitle: activeTitle ?? this.activeTitle,
    );
  }

  @override
  String toString() =>
      'UserModel(userId: $userId, email: $email, username: $username, displayName: $displayName)';
}
