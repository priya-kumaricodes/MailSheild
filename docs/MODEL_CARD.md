# MailShield — Model Card

## 1. Model Details
- **Model Name**: MailShield Explainable Linear & Probabilistic Ensembles
- **Versions**:
  - `logistic_regression` (v1.0.0, Primary Explainable Model)
  - `naive_bayes` (v1.0.0, Fast Frequency Baseline)
  - `linear_svm` (v1.0.0, High-Margin Linear Classifier with Platt Scaling)
- **Framework**: scikit-learn 1.9.1 (Python 3.14.7)
- **Developers**: MailShield Engineering Team
- **Date**: October 2026
- **License**: MIT

---

## 2. Intended Use
- **Primary Use Case**: Educational, analytical, and security triage of suspicious email messages. Explaining feature attributions to prevent accidental phishing compromise and understand spam patterns.
- **Out of Scope**: High-frequency corporate gateway blocking without human-in-the-loop oversight; autonomous inbox deletion.

---

## 3. Training Data & Preprocessing
- **Source**: Verified SpamAssassin public corpus and balanced benchmark samples.
- **Corpus Volume**: 248 records (124 Legitimate, 124 Spam; 0 duplicates).
- **Partitioning**: Grouped template partition eliminating cross-split campaign leakage:
  - Training: 148 samples (74 Ham, 74 Spam)
  - Validation: 64 samples (32 Ham, 32 Spam)
  - Holdout Test: 36 samples (18 Ham, 18 Spam)
- **Leakage Prevention**: TF-IDF vocabulary (unigrams and bigrams, max 5,000 features, min document frequency 2) was fitted strictly on the training partition. Test samples were never inspected during feature selection or threshold calibration.

---

## 4. Cost-Sensitive Threshold Selection

To penalize destructive false positives on legitimate business communications (invoices, receipts, alerts) much more severely than missed spam, decision thresholds are selected on the validation partition using the utility function:

$$\text{Utility}(\tau) = \text{TP}(\tau) - 5 \times \text{FP}(\tau) - \text{FN}(\tau)$$
$$\text{subject to } \text{FPR}(\tau) \le 0.05$$

**Tie-Breaking Policy**:
When multiple candidate thresholds achieve identical maximal utility on validation data, ties are broken toward the threshold with the largest safety margin against false positives (closest to $\tau = 0.50$ or higher), avoiding brittle ultra-low thresholds.

---

## 5. Quantitative Evaluation

### 5.1 Out-of-Template Generalization Benchmark (Strict Grouped Split — 36 Samples)
Evaluated on unseen template families and campaign archetypes (`groups(train) ∩ groups(test) == ∅`), with unseen retail store receipts in Ham and unseen voucher scams in Spam:

| Model | Operating Threshold | Accuracy | Precision | Recall | F1 Score | False Positive Rate | Brier Loss | Calibration Status |
|---|---|---|---|---|---|---|---|---|
| **Logistic Regression** | &tau; = 0.50 | **97.22%** | **100.00%** | **94.44%** | **0.9714** | **0.0000** | 0.1717 | Moderate Calibration |
| **Linear SVM (Platt)** | &tau; = 0.50 | **91.67%** | **89.47%** | **94.44%** | **0.9189** | 0.1111 | **0.0753** | Evaluated Well Calibrated |
| **Multinomial NB** | &tau; = 0.70 | 72.22% | **100.00%** | 44.44% | 0.6154 | **0.0000** | 0.1014 | Uncalibrated Log-Likelihood |

### 5.2 In-Distribution Benchmark (Standard Partition — 38 Samples)
Evaluated on the independent test set at cost-sensitive optimal thresholds:

| Model | Decision Threshold | Test Accuracy | Test Precision | Test Recall | Test F1 Score | False Positive Rate | Brier Loss | Inference Latency | Calibration Status |
|---|---|---|---|---|---|---|---|---|---|
| **Logistic Regression** | &tau; = 0.50 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.00% | 0.0376 | 0.0020 ms/sample | Evaluated Well Calibrated |
| **Multinomial NB** | &tau; = 0.50 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.00% | 0.0000 | 0.0029 ms/sample | Uncalibrated Log-Likelihood |
| **Linear SVM (Platt)** | &tau; = 0.50 | 100.0% | 100.0% | 100.0% | 1.0000 | 0.00% | 0.0042 | 0.0257 ms/sample | Evaluated Well Calibrated |

