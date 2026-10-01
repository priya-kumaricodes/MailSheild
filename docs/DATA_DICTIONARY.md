# MailShield — Database Data Dictionary

The application supports both **SQLite** (for single-user offline desktop environments) and **PostgreSQL** (for concurrent online server environments) using SQLAlchemy 2.0 ORM.

---

## 1. Table: `users`
Stores user identities, credentials, and authorization roles.

| Column | Type | Nullable | Constraints / Index | Description |
|---|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key | UUID identifier |
| `username` | VARCHAR(64) | No | Unique, Indexed | Unique login handle |
| `email` | VARCHAR(255) | No | Unique, Indexed | Contact email address |
| `hashed_password`| VARCHAR(255) | No | - | Salted bcrypt password hash |
| `role` | VARCHAR(32) | No | Default: 'user' | Access role: `'user'` or `'admin'` |
| `created_at` | DATETIME | No | Default: UTC now | Account creation timestamp |

---

## 2. Table: `analyses`
Stores historical prediction records, confidence metrics, and serialized feature attributions.

| Column | Type | Nullable | Constraints / Index | Description |
|---|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key | UUID analysis identifier |
| `user_id` | VARCHAR(36) | Yes | FK `users.id` (CASCADE), Indexed | Owner user ID |
| `timestamp` | DATETIME | No | Indexed, UTC | Time prediction was generated |
| `subject` | VARCHAR(512) | No | Default: '' | Parsed email subject line |
| `email_hash` | VARCHAR(64) | No | Indexed | SHA-256 hash of normalized text |
| `prediction` | VARCHAR(32) | No | - | Classification: `'Spam'` or `'Legitimate'` |
| `is_spam` | BOOLEAN | No | - | Boolean flag (True = Spam) |
| `score` | FLOAT | No | - | Calibrated probability [0, 1] or margin |
| `score_type` | VARCHAR(32) | No | Default: 'probability'| `'probability'` or `'decision_function'` |
| `calibrated` | BOOLEAN | No | Default: True | Flag indicating Platt/sigmoid calibration |
| `confidence_level` | VARCHAR(32) | No | Default: 'Medium' | Categorical tier: `'High'`, `'Medium'`, `'Low'`|
| `model_name` | VARCHAR(64) | No | - | Name of classifier used |
| `model_version`| VARCHAR(32) | No | Default: '1.0.0' | Serialized model artifact version |
| `threshold_used`| FLOAT | No | Default: 0.5 | Decision threshold $\tau$ applied |
| `processing_time_ms`| FLOAT | No | - | Pipeline execution latency in ms |
| `feature_explanations_json`| TEXT | No | Default: '{}' | Serialized JSON of top token attributions |
| `is_content_stored`| BOOLEAN | No | Default: False | Privacy opt-in flag for body persistence |
| `email_body` | TEXT | Yes | - | Raw body text (NULL unless opt-in enabled)|

---

## 3. Table: `evaluation_runs`
Stores benchmark execution records on independent test datasets.

| Column | Type | Nullable | Constraints / Index | Description |
|---|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key | UUID benchmark run identifier |
| `timestamp` | DATETIME | No | Indexed, UTC | Run timestamp |
| `model_name` | VARCHAR(64) | No | - | Identifier of model evaluated |
| `dataset_name` | VARCHAR(64) | No | Default: 'test' | Dataset split evaluated |
| `num_samples` | INTEGER | No | - | Number of samples in test split |
| `accuracy` | FLOAT | No | - | Accuracy $(TP+TN)/(TP+FP+TN+FN)$ |
| `precision` | FLOAT | No | - | Precision $TP/(TP+FP)$ |
| `recall` | FLOAT | No | - | Recall $TP/(TP+FN)$ |
| `f1_score` | FLOAT | No | - | Harmonic mean of precision & recall |
| `false_positive_rate` | FLOAT | No | - | False Positive Rate $FP/(FP+TN)$ |
| `pr_auc` | FLOAT | Yes | - | Precision-Recall curve area |
| `roc_auc` | FLOAT | Yes | - | Receiver Operating Characteristic AUC |
| `confusion_matrix_json`| TEXT | No | Default: '{}' | Serialized $2 \times 2$ grid $[[TN, FP], [FN, TP]]$ |
| `triggered_by_user_id`| VARCHAR(36)| Yes | FK `users.id` (SET NULL) | Administrator who initiated run |

---

## 4. Table: `feedback`
Stores user corrections and auditing feedback.

| Column | Type | Nullable | Constraints / Index | Description |
|---|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key | UUID feedback identifier |
| `analysis_id` | VARCHAR(36) | No | FK `analyses.id` (CASCADE), Indexed | Referenced prediction |
| `user_id` | VARCHAR(36) | Yes | FK `users.id` (SET NULL), Indexed | User who provided feedback |
| `suggested_label`| VARCHAR(32) | No | - | Correct label: `'Spam'` or `'Legitimate'`|
| `comments` | TEXT | Yes | - | Optional diagnostic commentary |
| `created_at` | DATETIME | No | UTC | Timestamp feedback was submitted |
