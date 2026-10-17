# MailShield — Technical Design Specification (TDS)

## 1. System Architecture Overview

MailShield follows a multi-tier, modular architecture decoupling the user interface, API layer, business logic, persistence layer, and machine learning engine.

```
+-------------------------------------------------------------------+
|                        Client Tier                                |
|  +-----------------------------+  +----------------------------+  |
|  |   React / Vite Web UI       |  |  Electron Desktop Wrapper  |  |
|  |   (Tailwind CSS, TypeScript)|  |  (ContextIsolation, IPC)  |  |
|  +--------------+--------------+  +-------------+--------------+  |
+-----------------|-------------------------------|-----------------+
                  | Fetch API / JSON              | Local Spawn
                  v                               v
+-------------------------------------------------------------------+
|                        Backend API Tier                           |
|  +-------------------------------------------------------------+  |
|  |                     FastAPI Application                     |  |
|  |   - Router & Security Middleware (CORS, Defensive Headers)  |  |
|  |   - JWT Authentication & Role-Based Access Control (RBAC)   |  |
|  |   - Pydantic v2 Request/Response Contracts                  |  |
|  +--------------+-------------------------------+--------------+  |
+-----------------|-------------------------------|-----------------+
                  |                               |
                  v                               v
+----------------------------------+  +-----------------------------+
|        Persistence Tier          |  |     Machine Learning Tier   |
|  SQLAlchemy 2.0 ORM              |  |  scikit-learn 1.9.1         |
|  - SQLite (Desktop / Local)      |  |  - TF-IDF Vectorizer        |
|  - PostgreSQL (Cloud Persistent) |  |  - Logistic Regression (L2) |
|  - User Scoped History & Feedback|  |  - Multinomial Naive Bayes  |
|                                  |  |  - Linear SVM (Calibrated)  |
|                                  |  |  - Explainability Engine    |
+----------------------------------+  +-----------------------------+
```

---

## 2. Machine Learning Pipeline Design

### 2.1 Feature Representation
- **Text Normalization**: Custom preprocessor replaces URLs (`http_url`), email addresses (`email_addr`), currency symbols (`curr_symbol`), numeric values (`num_val`), and excessive punctuation marks (`multi_exclamation`).
- **TF-IDF Vectorization**:
  - `ngram_range = (1, 2)` (unigrams and bigrams).
  - `max_features = 5000` most informative tokens.
  - `min_df = 2` (eliminates idiosyncratic singletons).
  - `sublinear_tf = True` (applies $1 + \log(\text{tf})$ damping to high-frequency repetitions).
  - **Leakage Prevention Guarantee**: Fitted strictly on training set ($X_{\text{train}}$). Holdout validation ($X_{\text{val}}$) and test ($X_{\text{test}}$) sets are transformed strictly without updating the vocabulary.

### 2.2 Model Formulations & Calibration
1. **Logistic Regression (Primary Model)**:
   $$\text{logit}(x) = b + \sum_{i=1}^{V} w_i x_i$$
   $$P(\text{Spam} \mid x) = \sigma(\text{logit}(x)) = \frac{1}{1 + e^{-\text{logit}(x)}}$$
   - L2 Ridge regularization ($C=1.0$), L-BFGS solver.
   - Naturally produces calibrated class probabilities.

2. **Multinomial Naive Bayes**:
   $$\log P(\text{Spam} \mid x) \propto \log P(\text{Spam}) + \sum_{i=1}^{V} x_i \log P(w_i \mid \text{Spam})$$
   - Laplace smoothing ($\alpha = 0.1$).
   - Scores reported as posterior log-likelihood estimates with explicit `calibrated: false` flag.

3. **Linear Support Vector Machine (LinearSVC)**:
   - Raw decision function:
     $$f(x) = b + \sum_{i=1}^{V} w_i x_i$$
   - Probability calibration: 3-fold cross-validated Platt scaling (`CalibratedClassifierCV(..., method='sigmoid', cv=3)`) fit strictly on training fold data without test set exposure.
   - API supports both calibrated probabilities and raw margin signed distances.

