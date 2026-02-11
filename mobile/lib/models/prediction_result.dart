/// Data model representing the prediction result from the API.
class PredictionResult {
  final double riskScore;
  final String riskLevel;
  final List<String> reasons;

  PredictionResult({
    required this.riskScore,
    required this.riskLevel,
    required this.reasons,
  });

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    return PredictionResult(
      riskScore: (json['risk_score'] as num).toDouble(),
      riskLevel: json['risk_level'] as String,
      reasons: List<String>.from(json['reasons'] as List),
    );
  }
}
