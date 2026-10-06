"""Unit tests for multilingual language identification and Indic normalization."""

import pytest
from mailshield_ml.language import LanguageIdentifier, normalize_indic_text


@pytest.fixture
def identifier():
    return LanguageIdentifier()


def test_normalize_indic_text_preserves_matras_and_virama():
    # Hindi text with matras and virama (halant)
    text = "नमस्ते भारत! आपका स्वागत है।"
    normalized = normalize_indic_text(text)
    assert "नमस्ते" in normalized
    assert "स्वागत" in normalized
    # Halant/virama \u094d should be preserved
    assert "\u094d" in normalized


def test_normalize_indic_text_preserves_zwnj_and_zwj():
    # Bengali/Hindi text with ZWNJ and ZWJ
    text = "क्\u200dष और क\u200cष"
    normalized = normalize_indic_text(text)
    assert "\u200d" in normalized
    assert "\u200c" in normalized


def test_empty_and_whitespace_input(identifier):
    res_empty = identifier.identify_language("")
    assert res_empty.language == "unknown"
    assert res_empty.confidence is None
    assert res_empty.detection_method == "insufficient_text"

    res_spaces = identifier.identify_language("    \n\t  ")
    assert res_spaces.language == "unknown"
    assert res_spaces.confidence is None
    assert res_spaces.detection_method == "insufficient_text"


def test_short_message_uncertain(identifier):
    # Less than 3 words in Latin script
    res = identifier.identify_language("Hello ok")
    assert res.language == "unknown"
    assert res.confidence is None
    assert res.detection_method == "uncertain"
    assert "fewer than 3 words" in (res.warning or "")


def test_symbols_and_numbers_only(identifier):
    # Only numbers, punctuation, or emoji
    res = identifier.identify_language("12345 67890 $$$ !!! 🚀🎉")
    assert res.language == "unknown"
    assert res.confidence is None
    assert res.detection_method == "insufficient_text"


def test_devanagari_hindi_detection(identifier):
    text = "प्रिय ग्राहक, आपका बिजली का बिल बकाया है। कृपया तुरंत भुगतान करें अन्यथा कनेक्शन काट दिया जाएगा।"
    res = identifier.identify_language(text)
    assert res.language == "hi"
    assert res.primary_script == "Devanagari"
    assert res.confidence is not None
    assert res.confidence > 0.8
    assert res.detection_method == "script_analysis"


def test_tamil_detection(identifier):
    text = "அன்புள்ள வாடிக்கையாளரே, உங்கள் கணக்கு தற்காலிகமாக இடைநிறுத்தப்பட்டுள்ளது. விவரங்களை உடனே புதுப்பிக்கவும்."
    res = identifier.identify_language(text)
    assert res.language == "ta"
    assert res.primary_script == "Tamil"
    assert res.confidence is not None
    assert res.confidence > 0.8


def test_telugu_detection(identifier):
    text = "ప్రియమైన వినియోగదారు, మీ బ్యాంక్ ఖాతా కేవైసీ గడువు ముగిసింది. దయచేసి వెంటనే అప్‌డేట్ చేయండి."
    res = identifier.identify_language(text)
    assert res.language == "te"
    assert res.primary_script == "Telugu"
    assert res.confidence is not None
    assert res.confidence > 0.8


def test_kannada_detection(identifier):
    text = "ಆತ್ಮೀಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ಸಂಬಂಧಿಸಿದ ಕೆವೈಸಿ ಬಾಕಿ ಇದೆ. ದಯವಿಟ್ಟು ತಕ್ಷಣ ನವೀಕರಿಸಿ."
    res = identifier.identify_language(text)
    assert res.language == "kn"
    assert res.primary_script == "Kannada"
    assert res.confidence is not None
    assert res.confidence > 0.8


def test_english_detection(identifier):
    text = "Dear customer, your quarterly account statement is ready for review. Please find the attached document for full details."
    res = identifier.identify_language(text)
    assert res.language == "en"
    assert res.primary_script == "Latin"
    assert res.confidence is not None
    assert res.confidence > 0.7
    assert res.detection_method == "lexicon_analysis"


def test_hinglish_detection(identifier):
    text = "Aapka SBI bank khata band ho jayega. Kripya turant KYC update karein aur apna inaam paane ke liye link pe click kijiye."
    res = identifier.identify_language(text)
    assert res.language == "hinglish"
    assert res.primary_script == "Latin"
    assert res.confidence is not None
    assert res.confidence > 0.7
    assert res.detection_method == "lexicon_analysis"


def test_mixed_script_detection(identifier):
    # Hindi Devanagari + English Latin words
    text = "प्रिय ग्राहक, your account KYC is pending. कृपया तुरंत verify करें via https://fake-bank-update.com"
    res = identifier.identify_language(text)
    assert res.language == "hi"
    assert res.is_mixed is True
    assert res.detection_method == "mixed_script"
    assert "Devanagari" in res.scripts_detected
    assert "Latin" in res.scripts_detected


def test_emoji_and_urls_do_not_distort_language(identifier):
    text = "🔥🔥 ALERT! Aapka account suspend hone wala hai kripya turant login karein https://scam.example.com/login 🔥🔥"
    res = identifier.identify_language(text)
    assert res.language == "hinglish"
    assert res.primary_script == "Latin"
