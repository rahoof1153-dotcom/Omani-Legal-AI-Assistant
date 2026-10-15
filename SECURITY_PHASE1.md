# Security Phase 1 — offline-only review branch

**Status: NOT RELEASED / NOT DEPLOYED / NOT CERTIFIED FOR CONFIDENTIAL CASE FILES.**

This branch is an interim safety containment implementation, not the complete
consent-enabled application. The old feature modules are retained for review,
but `app.py` intentionally exposes only a local public-law PDF viewer.

## Containment implemented
- New `.gitignore` for future private material, secrets and local outputs.
- New `AGENTS.md` rules restricting legal data handling and deployment.
- Fail-closed provider guard `utils/privacy.py`. Both OpenAI generation and
  readability methods call it. Gemini initialization calls it before any API
  request. Merely setting an API key cannot activate network transmission.
- `app.py`: no recursive PDF scan, upload, AI call or creation of fake sample
  legislation. The viewer accepts only direct non-symlink PDF files under the
  repository's `data/` folder and labels excerpts by PDF file page and SHA-256.
- Removed raw exception indexing in `utils/document_processor.py`; PDF files
  are closed using a context manager.
- Voice processing is temporarily disabled rather than using the incorrect
  Whisper package or leaving audio recordings behind.
- Streamlit configuration binds to localhost and disables usage telemetry.
- New stdlib regression tests: `tests/test_privacy.py` and
  `tests/test_offline_entrypoint.py`.

## Mandatory pre-release work still outstanding
1. Make the public repository private if it contains any confidential content;
   manually approve the status, origin and redistribution rights of all PDFs.
   Existing tracked files and Git history are not cleaned by `.gitignore`.
2. Implement and independently test per-operation exact-payload approval UI
   before unblocking any API provider. Avoid automatic readability API calls.
3. Audit/escape any HTML-rendered legal content and remove raw file paths from
   any future cloud prompts or UI.
4. Implement a secure, validated private-case upload store separately from the
   public legal library, with isolation, retention policy and access controls.
5. Repair voice dependencies as an atomic controlled change: pin
   `openai-whisper==20240930` in `pyproject.toml`/`requirements.txt`,
   regenerate `uv.lock`, then validate installation and a cached local model.
   This branch does not change the dependency lock.
6. Verify authenticated TLS/restricted ingress for cloud operation. The interim
   Streamlit server is local-only; do not publish.
7. Run all tests in the actual target environment and do a separate security
   audit. **Passing static tests would not establish complete data security.**

## Verify in the original repository clone
```sh
python -m unittest discover -s tests -p 'test_privacy.py'
python -m unittest discover -s tests -p 'test_offline_entrypoint.py'
python -m compileall -q app.py utils tests
git diff main...security/offline-p0-20261016 --stat
```

**Do not add personal case documents, passport scans, evidence or API keys to Git.**
Do not merge, deploy, publish, erase history or delete tracked PDFs without
separate explicit approval.
