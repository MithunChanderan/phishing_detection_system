import hashlib
import re


class PrivacyGuard:
    @staticmethod
    def hash_content(content: str) -> str:
        if not content:
            return ""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def mask_email_addresses(text: str) -> str:
        if not text:
            return ""
        return re.sub(
            r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            r"***@***",
            text
        )
