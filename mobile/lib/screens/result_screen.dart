import 'dart:ui';
import 'package:flutter/material.dart';
import '../models/analysis_result.dart';

/// Structured result screen with glass panels.
class ResultScreen extends StatelessWidget {
  final AnalysisResult result;
  const ResultScreen({super.key, required this.result});

  Color get _riskColor {
    if (result.finalRisk.score >= 70) return const Color(0xFFEF4444);
    if (result.finalRisk.score >= 40) return const Color(0xFFF59E0B);
    return const Color(0xFF22C55E);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F14),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('Analysis Result',
            style: TextStyle(fontWeight: FontWeight.w700)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Risk gauge
            _RiskGauge(
              score: result.finalRisk.score,
              level: result.finalRisk.level,
              color: _riskColor,
              confidence: result.confidence.score,
              confidenceLevel: result.confidence.level,
            ),
            const SizedBox(height: 24),

            // Reasons summary
            if (result.reasons.isNotEmpty)
              _GlassPanel(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Key Findings',
                        style: TextStyle(
                            fontWeight: FontWeight.w700, fontSize: 15)),
                    const SizedBox(height: 10),
                    for (final r in result.reasons)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              margin: const EdgeInsets.only(top: 6),
                              width: 5,
                              height: 5,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.white.withValues(alpha: 0.3),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(r,
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: Colors.white.withValues(alpha: 0.6),
                                    height: 1.4,
                                  )),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            const SizedBox(height: 14),

            // Layer sections
            _LayerSection(
              icon: Icons.verified_outlined,
              title: 'Company Verification',
              color: _statusColor(result.verification.status),
              children: [
                _InfoRow('Status', result.verification.status.toUpperCase()),
                if (result.verification.companyName != null)
                  _InfoRow('Company', result.verification.companyName!),
                if (result.verification.officialDomain != null)
                  _InfoRow(
                      'Official Domain', result.verification.officialDomain!),
                if (result.verification.domainMatch != null)
                  _InfoRow('Domain Match',
                      result.verification.domainMatch! ? '✅ Yes' : '❌ No'),
              ],
            ),

            _LayerSection(
              icon: Icons.people_outline,
              title: 'Community Reports',
              color: const Color(0xFF8B5CF6),
              children: [
                _InfoRow('Total Reports', '${result.community.totalReports}'),
                if (result.community.totalReports > 0) ...[
                  _InfoRow('Scam', '${result.community.scamCount}'),
                  _InfoRow('Legit', '${result.community.legitCount}'),
                  _InfoRow('Scam Ratio',
                      '${(result.community.scamRatio * 100).toInt()}%'),
                  _InfoRow('Credibility',
                      '${result.community.credibilityScore.toInt()}/100'),
                ],
              ],
            ),

            _LayerSection(
              icon: Icons.dns_outlined,
              title: 'Domain Intelligence',
              color: result.domain.blacklistHits > 0
                  ? const Color(0xFFEF4444)
                  : const Color(0xFF8B5CF6),
              children: [
                if (result.domain.extractedDomain != null)
                  _InfoRow('Domain', result.domain.extractedDomain!),
                if (result.domain.ageDays != null)
                  _InfoRow('Domain Age', '${result.domain.ageDays} days'),
                _InfoRow('HTTPS', result.domain.https ? '✅' : '❌'),
                _InfoRow('Blacklist Hits', '${result.domain.blacklistHits}'),
                _InfoRow('Safe Browsing', result.domain.safeBrowsing),
                if (result.domain.suspiciousTld)
                  const _InfoRow('Suspicious TLD', '⚠️ Yes'),
                if (result.domain.domainMismatch)
                  const _InfoRow('Domain Mismatch', '⚠️ Yes'),
              ],
            ),

