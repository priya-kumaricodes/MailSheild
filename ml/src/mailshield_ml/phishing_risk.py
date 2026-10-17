"""Decoupled Phishing Risk Evaluation Engine.
Evaluates heuristic and behavioral indicators of phishing attacks independently of
the statistical spam classifier probability.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class PhishingIndicator:
    id: str
    category: str  # "credential_harvesting", "urgency_coercion", "suspicious_link", "spoofed_brand", "malicious_attachment"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    weight: float


@dataclass
class PhishingRiskResult:
    risk_score: float  # 0.0 to 1.0
    risk_level: str  # "low", "medium", "high", "critical"
    indicators_triggered: list[dict] = field(default_factory=list)
    suspicious_urls: list[str] = field(default_factory=list)
    has_credential_harvesting: bool = False
    has_urgency_threat: bool = False
    has_spoofed_brand: bool = False
    explanation: str = ""

    def to_dict(self) -> dict:
        return {
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "indicators_triggered": self.indicators_triggered,
            "suspicious_urls": self.suspicious_urls,
            "has_credential_harvesting": self.has_credential_harvesting,
            "has_urgency_threat": self.has_urgency_threat,
            "has_spoofed_brand": self.has_spoofed_brand,
            "explanation": self.explanation,
        }


class PhishingRiskEngine:
    """Analyzes message text and extracted links for phishing risk."""

    # Well-known Indian and global financial/technology brands frequently targeted
    TARGETED_BRANDS = [
        "sbi", "statebank", "hdfc", "icici", "axisbank", "pnb", "bob", "kotak",
        "paytm", "phonepe", "gpay", "paypal", "apple", "google", "microsoft",
        "amazon", "netflix", "incometax", "uidai", "aadhaar",
    ]

    # Legitimate primary domains for these brands
    LEGITIMATE_BRAND_DOMAINS = {
        "sbi": {"sbi.co.in", "onlinesbi.sbi", "onlinesbi.com"},
        "statebank": {"sbi.co.in", "onlinesbi.sbi"},
        "hdfc": {"hdfcbank.com", "hdfc.com"},
        "icici": {"icicibank.com"},
        "axisbank": {"axisbank.com"},
        "pnb": {"pnbindia.in"},
        "kotak": {"kotak.com"},
        "paytm": {"paytm.com"},
        "phonepe": {"phonepe.com"},
        "google": {"google.com", "google.co.in"},
        "apple": {"apple.com", "icloud.com"},
        "microsoft": {"microsoft.com", "live.com", "office.com"},
        "amazon": {"amazon.com", "amazon.in"},
        "paypal": {"paypal.com"},
        "netflix": {"netflix.com"},
        "incometax": {"incometax.gov.in"},
        "uidai": {"uidai.gov.in"},
        "aadhaar": {"uidai.gov.in"},
    }

    # URL Shorteners often used in SMS / email phishing
    SHORTENERS = {
        "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "buff.ly",
        "ow.ly", "cutt.ly", "rb.gy", "shorturl.at", "tiny.cc",
    }

    # Sensitive credentials / identity tokens
    CREDENTIAL_KEYWORDS = [
        r"\b(password|passwd|pin|cvv|otp|secret\s+code|passcode)\b",
        r"\b(netbanking\s+password|login\s+id|card\s+number)\b",
        r"\b(aadhaar\s+number|pan\s+card\s+details)\b",
    ]

    # Solicitation phrases (asking user to submit/enter/verify credentials)
    SOLICITATION_PHRASES = [
        r"(enter|submit|provide|fill|send|share|confirm|verify)\s+(your|the)?\s*(password|pin|cvv|otp|credentials|login|account\s+details)",
        r"(apna|apni)\s+(password|pin|cvv|otp|khata|pan|aadhaar)",
        r"(update|verify)\s+(your|apna|apni)\s+(kyc|pan|aadhaar)",
        r"(kyc|pan|aadhaar)\s+(update|verify|details)",
    ]

    # Urgency & Coercive Threats
    URGENCY_PHRASES = [
        r"\b(immediately|within\s+24\s+hours|within\s+12\s+hours|account\s+suspended|deactivated|terminated|will\s+be\s+blocked)\b",
        r"\b(action\s+required|urgent\s+notice|last\s+warning|final\s+notice)\b",
        r"(turant|24\s+ghante|band\s+kar\s+diya\s+jayega|block\s+hoga|khata\s+rok\s+diya)",
        r"(तुरंत|24\s*घंटे|बंद\s*कर\s*दिया|निलंबित|ब्लॉक|अंतिम\s*चेतावनी|अति\s*आवश्यक)",  # Hindi Devanagari urgency phrases
        r"(இடைநிறுத்தப்பட்டுள்ளது|உடனே|வழங்கப்படாது|எச்சரிக்கை|அவசரம்)",  # Tamil urgent phrases
        r"(తక్షణమే|నిలిపివేయబడుతుంది|ముగిసింది|హెచ్చరిక|అత్యవసరం)",      # Telugu urgent phrases
        r"(ತಕ್ಷಣ|ಅಮಾನತುಗೊಳಿಸಲಾಗಿದೆ|ಬಾಕಿ|ಎಚ್ಚರಿಕೆ|ತುರ್ತು)",            # Kannada urgent phrases
    ]

    # Benign defensive advice phrases (e.g., standard "Do not share OTP")
    DEFENSIVE_ADVICE = [
        r"do\s+not\s+share\s+(this\s+)?(otp|pin|password)",
        r"never\s+share\s+(your\s+)?(otp|password|pin)",
        r"bank\s+never\s+asks\s+for\s+(your\s+)?(otp|pin|password)",
        r"kisi\s+ke\s+saath\s+share\s+na\s+karein",
        r"kisi\s+ko\s+na\s+bataen",
    ]

    def __init__(self):
        self._url_regex = re.compile(
            r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s]*)?|"
            r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?(?:/[^\s]*)?",
            re.IGNORECASE,
        )

    def extract_urls(self, text: str) -> list[str]:
        return self._url_regex.findall(text)

    def evaluate_phishing_risk(
        self,
        text: str,
        sender: str | None = None,
        subject: str | None = None,
    ) -> PhishingRiskResult:
        full_text = f"{subject or ''} {text or ''}"
        full_text_lower = full_text.lower()
        urls = self.extract_urls(full_text)

        indicators: list[PhishingIndicator] = []
        suspicious_urls: list[str] = []
        has_cred = False
        has_urgency = False
        has_spoof = False

        # 1. URL Analysis
        for url in urls:
            try:
                parsed = urlparse(url)
                hostname = (parsed.hostname or "").lower()
                path = (parsed.path or "").lower()

                # IP Address used as host
                if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
                    suspicious_urls.append(url)
                    indicators.append(PhishingIndicator(
                        id="ip_host_url",
                        category="suspicious_link",
                        severity="high",
                        description=f"Direct IP address used as URL host ({hostname})",
                        weight=0.35,
                    ))

                # URL shortener
                if hostname in self.SHORTENERS:
                    suspicious_urls.append(url)
                    indicators.append(PhishingIndicator(
                        id="shortened_url",
                        category="suspicious_link",
                        severity="medium",
                        description=f"Shortened link detected ({hostname}) masking target destination",
                        weight=0.20,
                    ))

                # Brand spoofing in domain / subdomains (e.g. sbi-kyc-portal.com or hdfc.bank-verify.net)
                host_tokens = [t.lower() for t in re.split(r"[.\-_0-9]+", hostname) if t]
                for brand, leg_domains in self.LEGITIMATE_BRAND_DOMAINS.items():
                    if brand in host_tokens:
                        is_legit = any(hostname == ld or hostname.endswith("." + ld) for ld in leg_domains)
                        if not is_legit:
                            has_spoof = True
                            suspicious_urls.append(url)
                            indicators.append(PhishingIndicator(
                                id=f"spoofed_{brand}_domain",
                                category="spoofed_brand",
                                severity="critical",
                                description=f"Potential spoof of '{brand}' in untrusted domain '{hostname}'",
                                weight=0.45,
                            ))

                # Sensitive path targets on suspicious or unverified domains
                if any(p in path for p in ("/login", "/signin", "/verify", "/kyc", "/update-pan", "/security")):
                    # Check if host is not a known brand domain
                    is_known_brand = False
                    for leg_domains in self.LEGITIMATE_BRAND_DOMAINS.values():
                        if any(hostname == ld or hostname.endswith("." + ld) for ld in leg_domains):
                            is_known_brand = True
                            break
                    if not is_known_brand:
                        suspicious_urls.append(url)
                        indicators.append(PhishingIndicator(
                            id="credential_harvesting_path",
                            category="credential_harvesting",
                            severity="high",
                            description=f"Sensitive authentication or KYC path ('{path}') on external host",
                            weight=0.30,
                        ))
            except Exception:
                continue

        # 2. Check for Defensive Advice (e.g. Bank standard: "Do not share OTP")
        has_defensive_statement = any(re.search(pat, full_text_lower) for pat in self.DEFENSIVE_ADVICE)

        # 3. Urgency & Coercive Threats
        urgency_matches = [pat for pat in self.URGENCY_PHRASES if re.search(pat, full_text_lower)]
        if urgency_matches:
            has_urgency = True
            indicators.append(PhishingIndicator(
                id="urgency_coercion",
                category="urgency_coercion",
                severity="medium",
                description="Coercive or urgent psychological pressure detected (e.g. immediate suspension/block)",
                weight=0.25,
            ))

        # 4. Credential Harvesting Solicitation
        solicitation_matches = [pat for pat in self.SOLICITATION_PHRASES if re.search(pat, full_text_lower)]
        if solicitation_matches and not (has_defensive_statement and not urls):
            has_cred = True
            indicators.append(PhishingIndicator(
                id="credential_solicitation",
                category="credential_harvesting",
                severity="critical" if urls else "high",
                description="Active solicitation requesting user to enter or verify credentials / KYC details",
                weight=0.40 if urls else 0.20,
            ))

        # 5. Dangerous Attachments or Mentioned Executables
        if re.search(r"\b\w+\.(exe|scr|vbs|iso|apk|bat|cmd|ps1)\b", full_text_lower):
            indicators.append(PhishingIndicator(
                id="executable_attachment_reference",
                category="malicious_attachment",
                severity="high",
                description="Reference to executable or package file format (.exe, .scr, .apk)",
                weight=0.30,
            ))

        # 6. Sender Anomaly Check
        if sender and ("@" in sender):
            sender_lower = sender.lower()
            sender_domain = sender_lower.split("@", 1)[1] if "@" in sender_lower else sender_lower
            sender_tokens = [t.lower() for t in re.split(r"[.\-_0-9]+", sender_domain) if t]
            for brand, leg_domains in self.LEGITIMATE_BRAND_DOMAINS.items():
                if brand in sender_tokens:
                    is_legit = any(sender_lower.endswith("@" + ld) or sender_lower.endswith("." + ld) for ld in leg_domains)
                    if not is_legit:
                        has_spoof = True
                        indicators.append(PhishingIndicator(
                            id=f"sender_spoofed_{brand}",
                            category="spoofed_brand",
                            severity="high",
                            description=f"Sender address claims association with '{brand}' but originates from untrusted domain",
                            weight=0.35,
                        ))

        # Compute aggregate risk score
        if not indicators:
            risk_score = 0.0
            risk_level = "low"
            explanation = "No overt phishing or credential harvesting heuristics triggered."
        else:
            # Diminishing returns combination: score = 1 - prod(1 - w_i)
            cum_prob = 1.0
            for ind in indicators:
                cum_prob *= (1.0 - ind.weight)
            raw_score = 1.0 - cum_prob

            # If legitimate defensive advice is present with NO suspicious URLs, NO credential harvesting,
            # NO brand spoofing, and NO external links, dampen benign urgency to prevent false positives on genuine banking alerts.
            # Defensive advice must NEVER dampen an email if it contains credential harvesting, suspicious links,
            # brand spoofing, or external URLs.
            has_high_risk = any(
                ind.category in ("credential_harvesting", "suspicious_link", "spoofed_brand", "malicious_attachment")
                for ind in indicators
            )
            if has_defensive_statement and not has_high_risk and not suspicious_urls and not has_spoof and not urls:
                raw_score = min(raw_score, 0.15)

            risk_score = round(min(1.0, max(0.0, raw_score)), 3)

            if risk_score >= 0.70:
                risk_level = "critical"
            elif risk_score >= 0.45:
                risk_level = "high"
            elif risk_score >= 0.25:
                risk_level = "medium"
            else:
                risk_level = "low"

            reasons = [ind.description for ind in indicators]
            explanation = "; ".join(reasons)

        has_cred = any(ind.category == "credential_harvesting" for ind in indicators)
        has_urgency = any(ind.category == "urgency_coercion" for ind in indicators)
        has_spoof = any(ind.category == "spoofed_brand" for ind in indicators)

        return PhishingRiskResult(
            risk_score=risk_score,
            risk_level=risk_level,
            indicators_triggered=[
                {
                    "id": ind.id,
                    "category": ind.category,
                    "severity": ind.severity,
                    "description": ind.description,
                    "weight": ind.weight,
                }
                for ind in indicators
            ],
            suspicious_urls=list(set(suspicious_urls)),
            has_credential_harvesting=has_cred,
            has_urgency_threat=has_urgency,
            has_spoofed_brand=has_spoof,
            explanation=explanation,
        )
