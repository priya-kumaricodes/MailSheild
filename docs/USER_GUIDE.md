# MailShield — User & Analyst Guide

Welcome to **MailShield**, an explainable spam classification platform designed for security analysts, researchers, and privacy-conscious users.

---

## 1. Getting Started

### 1.1 Running the Web Application
1. Start the FastAPI backend:
   ```bash
   .venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
   ```
2. Start the Vite development frontend:
   ```bash
   npm --prefix apps/web run dev
   ```
3. Open your browser at `http://localhost:5173`.

### 1.2 Running the Offline Desktop Application
1. Build the desktop components:
   ```bash
   npm --prefix apps/web run build
   npm --prefix apps/desktop run build
   ```
2. Launch Electron:
   ```bash
   npm --prefix apps/desktop start
   ```

---

## 2. Using the Email Analyzer

1. **Inputting Content**:
   - **Manual Text**: Paste subject (optional) and email body text into the text area.
   - **File Upload**: Drag and drop a `.eml` or `.txt` file onto the dropzone.
   - **Quick Benchmark Samples**: Click any of the 1-click sample buttons (e.g. "Phishing: Bank Alert", "Work: Sprint Planning", "Multilingual: Hindi Meeting").
2. **Selecting Inference Options**:
   - **Model Selector**:
     - *Logistic Regression*: Recommended for explainability; provides calibrated probabilities and exact token log-odds.
     - *Multinomial Naive Bayes*: Fast frequency baseline.
     - *Linear SVM*: High-margin classifier with Platt-calibrated probabilities.
   - **Decision Threshold (&tau;)**: Default is 0.50. Lower values increase spam sensitivity; higher values decrease false positive risk.
   - **Persist Full Text**: Check this if you want to store the body in history for later inspection. (Defaults to OFF for privacy).
3. **Interpreting Results**:
   - **Prediction Badge**: Displays **SPAM** (Rose) or **LEGITIMATE** (Emerald).
   - **Score**: Calibrated probability percentage (e.g., 94.1%) or raw decision margin score.
   - **Confidence Level**: High, Medium, or Low based on distance from the decision boundary.
   - **Feature Attribution Breakdown**:
     - *Spam Evidence*: Words with positive weights that pushed the score toward Spam.
     - *Legitimate Evidence*: Words with negative weights that pushed the score toward Legitimate.
     - *Relative Impact*: Percentage of directional attribution contributed by each token.

---

## 3. Managing Analysis History

- **Search**: Use the search bar to locate analyses by subject keyword or classification.
- **Filters**: Click "All", "Spam", or "Legitimate" pills to filter records.
- **Inspect**: Click the eye icon to view full token breakdowns and the stored email body.
- **Exporting**: Click **Export CSV** (formula-injection protected) or **Export JSON** to download audit trails.
- **Deletion**: Delete individual rows or check multiple boxes and click **Delete Selected**.

---

## 4. Exploring the Model Lab

1. **Model Comparison**:
   - Inspect side-by-side performance cards showing Test Accuracy, F1 Score, Precision, Recall, and False Positive Rate.
2. **Threshold Simulator**:
   - Select a model and move the threshold slider from 0.05 to 0.95.
   - Observe in real time how changing the threshold affects the **Confusion Matrix** (True Negatives, False Positives, False Negatives, True Positives) and shifts the balance between Recall and False Positive Rate.
   - All metrics are calculated from genuine validation predictions without simulated or fabricated numbers.

---

## 5. Submitting Feedback

If you encounter an email that was misclassified, click **Report Prediction Accuracy** at the bottom of the result card, select the suggested true label, enter optional notes, and click **Submit Feedback** to record the correction for model improvement.
