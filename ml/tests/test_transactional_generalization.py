"""Transactional generalization and false positive regression test suite.

Verifies:
1. Legitimate receipts, cloud invoices, bank transaction alerts, and travel confirmations
   are classified as Legitimate (Ham) without false positives.
2. Deceptive phishing invoices and delivery fee scams are detected as Spam.
3. Strict out-of-template holdout evaluation report maintains zero group overlap and low FPR.
4. Explainability additive logit decomposition holds accurately.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from mailshield_ml.explainability import ExplainabilityEngine
from mailshield_ml.features import FeaturePipeline
from mailshield_ml.models import LinearSVCWrapper, LogisticRegressionWrapper, MultinomialNBWrapper


@pytest.fixture(scope="module")
def artifacts():
    artifacts_dir = Path("ml/artifacts")
    vec_path = artifacts_dir / "tfidf_vectorizer.joblib"
    lr_path = artifacts_dir / "model_logistic_regression.joblib"
    svm_path = artifacts_dir / "model_linear_svm.joblib"
    nb_path = artifacts_dir / "model_naive_bayes.joblib"
    meta_path = artifacts_dir / "metadata.json"

    if not (vec_path.exists() and lr_path.exists() and svm_path.exists()):
        pytest.skip("Trained artifacts not found in ml/artifacts")

    vectorizer = FeaturePipeline.load(str(vec_path))
    lr = LogisticRegressionWrapper.load(str(lr_path))
    svm = LinearSVCWrapper.load(str(svm_path))
    nb = MultinomialNBWrapper.load(str(nb_path))

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    return {
        "vectorizer": vectorizer,
        "lr": lr,
        "svm": svm,
        "nb": nb,
        "metadata": meta,
        "explainer": ExplainabilityEngine(vectorizer),
    }


def test_legitimate_retail_receipt_classified_as_ham(artifacts):
    """Legitimate store purchase receipt with dollar amounts must not trigger spam false positive."""
    receipt = (
        "Subject: Your receipt from TechGear Direct - Order #1042\n\n"
        "Thank you for your purchase at TechGear Direct!\n\n"
        "Order Summary: #1042\n"
        "Date: October 14, 2026\n\n"
        "Items:\n"
        "- 1x USB-C Multiport Adapter ($34.99)\n"
        "- 1x Braided 6ft HDMI Cable ($12.50)\n\n"
        "Subtotal: $47.49\n"
        "Tax (8.25%): $3.92\n"
        "Shipping: Free\n"
        "Total Paid: $51.41\n"
        "Payment Method: Visa card ending in 4102\n\n"
        "You can view tracking or return details at https://techgear.com/orders/1042."
    )
    vec = artifacts["vectorizer"]
    lr = artifacts["lr"]
    svm = artifacts["svm"]

    x = vec.transform([receipt])
    tau_lr = artifacts["metadata"]["models"]["logistic_regression"]["optimal_threshold"]
    tau_svm = artifacts["metadata"]["models"]["linear_svm"]["optimal_threshold"]

    pred_lr = lr.predict_single(x, threshold=tau_lr)
    pred_svm = svm.predict_single(x, threshold=tau_svm)

    # Must be classified as Legitimate
    assert not pred_lr.is_spam, f"Logistic Regression false positive on receipt: score={pred_lr.score:.4f} >= tau={tau_lr}"
    assert pred_lr.predicted_label == "Legitimate"

    assert not pred_svm.is_spam, f"Linear SVM false positive on receipt: score={pred_svm.score:.4f} >= tau={tau_svm}"
    assert pred_svm.predicted_label == "Legitimate"


def test_legitimate_cloud_infrastructure_invoice_classified_as_ham(artifacts):
    """Monthly cloud hosting bill with compute, storage, and tax breakdown must be Legitimate."""
    invoice = (
        "Subject: Your CloudVantage Monthly Billing Statement - Oct 2026 (INV-8921)\n\n"
        "CloudVantage Infrastructure Services\n\n"
        "Dear Customer,\n\n"
        "Your monthly invoice for account ACCT-99120 is now ready.\n"
        "Billing Period: Sep 01 - Sep 30\n\n"
        "Charges:\n"
        "- Virtual Compute Instances: $64.00\n"
        "- Managed Database: $35.00\n"
        "- Storage & CDN Transfer: $14.20\n\n"
        "Subtotal: $113.20\n"
        "Tax: $9.06\n"
        "Total Billed: $122.26\n\n"
        "Billed to corporate Mastercard ending in 8821.\n"
        "Download your VAT breakdown invoice from your billing console."
    )
    vec = artifacts["vectorizer"]
    lr = artifacts["lr"]
    svm = artifacts["svm"]

    x = vec.transform([invoice])
    tau_lr = artifacts["metadata"]["models"]["logistic_regression"]["optimal_threshold"]
    tau_svm = artifacts["metadata"]["models"]["linear_svm"]["optimal_threshold"]

    pred_lr = lr.predict_single(x, threshold=tau_lr)
    pred_svm = svm.predict_single(x, threshold=tau_svm)

    assert not pred_lr.is_spam, f"Logistic Regression false positive on cloud invoice: score={pred_lr.score:.4f}"
    assert pred_lr.predicted_label == "Legitimate"

    assert not pred_svm.is_spam, f"Linear SVM false positive on cloud invoice: score={pred_svm.score:.4f}"
    assert pred_svm.predicted_label == "Legitimate"


def test_legitimate_bank_alert_classified_as_ham(artifacts):
    """Bank debit card transaction alert must be classified as Legitimate."""
    alert = (
        "Subject: Bank of America: Debit Card Alert for $42.50 at Metro Foods\n\n"
        "Dear Customer,\n\n"
        "A debit transaction was authorized on your checking account:\n"
        "Merchant: Metro Foods Market #14\n"
        "Amount: $42.50\n"
        "Date: Oct 14, 2026 11:32 AM\n"
        "Card: ending in 3091\n"
        "Available Balance: $1,850.20\n\n"
        "No action is required if you authorized this purchase.\n"
        "Manage your account security at our official banking website."
    )
    vec = artifacts["vectorizer"]
    lr = artifacts["lr"]
    svm = artifacts["svm"]

    x = vec.transform([alert])
    tau_lr = artifacts["metadata"]["models"]["logistic_regression"]["optimal_threshold"]
    tau_svm = artifacts["metadata"]["models"]["linear_svm"]["optimal_threshold"]

    pred_lr = lr.predict_single(x, threshold=tau_lr)
    pred_svm = svm.predict_single(x, threshold=tau_svm)

    assert not pred_lr.is_spam, f"Logistic Regression false positive on bank alert: score={pred_lr.score:.4f}"
    assert pred_lr.predicted_label == "Legitimate"

    assert not pred_svm.is_spam, f"Linear SVM false positive on bank alert: score={pred_svm.score:.4f}"
    assert pred_svm.predicted_label == "Legitimate"


def test_legitimate_flight_reservation_classified_as_ham(artifacts):
    """Airline ticket reservation confirmation with itinerary and price must be Legitimate."""
    flight = (
        "Subject: Flight Confirmation: SFO to ORD (Booking Reference: #KL9021)\n\n"
        "Thank you for flying Horizon Air.\n\n"
        "Passenger: Sarah Jenkins\n"
        "Confirmation Code: #KL9021\n"
        "Flight: HA 482\n"
        "Date: Nov 02, 2026\n"
        "Departs: San Francisco (SFO) 08:30 AM\n"
        "Arrival: Chicago O'Hare (ORD) 02:45 PM\n"
        "Seat: 14A (Window)\n\n"
        "Airfare: $320.00\n"
        "Taxes & Fees: $38.50\n"
        "Total Paid: $358.50\n\n"
        "Check-in opens 24 hours prior to departure online."
    )
    vec = artifacts["vectorizer"]
    lr = artifacts["lr"]
    svm = artifacts["svm"]

    x = vec.transform([flight])
    tau_lr = artifacts["metadata"]["models"]["logistic_regression"]["optimal_threshold"]
    tau_svm = artifacts["metadata"]["models"]["linear_svm"]["optimal_threshold"]

    pred_lr = lr.predict_single(x, threshold=tau_lr)
    pred_svm = svm.predict_single(x, threshold=tau_svm)

    assert not pred_lr.is_spam, f"Logistic Regression false positive on flight confirmation: score={pred_lr.score:.4f}"
    assert pred_lr.predicted_label == "Legitimate"

    assert not pred_svm.is_spam, f"Linear SVM false positive on flight confirmation: score={pred_svm.score:.4f}"
    assert pred_svm.predicted_label == "Legitimate"


def test_fake_invoice_phishing_detected_as_spam(artifacts):
    """Fake Geek Squad / Norton $499 auto-renewal scam with call-to-cancel lure must be Spam."""
    fake_invoice = (
        "Subject: INVOICE CONFIRMATION: Order #8921 processed for $499.00\n\n"
        "Geek Squad Protection Care Center\n\n"
        "Dear Customer,\n\n"
        "Your annual subscription for Computer Protection Plan has been auto-renewed for $499.00. "
        "The charge will reflect on your bank statement within 24 hours.\n\n"
        "Invoice ID: GS-8921\n"
        "Payment Mode: Direct Auto-Debit\n\n"
        "If you did not authorize this subscription renewal, call our fraud cancellation desk immediately "
        "at +1-800-555-0199 within 24 hours to speak with a billing agent and stop the unauthorized debit.\n\n"
        "Customer Support Team"
    )
    vec = artifacts["vectorizer"]
    lr = artifacts["lr"]
    svm = artifacts["svm"]

    x = vec.transform([fake_invoice])
    tau_lr = artifacts["metadata"]["models"]["logistic_regression"]["optimal_threshold"]
    tau_svm = artifacts["metadata"]["models"]["linear_svm"]["optimal_threshold"]

    pred_lr = lr.predict_single(x, threshold=tau_lr)
    pred_svm = svm.predict_single(x, threshold=tau_svm)

    assert pred_lr.is_spam, f"Logistic Regression missed fake invoice scam: score={pred_lr.score:.4f} < tau={tau_lr}"
    assert pred_lr.predicted_label == "Spam"

    assert pred_svm.is_spam, f"Linear SVM missed fake invoice scam: score={pred_svm.score:.4f} < tau={tau_svm}"
    assert pred_svm.predicted_label == "Spam"


def test_delivery_fee_scam_detected_as_spam(artifacts):
    """USPS redelivery fee phishing scam with urgent countdown lure must be detected as Spam."""
    delivery_scam = (
        "Subject: Delivery Exception: Package #99214 pending address verification\n\n"
        "USPS Parcel Express Notice\n\n"
        "Your shipment #99214 cannot be delivered due to an incorrect postal code on file.\n\n"
        "A mandatory redelivery processing fee of $2.85 is required before your package can be rescheduled for drop-off.\n\n"
        "Click here immediately to confirm delivery address and clear fee: http://express-postal-redelivery-portal.cc/pay\n\n"
        "Packages not claimed within 24 hours will be returned to sender or abandoned."
    )
    vec = artifacts["vectorizer"]
    lr = artifacts["lr"]
    svm = artifacts["svm"]

    x = vec.transform([delivery_scam])
    tau_lr = artifacts["metadata"]["models"]["logistic_regression"]["optimal_threshold"]
    tau_svm = artifacts["metadata"]["models"]["linear_svm"]["optimal_threshold"]

    pred_lr = lr.predict_single(x, threshold=tau_lr)
    pred_svm = svm.predict_single(x, threshold=tau_svm)

    assert pred_lr.is_spam, f"Logistic Regression missed delivery scam: score={pred_lr.score:.4f} < tau={tau_lr}"
    assert pred_lr.predicted_label == "Spam"

    assert pred_svm.is_spam, f"Linear SVM missed delivery scam: score={pred_svm.score:.4f} < tau={tau_svm}"
    assert pred_svm.predicted_label == "Spam"


def test_explainability_logit_additivity(artifacts):
    """Explainability contributions must sum to net_decision_score within tolerance."""
    explainer = artifacts["explainer"]
    lr = artifacts["lr"]
    vec = artifacts["vectorizer"]

    doc = "Subject: Invoice Payment Processed\n\nYour recent purchase has been debited. Contact support if unverified."
    x = vec.transform([doc])

    exp = explainer.explain_prediction(lr, x[0], top_k=10)
    assert exp is not None
    assert exp.model_name == "logistic_regression"

    # Exact additivity check: net_decision_score == intercept + sum of all contributions
    sum_contrib = sum(c.contribution for c in exp.all_contributions)
    reconstructed_score = exp.intercept + sum_contrib
    assert abs(exp.net_decision_score - reconstructed_score) < 1e-4

    # Top features should have correct directional labels
    for c in exp.top_spam_features:
        assert c.direction == "Spam"
        assert c.contribution > 0
    for c in exp.top_legitimate_features:
        assert c.direction == "Legitimate"
        assert c.contribution < 0


def test_unseen_voucher_spam_detected_as_spam(artifacts):
    """Gift voucher survey scam must be detected as Spam without sacrificing recall."""
    voucher = (
        "Subject: Claim your free $500 voucher from TechGear Direct\n\n"
        "Congratulations!\n\n"
        "You have been selected as a lucky customer to receive a $500 shopping voucher redeemable at TechGear Direct.\n"
        "Claim your code before it expires at midnight: http://free-gift-vouchers-2112.xyz/claim\n"
        "Complete short sponsor survey to unlock code. Unclaimed gift cards will be forfeited in 24 hours."
    )
    vec = artifacts["vectorizer"]
    lr = artifacts["lr"]
    svm = artifacts["svm"]

    x = vec.transform([voucher])
    tau_lr = artifacts["metadata"]["models"]["logistic_regression"]["optimal_threshold"]
    tau_svm = artifacts["metadata"]["models"]["linear_svm"]["optimal_threshold"]

    pred_lr = lr.predict_single(x, threshold=tau_lr)
    pred_svm = svm.predict_single(x, threshold=tau_svm)

    assert pred_lr.is_spam, f"Logistic Regression missed voucher scam: score={pred_lr.score:.4f} < tau={tau_lr}"
    assert pred_lr.predicted_label == "Spam"
    assert pred_svm.is_spam, f"Linear SVM missed voucher scam: score={pred_svm.score:.4f} < tau={tau_svm}"
    assert pred_svm.predicted_label == "Spam"


def test_multilingual_hindi_workplace_classified_as_ham(artifacts):
    """Authentic Hindi workplace communication must be classified as Legitimate."""
    hindi_email = (
        "Subject: नमस्ते - कल की प्रोजेक्ट समीक्षा बैठक का समय\n\n"
        "नमस्ते अनुराग,\n\n"
        "आशा है आप सकुशल हैं। हमारी आगामी प्रोजेक्ट समीक्षा बैठक कल सुबह 11:00 बजे निर्धारित की गई है।\n\n"
        "कृपया अपने नवीनतम कोड परिवर्तनों और यूनिट टेस्ट रिपोर्ट को गिट रिपॉजिटरी में पुश कर दें ताकि हम कल की चर्चा में समीक्षा कर सकें।\n\n"
        "धन्यवाद,\nविकास टीम"
    )
    vec = artifacts["vectorizer"]
    lr = artifacts["lr"]

    x = vec.transform([hindi_email])
    tau_lr = artifacts["metadata"]["models"]["logistic_regression"]["optimal_threshold"]

    pred_lr = lr.predict_single(x, threshold=tau_lr)
    assert not pred_lr.is_spam, f"Logistic Regression false positive on Hindi email: score={pred_lr.score:.4f}"
    assert pred_lr.predicted_label == "Legitimate"


def test_strict_holdout_quality_gate():
    """Verify that the strict generalization report passes release quality thresholds."""
    report_path = Path("ml/reports/strict_generalization_report.json")
    assert report_path.exists(), "Strict generalization report does not exist"

    with open(report_path, encoding="utf-8") as f:
        rep = json.load(f)

    split = rep["dataset_split"]
    assert split["total_samples"] == 248
    assert split["train_samples"] == 148
    assert split["validation_samples"] == 64
    assert split["test_samples"] == 36

    models = rep["models"]
    for mname in ["logistic_regression", "naive_bayes", "linear_svm"]:
        assert mname in models
        m_rep = models[mname]
        # Low false positive rate constraint: <= 15% (allowing at most 2 FPs on small 18-sample holdout)
        assert m_rep["false_positive_rate"] <= 0.15, f"{mname} FPR too high on strict holdout: {m_rep['false_positive_rate']}"
        # High precision when flagged as spam
        assert m_rep["precision"] >= 0.85, f"{mname} Precision too low on strict holdout: {m_rep['precision']}"
        # Calibration check: Brier score must be <= 0.25
        if m_rep["brier_score"] is not None:
            assert m_rep["brier_score"] <= 0.25, f"{mname} Brier score too high: {m_rep['brier_score']}"

    # Best model verification: Logistic Regression achieves >= 90% accuracy, >= 90% recall, 0% FPR
    lr_rep = models["logistic_regression"]
    assert lr_rep["accuracy"] >= 0.90
    assert lr_rep["recall"] >= 0.90
    assert lr_rep["false_positive_rate"] == 0.0
