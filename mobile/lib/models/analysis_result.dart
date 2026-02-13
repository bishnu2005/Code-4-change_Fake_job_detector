// Layered analysis result model matching the backend AnalyzeResponse.

class AnalysisResult {
  final VerificationResult verification;
  final CommunityResult community;
  final DomainResult domain;
  final MLResult ml;
  final ContentAnalysisResult contentAnalysis;
  final FinalRisk finalRisk;
  final ConfidenceResult confidence;
  final List<String> reasons;

  AnalysisResult({
    required this.verification,
    required this.community,
    required this.domain,
    required this.ml,
    required this.contentAnalysis,
    required this.finalRisk,
    required this.confidence,
    required this.reasons,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      verification: VerificationResult.fromJson(
        json['verification'] as Map<String, dynamic>? ?? {},
      ),
      community: CommunityResult.fromJson(
        json['community'] as Map<String, dynamic>? ?? {},
      ),
      domain: DomainResult.fromJson(
        json['domain'] as Map<String, dynamic>? ?? {},
      ),
      ml: MLResult.fromJson(json['ml'] as Map<String, dynamic>? ?? {}),
      contentAnalysis: ContentAnalysisResult.fromJson(
        json['content_analysis'] as Map<String, dynamic>? ?? {},
      ),
      finalRisk: FinalRisk.fromJson(
        json['final_risk'] as Map<String, dynamic>? ?? {},
      ),
      confidence: ConfidenceResult.fromJson(
        json['confidence'] as Map<String, dynamic>? ?? {},
      ),
      reasons: (json['reasons'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}

class VerificationResult {
  final String status;
  final String? companyName;
  final String? officialDomain;
  final bool? domainMatch;

  VerificationResult({
    this.status = 'unknown',
    this.companyName,
    this.officialDomain,
    this.domainMatch,
  });

  factory VerificationResult.fromJson(Map<String, dynamic> json) {
    return VerificationResult(
      status: json['status'] as String? ?? 'unknown',
      companyName: json['company_name'] as String?,
      officialDomain: json['official_domain'] as String?,
      domainMatch: json['domain_match'] as bool?,
    );
  }
}

class CommunityResult {
  final int totalReports;
  final int scamCount;
  final int legitCount;
  final double scamRatio;
  final double credibilityScore;

  CommunityResult({
    this.totalReports = 0,
    this.scamCount = 0,
    this.legitCount = 0,
    this.scamRatio = 0.0,
    this.credibilityScore = 0.0,
  });

  factory CommunityResult.fromJson(Map<String, dynamic> json) {
    return CommunityResult(
      totalReports: json['total_reports'] as int? ?? 0,
      scamCount: json['scam_count'] as int? ?? 0,
      legitCount: json['legit_count'] as int? ?? 0,
      scamRatio: (json['scam_ratio'] as num?)?.toDouble() ?? 0.0,
      credibilityScore: (json['credibility_score'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class DomainResult {
  final String? extractedDomain;
  final int? ageDays;
  final int blacklistHits;
  final String safeBrowsing;
  final bool domainMismatch;
  final bool https;
  final bool? reachable;
  final bool suspiciousTld;
  final double similarityScore;

  DomainResult({
    this.extractedDomain,
    this.ageDays,
    this.blacklistHits = 0,
    this.safeBrowsing = 'skipped',
    this.domainMismatch = false,
    this.https = false,
    this.reachable,
    this.suspiciousTld = false,
    this.similarityScore = 0.0,
  });

  factory DomainResult.fromJson(Map<String, dynamic> json) {
    return DomainResult(
      extractedDomain: json['extracted_domain'] as String?,
      ageDays: json['age_days'] as int?,
      blacklistHits: json['blacklist_hits'] as int? ?? 0,
      safeBrowsing: json['safe_browsing'] as String? ?? 'skipped',
      domainMismatch: json['domain_mismatch'] as bool? ?? false,
      https: json['https'] as bool? ?? false,
      reachable: json['reachable'] as bool?,
      suspiciousTld: json['suspicious_tld'] as bool? ?? false,
      similarityScore: (json['similarity_score'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class MLResult {
  final bool triggered;
  final double? probability;
  final double? riskScore;

  MLResult({this.triggered = false, this.probability, this.riskScore});

  factory MLResult.fromJson(Map<String, dynamic> json) {
    return MLResult(
      triggered: json['triggered'] as bool? ?? false,
      probability: (json['probability'] as num?)?.toDouble(),
      riskScore: (json['risk_score'] as num?)?.toDouble(),
    );
  }
}

class ContentAnalysisResult {
  final bool triggered;
  final List<String> heuristicFlags;
  final double riskBoost;

  ContentAnalysisResult({
    this.triggered = false,
    this.heuristicFlags = const [],
    this.riskBoost = 0.0,
  });

  factory ContentAnalysisResult.fromJson(Map<String, dynamic> json) {
    return ContentAnalysisResult(
      triggered: json['triggered'] as bool? ?? false,
      heuristicFlags: (json['heuristic_flags'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      riskBoost: (json['risk_boost'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class FinalRisk {
  final double score;
  final String level;

  FinalRisk({this.score = 0.0, this.level = 'Unknown'});

  factory FinalRisk.fromJson(Map<String, dynamic> json) {
    return FinalRisk(
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      level: json['level'] as String? ?? 'Unknown',
    );
  }
}

class ConfidenceResult {
  final int score;
  final String level;

  ConfidenceResult({this.score = 0, this.level = 'Low'});

  factory ConfidenceResult.fromJson(Map<String, dynamic> json) {
    return ConfidenceResult(
      score: json['score'] as int? ?? 0,
      level: json['level'] as String? ?? 'Low',
    );
  }
}
