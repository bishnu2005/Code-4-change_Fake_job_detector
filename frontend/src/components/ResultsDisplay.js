import React from 'react';

function ResultsDisplay({ data }) {
  const {
    prediction,
    fraud_probability,
    confidence,
    risk_level,
    risk_score,
    risk_breakdown,
    recommendations,
  } = data;

  const riskClass = `risk-${risk_level.toLowerCase()}`;

  return (
    <div className="results">
      {/* Risk Score Card */}
      <div className={`card risk-score-card ${riskClass}`}>
        <div className={`risk-verdict ${prediction.toLowerCase()}`}>
          {prediction === 'FRAUDULENT' ? '⚠ POTENTIAL FRAUD DETECTED' : '✓ LIKELY LEGITIMATE'}
        </div>

        <div className="risk-score-circle">
          <span className="risk-score-number">{risk_score}</span>
          <span className="risk-score-label">Risk Score</span>
        </div>

        <div className="risk-level-badge">{risk_level} RISK</div>

        <div className="prob-bar-container">
          <div className="prob-bar-label">
            <span>Fraud Probability</span>
            <span>{(fraud_probability * 100).toFixed(1)}%</span>
          </div>
          <div className="prob-bar">
            <div
              className="prob-bar-fill"
              style={{ width: `${fraud_probability * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="card">
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-value">{(confidence * 100).toFixed(1)}%</div>
            <div className="stat-label">Confidence</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{risk_breakdown.missing_fields_count}</div>
            <div className="stat-label">Missing Fields</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{risk_breakdown.scam_keywords_found.length}</div>
            <div className="stat-label">Scam Keywords</div>
          </div>
        </div>
      </div>

      {/* Risk Factors */}
      {risk_breakdown.risk_factors && risk_breakdown.risk_factors.length > 0 && (
        <div className="card">
          <div className="card-header">
            <span className="card-header-icon">🚩</span>
            <h2>Risk Factors Identified</h2>
          </div>
          <ul className="risk-factors-list">
            {risk_breakdown.risk_factors.map((factor, i) => (
              <li key={i} className="risk-factor-item">
                <span className="icon">▸</span>
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Scam Keywords */}
      <div className="card">
        <div className="card-header">
          <span className="card-header-icon">🔑</span>
          <h2>Scam Keywords Detected</h2>
        </div>
        {risk_breakdown.scam_keywords_found.length > 0 ? (
          <div className="keyword-tags">
            {risk_breakdown.scam_keywords_found.map((keyword, i) => (
              <span key={i} className="keyword-tag">{keyword}</span>
            ))}
          </div>
        ) : (
          <p className="no-keywords">✓ No scam keywords detected</p>
        )}
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="card">
          <div className="card-header">
            <span className="card-header-icon">💡</span>
            <h2>Recommendations</h2>
          </div>
          <ul className="recommendations-list">
            {recommendations.map((rec, i) => (
              <li key={i} className="recommendation-item">{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ResultsDisplay;
