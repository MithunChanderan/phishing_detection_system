from parser.eml_parser import EMLParser
from parser.header_auth import HeaderAuthAnalyzer

parser = EMLParser("data/phishing/sample1.eml")

# 🔴 THIS LINE IS MANDATORY
parser.load_email()

headers = parser.get_headers()
auth = HeaderAuthAnalyzer(headers)

results = {
    "spf": auth.check_spf(),
    "dkim_present": auth.check_dkim(),
    "from_return_path_mismatch": auth.from_return_path_mismatch(),
    "display_name_spoofing": auth.display_name_spoofing()
}

print(results)
