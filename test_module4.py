from scoring.risk_engine import RiskEngine

header_signals = {
    "spf": "fail",
    "dkim_present": False,
    "from_return_path_mismatch": True,
    "display_name_spoofing": True
}

url_signals = {
    "shortened": True,
    "suspicious_tld": False,
    "heuristic_new_domain": False
}

nlp_signals = {
    "urgency_score": 2,
    "fear_score": 2,
    "authority_score": 1,
    "imperative_language": True,
    "sentiment_polarity": -0.7
}

engine = RiskEngine()
engine.evaluate_headers(header_signals)
engine.evaluate_urls(url_signals)
engine.evaluate_nlp(nlp_signals)

print(engine.result())
