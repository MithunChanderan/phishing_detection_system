from url_analysis.url_extractor import URLExtractor
from url_analysis.domain_analysis import DomainAnalyzer

sample_text = """
Urgent! Verify your account now:
https://bit.ly/secure-login
"""

extractor = URLExtractor(sample_text)
urls = extractor.extract_urls()

print("Extracted URLs:", urls)

for url in urls:
    analyzer = DomainAnalyzer(url)
    print({
        "domain": analyzer.get_registered_domain(),
        "shortened": analyzer.is_shortened_url(),
        "suspicious_tld": analyzer.suspicious_tld(),
        "heuristic_new_domain": analyzer.heuristic_new_domain()
    })
