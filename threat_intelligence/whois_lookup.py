"""
WHOIS Lookup — domain registration data and age detection.
"""

from datetime import datetime, timezone


class WhoisLookup:
    """
    Looks up WHOIS data for a domain and calculates domain age.
    Falls back gracefully when the ``python-whois`` library is not
    installed or the query fails.
    """

    def lookup(self, domain: str) -> dict:
        """
        Return a dict with keys:
            registrar, creation_date, expiration_date, domain_age_days, raw_error
        """
        result = {
            "domain": domain,
            "registrar": None,
            "creation_date": None,
            "expiration_date": None,
            "domain_age_days": None,
            "raw_error": None,
        }

        try:
            import whois  # python-whois

            w = whois.whois(domain)

            result["registrar"] = w.registrar

            creation = w.creation_date
            if isinstance(creation, list):
                creation = creation[0]
            if creation:
                result["creation_date"] = str(creation)
                age = (datetime.now(timezone.utc) - creation.replace(tzinfo=timezone.utc)).days
                result["domain_age_days"] = max(age, 0)

            expiration = w.expiration_date
            if isinstance(expiration, list):
                expiration = expiration[0]
            if expiration:
                result["expiration_date"] = str(expiration)

        except ImportError:
            result["raw_error"] = "python-whois not installed"
        except Exception as exc:
            result["raw_error"] = str(exc)

        return result

    @staticmethod
    def is_newly_registered(domain_age_days: int | None, threshold: int = 90) -> bool:
        """Return True if the domain is younger than *threshold* days."""
        if domain_age_days is None:
            return False
        return domain_age_days < threshold
