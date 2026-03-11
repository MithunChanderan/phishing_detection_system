"""
Report Generator — creates JSON and PDF security reports from
analysis results.
"""

import json
from datetime import datetime, timezone
from io import BytesIO


class ReportGenerator:
    """
    Produces exportable security reports in JSON and PDF formats.
    """

    def __init__(self, analysis: dict):
        self.analysis = analysis
        self.generated_at = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------ #
    #  JSON
    # ------------------------------------------------------------------ #

    def generate_json(self) -> str:
        """Return a pretty-printed JSON report string."""
        report = {
            "report_type": "Phishing Analysis Security Report",
            "generated_at": self.generated_at,
            **self.analysis,
        }
        return json.dumps(report, indent=2, default=str)

    # ------------------------------------------------------------------ #
    #  PDF
    # ------------------------------------------------------------------ #

    def generate_pdf(self) -> bytes:
        """
        Return a PDF report as bytes.
        Uses ``fpdf2``; falls back to a text-based PDF if unavailable.
        """
        try:
            return self._build_pdf_fpdf()
        except ImportError:
            return self._build_pdf_fallback()

    def _build_pdf_fpdf(self) -> bytes:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ---- Title ----
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(220, 50, 50)
        pdf.cell(0, 14, "Phishing Analysis Security Report", ln=True, align="C")
        pdf.ln(4)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f"Generated: {self.generated_at}", ln=True, align="C")
        pdf.ln(8)

        # ---- Summary ----
        self._section(pdf, "Risk Assessment")
        self._kv(pdf, "Risk Score", self.analysis.get("risk_score", "N/A"))
        self._kv(pdf, "Verdict", self.analysis.get("verdict", "N/A"))
        self._kv(pdf, "ML Probability", self.analysis.get("ml_phishing_probability", "N/A"))
        self._kv(pdf, "Combined Score", self.analysis.get("combined_score", "N/A"))
        pdf.ln(4)

        # ---- Attack classification ----
        self._section(pdf, "Attack Classification")
        self._kv(pdf, "Type", self.analysis.get("attack_type", "N/A"))
        self._kv(pdf, "Confidence", self.analysis.get("attack_confidence", "N/A"))
        pdf.ln(4)

        # ---- Detected indicators ----
        reasons = self.analysis.get("reasons", [])
        self._section(pdf, "Detected Indicators")
        if reasons:
            for r in reasons:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(60, 60, 60)
                pdf.cell(0, 7, f"  - {r}", ln=True)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, "  None", ln=True)
        pdf.ln(4)

        # ---- Threat intelligence ----
        ti = self.analysis.get("threat_intelligence", {})
        if ti:
            self._section(pdf, "Threat Intelligence")
            whois = ti.get("whois", {})
            if whois:
                self._kv(pdf, "Domain", whois.get("domain", "N/A"))
                self._kv(pdf, "Registrar", whois.get("registrar", "N/A"))
                self._kv(pdf, "Domain Age (days)", whois.get("domain_age_days", "N/A"))
            vt = ti.get("virustotal", {})
            if vt:
                self._kv(pdf, "VT Malicious", vt.get("malicious", "N/A"))
                self._kv(pdf, "VT Suspicious", vt.get("suspicious", "N/A"))
            pdf.ln(4)

        # ---- Recommendations ----
        recs = self.analysis.get("recommendations", [])
        if recs:
            self._section(pdf, "Security Recommendations")
            for r in recs:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(60, 60, 60)
                pdf.cell(0, 7, f"  - {r}", ln=True)

        buf = BytesIO()
        pdf.output(buf)
        return buf.getvalue()

    # ---- helpers ----

    @staticmethod
    def _section(pdf, title: str):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_draw_color(220, 50, 50)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

    @staticmethod
    def _kv(pdf, key: str, value):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(55, 7, f"{key}:")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, str(value), ln=True)

    def _build_pdf_fallback(self) -> bytes:
        """Minimal text-based fallback when fpdf2 is not installed."""
        text = f"PHISHING ANALYSIS REPORT\n{'=' * 40}\n"
        text += f"Generated: {self.generated_at}\n\n"
        text += json.dumps(self.analysis, indent=2, default=str)
        return text.encode("utf-8")
