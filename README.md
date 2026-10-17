# MailShield — Explainable Spam Classification Platform

[![CI Pipeline](https://github.com/mailshield/mailshield/actions/workflows/ci.yml/badge.svg)](https://github.com/mailshield/mailshield)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![React: 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688.svg)](https://fastapi.tiangolo.com/)

**MailShield 2.1** is an explainable machine learning spam classification platform and security analysis suite. It supports direct Gmail inbox integration via Google OAuth 2.0 PKCE with strict read-only access, multilingual email classification across English, Hindi, Tamil, Telugu, Kannada, and Hinglish, true linear explainability ($w_i \cdot x_i$), a decoupled heuristic phishing risk engine, and an Evaluation Lab for transparent empirical benchmarking with zero template-group leakage.

---

## Key Features

1. **Gmail Inbox Scanner (New in v2.1)**:
   - Connect Gmail directly using Google OAuth 2.0 with minimal read-only scopes (`gmail.readonly`, `userinfo.email`).
   - RFC 7636 PKCE (S256) for native desktop Electron flows with single-use CSRF state tokens.
   - Tokens encrypted at rest using authenticated symmetric AES-256-GCM with HKDF key derivation and AAD identity binding.
   - Strict privacy-first defaults: email bodies are processed purely in-memory and discarded immediately after classification unless explicitly opted in.
   - Batch inbox scanning (5, 10, 25, 50 messages) with explainable classification breakdown.
2. **Multilingual Spam Detection**:
   - Robust classification across 6 target languages: **English (`en`)**, **Hindi in Devanagari (`hi`)**, **Tamil (`ta`)**, **Telugu (`te`)**, **Kannada (`kn`)**, and **Hinglish / Romanized Indic (`hinglish`)**.
   - Dual-channel `FeatureUnion` combining word n-grams (1-2) with subword `char_wb` (3-5) to handle spelling mutations, compounding, and transliteration noise.
2. **Language Identification Engine**:
   - Unicode script analysis (Devanagari, Tamil, Telugu, Kannada) and Latin-script disambiguation between Hinglish and English using curated Indic lexicons free of cross-linguistic false friends.
   - Calibrated confidence reporting and explicit fallbacks for short, malformed, or ambiguous messages.
3. **Decoupled Phishing Risk Engine**:
   - Independent security heuristic layer detecting IP hostnames, URL shorteners, spoofed financial domains (SBI, HDFC, ICICI, etc.), credential harvesting paths (`/kyc`, `/login`), and multilingual urgency lures.
   - Fully decoupled from the ML classifier's probability score, preventing false positives on authentic banking OTP alerts and transaction statements.
4. **Interactive Evaluation Lab**:
   - In-depth empirical benchmarking UI with model selectors, untouched holdout partition inspection, per-language filters, 2x2 confusion matrices, false positive/negative drill-downs, dataset provenance audits, and interactive testing playground.
5. **Email & File Analysis**:
   - Paste subject, sender, and body text, or drag and drop `.eml` (RFC 822) and `.txt` files up to 5MB.
   - Pre-loaded benchmark samples for 1-click testing (phishing, financial scams, corporate meetings, travel receipts, Indic/Hinglish banking alerts).
6. **True Explainability & Calibration**:
   - Exact additive feature contributions ($w_i \cdot x_i$) for Logistic Regression, Naive Bayes, and Linear SVM.
   - Transparent distinction between calibrated posterior probabilities and raw decision margin scores.
7. **Model Lab & Dynamic Validation Threshold Simulator**:
   - Move the decision threshold slider ($\tau \in [0.05, 0.95]$) to evaluate live impact on False Positive Rate, Recall, and Confusion Matrices computed from genuine validation predictions.
8. **Analysis History & Audit Export**:
   - Multi-filter search, pagination, sorting, single deletion, and bulk deletion.
   - Formula-injection protected CSV and JSON exports.
9. **Privacy by Design**:
   - Email bodies are not permanently persisted by default; only one-way SHA-256 hashes and token attributions are saved unless the user explicitly opts in.
10. **Dual Online & Desktop Offline Modes**:
    - Runs as a scalable web application (FastAPI + React) or as an Electron desktop application operating completely offline with local SQLite storage.

---

## Technology Stack

- **Frontend**: React 18, TypeScript 5, Vite 6, Tailwind CSS 3, Lucide Icons, Vitest, React Testing Library.
- **Backend**: Python 3.14 / 3.11+, FastAPI 0.143, Pydantic v2, SQLAlchemy 2.0, Uvicorn, Pytest, PyJWT, bcrypt.
- **Machine Learning**: scikit-learn 1.9, pandas 3.0, NumPy 2.5, TF-IDF vectorization, Logistic Regression (L2), Multinomial Naive Bayes, Linear Support Vector Machine (Platt Calibrated), Joblib.
- **Desktop**: Electron 34, secure context isolation, supervised local backend child process.

---

## Quickstart & Installation

### Prerequisites
- Python 3.11 or newer (Python 3.14.7 verified)
- Node.js v20+ and npm

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/mailshield/mailshield.git
cd mailshield

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend and ML dependencies
pip install scikit-learn pandas numpy scipy joblib fastapi uvicorn pydantic pydantic-settings sqlalchemy python-multipart pyjwt bcrypt httpx pytest pytest-asyncio ruff

# Install frontend dependencies
npm --prefix apps/web install

# Install desktop dependencies
npm --prefix apps/desktop install
```

### 2. Generate Corpus & Train ML Pipeline
```bash
# Generate verified benchmark corpus
python3 scripts/generate_seed_corpus.py

# Execute ML training, validation calibration, and artifact serialization
PYTHONPATH=ml/src python3 ml/src/mailshield_ml/pipeline.py
```

### 3. Start the Backend API Server
```bash
# Start FastAPI backend (port 8000)
source .venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Interactive OpenAPI documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 4. Start the React Web Application
```bash
# Start Vite development server (port 5173)
npm --prefix apps/web run dev
```
Open your browser at [http://localhost:5173](http://localhost:5173).

### 5. Launch & Package the Offline Desktop Application
```bash
# Build web bundle and desktop TypeScript
npm --prefix apps/web run build
npm --prefix apps/desktop run build

# Launch Electron directly in development/preview mode
npm --prefix apps/desktop start

# Package standalone macOS application bundle (.app) and distributable zip
npm --prefix apps/desktop run package
# Outputs:
#   apps/desktop/dist/MailShield.app
#   apps/desktop/dist/MailShield-2.1.0-mac-arm64.zip (151.69 MB)
```

### Standalone Desktop Packaging & Platform Notes

The Electron desktop application bundles a **native compiled Python backend executable** built with PyInstaller:
- **Zero External Python Dependency**: Does not require system Python, Python 3.11+, `.venv`, or pip on the target machine.
- **Dynamic Port Selection**: Electron dynamically allocates an ephemeral port via Node's `net.createServer()` and passes it to the frontend via `--backend-port`, eliminating port collisions.
- **Process Supervision**: Electron launches `backend_bin/mailshield_server` inside `MailShield.app/Contents/Resources`. A parent PID watchdog thread terminates the backend immediately if Electron quits, preventing orphaned processes.
- **Platform Target**: This release is built and verified specifically for **macOS Apple Silicon (`darwin-arm64`)**. Windows, Intel Mac (`darwin-x64`), and Linux builds are not included in this release archive.
- **macOS Gatekeeper / Ad-Hoc Signing**: The application bundle is signed ad-hoc (`codesign --force --deep --sign -`). When extracting on macOS, if Gatekeeper quarantines untrusted downloaded applications, clear the quarantine attribute:
  ```bash
  xattr -cr /path/to/MailShield.app
  ```

---

## Automated Test Verification

All unit, API contract, security, multilingual generalization, and desktop standalone packaging tests are verified:

```bash
# Run complete Python test suite (87 tests)
.venv/bin/pytest -v

# Run linting check
.venv/bin/ruff check .

# Run frontend Vitest suite (29 tests across 6 suites)
npm --prefix apps/web test

# Test frontend production build
npm --prefix apps/web run build

# Test desktop production build and standalone packaging
npm --prefix apps/desktop run package
```

---

## Documentation Suite

Comprehensive technical and operational specifications are available in the `docs/` directory:
- [PDS.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/PDS.md) — Product Definition Specification
- [TDS.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/TDS.md) — Technical Design Specification
- [ARCHITECTURE.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/ARCHITECTURE.md) — Monorepo Architecture & Sequence Diagrams
- [API.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/API.md) — REST API Documentation
- [DATA_DICTIONARY.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/DATA_DICTIONARY.md) — Database Schema & Data Dictionary
- [MODEL_CARD.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/MODEL_CARD.md) — Machine Learning Model Cards
- [DATASET_CARD.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/DATASET_CARD.md) — Dataset Provenance & Licensing Terms
- [PRIVACY.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/PRIVACY.md) — Privacy & Non-Persistence Policies
- [THREAT_MODEL.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/THREAT_MODEL.md) — Security Threat Model (STRIDE)
- [TEST_PLAN.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/TEST_PLAN.md) — Test Plan & Quality Assurance Matrix
- [USER_GUIDE.md](file:///Users/anuragtiwari/Documents/antigravity/zealous-mendeleev/docs/USER_GUIDE.md) — User & Security Analyst Guide

---

## License

This project is licensed under the MIT License. See LICENSE for details.
Corpus emails are distributed for spam-filtering research and testing purposes.
