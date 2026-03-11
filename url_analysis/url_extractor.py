import re

URL_REGEX = r"(https?://[^\s<>\"']+)"

class URLExtractor:
    def __init__(self, text: str):
        self.text = text

    def extract_urls(self) -> list:
        if not self.text:
            return []
        urls = re.findall(URL_REGEX, self.text)
        return list(set(urls))  # deduplicate
