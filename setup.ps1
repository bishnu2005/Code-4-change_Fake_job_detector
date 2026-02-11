# Windows Setup Script for Fake Job Posting Detector
# Run this script to set up the entire development environment

Write-Host "🚀 Starting Fake Job Posting Detector Setup..." -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "📌 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Check Node.js installation
Write-Host "📌 Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Setting up Python virtual environment..." -ForegroundColor Cyan

# Create virtual environment if it doesn't exist
if (-Not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install ML dependencies
Write-Host ""
Write-Host "📦 Installing ML dependencies..." -ForegroundColor Cyan
& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\pip.exe install -r ml_model\requirements.txt
Write-Host "✅ ML dependencies installed" -ForegroundColor Green

# Install backend dependencies
Write-Host ""
Write-Host "📦 Installing Backend dependencies..." -ForegroundColor Cyan
& .\venv\Scripts\pip.exe install -r backend\requirements.txt
Write-Host "✅ Backend dependencies installed" -ForegroundColor Green

# Setup Frontend
Write-Host ""
Write-Host "⚛️ Setting up React Frontend..." -ForegroundColor Cyan
if (-Not (Test-Path "frontend\package.json")) {
    Write-Host "Creating React app..." -ForegroundColor Yellow
    Set-Location frontend
    npx create-react-app . --template minimal
    npm install axios recharts react-icons
    Set-Location ..
    Write-Host "✅ Frontend setup complete" -ForegroundColor Green
} else {
    Write-Host "✅ Frontend already initialized" -ForegroundColor Green
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host ""
Write-Host "✨ Setup Complete! ✨" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Train the ML model: .\venv\Scripts\python.exe ml_model\train_model.py"
Write-Host "2. Start backend: .\venv\Scripts\python.exe -m uvicorn backend.main:app --reload"
Write-Host "3. Start frontend: cd frontend && npm start"
Write-Host ""
