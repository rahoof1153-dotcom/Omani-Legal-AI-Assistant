"""Static regression checks for the interim safe entrypoint."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class OfflineEntrypointTests(unittest.TestCase):
    def test_entrypoint_does_not_import_cloud_managers(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        for forbidden in ["OpenAIManager", "LLMManager", "google.generativeai",
                          "chat.completions.create", "generate_content(",
                          "glob.glob(\"**/*.pdf\"", "file_uploader("]:
            self.assertNotIn(forbidden, source)

    def test_library_is_explicit_and_nonrecursive(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('ROOT / "data"', source)
        self.assertIn("candidate.is_symlink()", source)
        self.assertIn("resolved.parent != approved_root", source)
        self.assertIn("candidate.suffix.lower()", source)
        self.assertNotIn("rglob(", source)

    def test_openai_and_gemini_have_fail_closed_guards(self):
        openai = (ROOT / "utils" / "openai_manager.py").read_text(encoding="utf-8")
        gemini = (ROOT / "utils" / "llm_manager.py").read_text(encoding="utf-8")
        self.assertIn('require_approved_transmission("openai", "generate_response"', openai)
        self.assertIn('require_approved_transmission("openai", "readability"', openai)
        self.assertIn('require_approved_transmission("gemini", "initialize"', gemini)

    def test_voice_disabled_until_safe_pipeline(self):
        source = (ROOT / "utils" / "speech_to_text.py").read_text(encoding="utf-8")
        self.assertNotIn("NamedTemporaryFile", source)
        self.assertNotIn("whisper.load_model", source)

if __name__ == "__main__":
    unittest.main()
