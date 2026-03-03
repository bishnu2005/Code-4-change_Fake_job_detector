# Fake Job Posting Detector — Mobile App

Flutter-based mobile client for the Fake Job Posting Detector.

## Setup

```bash
cd mobile
flutter pub get
```

## Configure API URL

Edit `lib/services/api_service.dart` and set `baseUrl`:

```dart
static String baseUrl = 'http://10.0.2.2:8000'; // Android emulator
// static String baseUrl = 'http://localhost:8000'; // iOS simulator
// static String baseUrl = 'https://your-app.onrender.com'; // Production
```

## Run

```bash
flutter run
```

## Features

- Text input form (company, salary, description, apply URL)
- Image upload with OCR analysis
- Animated risk gauge
- Detailed explanation reasons
- Error handling with snackbar messages
- Loading overlay during API calls
