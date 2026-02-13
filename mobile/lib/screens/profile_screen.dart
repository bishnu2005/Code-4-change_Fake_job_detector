import 'dart:ui';
import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/api_service.dart';

/// Profile screen with login and user stats.
class ProfileScreen extends StatefulWidget {
  final User? user;
  final ValueChanged<User> onLogin;

  const ProfileScreen({super.key, this.user, required this.onLogin});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _usernameCtrl = TextEditingController();
  bool _loading = false;

  Future<void> _login() async {
    if (_usernameCtrl.text.trim().isEmpty) return;
    setState(() => _loading = true);
    try {
      final user = await ApiService.loginOrCreate(_usernameCtrl.text.trim());
      widget.onLogin(user);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: widget.user == null ? _buildLogin() : _buildProfile(),
      ),
    );
  }

  Widget _buildLogin() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const SizedBox(height: 60),
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: const Color(0xFF8B5CF6).withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(24),
            border:
                Border.all(color: const Color(0xFF8B5CF6).withValues(alpha: 0.25)),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: Image.asset(
              'assets/images/logo.png',
              fit: BoxFit.contain,
            ),
          ),
        ),
        const SizedBox(height: 20),
        const Text('Welcome to HireLiar',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w700,
              letterSpacing: -0.5,
            )),
        const SizedBox(height: 8),
        Text('Enter a username to get started',
            style: TextStyle(color: Colors.white.withValues(alpha: 0.4))),
        const SizedBox(height: 32),

        // Glass username field
        ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.06),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
              ),
              child: TextField(
                controller: _usernameCtrl,
                decoration: InputDecoration(
                  labelText: 'Username',
                  labelStyle: TextStyle(color: Colors.white.withValues(alpha: 0.35)),
                  prefixIcon: Icon(Icons.person_outline,
                      color: Colors.white.withValues(alpha: 0.25)),
                  filled: false,
                  border: InputBorder.none,
                  enabledBorder: InputBorder.none,
                  focusedBorder: InputBorder.none,
                ),
                onSubmitted: (_) => _login(),
              ),
            ),
          ),
        ),
        const SizedBox(height: 20),

        // Gradient button
        SizedBox(
          width: double.infinity,
          height: 56,
          child: DecoratedBox(
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF8B5CF6), Color(0xFF6D28D9)],
              ),
              borderRadius: BorderRadius.circular(28),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF8B5CF6).withValues(alpha: 0.3),
                  blurRadius: 20,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: ElevatedButton(
              onPressed: _loading ? null : _login,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(28),
                ),
              ),
              child: _loading
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white),
                    )
                  : const Text('Get Started',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                        fontSize: 16,
                      )),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildProfile() {
    final user = widget.user!;
    return Column(
      children: [
        const SizedBox(height: 20),
        // Avatar
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: const Color(0xFF8B5CF6).withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(24),
            border:
                Border.all(color: const Color(0xFF8B5CF6).withValues(alpha: 0.25)),
          ),
          child: Center(
            child: Text(
              user.username[0].toUpperCase(),
              style: const TextStyle(
                fontSize: 32,
                color: Color(0xFF8B5CF6),
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
        Text(user.username,
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w700,
              letterSpacing: -0.3,
            )),
        const SizedBox(height: 4),
        Text('Joined ${_formatDate(user.createdAt)}',
            style:
                TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 12)),
        const SizedBox(height: 32),

        // Stats glass cards
        Row(
          children: [
            Expanded(
              child: _GlassStatCard(
                icon: Icons.star_rounded,
                label: 'Reputation',
                value: user.reputationScore.toStringAsFixed(1),
                color: const Color(0xFFF59E0B),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _GlassStatCard(
                icon: Icons.article_outlined,
                label: 'Reports',
                value: '${user.reportCount}',
                color: const Color(0xFF8B5CF6),
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),

        // Reputation progress — glass panel
        ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                color: Colors.white.withValues(alpha: 0.06),
                border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Reputation Level',
                      style: TextStyle(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 14),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: LinearProgressIndicator(
                      value: user.reputationScore / 100,
                      minHeight: 8,
                      backgroundColor: Colors.white.withValues(alpha: 0.06),
                      color: _repColor(user.reputationScore),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    _repLabel(user.reputationScore),
                    style: TextStyle(
                      color: _repColor(user.reputationScore),
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  String _formatDate(String iso) {
    try {
      final dt = DateTime.parse(iso);
      return '${dt.day}/${dt.month}/${dt.year}';
    } catch (_) {
      return '';
    }
  }

  Color _repColor(double score) {
    if (score >= 75) return const Color(0xFF22C55E);
    if (score >= 50) return const Color(0xFF8B5CF6);
    if (score >= 25) return const Color(0xFFF59E0B);
    return const Color(0xFFEF4444);
  }

  String _repLabel(double score) {
    if (score >= 75) return 'Trusted Contributor';
    if (score >= 50) return 'Active Member';
    if (score >= 25) return 'New Member';
    return 'Building Trust';
  }
}

/// Glass stat card.
class _GlassStatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _GlassStatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            color: Colors.white.withValues(alpha: 0.06),
            border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.35),
                blurRadius: 32,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Column(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(icon, color: color, size: 22),
              ),
              const SizedBox(height: 10),
              Text(value,
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w800,
                    color: color,
                    letterSpacing: -0.5,
                  )),
              const SizedBox(height: 4),
              Text(label,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.3),
                    fontSize: 12,
                  )),
            ],
          ),
        ),
      ),
    );
  }
}
