import React, { useState } from 'react';
import ReportModal from './ReportModal';

function ResultsDisplay({ data }) {
  const [showReport, setShowReport] = useState(false);
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

      {/* Email Domain Analysis */}
      {risk_breakdown.email_analysis && (
        <div className="card">
          <div className="card-header">
            <span className="card-header-icon">📧</span>
            <h2>Email Domain Verification</h2>
          </div>
          {risk_breakdown.email_analysis.email_found ? (
            <div className="email-analysis">
              <div className="email-domain-row">
                <span className="email-label">Email:</span>
                <span className="email-value">{risk_breakdown.email_analysis.email}</span>
              </div>
              <div className="email-domain-row">
                <span className="email-label">Domain:</span>
                <span className="email-value">{risk_breakdown.email_analysis.email_domain}</span>
              </div>
              <div className="email-badges">
                {risk_breakdown.email_analysis.free_provider && (
                  <span className="email-badge badge-danger">⚠ Free Email Provider</span>
                )}
                {!risk_breakdown.email_analysis.domain_matches_company && (
                  <span className="email-badge badge-warning">⚠ Domain Mismatch</span>
                )}
                {risk_breakdown.email_analysis.suspicious_pattern && (
                  <span className="email-badge badge-danger">🚨 Lookalike Domain</span>
                )}
                {!risk_breakdown.email_analysis.free_provider &&
                 risk_breakdown.email_analysis.domain_matches_company &&
                 !risk_breakdown.email_analysis.suspicious_pattern && (
                  <span className="email-badge badge-safe">✓ Domain Verified</span>
                )}
              </div>
            </div>
          ) : (
            <p className="no-keywords">No email address found in posting</p>
          )}
        </div>
      )}

      {/* URL Legitimacy Analysis */}
      {risk_breakdown.url_analysis && risk_breakdown.url_analysis.url_provided && (
        <div className="card">
          <div className="card-header">
            <span className="card-header-icon">🌐</span>
            <h2>URL Legitimacy Analysis</h2>
          </div>
          <div className="email-analysis">
            <div className="email-domain-row">
              <span className="email-label">URL:</span>
              <span className="email-value">{risk_breakdown.url_analysis.url}</span>
            </div>
            <div className="email-domain-row">
              <span className="email-label">Domain:</span>
              <span className="email-value">{risk_breakdown.url_analysis.domain}</span>
            </div>
            <div className="email-badges">
              {risk_breakdown.url_analysis.ip_based && (
                <span className="email-badge badge-danger">🚨 IP-Based URL</span>
              )}
              {risk_breakdown.url_analysis.free_hosting && (
                <span className="email-badge badge-danger">⚠ Free Hosting</span>
              )}
              {!risk_breakdown.url_analysis.dns_resolves && (
                <span className="email-badge badge-danger">❌ DNS Failure</span>
              )}
              {risk_breakdown.url_analysis.ssl_error && (
                <span className="email-badge badge-warning">🔓 SSL Error</span>
              )}
              {risk_breakdown.url_analysis.numeric_substitutions && (
                <span className="email-badge badge-danger">🔢 Lookalike Domain</span>
              )}
              {!risk_breakdown.url_analysis.domain_matches_company && (
                <span className="email-badge badge-warning">⚠ Domain Mismatch</span>
              )}
              {risk_breakdown.url_analysis.excessive_subdomains && (
                <span className="email-badge badge-warning">🔗 Excessive Subdomains</span>
              )}
              {risk_breakdown.url_analysis.suspicious_keywords &&
                risk_breakdown.url_analysis.suspicious_keywords.length > 0 && (
                <span className="email-badge badge-danger">🚩 Suspicious Keywords</span>
              )}
              {risk_breakdown.url_analysis.reachable &&
               risk_breakdown.url_analysis.dns_resolves &&
               !risk_breakdown.url_analysis.ip_based &&
               !risk_breakdown.url_analysis.free_hosting &&
               !risk_breakdown.url_analysis.numeric_substitutions &&
               !risk_breakdown.url_analysis.ssl_error && (
                <span className="email-badge badge-safe">✓ URL Verified</span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Community Reports */}
      {risk_breakdown.community_reports && risk_breakdown.community_reports.total_reports > 0 && (
        <div className="card">
          <div className="card-header">
            <span className="card-header-icon">👥</span>
            <h2>Community Reports</h2>
          </div>
          {(() => {
            const count = risk_breakdown.community_reports.total_reports;
            let bannerClass = 'community-banner-yellow';
            if (count >= 10) bannerClass = 'community-banner-red';
            else if (count >= 5) bannerClass = 'community-banner-orange';
            return (
              <div className={`community-banner ${bannerClass}`}>
                <span className="community-icon">🚨</span>
                <span>This entity has been reported <strong>{count}</strong> time{count !== 1 ? 's' : ''} by community users.</span>
              </div>
            );
          })()}
        </div>
      )}

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

      {/* Report Button */}
      <button
        className="report-btn"
        onClick={() => setShowReport(true)}
      >
        🚩 Report This as Scam
      </button>

      {/* Report Modal */}
      {showReport && (
        <ReportModal
          entityType="company"
          entityValue={risk_breakdown.email_analysis?.email || risk_breakdown.url_analysis?.domain || 'unknown'}
          onClose={() => setShowReport(false)}
        />
      )}
    </div>
  );
}

export default ResultsDisplay;
