import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/job_posting.dart';
import '../models/prediction_result.dart';

/// Service for communicating with the FastAPI backend.
class ApiService {
  /// Configurable base URL. Change this for production deployment.
  static String baseUrl = 'http://10.0.2.2:8000'; // Android emulator default

  /// Unified analysis: sends text fields + optional image in one request.
  static Future<PredictionResult> analyze(
    JobPosting posting, {
    File? imageFile,
  }) async {
    final uri = Uri.parse('$baseUrl/analyze');

    try {
      final request = http.MultipartRequest('POST', uri);

      // Add text fields
      request.fields['description'] = posting.description;
      request.fields['company'] = posting.company;
      request.fields['salary'] = posting.salary;
      request.fields['apply_link'] = posting.applyLink;

      // Add optional image
      if (imageFile != null) {
        request.files.add(
          await http.MultipartFile.fromPath('file', imageFile.path),
        );
      }

      final streamedResponse =
          await request.send().timeout(const Duration(seconds: 30));
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return PredictionResult.fromJson(data);
      } else {
        final detail = _extractDetail(response.body);
        throw ApiException('Server error (${response.statusCode}): $detail');
      }
    } on SocketException {
      throw ApiException(
          'Unable to connect to server. Check your network and API URL.');
    } on http.ClientException catch (e) {
      throw ApiException('Network error: ${e.message}');
    }
  }

  static String _extractDetail(String body) {
    try {
      final json = jsonDecode(body);
      return json['detail']?.toString() ?? body;
    } catch (_) {
      return body;
    }
  }
}

/// Custom exception for API errors.
class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}
