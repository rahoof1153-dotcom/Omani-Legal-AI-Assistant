"""Offline fail-closed regression tests (stdlib only)."""
import os
import unittest
from unittest.mock import patch

from utils.privacy import TransmissionDenied, require_approved_transmission


class PrivacyTests(unittest.TestCase):
    def test_no_environment_override(self):
        with patch.dict(os.environ, {"LEGAL_AI_ONLINE_ENABLED": "1",
                                     "OPENAI_API_KEY": "dummy-test-token",
                                     "GOOGLE_API_KEY": "dummy-test-token"}):
            with self.assertRaises(TransmissionDenied):
                require_approved_transmission("openai", "document_qa", "PRIVATE CASE CONTENT")

    def test_error_does_not_contain_payload(self):
        sensitive = "secret-test-case-123456"
        with self.assertRaises(TransmissionDenied) as caught:
            require_approved_transmission("gemini", "analysis", sensitive)
        self.assertNotIn(sensitive, str(caught.exception))

    def test_failure_also_with_empty_payload(self):
        with self.assertRaises(TransmissionDenied):
            require_approved_transmission("openai", "init", "")


if __name__ == "__main__":
    unittest.main()
