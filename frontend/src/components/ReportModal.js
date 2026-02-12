import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ReportModal({ entityType, entityValue, onClose }) {
  const [reason, setReason] = useState('');
  const [status, setStatus] = useState(null); // null | 'loading' | 'success' | 'error'
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('loading');

    try {
      const response = await axios.post(`${API_URL}/report`, {
        entity_type: entityType,
        entity_value: entityValue,
        report_reason: reason,
      });
      setStatus('success');
      setMessage(response.data.message || 'Report submitted!');
    } catch (err) {
      setStatus('error');
      if (err.response && err.response.data) {
        setMessage(err.response.data.detail || 'Failed to submit report.');
      } else {
        setMessage('Network error. Please try again.');
      }
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="card-header-icon">🚩</span>
          <h2>Report as Scam</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {status === 'success' ? (
          <div className="modal-success">
            <p>✅ {message}</p>
            <button className="submit-btn" onClick={onClose}>Close</button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              <p className="modal-entity">
                <strong>{entityType}:</strong> {entityValue}
              </p>

              <div className="form-group">
                <label>Reason for reporting</label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="e.g. Asked for upfront payment, fake recruiter, etc."
                  maxLength={500}
                  rows={3}
                />
              </div>

              {status === 'error' && (
                <p className="modal-error">⚠️ {message}</p>
              )}
            </div>

            <button
              type="submit"
              className="submit-btn"
              disabled={status === 'loading'}
            >
              {status === 'loading' ? 'Submitting...' : '🚩 Submit Report'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

export default ReportModal;
