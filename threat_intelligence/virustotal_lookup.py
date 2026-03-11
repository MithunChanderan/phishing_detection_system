"""
VirusTotal Lookup — URL reputation check via the VirusTotal API v3.

When no API key is configured the module returns simulated demo data
so the dashboard can still render the panel.
"""

import os
import requests


class VirusTotalLookup:
    """
    Queries VirusTotal for a URL's reputation.
    Reads the API key from the ``VIRUSTOTAL_API_KEY`` environment variable
    or accepts it explicitly at construction time.
    """

    API_URL = "https://www.virustotal.com/api/v3/urls"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("VIRUSTOTAL_API_KEY")

    # ------------------------------------------------------------------ #
    #  Public
    # ------------------------------------------------------------------ #

    def check_url(self, url: str) -> dict:
        """
        Return reputation stats for *url*.

        Keys:
            malicious, suspicious, harmless, undetected, demo_mode, error
        """
        if not self.api_key:
            return self._demo_result(url)

        try:
            return self._query_api(url)
        except Exception as exc:
            return {
                "url": url,
                "malicious": 0,
                "suspicious": 0,
                "harmless": 0,
                "undetected": 0,
                "demo_mode": False,
                "error": str(exc),
            }

    # ------------------------------------------------------------------ #
    #  Private
    # ------------------------------------------------------------------ #

    def _query_api(self, url: str) -> dict:
        """Submit URL to VT and parse the analysis stats."""
        import base64

        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        headers = {"x-apikey": self.api_key}
        resp = requests.get(f"{self.API_URL}/{url_id}", headers=headers, timeout=15)
        resp.raise_for_status()

        stats = (
            resp.json()
            .get("data", {})
            .get("attributes", {})
            .get("last_analysis_stats", {})
        )

        return {
            "url": url,
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "demo_mode": False,
            "error": None,
        }

    @staticmethod
    def _demo_result(url: str) -> dict:
        """Return plausible placeholder data when no API key is set."""
        return {
            "url": url,
            "malicious": 0,
            "suspicious": 0,
            "harmless": 0,
            "undetected": 0,
            "demo_mode": True,
            "error": None,
        }
