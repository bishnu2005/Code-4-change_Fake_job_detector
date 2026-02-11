# 🛠️ Quick Setup Guide

## Automated Setup (Recommended)

### Windows

```powershell
.\setup.ps1
```

This will:

- ✅ Check Python and Node.js installations
- ✅ Create virtual environment
- ✅ Install all Python dependencies (ML + Backend)
- ✅ Setup React frontend with dependencies

---

## Manual Setup

### 1. Python Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install ML dependencies
pip install -r ml_model\requirements.txt

# Install Backend dependencies
pip install -r backend\requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

---

## Verify Installation

### Check Python packages

```bash
.\venv\Scripts\pip list
```

Should show: pandas, scikit-learn, fastapi, uvicorn, etc.

### Check Node packages

```bash
cd frontend
npm list --depth=0
```

Should show: react, axios, recharts, react-icons

---

## 🚀 Running the Application

### 1. Train ML Model (First Time Only)

```bash
.\venv\Scripts\python ml_model\train_model.py
```

### 2. Start Backend

```bash
.\venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000
```

### 3. Start Frontend (New Terminal)

```bash
cd frontend
npm start
```

Access at: `http://localhost:3000`

---

## 📦 Dependencies Summary

### ML Model (`ml_model/requirements.txt`)

- pandas==2.0.3
- numpy==1.24.3
- scikit-learn==1.3.0
- joblib==1.3.2
- matplotlib==3.7.2
- seaborn==0.12.2

### Backend (`backend/requirements.txt`)

- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.5.0
- scikit-learn==1.3.0
- pandas==2.0.3
- numpy==1.24.3
- joblib==1.3.2
- python-multipart==0.0.6

### Frontend (`frontend/package.json`)

- react ^18.2.0
- axios ^1.6.0
- recharts ^2.10.0
- react-icons ^4.12.0

---

## Troubleshooting

### Python Issues

**Error**: `python: command not found`

- Install Python 3.9+ from python.org
- Add Python to PATH during installation

**Error**: `pip: command not found`

- Use: `python -m pip` instead of `pip`

### Node.js Issues

**Error**: `npm: command not found`

- Install Node.js 18+ from nodejs.org
- Restart terminal after installation

### Virtual Environment

**Error**: Cannot activate venv

- Windows: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Then retry: `.\venv\Scripts\activate`

---

## ✅ Pre-flight Checklist

Before starting development:

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Virtual environment created
- [ ] ML dependencies installed
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] All folders exist (ml_model, backend, frontend)
