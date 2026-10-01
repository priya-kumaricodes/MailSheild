# MailShield — Product Definition Specification (PDS)

## 1. Executive Summary & Objective

MailShield is an explainable machine learning spam classification platform. Designed as an analytical and educational intelligence tool, MailShield accepts inbound email messages (via direct text input or file uploads of RFC 822 `.eml` and `.txt` files), predicts whether the message is **Spam** or **Legitimate**, and displays mathematical feature attributions explaining which tokens pushed the decision toward or away from spam.

Unlike black-box commercial filters, MailShield provides verifiable decision boundaries, cross-model comparison, threshold simulation, and offline-capable desktop execution.

---

## 2. Target Users & Personas

1. **Security Operations Analysts (SOC)**:
   - Need to inspect suspicious inbound phishing alerts and determine which malicious indicators (domains, payment tokens, urgency phrases) triggered filter alarms.
2. **Machine Learning Engineers & Data Scientists**:
   - Require transparency into feature weights, TF-IDF representations, probability calibration curves, and false-positive versus recall trade-offs.
3. **Privacy-Conscious Professionals**:
   - Need local desktop execution without routing proprietary or confidential emails to third-party cloud LLMs or external APIs.
4. **Students & Educators**:
   - Require an intuitive, verifiable testbed demonstrating classical NLP classification, Bayes rule, Logistic link functions, and hyperplane margins.

---

## 3. Core Functional Requirements

| Req ID | Feature Area | Description | Verification Status |
|---|---|---|---|
| **FR-01** | Input Parsing | Accepts subject and body text, with character counting and empty validation. | Implemented & Tested |
| **FR-02** | File Import | Safely uploads and decodes `.eml` and `.txt` files up to 5MB, stripping attachments. | Implemented & Tested |
| **FR-03** | ML Inference | Real-time prediction using scikit-learn Logistic Regression, Naive Bayes, and Linear SVM. | Implemented & Tested |
| **FR-04** | Explainability | Exact token-level linear feature attribution ($w_i \cdot x_i$) categorized by polarity and percentage impact. | Implemented & Tested |
| **FR-05** | Score Semantics | Clear differentiation between calibrated posterior probabilities and raw decision margins. | Implemented & Tested |
| **FR-06** | Threshold Sim | Real-time threshold slider computing genuine confusion matrices and FPR on validation data. | Implemented & Tested |
| **FR-07** | History & CRUD | Paginated analysis history, multi-filter search, sorting, and single/bulk deletion. | Implemented & Tested |
| **FR-08** | Audit Export | CSV and JSON export with mandatory CSV formula injection mitigation. | Implemented & Tested |
| **FR-09** | User Scoping | JWT authentication ensuring users only access and delete their own analysis records. | Implemented & Tested |
| **FR-10** | Offline Desktop | Electron desktop mode running local Python backend and SQLite history with zero internet access. | Implemented & Tested |

---

## 4. Scope & Non-Goals (Version 1.0)

### In Scope
- Manual email subject and body analysis.
- Drag-and-drop `.eml` and `.txt` file parsing.
- Feature attribution and explainability breakdown.
- Validation threshold sweep simulation.
- Audit history and CSV/JSON export.
- Offline desktop application.

### Explicit Non-Goals (Out of Scope for v1)
- Automatic background inbox crawling or IMAP/POP3 listening.
- Gmail or Microsoft 365 OAuth inbox synchronization.
- Automated email deletion or routing.
- Outbound marketing email sending.

---

## 5. Success & Acceptance Criteria

1. **Zero Fabricated Metrics**: Dashboard metrics, confusion matrices, and feature contributions must derive strictly from real backend database queries and genuine validation predictions.
2. **Deterministic Explainability**: The sum of feature contributions plus the model intercept must equal the net decision score ($b + \sum w_i x_i = \text{logit}$).
3. **Data Isolation**: User A cannot read, query, or delete analysis records created by User B.
4. **Offline Resilience**: When disconnected from the internet, the desktop application performs predictions and persists history to local SQLite without errors.
