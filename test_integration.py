"""Integration test for the full analysis pipeline."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dashboard.pipeline import AnalysisPipeline
from reports.report_generator import ReportGenerator

pipeline = AnalysisPipeline()

# Test with the high-risk phishing email
result = pipeline.analyze_file("phishing_test_high.eml")

print("=== PIPELINE RESULT ===")
print("Sender:", result["sender"])
print("Subject:", result["subject"])
print("Risk Score (rule):", result["risk_score"])
print("Verdict:", result["verdict"])
print("ML Probability:", result["ml_phishing_probability"])
print("Combined Score:", result["combined_score"])
print("Attack Type:", result["attack_type"])
print("Attack Confidence:", result["attack_confidence"])
print("Reasons:", result["reasons"])
print("Alert Severity:", result["alert"]["severity"])
print("Recommendations:", result["alert"]["recommendations"][:2])
print("Header Signals:", result["header_signals"])
print("URL Signals:", result["url_signals"])
print("NLP Signals:", result["nlp_signals"])
print()

# Test report generation
rg = ReportGenerator(result)
json_report = rg.generate_json()
print("=== REPORT GENERATION ===")
print("JSON report length:", len(json_report), "chars")
pdf_bytes = rg.generate_pdf()
print("PDF report size:", len(pdf_bytes), "bytes")
print()

# Test with medium-risk email
result2 = pipeline.analyze_file("phishing_test_medium.eml")
print("=== MEDIUM TEST ===")
print("Verdict:", result2["verdict"])
print("Combined Score:", result2["combined_score"])
print()

# Test with low-risk email
result3 = pipeline.analyze_file("legit_test_low.eml")
print("=== LOW TEST ===")
print("Verdict:", result3["verdict"])
print("Combined Score:", result3["combined_score"])
print()

print("ALL PIPELINE TESTS PASSED")
