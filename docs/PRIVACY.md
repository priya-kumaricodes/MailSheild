# MailShield — Privacy & Data Protection Policy

## 1. Privacy Philosophy: Data Minimization by Design

MailShield was engineered around the principle of strict data minimization. Analyzing email content must never compromise confidentiality or inadvertently leak sensitive communications.

---

## 2. Email Body Text Persistence Policy

1. **Default Non-Storage**:
   - In both the online web application and local desktop version, **email body text is not permanently persisted by default**.
   - The `email_body` column in the `analyses` table remains `NULL` unless the user explicitly checks the "Persist Full Email Text" toggle.
2. **Cryptographic Fingerprinting**:
   - For auditing and duplicate detection, MailShield stores a one-way **SHA-256 content hash** (`email_hash`) computed over the normalized subject and body. The original text cannot be reversed from this hash.
3. **Log Sanitization**:
   - Backend application logs, terminal outputs, and HTTP access logs are strictly scrubbed of email body text and potential authentication tokens.

---

## 3. History Retention & Purge Policies

Users can configure retention policies via the Settings panel:
- **Keep All**: Records persist until manually deleted.
- **30 Days**: Analyses older than 30 days are automatically pruned.
- **7 Days**: Analyses older than 7 days are automatically pruned.
- **Do Not Persist**: In-memory ephemeral evaluation only; zero database rows are committed.

---

## 4. User Scoping & Tenant Isolation

1. **Authentication Boundaries**:
   - Online mode requires JWT authentication.
   - Every history query, analysis detail request, deletion request, and feedback submission is strictly bound to `current_user.id`.
   - Access attempts to records belonging to other users result in `HTTP 404 Not Found` (preventing user enumeration).
2. **Offline Desktop Mode**:
   - The desktop build uses a local SQLite database (`mailshield_desktop.db`) on the user's filesystem.
   - Zero telemetry, analytics, or prediction payloads are sent over the network.
