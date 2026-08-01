# Dijital Gardrop - Setup Guide

This guide will help you set up and run the Dijital Gardrop social media application with AI-powered wardrobe features.

## Project Structure

```
yzta_bootcamp_2026/
├── socialMedia_backend/     # FastAPI Python backend
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── api/routers/    # API endpoints
│   │   ├── core/           # Config, database
│   │   ├── services/       # AI services (Ollama, FashionSigLIP)
│   │   └── ...
│   ├── requirements.txt
│   ├── .env.example
│   └── dijital_gardrop.db  # SQLite database (auto-created)
│
└── socialMedia_frontend/    # Flutter mobile app
    ├── lib/
    │   ├── main.dart
    │   ├── core/           # Theme, navigation, API service
    │   ├── features/       # Feature modules (auth, feed, wardrobe, etc.)
    │   └── ...
    ├── pubspec.yaml
    └── ...
```

---

## Prerequisites

### Backend Requirements
- **Python 3.9+** (3.10+ recommended for torch compatibility)
- **Ollama** installed and running (for AI features)
- **Git** (for cloning)

### Frontend Requirements
- **Flutter SDK 3.10+**
- **Dart SDK 3.0+** (included with Flutter)
- **Android Studio / Xcode** (for device emulators)
- **VS Code** with Flutter extension (recommended)

### AI Models (via Ollama)
```bash
# Install Ollama from https://ollama.com
# Then pull required models:
ollama pull moondream        # ~1.7GB - Vision model for image analysis
ollama pull llama3.2         # ~2GB - Text model for chat/stylist
```

---

## Backend Setup

### 1. Navigate to backend directory
```bash
cd socialMedia_backend
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** The first install may take a while due to PyTorch and transformers. If you have issues with torch on macOS, try:
> ```bash
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
> ```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Server - Use your local IP for physical device testing
# Mac: ipconfig getifaddr en0
# Windows: ipconfig | findstr IPv4
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# AI Services (optional - for Gemini fallback)
# GEMINI_API_KEY=your_key_here
# GEMINI_MODEL=gemini-2.5-flash

# CORS - Add your Flutter app's origin
# For iOS Simulator: http://localhost:8081
# For Android Emulator: http://10.0.2.2:8081
# For physical device: http://YOUR_IP:8081
CORS_ORIGINS=http://localhost:8081,http://10.0.2.2:8081
```

### 5. Initialize database
The database is auto-created on first run, but you can also run:
```bash
python -c "from app.core.database import init_db; init_db()"
```

Or run the migration script:
```bash
python migrate.py
```

### 6. Start Ollama (in a separate terminal)
```bash
ollama serve
```

### 7. Run the backend
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

---

## Frontend Setup

### 1. Navigate to frontend directory
```bash
cd socialMedia_frontend
```

### 2. Get Flutter dependencies
```bash
flutter pub get
```

### 3. Configure API base URL

The API base URL is configured in `lib/core/api/api_service.dart`. For different environments:

**For iOS Simulator:**
```dart
// lib/core/api/api_service.dart
static const String baseUrl = 'http://localhost:8000';
```

**For Android Emulator:**
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

