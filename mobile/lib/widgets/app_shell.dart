import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../screens/home_screen.dart';
import '../screens/analyze_screen.dart';
import '../screens/profile_screen.dart';

/// Main Shell with Glass Bottom Navigation.
class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    // The 'user' variable was previously defined here but is not used by ProfileScreen
    // and is not needed for other screens in this context.
    // final user = context.watch<AuthService>().username; // Use provider properly

    final List<Widget> screens = [
      HomeScreen(
          user: context
              .read<AuthService>()
              .userModel), // Pass full user if possible
      AnalyzeScreen(user: context.read<AuthService>().userModel),
      const ProfileScreen(), // ProfileScreen no longer takes 'user' or 'onLogin' parameters
    ];

    return Scaffold(
      extendBody: true, // Important for glass nav
      body: Stack(
        children: [
          // Global Background Gradient
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Color(0xFF0F0F14),
                  Color(0xFF13131F),
                ],
              ),
            ),
          ),
          screens[_currentIndex],
        ],
      ),
      bottomNavigationBar: _GlassBottomNav(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
      ),
    );
  }
}

class _GlassBottomNav extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;

  const _GlassBottomNav({required this.currentIndex, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 80,
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F14).withValues(alpha: 0.8),
        border: Border(
            top: BorderSide(color: Colors.white.withValues(alpha: 0.08))),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _NavItem(
            icon: Icons.home_rounded,
            label: 'Home',
            isSelected: currentIndex == 0,
            onTap: () => onTap(0),
          ),
          _NavItem(
            icon: Icons.search_rounded,
            label: 'Analyze',
            isSelected: currentIndex == 1,
            onTap: () => onTap(1),
          ),
          _NavItem(
            icon: Icons.person_rounded,
            label: 'Profile',
            isSelected: currentIndex == 2,
            onTap: () => onTap(2),
          ),
        ],
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _NavItem({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = isSelected
        ? const Color(0xFF8B5CF6)
        : Colors.white.withValues(alpha: 0.4);

    return InkWell(
      onTap: onTap,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: isSelected
                  ? const Color(0xFF8B5CF6).withValues(alpha: 0.15)
                  : Colors.transparent,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }
}
