import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/api_service.dart';
import '../models/user.dart';

class AuthService extends ChangeNotifier {
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile', 'openid'],
  );
  final _storage = const FlutterSecureStorage();

  bool _isAuthenticated = false;
  String? _accessToken;
  String? _avatarUrl;
  String? _username;

  bool get isAuthenticated => _isAuthenticated;
  String? get accessToken => _accessToken;
  String? get avatarUrl => _avatarUrl;
  String? get username => _username;

  User? get userModel {
    if (!_isAuthenticated) return null;
    return User(
      id: 0,
      username: _username ?? 'User',
      reputationScore: 0.0,
      reportCount: 0,
      createdAt: DateTime.now(),
      googleId: 'current',
      email: 'user@example.com',
      avatarUrl: _avatarUrl,
    );
  }

  Future<void> init() async {
    _accessToken = await _storage.read(key: 'jwt_token');
    _avatarUrl = await _storage.read(key: 'user_avatar');
    _username = await _storage.read(key: 'user_name');

    if (_accessToken != null) {
      _isAuthenticated = true;
      notifyListeners();
    }
  }

  Future<bool> signInWithGoogle() async {
    try {
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) return false; // Canceled

      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;
      final String? idToken = googleAuth.idToken;

      if (idToken == null) return false;

      // Exchange ID Token for JWT with Backend
      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/auth/google'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'id_token': idToken}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _accessToken = data['access_token'];
        _username = data['username'];
        _avatarUrl = data['avatar_url'];

        await _storage.write(key: 'jwt_token', value: _accessToken);
        await _storage.write(key: 'user_name', value: _username);
        if (_avatarUrl != null) {
          await _storage.write(key: 'user_avatar', value: _avatarUrl);
        }

        _isAuthenticated = true;
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Google Sign-In Error: $e');
      return false;
    }
  }

  Future<void> signOut() async {
    await _googleSignIn.signOut();
    await _storage.deleteAll();
    _isAuthenticated = false;
    _accessToken = null;
    _username = null;
    _avatarUrl = null;
    notifyListeners();
  }
}