            _LayerSection(
              icon: Icons.psychology_outlined,
              title: 'AI Risk Engine',
              color: result.ml.triggered
                  ? (result.ml.riskScore != null && result.ml.riskScore! > 60
                      ? const Color(0xFFEF4444)
                      : const Color(0xFF22C55E))
                  : Colors.white38,
              children: [
                _InfoRow('Triggered', result.ml.triggered ? 'Yes' : 'Skipped'),
                if (result.ml.probability != null)
                  _InfoRow('Fraud Probability',
                      '${(result.ml.probability! * 100).toStringAsFixed(1)}%'),
                if (result.ml.riskScore != null)
                  _InfoRow('ML Risk Score',
                      '${result.ml.riskScore!.toStringAsFixed(1)}/100'),
              ],
            ),

            if (result.contentAnalysis.triggered)
              _LayerSection(
                icon: Icons.article_outlined,
                title: 'Deep Content Analysis',
                color: result.contentAnalysis.heuristicFlags.isNotEmpty
                    ? const Color(0xFFF59E0B)
                    : const Color(0xFF22C55E),
                children: [
                  _InfoRow('Risk Boost',
                      '+${result.contentAnalysis.riskBoost.toInt()} points'),
                  if (result.contentAnalysis.heuristicFlags.isNotEmpty)
                    _InfoRow('Flags',
                        result.contentAnalysis.heuristicFlags.join(', ')),
                ],
              ),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'trusted':
        return const Color(0xFF22C55E);
      case 'flagged':
        return const Color(0xFFEF4444);
      default:
        return const Color(0xFFF59E0B);
    }
  }
}

/// Glass panel wrapper.
class _GlassPanel extends StatelessWidget {
  final Widget child;
  const _GlassPanel({required this.child});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          width: double.infinity,
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
          child: child,
        ),
      ),
    );
  }
}

/// Risk gauge widget.
class _RiskGauge extends StatelessWidget {
  final double score;
  final String level;
  final Color color;
  final int confidence;
  final String confidenceLevel;

  const _RiskGauge({
    required this.score,
    required this.level,
    required this.color,
    required this.confidence,
    required this.confidenceLevel,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(28),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(28),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(28),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                color.withValues(alpha: 0.08),
                color.withValues(alpha: 0.03),
              ],
            ),
            border: Border.all(color: color.withValues(alpha: 0.25)),
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
              SizedBox(
                width: 130,
                height: 130,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    SizedBox(
                      width: 130,
                      height: 130,
                      child: CircularProgressIndicator(
                        value: score / 100,
                        strokeWidth: 8,
                        strokeCap: StrokeCap.round,
                        backgroundColor: Colors.white.withValues(alpha: 0.06),
                        color: color,
                      ),
                    ),
                    Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          '${score.toInt()}',
                          style: TextStyle(
                            fontSize: 40,
                            fontWeight: FontWeight.w800,
                            color: color,
                            letterSpacing: -1,
                          ),
                        ),
                        Text(
                          level,
                          style: TextStyle(
                            fontSize: 12,
                            color: color.withValues(alpha: 0.8),
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 7),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(20),
                  color: Colors.white.withValues(alpha: 0.06),
                  border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
                ),
                child: Text(
                  'Confidence: $confidence% ($confidenceLevel)',
                  style: TextStyle(
                      fontSize: 12, color: Colors.white.withValues(alpha: 0.4)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Collapsible glass layer section.
class _LayerSection extends StatelessWidget {
  final IconData icon;
  final String title;
  final Color color;
  final List<Widget> children;

  const _LayerSection({
    required this.icon,
    required this.title,
    required this.color,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: Colors.white.withValues(alpha: 0.06),
        border: Border.all(color: Colors.white.withValues(alpha: 0.12)),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Theme(
            data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
            child: ExpansionTile(
              leading: Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 18),
              ),
              title: Text(title,
                  style: const TextStyle(
                      fontSize: 14, fontWeight: FontWeight.w600)),
              initiallyExpanded: true,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                  child: Column(children: children),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Key-value info row.
class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  const _InfoRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 130,
            child: Text(label,
                style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.3), fontSize: 13)),
          ),
          Expanded(
            child: Text(value, style: const TextStyle(fontSize: 13)),
          ),
        ],
      ),
    );
  }
}
