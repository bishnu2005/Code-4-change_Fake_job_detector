import 'package:flutter/material.dart';
import '../models/prediction_result.dart';
import '../widgets/risk_indicator.dart';

/// Result screen showing risk score, level, and explanation reasons.
class ResultScreen extends StatelessWidget {
  final PredictionResult result;

  const ResultScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF0F0C29),
              Color(0xFF302B63),
              Color(0xFF24243E),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // App bar
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios_rounded,
                          color: Colors.tealAccent),
                      onPressed: () => Navigator.pop(context),
                    ),
                    const Expanded(
                      child: Text(
                        'Analysis Result',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(width: 48), // balance the back button
                  ],
                ),
              ),

              // Scrollable content
              Expanded(
                child: SingleChildScrollView(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                  child: Column(
                    children: [
                      const SizedBox(height: 16),

                      // Risk gauge
                      RiskIndicator(
                        riskScore: result.riskScore,
                        riskLevel: result.riskLevel,
                      ),
                      const SizedBox(height: 36),

                      // Reasons section
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          'Analysis Details',
                          style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.8),
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),

                      // Reason cards
                      ...result.reasons.asMap().entries.map((entry) {
                        final index = entry.key;
                        final reason = entry.value;
                        return _buildReasonCard(reason, index);
                      }),

                      const SizedBox(height: 32),

                      // Scan another button
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: () => Navigator.pop(context),
                          icon: const Icon(Icons.refresh_rounded),
                          label: const Text('Scan Another Posting',
                              style: TextStyle(
                                  fontSize: 16, fontWeight: FontWeight.w600)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.tealAccent,
                            foregroundColor: const Color(0xFF0F0C29),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(14)),
                            elevation: 4,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildReasonCard(String reason, int index) {
    IconData icon;
    Color iconColor;

    if (reason.toLowerCase().contains('ml model')) {
      icon = Icons.psychology_rounded;
      iconColor = const Color(0xFF70A1FF);
    } else if (reason.toLowerCase().contains('keyword')) {
      icon = Icons.text_fields_rounded;
      iconColor = const Color(0xFFFFA502);
    } else if (reason.toLowerCase().contains('salary')) {
      icon = Icons.attach_money_rounded;
      iconColor = const Color(0xFFFF6B81);
    } else if (reason.toLowerCase().contains('domain') ||
        reason.toLowerCase().contains('url')) {
      icon = Icons.link_rounded;
      iconColor = const Color(0xFFA29BFE);
    } else {
      icon = Icons.info_outline_rounded;
      iconColor = const Color(0xFF2ED573);
    }

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              reason,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.85),
                fontSize: 14,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