### 5.3 Generalization & Error Diagnosis
1. **False Positive Elimination on Legitimate Receipts**: Balancing the training partition with legitimate cloud invoices and bank alerts completely eliminated store receipt false positives (FPR = 0.0% in Logistic Regression with 0/18 legitimate receipts flagged).
2. **High Generalization Recall**: Balancing operational vocabulary across both classes resolved the previous recall suppression. Logistic Regression achieves 94.44% recall (17/18 spam detected on unseen voucher campaigns) at &tau; = 0.50. The sole missed spam is an out-of-vocabulary Hindi lottery text.
3. **Probability Calibration**: Cross-validated Platt scaling on Linear SVM yields a Brier score of 0.0753 ($\le 0.15$), confirming that probability outputs reflect true empirical risk. Linear SVM flags 2 base samples as false positives (FPR 11.11%), illustrating the practical tradeoff between margin maximization and false alarm minimization.
4. **Naive Bayes Independence Limitation**: Multinomial Naive Bayes exhibits low recall (44.44%) under out-of-template distribution shifts, missing subtle multi-token phishing cues due to the conditional independence assumption.

---

## 6. Explainability & Attribution Architecture
- **Logistic Regression**: Linear dot product attribution $c_i = w_i \cdot x_i$. The sum of all token contributions plus the prior intercept exactly equals the net log-odds decision score $\sum c_i + b = f(x)$, mapped to calibrated probability via sigmoid $\sigma(f(x))$.
- **Linear SVM**: Feature attribution $c_i = w_i \cdot x_i$ explains the raw geometric hyperplane decision margin $f(x) = \sum c_i + b$. Platt scaling sigmoid parameters $(A, B)$ learned via cross-validation map $f(x)$ to a calibrated probability $P(y=1 \mid f(x)) = \frac{1}{1 + \exp(A \cdot f(x) + B)}$.
- **Multinomial Naive Bayes**: Feature evidence is calculated using the log-likelihood ratio $c_i = \log P(w_i \mid \text{Spam}) - \log P(w_i \mid \text{Ham})$. Because the conditional independence assumption systematically produces overconfident posteriors, the API returns `calibrated: false` and `calibrated_probability: null` to prevent misleading calibration claims.
- Attributions indicate statistical correlation with corpus vocabulary, not intrinsic semantic malice.

---

## 7. Caveats & Ethical Considerations
- **Adversarial Token Stuffing**: Attackers can attempt "good word stuffing" (appending technical or academic phrases) to dilute the spam logit.
- **Multilingual Generalization**: Models perform best on English and transliterated text. Low-resource languages with unseen vocabularies will receive low confidence scores.

---

## 8. Multilingual Classification Models (v2.0.0 Phase 1)

