/// Data model representing the prediction result from the API.
class PredictionResult {
  final double riskScore;
  final String riskLevel;
  final int confidenceScore;
  final String confidenceLevel;
  final double? textProbability;
  final List<ShapFactor> shapRiskFactors;
  final List<ShapFactor> shapTrustFactors;
  final UrlAnalysis? urlAnalysis;
  final EmailAnalysis? emailAnalysis;
  final String sufficiencyLevel;
  final bool dataSufficiencyFlag;
  final SignalsUsed signalsUsed;
  final List<String> reasons;

  PredictionResult({
    required this.riskScore,
    required this.riskLevel,
    required this.confidenceScore,
    required this.confidenceLevel,
    this.textProbability,
    required this.shapRiskFactors,
    required this.shapTrustFactors,
    required this.urlAnalysis,
    required this.emailAnalysis,
    required this.sufficiencyLevel,
    required this.dataSufficiencyFlag,
    required this.signalsUsed,
    required this.reasons,
  });

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    return PredictionResult(
      riskScore: (json['risk_score'] as num).toDouble(),
      riskLevel: json['risk_level'] as String,
      confidenceScore: (json['confidence_score'] as num).toInt(),
      confidenceLevel: json['confidence_level'] as String,
      textProbability: json['text_probability'] != null
          ? (json['text_probability'] as num).toDouble()
          : null,
      shapRiskFactors: (json['shap_risk_factors'] as List? ?? [])
          .map((e) => ShapFactor.fromJson(e))
          .toList(),
      shapTrustFactors: (json['shap_trust_factors'] as List? ?? [])
          .map((e) => ShapFactor.fromJson(e))
          .toList(),
      urlAnalysis: json['url_analysis'] != null
          ? UrlAnalysis.fromJson(json['url_analysis'] as Map<String, dynamic>)
          : null,
      emailAnalysis: json['email_analysis'] != null
          ? EmailAnalysis.fromJson(
              json['email_analysis'] as Map<String, dynamic>)
          : null,
      sufficiencyLevel: json['sufficiency_level'] as String? ?? 'Strong',
      dataSufficiencyFlag: json['data_sufficiency_flag'] as bool? ?? false,
      signalsUsed: SignalsUsed.fromJson(
          json['signals_used'] as Map<String, dynamic>? ?? {}),
      reasons: List<String>.from(json['reasons'] as List? ?? []),
    );
  }
}

/// SHAP explanation factor.
class ShapFactor {
  final String feature;
  final double weight;

  ShapFactor({required this.feature, required this.weight});

  factory ShapFactor.fromJson(Map<String, dynamic> json) {
    return ShapFactor(
      feature: json['feature'] as String,
      weight: (json['weight'] as num).toDouble(),
    );
  }
}

/// URL verification analysis details.
class UrlAnalysis {
  final double urlRiskScore;
  final double urlTrustScore;
  final bool httpsFlag;
  final bool ipFlag;
  final bool? reachableFlag;
  final bool suspiciousTldFlag;
  final double domainSimilarityScore;
  final int? domainAgeDays;
  final double? pageContentRiskScore;
  final bool blacklisted;
  final String safeBrowsingStatus;
  final String? extractedDomain;

  UrlAnalysis({
    this.urlRiskScore = 0,
    this.urlTrustScore = 0,
    this.httpsFlag = false,
    this.ipFlag = false,
    this.reachableFlag,
    this.suspiciousTldFlag = false,
    this.domainSimilarityScore = 0,
    this.domainAgeDays,
    this.pageContentRiskScore,
    this.blacklisted = false,
    this.safeBrowsingStatus = 'skipped',
    this.extractedDomain,
  });

  bool get hasData => extractedDomain != null && extractedDomain!.isNotEmpty;

  factory UrlAnalysis.fromJson(Map<String, dynamic> json) {
    return UrlAnalysis(
      urlRiskScore: (json['url_risk_score'] as num?)?.toDouble() ?? 0,
      urlTrustScore: (json['url_trust_score'] as num?)?.toDouble() ?? 0,
      httpsFlag: json['https_flag'] as bool? ?? false,
      ipFlag: json['ip_flag'] as bool? ?? false,
      reachableFlag: json['reachable_flag'] as bool?,
      suspiciousTldFlag: json['suspicious_tld_flag'] as bool? ?? false,
      domainSimilarityScore:
          (json['domain_similarity_score'] as num?)?.toDouble() ?? 0,
      domainAgeDays: json['domain_age_days'] as int?,
      pageContentRiskScore:
          (json['page_content_risk_score'] as num?)?.toDouble(),
      blacklisted: json['blacklisted'] as bool? ?? false,
      safeBrowsingStatus: json['safe_browsing_status'] as String? ?? 'skipped',
      extractedDomain: json['extracted_domain'] as String?,
    );
  }
}

/// Email verification analysis details.
class EmailAnalysis {
  final String emailAddress;
  final String emailDomain;
  final double emailRiskScore;
  final double emailSignalStrength;
  final bool disposableFlag;
  final bool freeProviderFlag;
  final double domainSimilarityScore;
  final bool? mxRecordExists;

  EmailAnalysis({
    this.emailAddress = '',
    this.emailDomain = '',
    this.emailRiskScore = 0,
    this.emailSignalStrength = 0,
    this.disposableFlag = false,
    this.freeProviderFlag = false,
    this.domainSimilarityScore = 0,
    this.mxRecordExists,
  });

  factory EmailAnalysis.fromJson(Map<String, dynamic> json) {
    return EmailAnalysis(
      emailAddress: json['email_address'] as String? ?? '',
      emailDomain: json['email_domain'] as String? ?? '',
      emailRiskScore: (json['email_risk_score'] as num?)?.toDouble() ?? 0,
      emailSignalStrength:
          (json['email_signal_strength'] as num?)?.toDouble() ?? 0,
      disposableFlag: json['disposable_flag'] as bool? ?? false,
      freeProviderFlag: json['free_provider_flag'] as bool? ?? false,
      domainSimilarityScore:
          (json['domain_similarity_score'] as num?)?.toDouble() ?? 0,
      mxRecordExists: json['mx_record_exists'] as bool?,
    );
  }
}

/// Signals used in the analysis.
class SignalsUsed {
  final bool text;
  final bool image;
  final bool url;
  final bool email;

  SignalsUsed({
    this.text = false,
    this.image = false,
    this.url = false,
    this.email = false,
  });

  factory SignalsUsed.fromJson(Map<String, dynamic> json) {
    return SignalsUsed(
      text: json['text'] as bool? ?? false,
      image: json['image'] as bool? ?? false,
      url: json['url'] as bool? ?? false,
      email: json['email'] as bool? ?? false,
    );
  }
}
