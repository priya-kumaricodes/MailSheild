# MailShield — Security Threat Model (STRIDE)

## 1. Threat Matrix & Mitigations

| Threat Category | Potential Attack Vector | Impact | MailShield Defensive Mitigation |
|---|---|---|---|
| **Spoofing** | Attacker impersonates another user to read private email analyses. | High | Cryptographically signed JWT Bearer tokens with expiration. Database queries strictly filter by `user_id == current_user.id`. |
| **Tampering** | Attacker manipulates CSV export to execute dynamic commands via Excel / LibreOffice formulas. | High | **CSV Formula Injection Defense**: Any cell beginning with `=`, `+`, `-`, `@`, `\t`, or `\r` is prepended with a single quote `'` in `sanitize_csv_value()`. |
| **Repudiation** | User disputes having submitted an evaluation or feedback. | Low | Immutable timestamped audit entries recorded in `evaluation_runs` and `feedback` tables with user foreign keys. |
| **Information Disclosure** | Email body PII or confidential company text leaked in logs or database breaches. | Critical | Non-storage by default (`is_content_stored = False`). Raw bodies are omitted from logs and only one-way SHA-256 hashes are stored. |
| **Denial of Service** | Oversized payloads or recursive MIME zip-bombs consume system memory during parsing. | High | Strict 5MB file upload limit (`HTTP 413 Content Too Large`). Memory-safe streaming and rejection of unauthorized file extensions. |
| **Elevation of Privilege**| Standard user triggers compute-heavy model training or evaluation jobs. | High | **RBAC Dependency**: `POST /api/v1/evaluation/run` enforces `require_admin_user`, returning `HTTP 403 Forbidden` for standard users. |

---

## 2. Electron Desktop Security Configuration

The desktop application enforces Electron security best practices:
1. `contextIsolation: true`: Ensures renderer scripts cannot access Node.js internals or prototype tampering.
2. `nodeIntegration: false`: Disables Node APIs in DOM window contexts.
3. `sandbox: true`: Enforces Chromium sandbox isolation.
4. `webSecurity: true`: Enforces same-origin policy.
5. `setWindowOpenHandler(() => ({ action: 'deny' }))`: Prohibits untrusted child windows or external link injection.
6. **Preload Bridge**: Only explicit, sanitized IPC invocations (`check-backend-health`, `get-app-version`) are exposed via `window.mailshieldDesktop`.
