from privacy.content_hashing import PrivacyGuard

sample_text = "Contact user@example.com immediately to avoid suspension."

masked = PrivacyGuard.mask_email_addresses(sample_text)
hashed = PrivacyGuard.hash_content(sample_text)

print("Masked:", masked)
print("Hashed:", hashed)
