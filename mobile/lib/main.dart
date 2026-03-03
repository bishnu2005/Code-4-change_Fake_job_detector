import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const FakeJobDetectorApp());
}

class FakeJobDetectorApp extends StatelessWidget {
  const FakeJobDetectorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fake Job Detector',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: Colors.tealAccent,
        scaffoldBackgroundColor: const Color(0xFF0F0C29),
        colorScheme: ColorScheme.dark(
          primary: Colors.tealAccent,
          secondary: Colors.tealAccent.shade400,
          surface: const Color(0xFF1E1E2E),
        ),
        fontFamily: 'Roboto',
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
