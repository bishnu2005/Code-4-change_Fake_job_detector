import React, { useState } from 'react';

function UrlInput({ onSubmit, loading }) {
  const [jobUrl, setJobUrl] = useState('');
  const [companyName, setCompanyName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!jobUrl.trim()) return;
    onSubmit({
      job_url: jobUrl.trim(),
      company_name: companyName.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="card">
        <div className="card-header">
          <span className="card-header-icon">🔗</span>
          <h2>URL Legitimacy Check</h2>
        </div>

        <div className="form-grid">
          <div className="form-group full-width">
            <label>Job Posting URL <span className="required">*</span></label>
            <input
              type="url"
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
              placeholder="e.g. https://careers.google.com/jobs/123"
              required
            />
          </div>

          <div className="form-group full-width">
            <label>Company Name <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>(optional, improves accuracy)</span></label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Google"
            />
          </div>
        </div>

        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
          We'll analyze the URL structure, verify DNS, check SSL, and optionally scrape page content for ML analysis.
        </p>
      </div>

      <button type="submit" className="submit-btn" disabled={loading || !jobUrl.trim()}>
        {loading ? (
          <>
            <div className="spinner"></div>
            Analyzing URL...
          </>
        ) : (
          <>🔍 Analyze URL</>
        )}
      </button>
    </form>
  );
}

export default UrlInput;
