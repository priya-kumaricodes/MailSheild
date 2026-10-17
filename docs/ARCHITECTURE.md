# MailShield — Monorepo Architecture & Sequence Workflows

## 1. Monorepo Organization

```text
MailShield/
├── apps/
│   ├── web/                    # React 18 + Vite + TypeScript + Tailwind CSS
│   │   ├── src/
│   │   │   ├── components/     # Header, Dashboard, Analyzer, History, ModelLab, Settings
│   │   │   ├── services/       # Typed API client
│   │   │   ├── types/          # Contract interfaces
│   │   │   └── App.tsx         # Tab router and root view
│   │   └── tests/              # Vitest + RTL component tests
│   └── desktop/                # Electron offline desktop runtime
│       └── src/
│           ├── main.ts         # Process supervision, backend lifecycle, window controls
│           └── preload.ts      # Secure contextBridge API
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # predict, history, models, evaluation, auth, feedback, reports
│   │   ├── core/               # config, security, logging
│   │   ├── db/                 # SQLAlchemy engine, sessionmaker, base
│   │   ├── models/             # User, AnalysisRecord, EvaluationRun, UserFeedback
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   ├── services/           # PredictionService, HistoryService, EvaluationService, AuthService
│   │   └── main.py             # FastAPI application and middleware
│   └── tests/                  # Pytest integration and contract tests
├── ml/
│   ├── artifacts/              # Serialized .joblib models and metadata.json
│   ├── data/                   # Seed corpus and dataset splits
│   ├── reports/                # Evaluation reports
│   ├── src/mailshield_ml/      # dataset, features, models, explainability, evaluation, pipeline
│   └── tests/                  # Pytest ML leakage, calibration, and math tests
├── docs/                       # 12 living engineering documentation files
├── scripts/                    # fetch_corpus.py, generate_seed_corpus.py
├── pyproject.toml              # Ruff and Pytest configuration
├── pytest.ini
└── README.md
```

---

## 2. Sequence Diagrams

### 2.1 Online Email Prediction & Feature Attribution

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Web as React Web UI
    participant API as FastAPI Backend
    participant ML as PredictionService / ML
    participant DB as SQLite / PostgreSQL

    User->>Web: Enter Subject & Body (or drag .eml)
    User->>Web: Click "Analyze Email"
    Web->>API: POST /api/v1/predict (JSON or Multipart)
    API->>ML: Extract Text & Compute SHA-256 Hash
    ML->>ML: Transform via TF-IDF Vectorizer
    ML->>ML: Run Classifier predict_single()
    ML->>ML: Compute Exact Token Contributions (w_i * x_i)
    ML->>DB: Save AnalysisRecord (Metadata + Hash + Attributions)
    DB-->>ML: Persisted ID
    ML-->>API: PredictResponse with Scores & Top Tokens
    API-->>Web: HTTP 200 OK (JSON)
    Web->>User: Display Prediction Card, Confidence Meter & Token Attribution Bars
```

### 2.2 Dynamic Validation Threshold Simulation (Model Lab)

```mermaid
sequenceDiagram
    autonumber
    actor Analyst
    participant Web as Model Lab UI
    participant API as FastAPI Backend
    participant Eval as EvaluationService
    participant Cache as val_predictions_cache.json

    Analyst->>Web: Move Threshold Slider (&tau; = 0.35)
    Web->>API: GET /api/v1/models/threshold-metrics?model=logistic_regression&threshold=0.35
    API->>Eval: simulate_threshold("logistic_regression", 0.35)
    Eval->>Cache: Read genuine validation scores & ground truth labels
    Eval->>Eval: Compute TP, FP, TN, FN at &tau;
    Eval->>Eval: Compute Precision, Recall, F1, and False Positive Rate
    Eval-->>API: ThresholdSimulationResponse
    API-->>Web: HTTP 200 OK (JSON)
    Web->>Analyst: Update Confusion Matrix Heatmap & Performance Gauges in Real Time
```

### 2.3 Electron Desktop Offline Supervision

```mermaid
sequenceDiagram
    autonumber
    participant Electron as Electron Main (main.ts)
    participant Python as Local Python Backend (.venv)
    participant Bridge as Preload Bridge (preload.ts)
    participant Renderer as Desktop Window (Renderer)

    Electron->>Python: Spawn child process (.venv/bin/python -m uvicorn)
    Note over Electron,Python: Passes MAILSHIELD_MODE=desktop & local SQLite DB
    loop Health Check Polling
        Electron->>Python: GET http://127.0.0.1:8000/api/v1/health
        Python-->>Electron: HTTP 200 (healthy)
    end
    Electron->>Renderer: Load built web application (dist/index.html)
    Renderer->>Bridge: Query system status via window.mailshieldDesktop
    Bridge-->>Renderer: Return platform and offline status
    Note over Renderer,Python: All predictions execute locally on local models
    Electron->>Python: SIGTERM on app before-quit (Clean Shutdown)
```
