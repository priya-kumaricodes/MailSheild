# MailShield — Test Plan & Quality Assurance Matrix

## 1. Automated Test Suites & Coverage

MailShield uses pytest for backend/ML validation and Vitest + React Testing Library for frontend component validation.

| Test Category | Suite File | Scenarios Covered | Passing Status |
|---|---|---|---|
| **Language Identification** | `ml/tests/test_language.py` | Unicode script analysis (Devanagari, Tamil, Telugu, Kannada), Latin Hinglish vs English disambiguation without cross-linguistic false friends (`is`, `in`, `the`), calibrated confidence, explicit unknown/uncertain fallback, short text, emoji, URLs, and mixed-language detection. | 13/13 Passed |
| **Decoupled Phishing Risk** | `ml/tests/test_phishing_risk.py` | Decoupled heuristic analysis independent of spam probability, IP host detection, URL shortener detection, financial brand domain spoofing (SBI, HDFC, ICICI), credential harvesting paths, multilingual urgency lures, and defensive dampening protecting legitimate bank OTPs. | 6/6 Passed |
| **Multilingual Features** | `ml/tests/test_multilingual_pipeline.py` | Dual-channel FeatureUnion (`w:` word n-grams 1-2, `c:` subword char_wb 3-5), vocab limit enforcement, save/load joblib serialization, transform isolation. | 5/5 Passed |
| **Multilingual Models & Splits** | `ml/tests/test_multilingual_models.py` | Zero template-group leakage across Train/Val/Test partitions across all 6 languages, artifact inference on Hindi spam and English ham. | 3/3 Passed |
| **Dataset Preprocessing** | `ml/tests/test_dataset.py` | Strip HTML, Unicode/Hindi normalization, deterministic content hash, duplicate elimination, stratified 70/15/15 split, RFC 822 MIME parser. | 6/6 Passed |
| **Leakage Prevention** | `ml/tests/test_leakage.py` | Unseen test vocabulary not added during transform, unfitted transform raises RuntimeError, stratified zero-hash overlap, grouped template split zero-group overlap. | 4/4 Passed |
| **Feature Explainability** | `ml/tests/test_explainability.py` | Additive logit math consistency ($b + \sum w_i x_i = \text{logit}$), Linear SVM margin attribution, Multinomial NB log-likelihood evidence, unicode/repeated tokens, empty document handling. | 5/5 Passed |
| **Model Calibration** | `ml/tests/test_models.py` | Logistic Regression calibrated probabilities, Naive Bayes uncalibrated log-likelihood flag, Linear SVM calibrated vs raw margin distance, threshold sensitivity, artifact persistence, Brier score loss. | 6/6 Passed |
| **Transactional Generalization & Regression** | `ml/tests/test_transactional_generalization.py` | Retail store purchase receipts classified as Ham without false positives; cloud invoices classified as Ham; bank alerts classified as Ham; flight reservations classified as Ham; fake Geek Squad $499 auto-renewal invoice phish detected as Spam; parcel redelivery fee scam detected as Spam; additive logit decomposition verified ($\sum w_i x_i + b = \text{score}$); unseen voucher scam detection; multilingual Hindi workplace email classified as Ham; strict holdout release gate verified. | 10/10 Passed |
| **Evaluation Lab API** | `backend/tests/test_evaluation_api.py` | Endpoints for `/languages`, `/metrics`, `/confusion-matrix`, `/errors`, `/compare`, `/provenance`, `/demo-samples`, auth scoping, and 401 unauthenticated enforcement. | 7/7 Passed |
| **Authentication & RBAC** | `backend/tests/test_auth_and_scoping.py` | Registration, login, JWT validation, cross-user history isolation (User 2 cannot see User 1 records), cross-user bulk delete prevention, invalid/expired token rejection. | 4/4 Passed |
| **File Upload Security** | `backend/tests/test_file_upload_security.py` | Valid `.eml` and `.txt` parsing, rejection of unauthorized extensions (`.exe`), rejection of oversized files (>5MB). | 4/4 Passed |
| **History & Export** | `backend/tests/test_history_and_export.py` | History CRUD, bulk deletion, CSV formula injection defense (prepends `'`), feedback submission, user-scoped CSV/JSON export, search and label filters. | 6/6 Passed |
| **Health Diagnostics** | `backend/tests/test_health.py` | Reports backend, database, model availability, active models. | 1/1 Passed |
| **Model Lab & Benchmarks**| `backend/tests/test_models_and_evaluation.py` | Overview endpoint, dynamic validation threshold simulator, admin-only benchmark execution (403 for standard users), invalid model name validation. | 5/5 Passed |
| **Prediction Endpoints** | `backend/tests/test_predict_api.py` | Legitimate email prediction, spam email prediction, empty body rejection, multi-model selection (NB, SVM). | 4/4 Passed |
| **Desktop Offline Mode** | `backend/tests/test_desktop_offline.py` | Offline inference, SQLite persistence, transparent desktop user profile. | 1/1 Passed |
| **Desktop Standalone Packaging** | `backend/tests/test_standalone_packaging.py` | Packaged native executable runs in clean scrubbed environment with zero Python on `PATH`, executes database migration, loads ML models, and passes health/prediction requests. | 2/2 Passed |
| **Frontend Web App** | `apps/web/src/test/` | 6 test suites: `App.test.tsx`, `AnalyzerView.test.tsx`, `HistoryView.test.tsx`, `ModelLabView.test.tsx`, `SettingsView.test.tsx`, `EvaluationLabView.test.tsx`. | 29/29 Passed |
| **End-to-End User Journey** | `scratch/verify_e2e_journey.py` | 10 stages: registration, login, text & file prediction, explainability verification, history persistence & search, privacy opt-out (`store_content=False` NULL body check in SQLite), model & threshold switching, CSV/JSON export, multi-tenant isolation, error boundaries. | 10/10 Passed |

---

## 2. Test Execution Commands

```bash
# Run all Python backend and ML tests (85 standard unit & integration tests)
PYTHONPATH=ml/src:backend/src .venv/bin/pytest -v ml/tests backend/tests -m "not standalone"

# Run standalone desktop packaging verification test (scrubbed PATH, zero Python)
PYTHONPATH=ml/src:backend/src .venv/bin/pytest -v backend/tests/test_standalone_packaging.py

# Run linting check
.venv/bin/ruff check backend ml

# Run frontend unit tests (29 tests across 6 suites)
npm --prefix apps/web test -- --run

# Run frontend production build
npm --prefix apps/web run build

# Run desktop standalone packaging
npm --prefix apps/desktop run package
```

---

## 3. Verified Verification Results
- **Pytest (Standard Suite)**: 85 passed, 0 failures in 1.94s.
- **Pytest (Standalone Packaging)**: 2 passed, 0 failures in 3.18s (scrubbed environment with empty `PATH`).
- **Total Pytest Count**: 87 passed, 0 failures.
- **Vitest**: 29 passed, 0 failures across 6 suites in 1.42s.
- **Ruff**: 0 errors, all checks clean.
- **Web Build**: Clean compilation (`tsc -b && vite build`), zero warnings/errors.
- **Desktop Standalone Bundle**: Packaged into `apps/desktop/dist/MailShield.app` and `MailShield-2.0.0-mac-arm64.zip` (150.36 MB, signed and verified standalone).
- **E2E Journey Audit**: All 10 stages passed with zero mock data.

