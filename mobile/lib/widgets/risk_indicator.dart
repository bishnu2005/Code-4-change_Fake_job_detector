import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Animated circular risk gauge widget.
class RiskIndicator extends StatefulWidget {
  final double riskScore;
  final String riskLevel;

  const RiskIndicator({
    super.key,
    required this.riskScore,
    required this.riskLevel,
  });

  @override
  State<RiskIndicator> createState() => _RiskIndicatorState();
}

class _RiskIndicatorState extends State<RiskIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _animation = Tween<double>(begin: 0, end: widget.riskScore / 100).animate(
        CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic));
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Color _getRiskColor() {
    if (widget.riskScore >= 70) return const Color(0xFFFF4757);
    if (widget.riskScore >= 40) return const Color(0xFFFFA502);
    return const Color(0xFF2ED573);
  }

  IconData _getRiskIcon() {
    if (widget.riskScore >= 70) return Icons.dangerous_rounded;
    if (widget.riskScore >= 40) return Icons.warning_amber_rounded;
    return Icons.verified_user_rounded;
  }

  @override
  Widget build(BuildContext context) {
    final color = _getRiskColor();

    return Column(
      children: [
        SizedBox(
          width: 180,
          height: 180,
          child: AnimatedBuilder(
            animation: _animation,
            builder: (context, child) {
              return CustomPaint(
                painter: _RiskGaugePainter(
                  progress: _animation.value,
                  color: color,
                ),
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(_getRiskIcon(), color: color, size: 32),
                      const SizedBox(height: 4),
                      Text(
                        '${(_animation.value * 100).toStringAsFixed(0)}',
                        style: TextStyle(
                          color: color,
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: color.withValues(alpha: 0.4)),
          ),
          child: Text(
            widget.riskLevel,
            style: TextStyle(
              color: color,
              fontSize: 18,
              fontWeight: FontWeight.w700,
              letterSpacing: 1.2,
            ),
          ),
        ),
      ],
    );
  }
}

class _RiskGaugePainter extends CustomPainter {
  final double progress;
  final Color color;

  _RiskGaugePainter({required this.progress, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 12;

    // Background arc
    final bgPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.08)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 10
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi * 0.75,
      math.pi * 1.5,
      false,
      bgPaint,
    );

    // Progress arc
    final progressPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 10
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi * 0.75,
      math.pi * 1.5 * progress,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(covariant _RiskGaugePainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.color != color;
  }
}
