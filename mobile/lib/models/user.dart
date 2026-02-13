/// User model.
class User {
  final int id;
  final String username;
  final double reputationScore;
  final int reportCount;
  final String createdAt;

  User({
    required this.id,
    required this.username,
    this.reputationScore = 50.0,
    this.reportCount = 0,
    this.createdAt = '',
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      username: json['username'] as String,
      reputationScore: (json['reputation_score'] as num?)?.toDouble() ?? 50.0,
      reportCount: json['report_count'] as int? ?? 0,
      createdAt: json['created_at'] as String? ?? '',
    );
  }
}
