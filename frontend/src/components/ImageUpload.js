import React, { useState, useRef } from 'react';

function ImageUpload({ onSubmit, loading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/bmp', 'image/tiff'];
    if (!validTypes.includes(file.type)) {
      alert('Please upload a valid image (PNG, JPEG, WEBP, BMP, or TIFF).');
      return;
    }
    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('file', selectedFile);
    onSubmit(formData);
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreview(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="card">
        <div className="card-header">
          <span className="card-header-icon">📸</span>
          <h2>Upload Job Posting Screenshot</h2>
        </div>

        <div
          className={`drop-zone ${dragActive ? 'drop-zone-active' : ''} ${preview ? 'has-preview' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/webp,image/bmp,image/tiff"
            onChange={handleChange}
            style={{ display: 'none' }}
          />

          {preview ? (
            <div className="preview-container">
              <img src={preview} alt="Preview" className="image-preview" />
              <p className="preview-name">{selectedFile?.name}</p>
            </div>
          ) : (
            <div className="drop-zone-content">
              <div className="drop-zone-icon">📷</div>
              <p className="drop-zone-text">Drop an image here or click to browse</p>
              <p className="drop-zone-hint">Supports PNG, JPEG, WEBP, BMP, TIFF</p>
            </div>
          )}
        </div>
      </div>

      <button type="submit" className="submit-btn" disabled={loading || !selectedFile}>
        {loading ? (
          <>
            <div className="spinner"></div>
            Extracting & Analyzing...
          </>
        ) : (
          <>🔬 Analyze Screenshot</>
        )}
      </button>

      {selectedFile && !loading && (
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
          Clear Image
        </button>
      )}
    </form>
  );
}

export default ImageUpload;
