"""Unit tests for independent PhishingRiskEngine."""

import pytest
from mailshield_ml.phishing_risk import PhishingRiskEngine


@pytest.fixture
def engine():
    return PhishingRiskEngine()


def test_clean_benign_email(engine):
    text = "Hi Team, please find attached the meeting minutes from our sync earlier today. Let me know if you have any feedback."
    result = engine.evaluate_phishing_risk(text, sender="colleague@company.com", subject="Meeting Minutes")
    assert result.risk_level == "low"
    assert result.risk_score == 0.0
    assert len(result.indicators_triggered) == 0
    assert len(result.suspicious_urls) == 0


def test_legitimate_bank_otp_alert_not_flagged(engine):
    text = "Dear Customer, 482910 is your OTP for transaction of Rs 1,500.00 at Swiggy. Do not share this OTP with anyone, including bank officials."
    result = engine.evaluate_phishing_risk(text, sender="alerts@hdfcbank.com", subject="OTP for HDFC Bank Card")
    assert result.risk_level == "low"
    assert result.risk_score <= 0.15
    assert not result.has_spoofed_brand


def test_spoofed_sbi_phishing_attack(engine):
    text = "Dear customer, your SBI bank account will be blocked within 24 hours. Please update your KYC immediately at http://sbi-kyc-update.com/login to restore access."
    result = engine.evaluate_phishing_risk(text, sender="support@sbi-kyc-update.com", subject="URGENT: SBI Account Blocked")
    assert result.risk_level in ("high", "critical")
    assert result.risk_score >= 0.60
    assert result.has_urgency_threat is True
    assert result.has_spoofed_brand is True
    assert result.has_credential_harvesting is True
    assert any("sbi-kyc-update.com" in url for url in result.suspicious_urls)


def test_shortened_url_and_ip_host_links(engine):
    text = "Your package delivery failed. Please reschedule and pay redelivery fee at http://bit.ly/pkg-redelivery or http://192.168.1.100/pay"
    result = engine.evaluate_phishing_risk(text, sender="notice@post.com", subject="Package status")
    assert result.risk_level in ("medium", "high", "critical")
    assert len(result.suspicious_urls) == 2
    assert any("bit.ly" in url for url in result.suspicious_urls)
    assert any("192.168.1.100" in url for url in result.suspicious_urls)


def test_multilingual_phishing_lure_hindi(engine):
    text = "आपका बैंक खाता 24 ghante mein band kar diya jayega. Apna pan card details update karne ke liye http://bank-update-pan.net/kyc par click kijiye."
    result = engine.evaluate_phishing_risk(text, sender="kyc@bank-update-pan.net", subject="चेतावनी: खाता बंद")
    assert result.risk_level in ("medium", "high", "critical")
    assert result.has_urgency_threat is True
    assert result.has_credential_harvesting is True


def test_sender_brand_spoofing(engine):
    text = "Your monthly statement is ready for review."
    result = engine.evaluate_phishing_risk(text, sender="service@hdfc-fake-alert.com", subject="Statement")
    assert result.has_spoofed_brand is True
    assert any(ind["category"] == "spoofed_brand" for ind in result.indicators_triggered)


def test_brand_substring_not_flagged_as_false_positive(engine):
    text = "Check out our summer products and store orders at https://www.snapple.com and https://pineapple.com"
    result = engine.evaluate_phishing_risk(text, sender="news@snapple.com", subject="Summer Deals")
    assert result.has_spoofed_brand is False
    assert not any(ind["category"] == "spoofed_brand" for ind in result.indicators_triggered)


def test_malicious_email_with_defensive_otp_lure_not_dampened(engine):
    text = "Dear Customer, 482910 is your OTP. Do not share this OTP with anyone. Click here to verify your account: http://secure-bank-login.com/login"
    result = engine.evaluate_phishing_risk(text, sender="security@untrusted-domain.com", subject="OTP Verification")
    assert result.risk_level in ("medium", "high", "critical")
    assert result.risk_score >= 0.25
    assert len(result.suspicious_urls) > 0
    assert any("secure-bank-login.com" in u for u in result.suspicious_urls)

