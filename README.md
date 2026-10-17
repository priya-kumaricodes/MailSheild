#  MailShield

### Explainable Spam Detection. Transparent Decisions. Privacy by Design.

MailShield is an explainable machine-learning platform for detecting spam, identifying phishing risks, and understanding *why* an email was classified a certain way.

It combines multilingual text classification, feature-level explanations, an independent phishing-risk engine, and an interactive evaluation environment in one application—with a standalone desktop experience designed for local, offline analysis.

**No black-box verdicts. No mandatory cloud processing for local analysis. Just explainable email security.**

[**View Repository**](https://github.com/priya-kumaricodes/MailSheild) · [**Report a Bug**](https://github.com/priya-kumaricodes/MailSheild/issues) · [**Browse Releases**](https://github.com/priya-kumaricodes/MailSheild/releases)

---

##  What makes MailShield different?

Most spam classifiers return a label and a probability. MailShield goes further: it helps users inspect the evidence behind a decision, evaluate the model, and examine phishing indicators separately from the classifier's prediction.

- **Explainable ML:** Inspect the feature contributions behind classification decisions.
- **Multilingual Detection:** Supports English, Hindi, Tamil, Telugu, Kannada, and Hinglish.
- **Independent Phishing Analysis:** Evaluate suspicious URLs, domain patterns, credential-harvesting paths, and urgency indicators separately from the ML score.
- **Offline Desktop Mode:** Analyse email text locally without requiring a hosted backend for the core classification workflow.
- **Gmail Integration:** Scan inbox messages using Google OAuth with read-only access.
- **Evaluation Lab:** Examine confusion matrices, false positives, false negatives, language-specific performance, and validation-threshold trade-offs.
- **Privacy-Conscious Design:** Avoid retaining email bodies by default, subject to the application's configured workflow and explicit user choices.

---

##  Two ways to use MailShield

### 1. Standalone Desktop — for everyday use

The desktop application bundles its backend executable so users do not need to install Python or create a Python virtual environment on the target Mac.

The intended workflow is straightforward:

1. Download the packaged desktop release.
2. Extract the downloaded archive.
3. Move `MailShield.app` into Applications.
4. Open MailShield.
5. Analyse email content locally.

**Platform availability:** The documented standalone release targets macOS on Apple Silicon (`darwin-arm64`). Windows, Intel Mac, and Linux desktop packages are not included in this release.

Core local analysis is designed to work offline after installation, provided the required application assets are bundled. Gmail inbox scanning requires an internet connection and Google authentication.

### 2. Source Code — for developers

Prefer to inspect the implementation, run tests, train models, or modify MailShield?

Clone the repository or download the source ZIP and follow the development setup below.

Source code is not the same as a prebuilt desktop application: running from source requires the relevant development tools and dependencies.

---

##  Key Features

### Gmail Inbox Scanner

Connect a Gmail account to analyse selected inbox messages without granting permission to send, modify, or delete emails.

- Google OAuth 2.0 with PKCE for supported authentication flows.
- Read-only Gmail access using `gmail.readonly` and `userinfo.email`.
- Batch scanning for 5, 10, 25, or 50 messages.
- Classification breakdowns and explanations for scanned messages.
- Encrypted token storage using AES-256-GCM with key derivation and identity binding.

**Privacy note:** Gmail scanning requires an internet connection. Token encryption and email-retention behaviour depend on the implemented storage and configuration; review the privacy documentation before connecting a personal account.

###  Multilingual Spam Detection

MailShield's text-classification pipeline supports six target language categories:

| Language | Identifier |
|---|---|
| English | `en` |
| Hindi | `hi` |
| Tamil | `ta` |
| Telugu | `te` |
| Kannada | `kn` |
| Hinglish / Romanized Indic | `hinglish` |

The model combines word-level n-grams with character-level features to help recognise spelling variations, transliteration, and modified spam expressions.

###  Explainable Machine Learning

MailShield is built to make classification decisions easier to inspect.

- Feature-level contribution analysis.
- Support for Logistic Regression, Multinomial Naive Bayes, and Linear SVM workflows.
- Calibrated probabilities where supported by the model pipeline.
- A distinction between probability estimates and raw decision-margin scores.

A prediction is not presented as unquestionable truth. The supporting evidence matters, too.

###  Independent Phishing Risk Engine

The phishing-risk layer evaluates suspicious patterns independently of the ML classifier's probability.

Indicators include:

- IP-address-based hostnames.
- URL shorteners.
- Suspicious banking-domain patterns.
- Credential-related paths such as `/login` and `/kyc`.
- Urgency and credential-harvesting language.

This separation helps prevent the phishing heuristic from being confused with the classifier's own prediction.

**Important:** These indicators are heuristics, not proof that a message is malicious or legitimate.

###  Interactive Evaluation Lab

Evaluate the model instead of relying on a single accuracy figure.

- Model selection and validation inspection.
- Per-language filtering.
- Confusion matrices.
- False-positive and false-negative investigation.
- Dataset provenance inspection.
- Interactive classification experiments.
- Threshold simulation for examining precision/recall trade-offs.

###  Email and File Analysis

Analyse email content by pasting text or, where supported, uploading `.eml` and `.txt` files.

The interface includes sample messages for exploring spam, phishing, financial scams, ordinary business emails, travel receipts, and multilingual banking alerts.

###  Model Lab and Threshold Simulation

Explore how changing the classification threshold affects model behaviour.

The threshold simulator uses validation predictions to illustrate trade-offs involving false-positive rate, recall, and confusion matrices. Results depend on the selected model, dataset, and evaluation configuration.

###  History and Audit Export

The application includes analysis-history tools for searching, filtering, sorting, deleting records, and exporting supported results to CSV or JSON.

Export functionality includes protections against formula injection.

###  Privacy by Design

MailShield is designed to minimise unnecessary email-content retention.

- Local desktop analysis for supported workflows.
- No mandatory hosted classification service for core offline analysis.
- Email-body retention disabled by default in the documented workflow.
- Read-only Gmail permissions.
- Protected token storage for supported OAuth flows.

Privacy depends on the actual execution path and configuration. Connecting Gmail, enabling persistence, exporting results, or using an online deployment can change the data flows involved.

---

##  Architecture

MailShield separates the user interface, classification pipeline, phishing-risk analysis, and evaluation tooling.

```text
                     ┌──────────────────────┐
                     │      MailShield      │
                     │  User Interface      │
                     └──────────┬───────────┘
                                │
                     ┌──────────▼───────────┐
                     │  Input & Validation  │
                     └──────────┬───────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
       ┌──────────▼──────────┐    ┌───────────▼──────────┐
       │  ML Classification  │    │ Phishing Risk Engine │
       │  Spam / Legitimate  │    │ Security Heuristics  │
       └──────────┬──────────┘    └───────────┬──────────┘
                  │                           │
                  └─────────────┬─────────────┘
                                │
                     ┌──────────▼───────────┐
                     │ Explanation & Results│
                     └──────────┬───────────┘
                                │
                     ┌──────────▼───────────┐
                     │ Evaluation / History │
                     └──────────────────────┘
```

The architecture supports both a standalone desktop application and a web/API deployment. A local desktop backend is not the same as a publicly hosted API.

---

##  Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Machine Learning | scikit-learn, pandas, NumPy, SciPy |
| Classification | TF-IDF features, Logistic Regression, Multinomial Naive Bayes, Linear SVM |
| Desktop | Electron, PyInstaller, bundled Python backend |
| Testing | Pytest, Vitest, React Testing Library |
| Storage | SQLite for supported local desktop workflows |

Exact dependency versions are maintained in the project's dependency and configuration files.

---

##  Installation

### Option A — Download the standalone desktop release

**Recommended for users who simply want to run MailShield.**

1. Open [MailShield Releases](https://github.com/priya-kumaricodes/MailSheild/releases).
2. Download the published macOS Apple Silicon archive, if available.
3. Extract the archive.
4. Move `MailShield.app` into Applications.
5. Open the application and start analysing supported email content.

No separate Python installation, `pip install`, or virtual environment should be required for a correctly packaged standalone build.

**Release availability:** A downloadable archive must first be published under GitHub Releases. If no release asset is listed, use Option B or wait for the packaged release to be published.

### Option B — Download the source ZIP

1. Open the [repository](https://github.com/priya-kumaricodes/MailSheild).
2. Select **Code → Download ZIP**.
3. Extract the archive.
4. Open a terminal inside the extracted project folder.
5. Follow the developer setup below.

Downloading source code does not automatically install the dependencies or create a ready-to-run desktop application.

---

##  Developer Setup

### Prerequisites

- Python 3.11 or newer, using a version supported by the project's dependencies.
- Node.js 20 or newer and npm.
- Git, if cloning the repository.

### 1. Clone the repository

```bash
git clone https://github.com/priya-kumaricodes/MailSheild.git
cd MailSheild
```

### 2. Create a Python environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install project dependencies

Install the Python and JavaScript dependencies specified by the repository's current configuration. If the project provides dedicated dependency files, use those rather than maintaining a separate, manually assembled package list.

For example, where the relevant package manifests are present:

```bash
npm --prefix apps/web install
npm --prefix apps/desktop install
```

Install backend and ML dependencies according to the repository's dependency files and documented setup.

### 4. Build the frontend

```bash
npm --prefix apps/web run build
```

### 5. Build the desktop application

```bash
npm --prefix apps/desktop run build
npm --prefix apps/desktop run package
```

The packaging command should produce the desktop distributable configured for the current platform. Confirm the output path and supported architecture in the package configuration before distributing it.

For backend development, API testing, or web deployment, follow the project's technical documentation. Those are developer workflows and are separate from running the packaged offline desktop application.

---

##  Testing and Quality Checks

MailShield includes automated tests for supported backend, ML, frontend, and desktop workflows.

Run the checks available in the current checkout:

```bash
.venv/bin/pytest -v
```

```bash
npm --prefix apps/web test
```

```bash
npm --prefix apps/web run build
```

```bash
npm --prefix apps/desktop run build
```

For standalone packaging verification:

```bash
npm --prefix apps/desktop run package
```

Test counts and packaging results can change between releases. Consult the actual test output and release report before claiming a particular number of passing tests.

---

##  Documentation

The repository's `docs/` directory contains the detailed product and engineering specifications, where available:

- [Product Definition Specification](docs/PDS.md)
- [Technical Design Specification](docs/TDS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Data Dictionary](docs/DATA_DICTIONARY.md)
- [Model Card](docs/MODEL_CARD.md)
- [Dataset Card](docs/DATASET_CARD.md)
- [Privacy Documentation](docs/PRIVACY.md)
- [Threat Model](docs/THREAT_MODEL.md)
- [Test Plan](docs/TEST_PLAN.md)
- [User Guide](docs/USER_GUIDE.md)

These links refer to files in the repository; the files should be present in the published branch for the links to work.

---

##  Limitations and Security Notes

- The documented standalone release targets macOS Apple Silicon only.
- Gmail inbox integration requires internet access and Google authentication.
- Local offline classification and online Gmail scanning are distinct workflows.
- Classification scores are estimates, not guarantees.
- Phishing indicators are heuristics and may produce false positives or false negatives.
- Evaluation results depend on the dataset and validation methodology.
- Never commit real `.env` files, API keys, OAuth client secrets, access tokens, private emails, or personal datasets.
- Before connecting a Gmail account, review the OAuth scopes, token-storage implementation, and privacy documentation.

---

##  About the Developer

##  Developer

**Priya Kumari** — Creator and Developer of MailShield

- **GitHub:** [@priya-kumaricodes](https://github.com/priya-kumaricodes)
- **LinkedIn:** [Priya Kumari](https://www.linkedin.com/in/priya-kumari-411706444/)

##  Contributions

**Anurag Tiwari** — Contributor; provided limited assistance during development.
- **GitHub:** [@anurag-tiwaricodes](https://github.com/Anurag-tiwaricodes)
- **LinkedIn:** [Anurag Tiwari](https://www.linkedin.com/in/anurag-tiwari-2b1913427/)

---

##  License

MailShield is intended to be distributed under the MIT License. See the repository's `LICENSE` file for the applicable terms.

Dataset and sample-email licensing may differ from the software license. Review the relevant dataset documentation before redistributing sample data.

---


## 📅 Development Timeline

- **Project Started:** September 25, 2026
- **Development Through:** October 17, 2026

**MailShield — Security you can inspect. Decisions you can explain.**