**For Physical Device (replace with your computer's IP):**
```dart
static const String baseUrl = 'http://192.168.1.XXX:8000';
```

> **Tip:** Find your IP with `ipconfig getifaddr en0` (Mac) or `ipconfig` (Windows)

### 4. Run the app

**List available devices:**
```bash
flutter devices
```

**Run on a device:**
```bash
# iOS Simulator
flutter run -d ios

# Android Emulator
flutter run -d android

# Physical device (replace with device ID)
flutter run -d <device_id>

# Web (for testing)
flutter run -d chrome
```

---

## Running Both Services Together

### Option 1: Two Terminal Windows (Recommended)

**Terminal 1 - Backend:**
```bash
cd socialMedia_backend
source venv/bin/activate
ollama serve  # In another tab/window
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd socialMedia_frontend
flutter run -d <your_device>
```

### Option 2: Using a Process Manager (Optional)

Create a `Procfile` in the root:
```
backend: cd socialMedia_backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
frontend: cd socialMedia_frontend && flutter run -d <device_id>
```

Then use `foreman start` or similar.

---

## Testing the Setup

### 1. Verify Backend
```bash
curl http://localhost:8000/
# Should return: {"status":"healthy","service":"dijital-gardrop-api","version":"1.0.0"}

curl http://localhost:8000/docs
# Should show Swagger UI
```

### 2. Verify Ollama Models
```bash
ollama list
# Should show moondream and llama3.2

# Test vision model
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"moondream","prompt":"Describe this image","stream":false,"images":["base64_image"]}'
```

### 3. Verify Frontend
- App should launch on your device/emulator
- Check console for API connection logs
- Try registering a new account

---

## Common Issues & Solutions

### Backend Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: torch` | Reinstall: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu` |
| `Ollama connection refused` | Ensure `ollama serve` is running in another terminal |
| `CUDA out of memory` | Use CPU-only torch: `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| Database locked | Delete `dijital_gardrop.db` and restart (dev only) |
| CORS errors | Check `CORS_ORIGINS` in `.env` matches your Flutter app origin |

### Frontend Issues

| Issue | Solution |
|-------|----------|
| `Connection refused` | Verify backend is running and `baseUrl` in `api_service.dart` is correct |
| `SocketException` on Android | Use `10.0.2.2` instead of `localhost` for emulator |
| `SocketException` on iOS | Use your Mac's IP address, not `localhost` |
| Build errors | Run `flutter clean && flutter pub get` |
| White screen | Check console for errors, verify API connectivity |

### AI Features Not Working

1. **Ollama not running**: `ollama serve`
2. **Models not pulled**: `ollama pull moondream && ollama pull llama3.2`
3. **Slow responses**: First request loads model into RAM (~10-30s), subsequent requests are fast
4. **Vision model errors**: Ensure image is valid base64, check Ollama logs

---

## Development Workflow

### Backend Development
```bash
# Run tests
cd socialMedia_backend
source venv/bin/activate
pytest app/tests/ -v

# Check code style
# (Add ruff/black if needed)
```

### Frontend Development
```bash
# Run tests
cd socialMedia_frontend
flutter test

# Analyze code
flutter analyze

# Format code
dart format .
```

### Database Management
```bash
# Reset database (development)
cd socialMedia_backend
rm dijital_gardrop.db
python -c "from app.core.database import init_db; init_db()"

# Run migrations
python migrate.py

# Check database
sqlite3 dijital_gardrop.db ".tables"
```

---

## Project Architecture Overview

### Backend (FastAPI)
- **Routers**: Auth, Posts, Feed, Follows, Users, Wardrobe, Search, Notifications, Analytics, Captions
- **Services**: Ollama caption service, FashionSigLIP classifier, Email service
- **Database**: SQLite with aiosqlite (async)
- **AI**: Moondream2 (vision), Llama3.2 (text) via Ollama

### Frontend (Flutter)
- **State Management**: Riverpod
- **Navigation**: GoRouter
- **API**: Centralized `ApiService` with Dio
- **Features**: Auth, Feed, Wardrobe, AI Stylist, Profile, Notifications, Analytics
- **Theme**: Custom `AppTheme` with violet/gold accents

---

## Useful Commands Quick Reference

```bash
# Backend
cd socialMedia_backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd socialMedia_frontend
flutter pub get
flutter run -d <device_id>

# Ollama
ollama serve
ollama pull moondream
ollama pull llama3.2
ollama list

# Database
cd socialMedia_backend
rm dijital_gardrop.db && python -c "from app.core.database import init_db; init_db()"

# Testing
cd socialMedia_backend && pytest -v
cd socialMedia_frontend && flutter test
```

---

## Environment-Specific Notes

### macOS (Apple Silicon)
- Use `pip install torch --index-url https://download.pytorch.org/whl/cpu` for CPU-only PyTorch
- Ollama runs natively on Apple Silicon

### Windows
- Use WSL2 for best compatibility
- Or run Ollama as Windows service
- Use `venv\Scripts\activate` for virtual environment

### Linux
- Standard setup works
- May need `sudo apt-get install python3-venv sqlite3` for dependencies

---

## Support

For issues:
1. Check the console logs in both backend and frontend
2. Verify Ollama is running and models are loaded
3. Check network connectivity between frontend and backend
4. Review the Swagger docs at http://localhost:8000/docs for API testing

---

*Last updated: 2026*
*Project: Dijital Gardrop - AI-Powered Social Fashion Platform*