### 2.3 Mathematical Explainability
For linear classifiers with learned weights $w$ and input TF-IDF vector $x$, the contribution of each active token $i$ is:
$$c_i = w_i \cdot x_i$$
- When $c_i > 0$, the feature supplies positive evidence pushing toward **Spam**.
- When $c_i < 0$, the feature supplies negative evidence pushing toward **Legitimate**.
- For Multinomial Naive Bayes, feature evidence reflects vocabulary log-likelihood differences:
  $$c_i = \log P(w_i \mid \text{Spam}) - \log P(w_i \mid \text{Ham})$$
  with `calibrated: false` and `calibrated_probability: null`.

### 2.4 Validation Threshold Simulator Architecture
To prevent test set snooping or target leakage:
1. `val_predictions_cache.json` stores validation split probabilities and ground truth labels ($X_{\text{val}}, y_{\text{val}}$) generated during model training.
2. The Model Lab endpoint (`GET /api/v1/models/threshold-metrics?model={name}&threshold={tau}`) calculates dynamic confusion matrices, F1, precision, recall, and false positive rates *only* against genuine validation data.
3. The independent test set ($X_{\text{test}}, y_{\text{test}}$) remains completely untouched and is evaluated solely during pipeline completion.

### 2.5 Strict Grouped Partitioning (`grouped_template_split`)
To evaluate out-of-template generalization, the pipeline implements `grouped_template_split`:
- Semantic clustering maps near-duplicate campaign templates (receipts, voucher giveaways, account compromises, sprint notes) into disjoint partitions.
- Zero group leakage constraint: `groups(train) ∩ groups(val) == ∅`, `groups(train) ∩ groups(test) == ∅`, and `groups(val) ∩ groups(test) == ∅`.
- Results are recorded in `ml/reports/strict_generalization_report.json` and compared side-by-side with standard in-distribution metrics.

---

## 3. Data Schema & Persistence

### 3.1 `analyses` Table
- `id` (VARCHAR(36), PK): UUID string.
- `user_id` (VARCHAR(36), FK `users.id`, nullable): Scopes records strictly to specific users.
- `timestamp` (DATETIME, Indexed): UTC timestamp of inference.
- `subject` (VARCHAR(512)): Email subject line.
- `email_hash` (VARCHAR(64), Indexed): SHA-256 hash of normalized content.
- `prediction` (VARCHAR(32)): 'Spam' or 'Legitimate'.
- `is_spam` (BOOLEAN): Boolean label.
- `score` (FLOAT): Calibrated probability or raw decision margin.
- `score_type` (VARCHAR(32)): 'probability' or 'decision_function'.
- `calibrated` (BOOLEAN): Calibration indicator.
- `confidence_level` (VARCHAR(32)): 'High', 'Medium', or 'Low'.
- `model_name` (VARCHAR(64)): Active model identifier.
- `threshold_used` (FLOAT): Applied decision threshold $\tau$.
- `processing_time_ms` (FLOAT): Latency in milliseconds.
- `feature_explanations_json` (TEXT): Serialized JSON of top positive/negative token attributions.
- `is_content_stored` (BOOLEAN): User privacy opt-in flag.
- `email_body` (TEXT, Nullable): Only persisted if `is_content_stored == True`.

---

## 4. Security & Defensive Controls

1. **User-Level Multi-Tenant Scoping**:
   - Analysis records, single-record lookups, single/bulk deletion, and CSV/JSON export downloads are strictly scoped by `user_id`. Requests attempting to access or modify records owned by other users or anonymous requests to authenticated records receive `HTTP 404 Not Found`.
2. **Authenticated Export Delivery**:
   - Frontend triggers file downloads via `fetch` with `Authorization: Bearer <token>` and transient Blob URLs, preventing session loss or credential leakage through raw anchor tags.
3. **CSV Formula Injection Mitigation**:
   - Any cell starting with `=`, `+`, `-`, `@`, `\t`, or `\r` is prepended with `'` during export.
4. **File Upload Restrictions**:
   - Strictly validates extensions (`.txt`, `.eml`).
   - Rejects payloads exceeding 5 MB (`HTTP 413 Content Too Large`).
   - Strips attachments during MIME tree traversal.
5. **Electron Desktop Isolation**:
   - `contextIsolation: true`
   - `nodeIntegration: false`
   - `sandbox: true`
   - Typed IPC bridge via `preload.ts`.
6. **Administrative Role-Based Authorization**:
   - `POST /api/v1/evaluation/run` is restricted to users with `role == 'admin'`.
