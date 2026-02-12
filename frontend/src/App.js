import React, { useState } from 'react';
import axios from 'axios';
import JobForm from './components/JobForm';
import ImageUpload from './components/ImageUpload';
import UrlInput from './components/UrlInput';
import ResultsDisplay from './components/ResultsDisplay';

// Default to localhost in dev, override for production
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('form'); // 'form', 'image', or 'url'

  const handleAnalyze = async (formData) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post(`${API_URL}/predict`, formData, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 30000,
      });
      setResults(response.data);
    } catch (err) {
      if (err.response) {
        setError(`Server error: ${err.response.data.detail || err.response.statusText}`);
      } else if (err.request) {
        setError('Cannot connect to the server. Make sure the backend is running on port 8000.');
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleImageAnalyze = async (formData) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post(`${API_URL}/predict-image`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
      });
      setResults(response.data);
    } catch (err) {
      if (err.response) {
        setError(`Server error: ${err.response.data.detail || err.response.statusText}`);
      } else if (err.request) {
        setError('Cannot connect to the server. Make sure the backend is running on port 8000.');
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUrlAnalyze = async (urlData) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post(`${API_URL}/predict-url`, urlData, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 30000,
      });
      setResults(response.data);
    } catch (err) {
      if (err.response) {
        setError(`Server error: ${err.response.data.detail || err.response.statusText}`);
      } else if (err.request) {
        setError('Cannot connect to the server. Make sure the backend is running on port 8000.');
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (newMode) => {
    setMode(newMode);
    setResults(null);
    setError(null);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-icon">🛡️</div>
          <div>
            <h1>Fake Job Detector</h1>
            <p>AI-powered fraud analysis engine</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        {/* Mode Tabs */}
        <div className="mode-tabs">
          <button
            className={`mode-tab ${mode === 'form' ? 'active' : ''}`}
            onClick={() => switchMode('form')}
          >
            📋 Manual Input
          </button>
          <button
            className={`mode-tab ${mode === 'image' ? 'active' : ''}`}
            onClick={() => switchMode('image')}
          >
          📸 Screenshot Upload
          </button>
          <button
            className={`mode-tab ${mode === 'url' ? 'active' : ''}`}
            onClick={() => switchMode('url')}
          >
            🔗 URL Check
          </button>
        </div>

        {mode === 'form' && (
          <JobForm onSubmit={handleAnalyze} loading={loading} />
        )}
        {mode === 'image' && (
          <ImageUpload onSubmit={handleImageAnalyze} loading={loading} />
        )}
        {mode === 'url' && (
          <UrlInput onSubmit={handleUrlAnalyze} loading={loading} />
        )}

        {error && (
          <div className="card error-card">
            <div className="error-icon">⚠️</div>
            <h3>Analysis Failed</h3>
            <p>{error}</p>
          </div>
        )}

        {results && <ResultsDisplay data={results} />}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Fake Job Posting Detector v1.0 — AI Risk Analysis Engine</p>
        <p>Built with Random Forest ML + Rule-Based Risk Engine</p>
      </footer>
    </div>
  );
}

export default App;
