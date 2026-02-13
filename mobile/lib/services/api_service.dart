import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import '../models/analysis_result.dart';
import '../models/feed_post.dart';
import '../models/user.dart';

/// Central API service for all backend calls.
class ApiService {
  // Change this to your machine's IP for real device testing
  static const String _baseUrl = 'http://10.0.2.2:8000';

  // ── Users ────────────────────────────────────────────────────

  static Future<User> loginOrCreate(String username) async {
    final resp = await http.post(
      Uri.parse('$_baseUrl/users/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username}),
    );
    if (resp.statusCode != 200) {
      throw Exception('Login failed: ${resp.body}');
    }
    return User.fromJson(jsonDecode(resp.body));
  }

  static Future<User> getUser(int userId) async {
    final resp = await http.get(Uri.parse('$_baseUrl/users/$userId'));
    if (resp.statusCode != 200) {
      throw Exception('Failed to get user');
    }
    return User.fromJson(jsonDecode(resp.body));
  }

  // ── Feed ─────────────────────────────────────────────────────

  static Future<Map<String, dynamic>> getFeed({
    int? cursor,
    int limit = 20,
    String filter = 'all',
    String search = '',
  }) async {
    final params = <String, String>{
      'limit': limit.toString(),
      'filter': filter,
    };
    if (cursor != null) params['cursor'] = cursor.toString();
    if (search.isNotEmpty) params['search'] = search;

    final uri = Uri.parse('$_baseUrl/feed').replace(queryParameters: params);
    final resp = await http.get(uri);
    if (resp.statusCode != 200) throw Exception('Feed fetch failed');

    final data = jsonDecode(resp.body);
    return {
      'posts': (data['posts'] as List)
          .map((p) => FeedPost.fromJson(p as Map<String, dynamic>))
          .toList(),
      'next_cursor': data['next_cursor'],
      'total_count': data['total_count'],
    };
  }

  static Future<FeedPost> createReport({
    required int userId,
    required String companyName,
    String? domain,
    required String title,
    required String description,
    required String verdict,
  }) async {
    final resp = await http.post(
      Uri.parse('$_baseUrl/feed'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'company_name': companyName,
        'domain': domain,
        'title': title,
        'description': description,
        'verdict': verdict,
      }),
    );
    if (resp.statusCode != 201) throw Exception('Failed to create report');
    return FeedPost.fromJson(jsonDecode(resp.body));
  }

  static Future<Map<String, dynamic>> vote({
    required int reportId,
    required int userId,
    required String voteType,
  }) async {
    final resp = await http.post(
      Uri.parse('$_baseUrl/feed/$reportId/vote'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId, 'vote_type': voteType}),
    );
    if (resp.statusCode == 409) throw Exception('Already voted');
    if (resp.statusCode != 200) throw Exception('Vote failed');
    return jsonDecode(resp.body);
  }

  // ── Analysis ─────────────────────────────────────────────────

  static Future<AnalysisResult> analyze({
    String companyName = '',
    String jobDescription = '',
    String url = '',
    XFile? image,
  }) async {
    final request =
        http.MultipartRequest('POST', Uri.parse('$_baseUrl/analyze'));

    if (companyName.isNotEmpty) request.fields['company_name'] = companyName;
    if (jobDescription.isNotEmpty) {
      request.fields['job_description'] = jobDescription;
    }
    if (url.isNotEmpty) request.fields['url'] = url;

    if (image != null) {
      final bytes = await image.readAsBytes();
      request.files.add(http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: image.name,
      ));
    }

    final streamed = await request.send();
    final resp = await http.Response.fromStream(streamed);

    if (resp.statusCode != 200) {
      throw Exception('Analysis failed: ${resp.body}');
    }
    return AnalysisResult.fromJson(jsonDecode(resp.body));
  }
}
