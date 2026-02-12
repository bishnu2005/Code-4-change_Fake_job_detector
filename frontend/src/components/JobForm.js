import React, { useState } from 'react';

const EMPLOYMENT_TYPES = ['', 'Full-time', 'Part-time', 'Contract', 'Temporary', 'Other'];
const EXPERIENCE_LEVELS = ['', 'Entry level', 'Mid-Senior level', 'Executive', 'Director', 'Internship', 'Associate', 'Not Applicable'];
const EDUCATION_LEVELS = ['', "Bachelor's Degree", "Master's Degree", "High School or equivalent", "Some College Coursework Completed", "Associate Degree", "Doctorate", "Professional", "Vocational", "Some High School Coursework", "Unspecified", "Certification"];

const initialFormState = {
  title: '',
  description: '',
  company_profile: '',
  requirements: '',
  benefits: '',
  salary_range: '',
  contact_email: '',
  job_url: '',
  location: '',
  department: '',
  employment_type: '',
  required_experience: '',
  required_education: '',
  industry: '',
  function: '',
  telecommuting: 0,
  has_company_logo: 1,
  has_questions: 1,
};

function JobForm({ onSubmit, loading }) {
  const [form, setForm] = useState(initialFormState);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (checked ? 1 : 0) : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  const handleClear = () => {
    setForm(initialFormState);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Job Details Card */}
      <div className="card">
        <div className="card-header">
          <span className="card-header-icon">📋</span>
          <h2>Job Posting Details</h2>
        </div>

        <div className="form-grid">
          <div className="form-group">
            <label>Job Title <span className="required">*</span></label>
            <input
              type="text"
              name="title"
              value={form.title}
              onChange={handleChange}
              placeholder="e.g. Senior Software Engineer"
              required
            />
          </div>

          <div className="form-group">
            <label>Location</label>
            <input
              type="text"
              name="location"
              value={form.location}
              onChange={handleChange}
              placeholder="e.g. US, CA, San Francisco"
            />
          </div>

          <div className="form-group">
            <label>Department</label>
            <input
              type="text"
              name="department"
              value={form.department}
              onChange={handleChange}
              placeholder="e.g. Engineering"
            />
          </div>

          <div className="form-group">
            <label>Salary Range</label>
            <input
              type="text"
              name="salary_range"
              value={form.salary_range}
              onChange={handleChange}
              placeholder="e.g. 50000-80000"
            />
          </div>

          <div className="form-group">
            <label>Contact Email</label>
            <input
              type="email"
              name="contact_email"
              value={form.contact_email}
              onChange={handleChange}
              placeholder="e.g. hr@company.com"
            />
          </div>

          <div className="form-group">
            <label>Job Posting URL</label>
            <input
              type="url"
              name="job_url"
              value={form.job_url}
              onChange={handleChange}
              placeholder="e.g. https://careers.company.com/job/123"
            />
          </div>

          <div className="form-group">
            <label>Employment Type</label>
            <select name="employment_type" value={form.employment_type} onChange={handleChange}>
              {EMPLOYMENT_TYPES.map(t => (
                <option key={t} value={t}>{t || '-- Select --'}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Experience Level</label>
            <select name="required_experience" value={form.required_experience} onChange={handleChange}>
              {EXPERIENCE_LEVELS.map(t => (
                <option key={t} value={t}>{t || '-- Select --'}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Education Level</label>
            <select name="required_education" value={form.required_education} onChange={handleChange}>
              {EDUCATION_LEVELS.map(t => (
                <option key={t} value={t}>{t || '-- Select --'}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Industry</label>
            <input
              type="text"
              name="industry"
              value={form.industry}
              onChange={handleChange}
              placeholder="e.g. Information Technology"
            />
          </div>

          <div className="form-group">
            <label>Function</label>
            <input
              type="text"
              name="function"
              value={form.function}
              onChange={handleChange}
              placeholder="e.g. Engineering"
            />
          </div>
        </div>
      </div>

      {/* Text Content Card */}
      <div className="card">
        <div className="card-header">
          <span className="card-header-icon">📝</span>
          <h2>Content & Description</h2>
        </div>

        <div className="form-grid">
          <div className="form-group full-width">
            <label>Job Description <span className="required">*</span></label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              placeholder="Paste the full job description here..."
              rows={5}
              required
            />
          </div>

          <div className="form-group full-width">
            <label>Company Profile</label>
            <textarea
              name="company_profile"
              value={form.company_profile}
              onChange={handleChange}
              placeholder="Company description or 'About Us' section..."
              rows={3}
            />
          </div>

          <div className="form-group full-width">
            <label>Requirements</label>
            <textarea
              name="requirements"
              value={form.requirements}
              onChange={handleChange}
              placeholder="Job requirements and qualifications..."
              rows={3}
            />
          </div>

          <div className="form-group full-width">
            <label>Benefits</label>
            <textarea
              name="benefits"
              value={form.benefits}
              onChange={handleChange}
              placeholder="Listed benefits and perks..."
              rows={2}
            />
          </div>
        </div>
      </div>

      {/* Flags Card */}
      <div className="card">
        <div className="card-header">
          <span className="card-header-icon">🔍</span>
          <h2>Posting Indicators</h2>
        </div>

        <div className="toggle-group">
          <label className="toggle-item">
            <input
              type="checkbox"
              name="has_company_logo"
              checked={form.has_company_logo === 1}
              onChange={handleChange}
            />
            <span>Has Company Logo</span>
          </label>

          <label className="toggle-item">
            <input
              type="checkbox"
              name="has_questions"
              checked={form.has_questions === 1}
              onChange={handleChange}
            />
            <span>Has Screening Questions</span>
          </label>

          <label className="toggle-item">
            <input
              type="checkbox"
              name="telecommuting"
              checked={form.telecommuting === 1}
              onChange={handleChange}
            />
            <span>Remote / Telecommuting</span>
          </label>
        </div>
      </div>

      {/* Action Buttons */}
      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? (
          <>
            <div className="spinner"></div>
            Analyzing...
          </>
        ) : (
          <>🔬 Analyze Job Posting</>
        )}
      </button>

      {!loading && (form.title || form.description) && (
        <button
          type="button"
          className="submit-btn"
          onClick={handleClear}
          style={{
            background: 'transparent',
            border: '1px solid var(--border-color)',
            marginTop: '0.5rem',
            fontSize: '0.85rem',
            textTransform: 'none',
            letterSpacing: 'normal',
          }}
        >
          Clear Form
        </button>
      )}
    </form>
  );
}

export default JobForm;
