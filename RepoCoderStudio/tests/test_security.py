from src.security import redact_secrets


def test_common_secrets_are_redacted():
    text = 'api_key = "abcdefghijk"\nvalue = 1'
    redacted = redact_secrets(text)
    assert "abcdefghijk" not in redacted
    assert "<REDACTED>" in redacted
