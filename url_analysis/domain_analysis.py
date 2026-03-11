import tldextract

SUSPICIOUS_TLDS = {
    "zip", "mov", "click", "country", "top", "xyz", "tk"
}

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly"
}

class DomainAnalyzer:
    def __init__(self, url: str):
        self.url = url
        self.domain_data = tldextract.extract(url)

    def get_registered_domain(self) -> str:
        return f"{self.domain_data.domain}.{self.domain_data.suffix}"

    def is_shortened_url(self) -> bool:
        return self.get_registered_domain() in SHORTENERS

    def suspicious_tld(self) -> bool:
        return self.domain_data.suffix in SUSPICIOUS_TLDS

    def heuristic_new_domain(self) -> bool:
        """
        Placeholder for WHOIS-based age detection.
        Feb10 version uses naming heuristics.
        """
        domain = self.domain_data.domain
        return any(char.isdigit() for char in domain) or len(domain) > 20
