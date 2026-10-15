"""Private-first, offline-only entry point for the Oman legal research library.

Security Phase 1: cloud AI and case uploads remain deliberately disabled.
Existing feature modules are preserved in the repository for later audited re-enablement.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import fitz
import streamlit as st

ROOT = Path(__file__).resolve().parent
PUBLIC_LIBRARY = ROOT / "data"
MAX_PDF_BYTES = 100 * 1024 * 1024
MAX_VISIBLE_RESULTS = 10
MAX_EXCERPT_CHARS = 1400

st.set_page_config(
    page_title="Omani Legal Research — Offline",
    page_icon="⚖️",
    layout="wide",
)
st.title("Omani Legal Research / البحث القانوني العماني")
st.info(
    "OFFLINE MODE. No AI API calls or private-case uploads are enabled. "
    "Research excerpts are unverified and must be checked against the official Arabic legal text."
)
st.caption("الوضع دون اتصال: البحث المحلي فقط. يجب مراجعة النص العربي الرسمي.")

def approved_pdfs():
    """Discover only direct PDF children under the explicitly approved data/ root."""
    if not PUBLIC_LIBRARY.is_dir() or PUBLIC_LIBRARY.is_symlink():
        return []
    approved_root = PUBLIC_LIBRARY.resolve()
    entries = []
    for candidate in sorted(PUBLIC_LIBRARY.iterdir(), key=lambda p: p.name.casefold()):
        if candidate.is_symlink() or not candidate.is_file() or candidate.suffix.lower() != ".pdf":
            continue
        try:
            resolved = candidate.resolve(strict=True)
            if resolved.parent != approved_root:
                continue
            if resolved.stat().st_size > MAX_PDF_BYTES:
                continue
            entries.append(candidate)
        except (OSError, ValueError):
            continue
    return entries

def selected_pages(path):
    """Return raw native text and numbered PDF file pages without reformatting."""
    if path.is_symlink() or path.parent.resolve() != PUBLIC_LIBRARY.resolve():
        raise ValueError("Unapproved document location")
    if path.resolve(strict=True).parent != PUBLIC_LIBRARY.resolve():
        raise ValueError("Unapproved document location")
    if path.stat().st_size > MAX_PDF_BYTES:
        raise ValueError("File exceeds local safety limit")
    with fitz.open(str(path)) as pdf:
        if pdf.needs_pass:
            raise ValueError("Encrypted PDF cannot be read in this mode")
        digest = sha256(path.read_bytes()).hexdigest()
        pages = [(i + 1, page.get_text("text", sort=False)) for i, page in enumerate(pdf)]
    return digest, pages

files = approved_pdfs()
if not files:
    st.warning("No approved PDF files found in the local data/ library.")
    st.stop()

chosen = st.selectbox("Select one public legal-library PDF / اختر ملفاً", files, format_func=lambda p: p.name)
if st.button("Read selected PDF offline / قراءة الملف محلياً"):
    try:
        file_hash, content = selected_pages(chosen)
    except (OSError, RuntimeError, ValueError):
        st.error("Local PDF reading failed. Verify the selected library file.")
    else:
        st.session_state["offline_selected"] = chosen.name
        st.session_state["offline_digest"] = file_hash
        st.session_state["offline_pages"] = content

if st.session_state.get("offline_selected") == chosen.name:
    st.caption("SHA-256: " + st.session_state["offline_digest"])
    query = st.text_input("Search this PDF / ابحث في هذا الملف")
    if query:
        matches = [(n, txt) for n, txt in st.session_state["offline_pages"] if query.casefold() in txt.casefold()]
        st.write(f"Matching file pages: {len(matches)}")
        for page_number, text in matches[:MAX_VISIBLE_RESULTS]:
            st.markdown(f"**PDF file page {page_number} — النص المستخرج كما هو**")
            idx = text.casefold().find(query.casefold())
            excerpt = text[max(0, idx - 200):min(len(text), idx + MAX_EXCERPT_CHARS)]
            st.text(excerpt)
        if len(matches) > MAX_VISIBLE_RESULTS:
            st.caption("Only the first 10 matching pages are displayed.")
    else:
        st.write(f"Loaded {len(st.session_state['offline_pages'])} file pages; search to view excerpts.")
st.warning(
    "Private evidence, lawyer documents and passport records must not be added to this public repository. "
    "Cloud AI, voice and document drafting are disabled until consent and deployment safeguards pass review."
)
