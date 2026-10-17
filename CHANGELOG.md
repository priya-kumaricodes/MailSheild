# Changelog

All notable changes to the MailShield platform will be documented in this file.

## [2.1.0] - 2026-10-15 — Gmail Integration & OAuth Security Architecture

### Gmail Integration Architecture
- **Google OAuth 2.0 PKCE & Minimal Read-Only Scopes**:
  - Request strictly `https://www.googleapis.com/auth/gmail.readonly` and `https://www.googleapis.com/auth/userinfo.email`.
  - Zero permissions requested for email sending, modification, composition, or deletion.
  - Native desktop Electron integration enforces RFC 7636 PKCE with `code_challenge_method=S256`.
- **Authenticated Symmetric Token Encryption at Rest (AES-256-GCM)**:
  - Tokens encrypted at rest using standard `cryptography.hazmat.primitives.ciphers.aead.AESGCM`.
  - 256-bit keys derived from `TOKEN_ENCRYPTION_KEY` via HKDF-SHA256 (`salt=b"mailshield-salt-v1"`).
  - 96-bit cryptographically secure random nonces per operation.
  - User ID bound into ciphertext authentication tag as Additional Authenticated Data (AAD) to prevent transposition attacks.
  - Versioned key payloads (`\x01`) supporting zero-downtime key rotation via `TOKEN_ENCRYPTION_KEY_FALLBACK`.
- **Server-Side Single-Use CSRF Protection**:
  - State tokens generated with 32-byte cryptographic entropy and tracked in dedicated `OAuthState` database table.
  - Enforces 10-minute validity window, single-use consumption, and identity binding. Replayed, expired, or cross-user state tokens are rejected with HTTP 400.
- **Separate, Consistent Web & Electron OAuth Flows**:
  - Web redirects via frontend callback with state and Bearer token validation.
  - Desktop redirects via loopback server (`http://127.0.0.1:{port}/api/v1/gmail/callback/desktop`), recovering initiating user without assuming browser authentication or issuing general session tokens.
  - Strict redirect URI whitelisting rejecting arbitrary or unapproved URIs.
- **Grant Revocation & Local Purge**:
  - Disconnect invokes Google's token revocation endpoint (`https://oauth2.googleapis.com/revoke`).
  - Local database credentials unconditionally purged even if remote revocation times out or fails, with accurate status reporting.
- **Strict Privacy Defaults**:
  - `store_content=False` is the strict default. Email bodies are processed purely in-memory and discarded immediately after classification.
  - Zero persistence of message bodies unless explicit user opt-in is provided.
  - Zero token or email body exposure in application logs, exceptions, or API responses.
- **Gmail Inbox Scanner UI (`GmailScannerView.tsx`)**:
  - Connection management card with real-time status and clear read-only scope guarantees.
  - Setup guidance banner with direct link to `docs/GMAIL_SETUP.md` when credentials are unconfigured.
  - Batch message inspector with configurable limits (5, 10, 25, 50 messages) and optional search query filters.
  - Explainable classification breakdown showing spam probability, phishing threat indicators, language identification, and predictive tokens.
- **Documentation**:
  - Added comprehensive `docs/GMAIL_SETUP.md` explaining Google Cloud Console setup, Testing mode limits (100 users, 7-day token expiry), CASA Tier 2 verification requirements for production, and loopback redirects.

## [2.0.0] - 2026-10-14 — Phase 1: Multilingual Spam Defense & Evaluation Lab

