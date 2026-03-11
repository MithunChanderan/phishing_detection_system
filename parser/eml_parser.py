from email import policy
from email.parser import BytesParser


class EMLParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.message = None

    def load_email(self):
        with open(self.file_path, "rb") as f:
            self.message = BytesParser(policy=policy.default).parse(f)
        return self.message

    def get_headers(self) -> dict:
        if not self.message:
            raise RuntimeError("Email not loaded")
        return dict(self.message.items())

    def get_body(self) -> dict:
        if not self.message:
            raise RuntimeError("Email not loaded")

        body = {"text": "", "html": ""}

        if self.message.is_multipart():
            for part in self.message.walk():
                content_type = part.get_content_type()
                try:
                    content = part.get_content()
                except Exception:
                    continue

                if content_type == "text/plain":
                    body["text"] += content
                elif content_type == "text/html":
                    body["html"] += content
        else:
            body["text"] = self.message.get_content()

        return body
