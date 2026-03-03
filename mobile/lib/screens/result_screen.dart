import 'package:flutter/material.dart';
import '../models/prediction_result.dart';
import '../widgets/risk_indicator.dart';

/// Result screen showing risk score, confidence, SHAP explanations,
/// URL verification, and detailed analysis.
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
                    const SizedBox(width: 48),
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
                      const SizedBox(height: 20),

                      // Confidence indicator
                      _buildConfidenceIndicator(),
                      const SizedBox(height: 24),

                      // Sufficiency warning banner
                      if (result.sufficiencyLevel == 'Weak')
                        _buildWarningBanner(
                          'Limited information provided. Add URL or more details for better accuracy.',
                        ),
                      if (result.dataSufficiencyFlag &&
                          result.sufficiencyLevel != 'Weak')
                        _buildWarningBanner(
                          '⚠️ Limited input provided. Assessment may be less reliable.',
                        ),

                      // SHAP Explanation Section
                      if (result.shapRiskFactors.isNotEmpty ||
                          result.shapTrustFactors.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        _buildShapSection(),
                      ],

                      // URL Verification Card
                      if (result.urlAnalysis != null) ...[
                        const SizedBox(height: 16),
                        _buildUrlCard(),
                      ],

                      // Email Analysis Card
                      if (result.emailAnalysis != null) ...[
                        const SizedBox(height: 16),
                        _buildEmailCard(),
                      ],

                      const SizedBox(height: 24),

                      // Reasons section
                      if (result.reasons.isNotEmpty) ...[
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
                        ...result.reasons.asMap().entries.map((entry) {
                          return _buildReasonCard(entry.value, entry.key);
                        }),
                      ],

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

  // ── Confidence Indicator ─────────────────────────────────────
  Widget _buildConfidenceIndicator() {
    Color confColor;
    IconData confIcon;
    switch (result.confidenceLevel) {
      case 'Very High':
        confColor = const Color(0xFF2ED573);
        confIcon = Icons.verified_rounded;
        break;
      case 'High':
        confColor = const Color(0xFF70A1FF);
        confIcon = Icons.thumb_up_rounded;
        break;
      case 'Medium':
        confColor = const Color(0xFFFFA502);
        confIcon = Icons.thumbs_up_down_rounded;
        break;
      default:
        confColor = const Color(0xFFFF6B81);
        confIcon = Icons.help_outline_rounded;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      decoration: BoxDecoration(
        color: confColor.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: confColor.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(confIcon, color: confColor, size: 22),
          const SizedBox(width: 10),
          Text(
            'Confidence: ${result.confidenceScore}%',
            style: TextStyle(
              color: confColor,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
            decoration: BoxDecoration(
              color: confColor.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              result.confidenceLevel,
              style: TextStyle(
                color: confColor,
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Warning Banner ───────────────────────────────────────────
  Widget _buildWarningBanner(String message) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFFFA502).withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(12),
        border:
            Border.all(color: const Color(0xFFFFA502).withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.warning_amber_rounded,
              color: Color(0xFFFFA502), size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                color: Color(0xFFFFA502),
                fontSize: 13,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── SHAP Explanation Section ─────────────────────────────────
  Widget _buildShapSection() {
    return _ExpandableSection(
      title: 'AI Explanation (SHAP)',
      icon: Icons.psychology_rounded,
      iconColor: const Color(0xFF70A1FF),
      children: [
        if (result.shapRiskFactors.isNotEmpty) ...[
          _buildShapSubheading('Why Risky', const Color(0xFFFF4757)),
          ...result.shapRiskFactors.map((f) =>
              _buildShapRow(f.feature, f.weight, const Color(0xFFFF4757))),
          const SizedBox(height: 12),
        ],
        if (result.shapTrustFactors.isNotEmpty) ...[
          _buildShapSubheading('Why Trustworthy', const Color(0xFF2ED573)),
          ...result.shapTrustFactors.map((f) =>
              _buildShapRow(f.feature, f.weight, const Color(0xFF2ED573))),
        ],
      ],
    );
  }

  Widget _buildShapSubheading(String text, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 14,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _buildShapRow(String feature, double weight, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              feature,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.85),
                fontSize: 13,
              ),
            ),
          ),
          Text(
            weight > 0
                ? '+${weight.toStringAsFixed(3)}'
                : weight.toStringAsFixed(3),
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w600,
              fontFamily: 'monospace',
            ),
          ),
        ],
      ),
    );
  }

  // ── URL Verification Card ────────────────────────────────────
  Widget _buildUrlCard() {
    final url = result.urlAnalysis!;
    return _ExpandableSection(
      title: 'URL Verification',
      icon: Icons.link_rounded,
      iconColor: const Color(0xFFA29BFE),
      children: [
        if (url.extractedDomain != null)
          _buildUrlRow('Domain', url.extractedDomain!, icon: Icons.dns_rounded),
        _buildUrlCheckRow('HTTPS', url.httpsFlag),
        _buildUrlCheckRow('Reachable', url.reachableFlag),
        _buildUrlCheckRow('Uses IP Address', url.ipFlag, invert: true),
        _buildUrlCheckRow('Suspicious TLD', url.suspiciousTldFlag,
            invert: true),
        if (url.blacklisted)
          _buildUrlCheckRow('Blacklisted', true, invert: true),
        if (url.domainSimilarityScore > 0)
          _buildUrlRow('Domain Similarity',
              '${(url.domainSimilarityScore * 100).toStringAsFixed(0)}%',
              icon: Icons.compare_arrows_rounded),
        _buildSafeBrowsingRow(url.safeBrowsingStatus),
      ],
    );
  }

  Widget _buildUrlRow(String label, String value, {IconData? icon}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          if (icon != null) ...[
            Icon(icon, color: Colors.white.withValues(alpha: 0.5), size: 16),
            const SizedBox(width: 8),
          ],
          Text(label,
              style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.6), fontSize: 13)),
          const Spacer(),
          Text(value,
              style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.9),
                  fontSize: 13,
                  fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _buildUrlCheckRow(String label, bool? value, {bool invert = false}) {
    if (value == null) {
      return _buildUrlRow(label, '—');
    }
    final isGood = invert ? !value : value;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(
            isGood ? Icons.check_circle_rounded : Icons.cancel_rounded,
            color: isGood ? const Color(0xFF2ED573) : const Color(0xFFFF4757),
            size: 16,
          ),
          const SizedBox(width: 8),
          Text(label,
              style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.7), fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildSafeBrowsingRow(String status) {
    Color color;
    String text;
    IconData icon;

    switch (status) {
      case 'clean':
        color = const Color(0xFF2ED573);
        text = 'Clean';
        icon = Icons.verified_user_rounded;
        break;
      case 'malicious':
        color = const Color(0xFFFF4757);
        text = 'Malicious';
        icon = Icons.gpp_bad_rounded;
        break;
      case 'skipped':
        color = Colors.white.withValues(alpha: 0.4);
        text = 'Not Checked';
        icon = Icons.remove_circle_outline_rounded;
        break;
      default:
        color = const Color(0xFFFFA502);
        text = 'Unavailable';
        icon = Icons.error_outline_rounded;
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, color: color, size: 16),
          const SizedBox(width: 8),
          Text('Safe Browsing',
              style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.7), fontSize: 13)),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(text,
                style: TextStyle(
                    color: color, fontSize: 11, fontWeight: FontWeight.w700)),
          ),
        ],
      ),
    );
  }

  // ── Reason Cards (legacy) ────────────────────────────────────
  Widget _buildReasonCard(String reason, int index) {
    IconData icon;
    Color iconColor;

    if (reason.toLowerCase().contains('ml model') ||
        reason.toLowerCase().contains('probability')) {
      icon = Icons.psychology_rounded;
      iconColor = const Color(0xFF70A1FF);
    } else if (reason.toLowerCase().contains('keyword')) {
      icon = Icons.text_fields_rounded;
      iconColor = const Color(0xFFFFA502);
    } else if (reason.toLowerCase().contains('salary')) {
      icon = Icons.currency_rupee_rounded;
      iconColor = const Color(0xFFFF6B81);
    } else if (reason.toLowerCase().contains('email') ||
        reason.toLowerCase().contains('disposable')) {
      icon = Icons.email_rounded;
      iconColor = const Color(0xFFE056A0);
    } else if (reason.toLowerCase().contains('domain') ||
        reason.toLowerCase().contains('url') ||
        reason.toLowerCase().contains('https') ||
        reason.toLowerCase().contains('safe browsing')) {
      icon = Icons.link_rounded;
      iconColor = const Color(0xFFA29BFE);
    } else if (reason.toLowerCase().contains('limited') ||
        reason.toLowerCase().contains('warning')) {
      icon = Icons.warning_amber_rounded;
      iconColor = const Color(0xFFFFA502);
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

  // ── Email Analysis Card ─────────────────────────────────────
  Widget _buildEmailCard() {
    final email = result.emailAnalysis!;
    return _ExpandableSection(
      title: 'Email Verification',
      icon: Icons.email_rounded,
      iconColor: const Color(0xFFE056A0),
      children: [
        if (email.emailAddress.isNotEmpty)
          _buildUrlRow('Email', email.emailAddress,
              icon: Icons.alternate_email),
        if (email.emailDomain.isNotEmpty)
          _buildUrlRow('Domain', email.emailDomain, icon: Icons.dns_rounded),
        _buildUrlCheckRow('Disposable Provider', email.disposableFlag,
            invert: true),
        _buildUrlCheckRow('Free Provider', email.freeProviderFlag,
            invert: true),
        _buildUrlCheckRow('MX Record Exists', email.mxRecordExists),
        if (email.domainSimilarityScore > 0)
          _buildUrlRow('Company Match',
              '${(email.domainSimilarityScore * 100).toStringAsFixed(0)}%',
              icon: Icons.compare_arrows_rounded),
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Row(
            children: [
              Text('Risk Score',
                  style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.6),
                      fontSize: 13)),
              const Spacer(),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                decoration: BoxDecoration(
                  color: (email.emailRiskScore > 40
                          ? const Color(0xFFFF4757)
                          : const Color(0xFF2ED573))
                      .withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '${email.emailRiskScore.toStringAsFixed(0)}%',
                  style: TextStyle(
                    color: email.emailRiskScore > 40
                        ? const Color(0xFFFF4757)
                        : const Color(0xFF2ED573),
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// ── Expandable Section Widget ──────────────────────────────────
class _ExpandableSection extends StatefulWidget {
  final String title;
  final IconData icon;
  final Color iconColor;
  final List<Widget> children;

  const _ExpandableSection({
    required this.title,
    required this.icon,
    required this.iconColor,
    required this.children,
  });

  @override
  State<_ExpandableSection> createState() => _ExpandableSectionState();
}

class _ExpandableSectionState extends State<_ExpandableSection> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Column(
        children: [
          // Header (tap to expand/collapse)
          InkWell(
            borderRadius: BorderRadius.circular(16),
            onTap: () => setState(() => _expanded = !_expanded),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: widget.iconColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(widget.icon, color: widget.iconColor, size: 18),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      widget.title,
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.9),
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  AnimatedRotation(
                    turns: _expanded ? 0.5 : 0,
                    duration: const Duration(milliseconds: 200),
                    child: Icon(
                      Icons.expand_more_rounded,
                      color: Colors.white.withValues(alpha: 0.5),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Expandable content
          AnimatedCrossFade(
            firstChild: const SizedBox.shrink(),
            secondChild: Padding(
              padding: const EdgeInsets.only(left: 16, right: 16, bottom: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Divider(color: Colors.white.withValues(alpha: 0.1)),
                  const SizedBox(height: 8),
                  ...widget.children,
                ],
              ),
            ),
            crossFadeState: _expanded
                ? CrossFadeState.showSecond
                : CrossFadeState.showFirst,
            duration: const Duration(milliseconds: 250),
          ),
        ],
      ),
    );
  }
}
