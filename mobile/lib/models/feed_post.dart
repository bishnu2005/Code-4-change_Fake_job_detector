/// Community feed post model.
class FeedPost {
  final int id;
  final String companyName;
  final String? domain;
  final String title;
  final String description;
  final String verdict;
  final int upvotes;
  final int downvotes;
  final String createdAt;
  final FeedAuthor author;

  FeedPost({
    required this.id,
    required this.companyName,
    this.domain,
    required this.title,
    required this.description,
    required this.verdict,
    this.upvotes = 0,
    this.downvotes = 0,
    this.createdAt = '',
    required this.author,
  });

  factory FeedPost.fromJson(Map<String, dynamic> json) {
    return FeedPost(
      id: json['id'] as int,
      companyName: json['company_name'] as String,
      domain: json['domain'] as String?,
      title: json['title'] as String,
      description: json['description'] as String,
      verdict: json['verdict'] as String,
      upvotes: json['upvotes'] as int? ?? 0,
      downvotes: json['downvotes'] as int? ?? 0,
      createdAt: json['created_at'] as String? ?? '',
      author: FeedAuthor.fromJson(json['author'] as Map<String, dynamic>),
    );
  }

  String get timeAgo {
    try {
      final created = DateTime.parse(createdAt);
      final diff = DateTime.now().difference(created);
      if (diff.inDays > 0) return '${diff.inDays}d ago';
      if (diff.inHours > 0) return '${diff.inHours}h ago';
      if (diff.inMinutes > 0) return '${diff.inMinutes}m ago';
      return 'just now';
    } catch (_) {
      return '';
    }
  }
}

class FeedAuthor {
  final int id;
  final String username;
  final double reputationScore;

  FeedAuthor({
    required this.id,
    required this.username,
    this.reputationScore = 50.0,
  });

  factory FeedAuthor.fromJson(Map<String, dynamic> json) {
    return FeedAuthor(
      id: json['id'] as int,
      username: json['username'] as String,
      reputationScore: (json['reputation_score'] as num?)?.toDouble() ?? 50.0,
    );
  }
}
