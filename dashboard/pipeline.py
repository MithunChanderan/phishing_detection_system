"""
Analysis Pipeline — orchestrates the full phishing detection flow:

    Email → Parse → Header Auth → URL Analysis → NLP → Risk Scoring
       → ML Prediction → Threat Intel → Attack Classification → Alerts

All existing modules are **reused** without modification.
"""

import re
import tempfile
from email import policy
from email.parser import BytesParser

from parser.eml_parser import EMLParser
from parser.header_auth import HeaderAuthAnalyzer

from url_analysis.url_extractor import URLExtractor
from url_analysis.domain_analysis import DomainAnalyzer

from nlp_analysis.tone_analyzer import ToneAnalyzer
from nlp_analysis.sentiment_engine import SentimentEngine

from scoring.risk_engine import RiskEngine
from privacy.content_hashing import PrivacyGuard

from ml_detection.feature_extractor import FeatureExtractor
from ml_detection.phishing_classifier import PhishingClassifier

from threat_intelligence.whois_lookup import WhoisLookup
from threat_intelligence.virustotal_lookup import VirusTotalLookup
from threat_intelligence.attack_classifier import AttackClassifier

from alerts.alert_generator import AlertGenerator


class AnalysisPipeline:
    """
    End-to-end analysis pipeline.
    Call ``analyze_file(path)`` for .eml uploads or
    ``analyze_message(email_msg)`` for Gmail-fetched messages.
    """

    def __init__(self, vt_api_key: str | None = None):
        self.feature_extractor = FeatureExtractor()
        self.classifier = PhishingClassifier()
        self.whois = WhoisLookup()
        self.virustotal = VirusTotalLookup(api_key=vt_api_key)
        self.attack_classifier = AttackClassifier()
        self.alert_generator = AlertGenerator()

    # ------------------------------------------------------------------ #
    #  Public entry points
    # ------------------------------------------------------------------ #

    def analyze_file(self, eml_path: str) -> dict:
        """Analyse an .eml file on disk."""
        parser = EMLParser(eml_path)
        parser.load_email()
        headers = parser.get_headers()
        body = parser.get_body()
        return self._run(headers, body)

    def analyze_message(self, msg) -> dict:
        """Analyse an ``email.message.EmailMessage`` (e.g. from Gmail)."""
        raw = msg.as_bytes()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as tmp:
            tmp.write(raw)
            tmp_path = tmp.name
        return self.analyze_file(tmp_path)

    # ------------------------------------------------------------------ #
    #  Core pipeline
    # ------------------------------------------------------------------ #

    def _run(self, headers: dict, body: dict) -> dict:
        text_body = body.get("text", "")
        html_body = body.get("html", "")
        full_text = text_body or html_body

        # ---- Metadata ----
        sender = headers.get("From", "Unknown")
        subject = headers.get("Subject", "(no subject)")

        # ---- 1. Header authentication ----
        header_auth = HeaderAuthAnalyzer(headers)
        header_signals = {
            "spf": header_auth.check_spf(),
            "dkim_present": header_auth.check_dkim(),
            "from_return_path_mismatch": header_auth.from_return_path_mismatch(),
            "display_name_spoofing": header_auth.display_name_spoofing(),
        }

        # ---- 2. URL analysis ----
        extractor = URLExtractor(full_text)
        urls = extractor.extract_urls()

        url_signals = {
            "shortened": False,
            "suspicious_tld": False,
            "heuristic_new_domain": False,
        }
        analyzed_urls: list[dict] = []

        for url in urls:
            da = DomainAnalyzer(url)
            url_signals["shortened"] |= da.is_shortened_url()
            url_signals["suspicious_tld"] |= da.suspicious_tld()
            url_signals["heuristic_new_domain"] |= da.heuristic_new_domain()
            analyzed_urls.append({
                "url": url,
                "domain": da.get_registered_domain(),
                "shortened": da.is_shortened_url(),
                "suspicious_tld": da.suspicious_tld(),
                "heuristic_new": da.heuristic_new_domain(),
            })

        # ---- 3. NLP analysis ----
        tone = ToneAnalyzer(full_text)
        sentiment = SentimentEngine(full_text)

        nlp_signals = {
            "urgency_score": tone.urgency_score(),
            "fear_score": tone.fear_score(),
            "authority_score": tone.authority_score(),
            "imperative_language": tone.imperative_language(),
            "sentiment_polarity": sentiment.polarity(),
            "sentiment_subjectivity": sentiment.subjectivity(),
        }

        # ---- 4. Rule-based risk scoring ----
        engine = RiskEngine()
        engine.evaluate_headers(header_signals)
        engine.evaluate_urls(url_signals)
        engine.evaluate_nlp(nlp_signals)
        rule_result = engine.result()

        # ---- 5. ML prediction ----
        features = self.feature_extractor.extract(
            header_signals, url_signals, nlp_signals, url_count=len(urls)
        )
        ml_result = self.classifier.predict(features)

        # Combined score: 60 % rule-based + 40 % ML
        rule_norm = min(rule_result["risk_score"] / 100.0, 1.0)
        ml_prob = ml_result["phishing_probability"]
        combined = round((0.6 * rule_norm + 0.4 * ml_prob) * 100, 1)

        # ---- 6. Threat intelligence ----
        ti: dict = {"whois": {}, "virustotal": {}}
        primary_domain = self._extract_sender_domain(sender)
        if primary_domain:
            ti["whois"] = self.whois.lookup(primary_domain)
        if urls:
            ti["virustotal"] = self.virustotal.check_url(urls[0])

        # ---- 7. Attack classification ----
        attack = self.attack_classifier.classify(full_text, urls, subject)

        # ---- 8. Privacy ----
        masked_body = PrivacyGuard.mask_email_addresses(full_text)

        # ---- 9. Alert ----
        analysis_result = {
            "sender": sender,
            "subject": subject,
            "risk_score": rule_result["risk_score"],
            "verdict": rule_result["verdict"],
            "reasons": rule_result["reasons"],
            "header_signals": header_signals,
            "url_signals": url_signals,
            "urls": analyzed_urls,
            "url_count": len(urls),
            "nlp_signals": nlp_signals,
            "ml_phishing_probability": ml_result["phishing_probability"],
            "ml_prediction": ml_result["prediction"],
            "combined_score": combined,
            "threat_intelligence": ti,
            "attack_type": attack["attack_type"],
            "attack_confidence": attack["confidence"],
            "attack_indicators": attack["matched_indicators"],
            "masked_body": masked_body,
            "raw_body": full_text,
        }

        alert = self.alert_generator.generate(analysis_result)
        analysis_result["alert"] = {
            "severity": alert.severity,
            "message": alert.message,
            "recommendations": alert.recommendations,
            "timestamp": alert.timestamp,
        }
        analysis_result["recommendations"] = alert.recommendations

        return analysis_result

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_sender_domain(sender: str) -> str | None:
        match = re.search(r"@([\w.-]+)", sender)
        return match.group(1) if match else None
