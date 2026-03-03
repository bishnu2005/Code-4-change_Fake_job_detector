import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/auth_service.dart';
import 'widgets/app_shell.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Create AuthService and initialize
  final authService = AuthService();
  await authService.init();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: authService),
      ],
      child: const HireLiarApp(),
    ),
  );
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
        scaffoldBackgroundColor: const Color(0xFF0F0F14), // Deep Space Black
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF8B5CF6), // Violet
          secondary: Color(0xFF6D28D9),
          surface: Color(0xFF151523), // Slightly lighter for contrast
          error: Color(0xFFEF4444),
        ),
        fontFamily: 'Roboto',
        useMaterial3: true,

        // Glass Card Theme
        cardTheme: CardThemeData(
          color: Colors.white.withValues(alpha: 0.06),
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
            side: BorderSide(color: Colors.white.withValues(alpha: 0.12)),
          ),
        ),

        // Glass Input Fields
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
            borderSide: const BorderSide(color: Color(0xFF8B5CF6), width: 1.5),
          ),
          hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.4)),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        ),

        // Text Theme
        textTheme: const TextTheme(
          headlineMedium: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w700,
            letterSpacing: -0.5,
          ),
          bodyMedium: TextStyle(
            color: Color(0xFFE2E8F0),
            fontSize: 15,
            height: 1.5,
          ),
        ),
      ),
      home: const AppShell(),
    );
  }
}
