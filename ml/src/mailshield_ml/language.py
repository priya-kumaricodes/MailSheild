"""Language identification and Indic Unicode normalization.
Supports English, Hindi (Devanagari), Tamil, Telugu, Kannada, Hinglish (Romanized Indic),
and mixed-script messages without external heavyweight dependencies.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


@dataclass
class LanguageIdentificationResult:
    """Structured result of language and script identification."""

    language: str  # "en", "hi", "ta", "te", "kn", "hinglish", or "unknown"
    confidence: float | None  # 0.0 - 1.0 where calibrated, None if uncertain
    detection_method: str  # "script_analysis", "lexicon_analysis", "mixed_script", "uncertain", "insufficient_text"
    is_mixed: bool = False
    primary_script: str = "Unknown"
    scripts_detected: dict[str, float] = field(default_factory=dict)
    warning: str | None = None

    def to_dict(self) -> dict:
        return {
            "language": self.language,
            "confidence": self.confidence,
            "detection_method": self.detection_method,
            "is_mixed": self.is_mixed,
            "primary_script": self.primary_script,
            "scripts_detected": self.scripts_detected,
            "warning": self.warning,
        }


def normalize_indic_text(text: str) -> str:
    """Normalize text using Unicode NFKC while preserving Indic combining characters,

    virama/halant, matras, and essential joiners (ZWJ/ZWNJ).
    """
    if not text:
        return ""

    # NFKC normalizes compatibility characters while preserving canonical decomposition
    normalized = unicodedata.normalize("NFKC", text)

    # Clean non-printable control characters except standard whitespace,
    # preserving Zero-Width Joiner (\u200D) and Zero-Width Non-Joiner (\u200C)
    cleaned_chars = []
    for c in normalized:
        code = ord(c)
        if c in ("\n", "\r", "\t", "\u200C", "\u200D"):
            cleaned_chars.append(c)
        elif 0 <= code <= 31 or 127 <= code <= 159:
            cleaned_chars.append(" ")
        else:
            cleaned_chars.append(c)

    cleaned = "".join(cleaned_chars)
    # Collapse multiple horizontal whitespace characters while preserving newlines
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in cleaned.splitlines()]
    return "\n".join(line for line in lines if line).strip()


class LanguageIdentifier:
    """Identifies email language using script analysis and Romanized Indic lexicon patterns."""

    # Script Unicode code point ranges
    SCRIPT_RANGES = {
        "Devanagari": (0x0900, 0x097F, "hi"),
        "Tamil": (0x0B80, 0x0BFF, "ta"),
        "Telugu": (0x0C00, 0x0C7F, "te"),
        "Kannada": (0x0C80, 0x0CFF, "kn"),
        "Latin": (0x0041, 0x024F, "latin"),
    }

    # Tokens that are almost uniquely Indic/Hinglish and never appear in English
    STRONG_INDIC_LEXICON = {
        "aap", "aapka", "aapke", "aapki", "humara", "tumhara", "tumhari",
        "unka", "unki", "unke", "uska", "uski", "uske", "kiska", "kiski",
        "isko", "usko", "inko", "unko", "ismein", "usmein",
        "karein", "kijiye", "karna", "karega", "karegi", "kiya", "kiye",
        "hoga", "hogi", "hoge", "chahiye", "sakta", "sakti", "sakte",
        "khata", "paisa", "paise", "rupaye", "inaam", "jeeta", "jeete",
        "muft", "shulk", "bima", "yojana", "sarkari", "naukri", "kamaye",
        "kamayein", "kripya", "turant", "sampark", "suchna", "namaste",
        "dhanyawad", "badhaai", "mubarak", "crore", "lakh", "suraksha",
        "aavedan", "kendra", "adhikari", "bhejo", "bhejein", "dekho",
        "batayein", "batao", "badlo", "samjho", "milega", "milegi", "milenge",
    }

    # Extended Hinglish vocabulary excluding English homographs (in, is, the, to, do, us, me, he, no, so)
    HINGLISH_LEXICON = {
        # Pronouns, postpositions, and conjunctions
        "aap", "aapka", "aapke", "aapki", "hum", "humara", "mera", "meri", "mere",
        "tera", "teri", "tere", "tumhara", "tumhari", "unka", "unki", "unke",
        "uska", "uski", "uske", "kiska", "kiski", "kiske", "yeh", "woh",
        "isko", "usko", "inko", "unko", "ismein", "usmein", "isse", "usse",
        "ko", "se", "ka", "ki", "ke", "mein", "par", "pe",
        "aur", "ya", "bhi", "toh", "hi", "tak", "liye", "bina", "saath",
        # Verbs and auxiliaries
        "hai", "hain", "ho", "hoon", "tha", "thi", "thhe", "hoga", "hogi", "hoge",
        "karna", "karo", "karein", "kijiye", "kiya", "kiye", "karega", "karegi",
        "hona", "hua", "hui", "hue", "dena", "dein", "dijiye", "diya",
        "lena", "lein", "liya", "aana", "aao", "aaye", "aayega", "aayegi",
        "jaana", "jao", "jaaye", "jaayega", "milega", "milegi", "milein", "milenge",
        "bhejo", "bhejein", "dekho", "dekhein", "bolo", "batao", "batayein",
        "rakho", "rakhein", "badlo", "suno", "samjho", "chahiye", "sakta", "sakti", "sakte",
        # Financial, transactional, and scam terms common in Indian SMS/emails
        "khata", "paisa", "paise", "rupaye", "inaam", "jeeta", "jeete", "muft",
        "shulk", "bima", "yojana", "sarkari", "naukri", "kamaye", "kamayein",
        "kamana", "dhan", "kripya", "turant", "sampark", "suchna", "namaste",
        "dhanyawad", "badhaai", "mubarak", "crore", "lakh", "dar", "khatra",
        "suraksha", "sandesh", "samay", "aavedan", "kendra", "adhikari",
    }

    # English common function words for contrast
    ENGLISH_STOPWORDS = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "say", "her",
        "she", "or", "an", "will", "my", "one", "all", "would", "there",
        "their", "what", "so", "up", "out", "if", "about", "who", "get",
        "which", "go", "me", "when", "make", "can", "like", "time", "no",
        "just", "him", "know", "take", "people", "into", "year", "your",
        "good", "some", "could", "them", "see", "other", "than", "then",
        "now", "look", "only", "come", "its", "over", "think", "also",
        "back", "after", "use", "two", "how", "our", "work", "first",
        "well", "way", "even", "new", "want", "because", "any", "these",
        "give", "day", "most", "us", "is", "are", "was", "were", "been",
        "has", "had", "does", "did", "please", "dear", "regards", "sincerely",
        "attached", "information", "account", "verification", "service", "customer",
    }

    def __init__(self):
        # Precompile token matching patterns
        self._word_re = re.compile(r"(?u)\b\w+\b")
        self._url_re = re.compile(r"https?://\S+|www\.\S+")
        self._num_re = re.compile(r"\b\d+\b")

    def _strip_urls_and_numbers(self, text: str) -> str:
        t = self._url_re.sub(" ", text)
        t = self._num_re.sub(" ", t)
        return t

    def identify_language(self, text: str) -> LanguageIdentificationResult:
        """Analyze message text and return language, confidence, script, and diagnostics."""
        if not text or not text.strip():
            return LanguageIdentificationResult(
                language="unknown",
                confidence=None,
                detection_method="insufficient_text",
                primary_script="None",
                warning="Input text is empty or contains only whitespace.",
            )

        norm_text = normalize_indic_text(text)
        text_no_urls = self._strip_urls_and_numbers(norm_text)

        # Count characters per Unicode script
        script_counts: dict[str, int] = {}
        total_script_chars = 0

        for char in text_no_urls:
            code = ord(char)
            # Only consider letters and combining marks
            cat = unicodedata.category(char)
            if not (cat.startswith("L") or cat.startswith("M")):
                continue

            matched_script = None
            for sname, (s_start, s_end, _) in self.SCRIPT_RANGES.items():
                if s_start <= code <= s_end:
                    matched_script = sname
                    break

            if matched_script:
                script_counts[matched_script] = script_counts.get(matched_script, 0) + 1
                total_script_chars += 1

        # Insufficient linguistic content check (e.g., only numbers, URLs, or symbols)
        if total_script_chars < 5:
            return LanguageIdentificationResult(
                language="unknown",
                confidence=None,
                detection_method="insufficient_text",
                primary_script="None",
                warning="Message contains insufficient linguistic characters for reliable language identification.",
            )

        # Calculate script ratios
        script_ratios = {s: round(c / total_script_chars, 4) for s, c in script_counts.items()}
        sorted_scripts = sorted(script_ratios.items(), key=lambda x: x[1], reverse=True)
        primary_script, primary_ratio = sorted_scripts[0]

        is_mixed = len([r for r in script_ratios.values() if r >= 0.15]) > 1

        # Case 1: Devanagari script (Hindi)
        if script_ratios.get("Devanagari", 0) >= 0.30:
            ratio = script_ratios["Devanagari"]
            # Calibrated confidence based on dominant script fraction
            confidence = min(0.99, round(0.70 + 0.29 * ratio, 3))
            return LanguageIdentificationResult(
                language="hi",
                confidence=confidence,
                detection_method="mixed_script" if is_mixed else "script_analysis",
                is_mixed=is_mixed,
                primary_script="Devanagari",
                scripts_detected=script_ratios,
            )

        # Case 2: Tamil script
        if script_ratios.get("Tamil", 0) >= 0.30:
            ratio = script_ratios["Tamil"]
            confidence = min(0.99, round(0.70 + 0.29 * ratio, 3))
            return LanguageIdentificationResult(
                language="ta",
                confidence=confidence,
                detection_method="mixed_script" if is_mixed else "script_analysis",
                is_mixed=is_mixed,
                primary_script="Tamil",
                scripts_detected=script_ratios,
            )

        # Case 3: Telugu script
        if script_ratios.get("Telugu", 0) >= 0.30:
            ratio = script_ratios["Telugu"]
            confidence = min(0.99, round(0.70 + 0.29 * ratio, 3))
            return LanguageIdentificationResult(
                language="te",
                confidence=confidence,
                detection_method="mixed_script" if is_mixed else "script_analysis",
                is_mixed=is_mixed,
                primary_script="Telugu",
                scripts_detected=script_ratios,
            )

        # Case 4: Kannada script
        if script_ratios.get("Kannada", 0) >= 0.30:
            ratio = script_ratios["Kannada"]
            confidence = min(0.99, round(0.70 + 0.29 * ratio, 3))
            return LanguageIdentificationResult(
                language="kn",
                confidence=confidence,
                detection_method="mixed_script" if is_mixed else "script_analysis",
                is_mixed=is_mixed,
                primary_script="Kannada",
                scripts_detected=script_ratios,
            )

        # Case 5: Latin Script -> Disambiguate English vs Hinglish / Romanized Indic
        if primary_script == "Latin":
            return self._disambiguate_latin_language(norm_text, script_ratios, is_mixed)

        # Case 6: Other / Ambiguous scripts
        return LanguageIdentificationResult(
            language="unknown",
            confidence=None,
            detection_method="uncertain",
            is_mixed=is_mixed,
            primary_script=primary_script,
            scripts_detected=script_ratios,
            warning="Dominant script does not correspond to a supported language target.",
        )

    def _disambiguate_latin_language(
        self,
        text: str,
        script_ratios: dict[str, float],
        is_mixed: bool,
    ) -> LanguageIdentificationResult:
        """Disambiguate Latin script text between English and Hinglish using lexical evidence."""
        tokens = [w.lower() for w in self._word_re.findall(text) if len(w) >= 2]

        if len(tokens) < 3:
            # Too few words to make a confident distinction
            return LanguageIdentificationResult(
                language="unknown",
                confidence=None,
                detection_method="uncertain",
                is_mixed=is_mixed,
                primary_script="Latin",
                scripts_detected=script_ratios,
                warning="Latin message has fewer than 3 words; language identification is uncertain.",
            )

        total_words = len(tokens)
        hinglish_matches = [t for t in tokens if t in self.HINGLISH_LEXICON]
        strong_indic_matches = [t for t in tokens if t in self.STRONG_INDIC_LEXICON]
        english_matches = [t for t in tokens if t in self.ENGLISH_STOPWORDS]

        hinglish_count = len(hinglish_matches)
        strong_indic_count = len(strong_indic_matches)
        english_count = len(english_matches)

        # Morphological suffix indicators for Romanized Hindi (e.g. kar-ein, kiji-ye, wa-la)
        indic_suffix_patterns = ("karein", "kijiye", "wali", "wala", "dari", "baazi")
        indic_suffix_count = sum(1 for t in tokens if any(t.endswith(sfx) for sfx in indic_suffix_patterns))
        distinct_hinglish = len(set(hinglish_matches))

        # Hinglish decision:
        # If strong indic words or indic suffixes are present, OR hinglish distinctly outweighs english
        is_hinglish = False
        if strong_indic_count >= 1 or indic_suffix_count >= 1:
            if hinglish_count >= english_count or strong_indic_count >= 2 or distinct_hinglish >= 2:
                is_hinglish = True
        elif distinct_hinglish >= 2 and hinglish_count > english_count:
            is_hinglish = True
        elif hinglish_count >= 3 and (hinglish_count / total_words) >= 0.20 and hinglish_count >= english_count:
            is_hinglish = True

        if is_hinglish:
            conf = min(0.98, round(0.60 + 0.38 * (hinglish_count / (hinglish_count + english_count + 1)), 3))
            return LanguageIdentificationResult(
                language="hinglish",
                confidence=conf,
                detection_method="lexicon_analysis",
                is_mixed=is_mixed or (english_count >= 2),
                primary_script="Latin",
                scripts_detected=script_ratios,
            )

        # English Classification Decision
        if english_count >= 2 or (english_count >= 1 and total_words <= 5 and hinglish_count == 0):
            conf = min(0.98, round(0.65 + 0.33 * (english_count / (english_count + hinglish_count + 1)), 3))
            return LanguageIdentificationResult(
                language="en",
                confidence=conf,
                detection_method="lexicon_analysis",
                is_mixed=is_mixed,
                primary_script="Latin",
                scripts_detected=script_ratios,
            )

        # Ambiguous Latin text (e.g. brand names, random jargon, unconfirmed Romanization)
        return LanguageIdentificationResult(
            language="unknown",
            confidence=None,
            detection_method="uncertain",
            is_mixed=is_mixed,
            primary_script="Latin",
            scripts_detected=script_ratios,
            warning="Insufficient lexical signals to distinguish between English and Hinglish.",
        )
