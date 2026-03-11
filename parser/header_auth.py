import re


class HeaderAuthAnalyzer:
    def __init__(self, headers: dict):
        self.headers = headers

    def check_spf(self) -> str:
        auth_results = self.headers.get("Authentication-Results", "")
        auth_results = auth_results.lower()

        if "spf=fail" in auth_results:
            return "fail"
        if "spf=softfail" in auth_results:
            return "softfail"
        if "spf=pass" in auth_results:
            return "pass"
        return "none"

    def check_dkim(self) -> bool:
        return "DKIM-Signature" in self.headers

    def from_return_path_mismatch(self) -> bool:
        from_header = self.headers.get("From", "")
        return_path = self.headers.get("Return-Path", "")

        from_domain = re.findall(r"@([\w\.-]+)", from_header)
        return_domain = re.findall(r"@([\w\.-]+)", return_path)

        if from_domain and return_domain:
            return from_domain[0].lower() != return_domain[0].lower()
        return False

    def display_name_spoofing(self) -> bool:
        from_header = self.headers.get("From", "")
        return "<" in from_header and "@" in from_header and not from_header.strip().startswith("<")