### Multilingual Spam Detection Architecture
- **Six Target Languages Supported**:
  - English (`en`), Hindi in Devanagari (`hi`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`), and Hinglish / Romanized Indic (`hinglish`).
- **Language Identification Engine (`mailshield_ml.language`)**:
  - Script detection for Unicode Devanagari, Tamil, Telugu, and Kannada.
  - Latin-script disambiguation between Hinglish and English using curated Indic lexicons (`STRONG_INDIC_LEXICON`) and morphological suffixes.
  - Disambiguated cross-linguistic homographs and false friends (`is`, `in`, `the`, `to`, `do`, `us`).
  - Explicit calibrated confidence and fallback to `unknown`/`uncertain` on short or ambiguous strings.
- **Decoupled Phishing Risk Engine (`mailshield_ml.phishing_risk`)**:
  - Independent heuristic security layer evaluating raw IP hostnames, URL shorteners, brand domain mismatches (SBI, HDFC, ICICI, etc.), credential harvesting paths (`/kyc`, `/login`), and coercive urgency lures across all target languages.
  - Output is strictly decoupled from the ML classifier's spam probability.
  - Legitimate bank OTP alerts and transactional statements receive defensive dampening, eliminating false alarms on authentic security notices.
- **Dual-Channel TF-IDF Feature Union (`mailshield_ml.multilingual_features`)**:
  - Combined word n-grams (1-2) with subword `char_wb` character n-grams (3-5), providing robust coverage against spelling variants, agglutinative morphology, and transliteration noise.
- **Curated Multilingual Benchmark Dataset (`ml/data/multilingual_corpus.json`)**:
  - 144 authentic-grade samples across 48 template groups (8 groups per language: 4 Ham, 4 Spam).
  - Strict zero-leakage grouped partitioning: Train (24 groups, 72 samples), Validation (12 groups, 36 samples), Holdout Test (12 groups, 36 samples).
  - Zero template group overlap verified across all split intersections.
  - Full provenance and licensing audit: `public_corpus` (Apache-2.0), `manually_curated` (CC-BY-4.0), `synthetic_template` (CC-BY-4.0).

### Evaluation Lab & Explainability UI
- **New Evaluation Lab Interface (`EvaluationLabView.tsx`)**:
  - Multi-tab auditing workspace: Performance & Confusion Matrix, Baseline Comparison, Error Inspection Drill-Down, Dataset Provenance & Integrity, and Interactive Multilingual Playground.
  - Independent model selectors (Linear SVM, Logistic Regression, Naive Bayes), dataset split selectors (Holdout Test, Validation), and language filters.
  - 2x2 confusion matrices with asymmetric cost parameters ($C_{FP}=5.0, C_{FN}=1.0$).
  - Side-by-side comparison illustrating multilingual model superiority over the English-only baseline on non-English holdout evaluation.

### Standalone Desktop Packaging (macOS ARM64)
- **Updated PyInstaller Standalone Executable**:
  - Bundled updated multilingual pipeline, language engine, phishing risk module, and `ml/artifacts/multilingual_*` models.
  - Bundled `ml/data/multilingual_corpus.json` into executable package.
  - Verified clean-environment startup without Python on PATH (`backend/tests/test_standalone_packaging.py`).
  - Packaged standalone `MailShield.app` and updated distributable zip archive `MailShield-2.0.0-mac-arm64.zip` (150.36 MB).

## [1.0.1] - 2026-10-14 — Standalone Desktop Packaging Fix

### Standalone Desktop Executable & Process Architecture
- **Bundled Standalone Python Backend Executable via PyInstaller**:
  - Packaged the complete FastAPI backend into a self-contained Mach-O arm64 binary (`mailshield_server`) located in `MailShield.app/Contents/Resources/backend_bin/`.
  - Bundled all Python dependencies (`uvicorn`, `fastapi`, `scikit-learn`, `scipy`, `numpy`, `sqlalchemy`, `pydantic`, `joblib`, `bcrypt`, `pyjwt`) and trained ML artifacts (`ml/artifacts/`) directly into the executable package.
  - Resolved model loading from PyInstaller internal directories (`_MEIPASS` and `_internal/ml/artifacts`) without requiring any repo-relative paths, system Python, or `.venv`.
- **Dynamic Port Selection & Zero Port Collisions**:
  - Implemented dynamic port allocation in Electron main process (`apps/desktop/src/main.ts`) using Node's `net.createServer().listen(0, '127.0.0.1')`.
  - Propagated the assigned port to the frontend renderer via `webPreferences.additionalArguments: ['--backend-port=${port}']`.
  - Updated `preload.ts` and `apps/web/src/services/api.ts` to expose `window.mailshieldDesktop.apiBase` dynamically.
- **Orphan Process Prevention & Process Supervision**:
  - Built an internal parent PID watchdog daemon thread in `backend/server_entry.py` monitoring `os.getppid()` that automatically terminates the backend cleanly if Electron exits or terminates unexpectedly.
  - Added graceful SIGTERM shutdown with 2-second timeout and SIGKILL fallback in Electron lifecycle handlers (`before-quit`, `window-all-closed`).
- **User Data Isolation & Persistence**:
  - Standalone desktop SQLite database is stored in standard macOS user data directory: `app.getPath('userData')/mailshield_desktop.db` (`~/Library/Application Support/mailshield-desktop/`).
- **Frontend Health Gating**:
  - Added `backendReady` state in `AnalyzerView.tsx`: email scanning and file imports are disabled with an informative connecting banner until `/api/v1/health` confirms `status: "healthy"` and `model_loaded: true`.
- **Automated Standalone Integration Test Suite**:
  - Added `backend/tests/test_standalone_packaging.py` validating that the standalone executable runs from a clean folder outside the repo with an isolated environment (`PATH=/usr/bin:/bin`, no Python), binds dynamically, initializes SQLite, passes health checks, performs inference, and cleanly terminates.
- **Platform Scope & Gatekeeper Guidance**:
  - Targeted Platform: macOS Apple Silicon (`darwin-arm64`). Explicitly documented that Windows, Intel Mac (`darwin-x64`), and Linux builds are not included in this release archive.
  - Provided guidance for macOS ad-hoc code signing and Gatekeeper quarantine (`xattr -cr /Applications/MailShield.app`).
- **Release Artifacts**:
  - Standalone Application Bundle: `apps/desktop/dist/MailShield.app`
  - Distributable Compressed Archive: `apps/desktop/dist/MailShield-1.0.1-mac-arm64.zip` (149.84 MB)

## [1.0.0] - 2026-10-14 — Final ML Improvement & Release Audit

### Generalization & ML Pipeline Improvements
- **Fixed Currency Token ($) False Positive Bug on Legitimate Receipts**:
  - Balanced the training split by introducing legitimate cloud infrastructure invoices (`grp_ham_invoice_cloud`) and bank transaction alerts (`grp_ham_banking_alert`) with currency values and taxes.
  - Eliminated the artificial correlation between currency symbols (`$`, `USD`) and spam in training.
  - In Logistic Regression, false positive rate on unseen retail store receipts plummeted from **85.7% (18 FPs) to 0.0% (0 FPs)** on the strict holdout test set.
  - In Linear SVM, false positive rate dropped from **95.2% to 5.56% (1 FP)**.
- **Dataset Expansion & Disambiguation**:
  - Expanded benchmark corpus to **248 records (124 Legitimate, 124 Spam)** with 0 duplicates.
  - Organized into 16 distinct template families (8 Ham, 8 Spam) and 24 base unique sample groups.
  - Added parametric slot randomized IDs (`{num}`, `{ref}`) ensuring zero hash collisions.
  - Explicitly demarcated synthetic template clusters (`provenance: synthetic_template`) from authentic historical public corpus samples.
- **Strict Out-of-Template Group Partitioning (`grouped_template_split`)**:
  - Programmatically enforced zero group overlap across partitions:
    $\text{groups}(\text{train}) \cap \text{groups}(\text{val}) = \emptyset$,
    $\text{groups}(\text{train}) \cap \text{groups}(\text{test}) = \emptyset$,
    $\text{groups}(\text{val}) \cap \text{groups}(\text{test}) = \emptyset$.
  - Preserved standard random stratified split for comparative baseline auditing.
- **Cost-Sensitive Threshold Selection**:
  - Implemented objective utility function: $\text{Utility}(\tau) = \text{TP}(\tau) - 5 \times \text{FP}(\tau) - \text{FN}(\tau)$ subject to validation $\text{FPR}(\tau) \le 0.05$.
  - Implemented false-positive-safe tie breaking: when multiple thresholds achieve maximal utility on validation data, ties break toward $\tau = 0.50+$ to maximize the margin of safety against false positives.
  - If the FPR constraint cannot be satisfied, the pipeline records the constraint violation explicitly in `metadata.json` rather than silently relaxing constraints.

### Test Automation & Quality Matrix
- **55 Automated Pytest Tests (100% Passing)**:
  - Added and expanded `ml/tests/test_transactional_generalization.py` (10 test cases) covering retail receipts, cloud invoices, bank alerts, flight confirmations, fake Geek Squad invoices, USPS delivery scams, explainability additivity, unseen voucher scam detection, multilingual Hindi workplace ham, and strict holdout quality gates.
  - Verified 12 authentication, file security, history, export, and desktop offline tests in `backend/tests/`.
  - Verified 21 ML preprocessing, leakage prevention, explainability, and calibration tests in `ml/tests/`.
- **23 Frontend Vitest Tests (100% Passing)**:
  - 5 comprehensive component suites covering Analyzer, History, Model Lab, Settings, and App navigation.
- **10-Stage End-to-End User Journey Audit (100% Passing)**:
  - Verified registration, JWT auth, text & file prediction, explainability additivity, history CRUD, privacy opt-out (`store_content=False` NULL body verified in SQLite), multi-model selection, CSV/JSON export, multi-tenant isolation, and input validation without mocking.
- **Packaging & Desktop Distribution Status**:
  - Web production bundle (`apps/web/dist`) compiled cleanly via Vite (`tsc -b && vite build`).
  - Desktop TypeScript bundle (`apps/desktop/dist`) compiled cleanly via `tsc`.
  - Electron prebuilt runtime (v34.5.8 darwin-arm64) downloaded and extracted preserving macOS framework symlinks.
  - Packaged standalone macOS application bundle: `apps/desktop/dist/MailShield.app`.
  - Created distributable compressed archive: `apps/desktop/dist/MailShield-1.0.0-mac-arm64.zip` (93.05 MB).
  - Ad-hoc code signed and verified via `codesign -v`.
  - Verified supervised local backend execution, SQLite initialization (`mailshield_desktop.db`), and health check (`GET /api/v1/health` 200 OK).
  - Final release status: **Ready for Release (v1.0.0)**.
