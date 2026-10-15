# Omani Legal AI Assistant — Safety Contract

This repository contains Omani legal research tooling. Public legislation and personal legal-case evidence must remain distinct.

## Hard safety rules
- OFFLINE FIRST: local extraction, keyword search, provenance and PDF exports must not require any AI API credential.
- Do not transmit prompts, queries, legal passages, document contents, file paths, or metadata to a provider without explicit per-operation, exact-payload consent. Never send data during application initialization, citation rendering, or readability improvement.
- Never put passports, civil IDs, criminal evidence, employment files, attorney communications, audio recordings, API keys, or private legal documents in this Git repository.
- Only search user-approved library directories. Do not recursively scan the repository or follow symlinks outside an approved library.
- Preserve original source bytes, Arabic text, dates, reference numbers, page-level provenance and SHA-256 identifiers. Do not silently normalize legal text or present unverified article citations as verified law.
- Do not log raw exceptions, document contents, user questions, private paths, credentials or provider request/response bodies.
- Audio and PDF temporary files must be private, bounded and reliably cleaned on both success and failure. Offline speech must use an already-cached model; no implicit downloads.
- Do not weaken XSRF/CORS protection, add unauthenticated public ingestion, or expose a cloud web UI without verified access controls.
- Never commit, delete, move or overwrite library PDFs; change repository visibility; rewrite Git history; or publish/deploy without explicit user approval.
- Git history and tracked files are not retroactively protected by .gitignore.

## Change requirements
- Keep changes confined to the explicitly approved task; work in a non-default branch.
- Add tests for privacy defaults, unauthorized network calls, consent invalidation, path traversal, logging redaction, cleanup and provenance.
- Report exactly what changed, what was tested and what remains unverified. Never claim a security guarantee or completed deployment without successful tests.
