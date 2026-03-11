from scoring.risk_engine import RiskEngine
from nlp_analysis.tone_analyzer import ToneAnalyzer
from nlp_analysis.sentiment_engine import SentimentEngine


def run_scenario(header_signals, url_signals, nlp_text=None, nlp_signals=None):
    engine = RiskEngine()

    # NLP from text (dynamic)
    if nlp_text:
        tone = ToneAnalyzer(nlp_text)
        sentiment = SentimentEngine(nlp_text)

        nlp_signals = {
            "urgency_score": tone.urgency_score(),
            "fear_score": tone.fear_score(),
            "authority_score": tone.authority_score(),
            "imperative_language": tone.imperative_language(),
            "sentiment_polarity": sentiment.polarity()
        }

    engine.evaluate_headers(header_signals)
    engine.evaluate_urls(url_signals)
    engine.evaluate_nlp(nlp_signals)

    return engine.result()


# =========================
# SCENARIO 1 — CLEAR PHISHING
# =========================
print(run_scenario(
    header_signals={
        "spf": "fail",
        "dkim_present": False,
        "from_return_path_mismatch": True,
        "display_name_spoofing": True
    },
    url_signals={
        "shortened": True,
        "suspicious_tld": True,
        "heuristic_new_domain": False
    },
    nlp_text="""
    URGENT: Your PayPal account has been suspended.
    Verify immediately to avoid permanent closure.
    """
))


# =========================
# SCENARIO 2 — LEGITIMATE EMAIL
# =========================
print(run_scenario(
    header_signals={
        "spf": "pass",
        "dkim_present": True,
        "from_return_path_mismatch": False,
        "display_name_spoofing": False
    },
    url_signals={
        "shortened": False,
        "suspicious_tld": False,
        "heuristic_new_domain": False
    },
    nlp_signals={
        "urgency_score": 0,
        "fear_score": 0,
        "authority_score": 0,
        "imperative_language": False,
        "sentiment_polarity": 0.5
    }
))


# =========================
# SCENARIO 3 — GRAY ZONE
# =========================
print(run_scenario(
    header_signals={
        "spf": "softfail",
        "dkim_present": True,
        "from_return_path_mismatch": False,
        "display_name_spoofing": True
    },
    url_signals={
        "shortened": False,
        "suspicious_tld": True,
        "heuristic_new_domain": True
    },
    nlp_signals={
        "urgency_score": 2,
        "fear_score": 1,
        "authority_score": 1,
        "imperative_language": True,
        "sentiment_polarity": -0.3
    }
))
