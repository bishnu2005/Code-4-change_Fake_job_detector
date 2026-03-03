/// User model.
class User {
  final int id;
  final String username;
  final double reputationScore;
  final int reportCount;
  final DateTime createdAt;
  final String? googleId;
  final String? email;
  final String? avatarUrl;

  User({
    required this.id,
    required this.username,
    this.reputationScore = 50.0,
    this.reportCount = 0,
    required this.createdAt,
    this.googleId,
    this.email,
    this.avatarUrl,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int? ?? 0,
      username: json['username'] as String? ?? 'User',
      reputationScore: (json['reputation_score'] as num?)?.toDouble() ?? 50.0,
      reportCount: json['report_count'] as int? ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      googleId: json['google_id'] as String?,
      email: json['email'] as String?,
      avatarUrl: json['avatar_url'] as String?,
    );
  }
}
