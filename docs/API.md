# MailShield — REST API Documentation (v1)

Base URL: `/api/v1`

All responses are formatted in JSON unless explicitly noted otherwise.

---

## 1. System Health & Diagnostics

### `GET /api/v1/health`
Checks runtime availability of FastAPI backend, database connection, and ML model in-memory loading.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "backend": true,
  "database": true,
  "model_loaded": true,
  "active_models": [
    "logistic_regression",
    "naive_bayes",
    "linear_svm",
    "multilingual_logistic_regression",
    "multilingual_naive_bayes",
    "multilingual_linear_svm"
  ],
  "environment": "development",
  "mode": "standard",
  "version": "2.1.0"
}
```

---

## 2. Authentication & User Management

### `POST /api/v1/auth/register`
Create a new user account.

**Request Body**:
```json
{
  "username": "analyst1",
  "email": "analyst1@corp.local",
  "password": "StrongPassword123!"
}
```
**Response (201 Created)**: Returns created `UserResponse`.

### `POST /api/v1/auth/login`
Authenticate with credentials and obtain a signed JWT Bearer token.

**Request Body**:
```json
{
  "username": "analyst1",
  "password": "StrongPassword123!"
}
```
**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer",
  "user": {
    "id": "c76d29b1-5e87-43cf-...",
    "username": "analyst1",
    "email": "analyst1@corp.local",
    "role": "user",
    "created_at": "2026-10-14T04:30:00Z"
  }
}
```

---

## 3. Email Prediction & Explainability

### `POST /api/v1/predict`
Predict classification and compute token-level feature attributions.

**Request Body**:
```json
{
  "subject": "Urgent: Verify Your Account",
  "body": "Your bank account has been suspended. Please confirm your credentials immediately.",
  "model_name": "logistic_regression",
  "threshold": 0.5,
  "store_content": false
}
```

**Response (200 OK)**:
```json
{
  "id": "e98fb120-6d2c-47ea-...",
  "prediction": "Spam",
  "is_spam": true,
  "score": 0.9412,
  "score_type": "probability",
  "calibrated": true,
  "raw_decision_score": 2.7725,
  "confidence_level": "High",
  "model_name": "logistic_regression",
  "model_version": "1.0.0",
  "threshold_used": 0.5,
  "processing_time_ms": 11.45,
  "explanations": {
    "model_name": "logistic_regression",
    "intercept": -0.152,
    "net_decision_score": 2.7725,
    "calibrated_probability": 0.9412,
    "top_spam_features": [
      {
        "token": "account",
        "weight": 1.452,
        "tfidf_value": 0.412,
        "contribution": 0.598,
        "direction": "Spam",
        "relative_impact": 21.5,
        "description": "'account' has positive association with spam patterns..."
      }
    ],
    "top_legitimate_features": [],
    "all_contributions": [],
    "attribution_notes": "Feature contributions represent linear mathematical attribution on log-odds..."
  },
  "created_at": "2026-10-14T04:35:00Z"
}
```

### `POST /api/v1/predict/file`
Multipart upload supporting RFC 822 `.eml` and plain `.txt` files up to 5MB.

---

## 4. History Management

### `GET /api/v1/history`
Query paginated analysis history. Filtered strictly by current authenticated user.

**Query Parameters**:
- `page` (int, default: 1)
- `page_size` (int, default: 10, max: 100)
- `search` (string, optional)
- `label` (string, optional: "Spam" | "Legitimate")
- `sort_by` (string, default: "timestamp")
- `sort_order` (string, default: "desc")

### `GET /api/v1/history/{id}`
Retrieve complete detail and feature attributions for a single analysis record.

### `DELETE /api/v1/history/{id}`
Delete a single record owned by the authenticated user.

### `DELETE /api/v1/history`
Bulk delete records owned by the authenticated user via JSON body: `{"ids": ["id1", "id2"]}`.

---

## 5. Model Lab & Benchmarking

### `GET /api/v1/models`
Retrieve specifications, version, vocabulary size, and independent test metrics for all models.

### `GET /api/v1/models/threshold-metrics`
Dynamically evaluate genuine validation set predictions at a selected threshold $\tau$.

**Query Parameters**:
- `model` (string, e.g. "logistic_regression")
- `threshold` (float, e.g. 0.35)

**Response (200 OK)**:
```json
{
  "model_name": "logistic_regression",
  "current_metrics": {
    "threshold": 0.35,
    "accuracy": 0.9643,
    "precision": 0.9333,
    "recall": 1.0,
    "f1_score": 0.9655,
    "false_positive_rate": 0.0714,
    "confusion_matrix": [[13, 1], [0, 14]]
  },
  "sweep_curve": [...]
}
```

### `POST /api/v1/evaluation/run`
Re-runs benchmark across models on independent test dataset. **Restricted to users with `role: "admin"`**.

---

## 6. Feedback & Reports Export

### `POST /api/v1/feedback`
Submit user review or label corrections for an analysis record.

### `GET /api/v1/reports/export`
Export analysis history in CSV or JSON format. Protects against CSV formula injection.
- Format parameter: `?format=csv` or `?format=json`.