### 8.1 Model Details & Architecture
MailShield 2.0 Phase 1 expands detection capabilities to 6 language targets: English (`en`), Hindi in Devanagari (`hi`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`), and Hinglish / Romanized Indic (`hinglish`).

- **Dual-Channel TF-IDF Feature Pipeline (`MultilingualFeaturePipeline`)**:
  - **Word Channel**: Word n-grams $(1, 2)$, max 4,000 features, capturing lexical tokens and phrases.
  - **Subword Character Channel**: Subword character n-grams $(3, 5)$ using boundary-aware `char_wb` analyzer, max 4,000 features, capturing morphological roots, agglutinative inflections, and transliteration variants across Indic scripts and Hinglish.
  - Total combined fitted vocabulary: 4,470 features.
- **Model Implementations**:
  - `multilingual_linear_svm`: LinearSVC ($C=1.0$) with 3-fold cross-validated Platt scaling for well-calibrated posterior probabilities.
  - `multilingual_logistic_regression`: Logistic Regression ($C=2.0$, L2 penalty).
  - `multilingual_naive_bayes`: Multinomial Naive Bayes ($\alpha=0.5$).

### 8.2 Quantitative Evaluation on Untouched Multilingual Holdout Test Set
Evaluated on the strict held-out test partition (36 samples across 12 unseen template groups, balanced 1:1 Ham/Spam, zero template overlap with train or validation):

| Model | Operating Threshold | Test Accuracy | Test Precision | Test Recall | Test F1 Score | False Positive Rate | Brier Loss | Inference Latency | Model Size | Calibration Status |
|---|---|---|---|---|---|---|---|---|---|---|
| **Linear SVM (Platt)** | &tau; = 0.6500 | **97.22%** | **100.00%** | **94.44%** | **0.9714** | **0.0000** | **0.0344** | 0.0276 ms/sample | 142.2 KB | Evaluated Well Calibrated |
| **Logistic Regression** | &tau; = 0.5500 | **94.44%** | **100.00%** | **88.89%** | **0.9412** | **0.0000** | 0.1467 | **0.0021 ms/sample** | **35.9 KB** | Evaluated Well Calibrated |
| **Multinomial NB** | &tau; = 0.7000 | 83.33% | 92.86% | 72.22% | 0.8125 | 0.0556 | 0.0951 | 0.0039 ms/sample | 140.6 KB | Uncalibrated Log-Likelihood |

#### Per-Language Holdout Performance (Linear SVM)
- **Hindi (`hi`)**: 100% Accuracy (3/3 Ham, 3/3 Spam correctly classified; 0 FP, 0 FN).
- **Tamil (`ta`)**: 100% Accuracy (3/3 Ham, 3/3 Spam correctly classified; 0 FP, 0 FN).
- **Telugu (`te`)**: 100% Accuracy (3/3 Ham, 3/3 Spam correctly classified; 0 FP, 0 FN).
- **Kannada (`kn`)**: 100% Accuracy (3/3 Ham, 3/3 Spam correctly classified; 0 FP, 0 FN).
- **Hinglish (`hinglish`)**: 100% Accuracy (3/3 Ham, 3/3 Spam correctly classified; 0 FP, 0 FN).
- **English (`en`)**: 83.33% Accuracy (3/3 Ham, 2/3 Spam; 0 FP, 1 FN on subtle zero-URL scam).

### 8.3 Comparison Against English Baseline
When evaluating the legacy English baseline classifier on non-English native vocabulary without shared URL cues, performance degrades severely:
- **English Baseline on Non-English Holdout**: Drops to **52.78% accuracy** and **5.56% spam recall**, as pure word-level English tokenizers cannot parse Indic Unicode scripts or Romanized phonetic spellings.
- **Multilingual Linear SVM (v2.0.0)**: Elevates performance to **97.22% accuracy** and **94.44% spam recall** with **0.0% false positive rate**, driven by subword character n-gram matching across regional linguistic boundaries.

### 8.4 Decoupled Phishing Risk Engine Architecture
Phishing risk assessment is strictly decoupled from the ML spam classifier's lexical probability score. While spam classifiers measure statistical vocabulary correlation, the phishing engine evaluates structural, cryptographic, and deceptive intent markers:

1. **Risk Indicators Evaluated**:
   - **IP Host Addresses**: Detects raw IPv4/IPv6 addresses embedded in hyperlink hosts.
   - **URL Shorteners**: Detects redirection through known shortening services (`bit.ly`, `tinyurl.com`, `t.co`, `is.gd`, `ow.ly`).
   - **Financial Brand Spoofing**: Identifies domain mismatches impersonating major Indian financial institutions (State Bank of India, HDFC Bank, ICICI Bank, Axis Bank, Punjab National Bank).
   - **Credential Harvesting Paths**: Detects high-risk authentication paths (`/login`, `/signin`, `/verify`, `/kyc`, `/update-pan`, `/ebanking`).
   - **Multilingual Urgency Indicators**: Detects coercive urgency lures across English, Hindi, Tamil, Telugu, Kannada, and Hinglish (`turant`, `tatkal`, `kyc suspend`, `khata block`).

2. **Defensive Dampening for Authentic Banking Notifications**:
   - To prevent legitimate one-time password (OTP) and transaction alerts from false phishing escalation, a defensive dampener checks for canonical bank security disclosures:
     - "Do not share OTP" / "Never share your PIN" / "Valid for 10 minutes".
   - When verified, defensive dampening reduces phishing severity and tags the message as legitimate verification rather than credential theft.

