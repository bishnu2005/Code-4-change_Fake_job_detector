import 'dart:ui';
import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'screens/analyze_screen.dart';
import 'screens/profile_screen.dart';
import 'models/user.dart';
import 'services/api_service.dart';

void main() {
  runApp(const HireLiarApp());
}

class HireLiarApp extends StatelessWidget {
  const HireLiarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HireLiar',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF8B5CF6),
        scaffoldBackgroundColor: const Color(0xFF0F0F14),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF8B5CF6),
          secondary: Color(0xFF6D28D9),
          surface: Color(0xFF151523),
          error: Color(0xFFEF4444),
        ),
        fontFamily: 'Roboto',
        useMaterial3: true,
        cardTheme: CardThemeData(
          color: Colors.white.withValues(alpha: 0.06),
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
            side: BorderSide(color: Colors.white.withValues(alpha: 0.12)),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white.withValues(alpha: 0.06),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.12)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.12)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: Color(0xFF8B5CF6)),
          ),
        ),
      ),
      home: const AppShell(),
    );
  }
}

/// Main shell with bottom navigation.
class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _currentIndex = 0;
  User? _currentUser;

  @override
  void initState() {
    super.initState();
    _autoLogin();
  }

  Future<void> _autoLogin() async {
    try {
      final user = await ApiService.loginOrCreate('default_user');
      setState(() => _currentUser = user);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      HomeScreen(user: _currentUser),
      AnalyzeScreen(user: _currentUser),
      ProfileScreen(
        user: _currentUser,
        onLogin: (user) => setState(() => _currentUser = user),
      ),
    ];

    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: screens),
      bottomNavigationBar: ClipRRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.06),
              border: Border(
                top: BorderSide(color: Colors.white.withValues(alpha: 0.12)),
              ),
            ),
            child: NavigationBar(
              backgroundColor: Colors.transparent,
              surfaceTintColor: Colors.transparent,
              selectedIndex: _currentIndex,
              onDestinationSelected: (i) => setState(() => _currentIndex = i),
              indicatorColor: const Color(0xFF8B5CF6).withValues(alpha: 0.15),
              destinations: const [
                NavigationDestination(
                  icon: Icon(Icons.home_outlined, color: Colors.white38),
                  selectedIcon: Icon(Icons.home, color: Color(0xFF8B5CF6)),
                  label: 'Home',
                ),
                NavigationDestination(
                  icon: Icon(Icons.search_outlined, color: Colors.white38),
                  selectedIcon: Icon(Icons.search, color: Color(0xFF8B5CF6)),
                  label: 'Analyze',
                ),
                NavigationDestination(
                  icon: Icon(Icons.person_outline, color: Colors.white38),
                  selectedIcon: Icon(Icons.person, color: Color(0xFF8B5CF6)),
                  label: 'Profile',
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
