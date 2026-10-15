import os
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import re
import arabic_reshaper
from bidi.algorithm import get_display

def extract_text_from_pdf(pdf_path):
    """Extract unmodified PDF text with a numbered file-page marker.

    On failure, return None. Exception details and source paths are not logged or
    turned into searchable text. The caller must treat gaps as extraction failures.
    """
    try:
        with fitz.open(pdf_path) as doc:
            text_parts = []
            metadata = {
                "source": str(pdf_path),
                "title": os.path.basename(str(pdf_path)),
                "num_pages": len(doc),
            }
            law_name = os.path.basename(str(pdf_path)).replace(".pdf", "")
            has_arabic = False
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text()
                has_arabic = has_arabic or any(0x0600 <= ord(c) <= 0x06FF for c in page_text)
                text_parts.append(chr(10) + f"===== Page {page_num} =====" + chr(10) + page_text)
                if page_num == 1:
                    lines = page_text.strip().splitlines()
                    if lines and len(lines[0].strip()) > 5:
                        law_name = lines[0].strip()
            metadata["law_name"] = law_name
            metadata["has_arabic"] = has_arabic
            return {"text": "".join(text_parts), "metadata": metadata}
    except Exception:
        # Never index an error as if it were content from a legal PDF.
        return None


def identify_articles(text):
    """
    Identify article numbers and sections in legal text.
    
    Args:
        text: The extracted text from a legal document
        
    Returns:
        Structured text with article identifiers
    """
    # Various patterns for article identification in both English and Arabic
    article_patterns = [
        r'Article\s+(\d+)',  # English: Article 5
        r'المادة\s+(\d+)',   # Arabic: المادة 5
        r'Art\.\s*(\d+)',    # Abbreviated: Art. 5
        r'Section\s+(\d+)',  # Section 5
        r'القسم\s+(\d+)'     # Arabic section
    ]
    
    structured_text = text
    
    # Identify and mark up articles
    for pattern in article_patterns:
        structured_text = re.sub(
            pattern,
            r'[ARTICLE_\1]',  # Mark up with a standardized format
            structured_text
        )
    
    return structured_text

def process_pdfs(pdf_paths):
    """
    Process multiple PDF files for use with LangChain.
    Properly handle Arabic text with bidirectional support.
    
    Args:
        pdf_paths: List of paths to PDF files
        
    Returns:
        List of LangChain Document objects
    """
    documents = []
    
    for pdf_path in pdf_paths:
        extracted_data = extract_text_from_pdf(pdf_path)
        
        if extracted_data:
            # Get the text and check if it contains Arabic
            text = extracted_data["text"]
            has_arabic = extracted_data["metadata"].get("has_arabic", False)
            
            # If document contains Arabic, ensure proper bidirectional text handling
            if has_arabic:
                # We don't reshape the entire document here as it might break structure
                # but we'll mark it for later processing
                extracted_data["metadata"]["has_arabic"] = True
            
            # Identify and structure articles
            structured_text = identify_articles(text)
            
            # Create text splitter for chunking
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Split the document into chunks
            chunks = text_splitter.split_text(structured_text)
            
            # Create LangChain documents with metadata
            for i, chunk in enumerate(chunks):
                # Extract page number from the chunk if possible
                page_num = "Unknown"
                page_match = re.search(r'===== Page (\d+) =====', chunk)
                if page_match:
                    page_num = page_match.group(1)
                
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": extracted_data["metadata"]["source"],
                        "law_name": extracted_data["metadata"]["law_name"],
                        "has_arabic": has_arabic,
                        "chunk": i,
                        "total_chunks": len(chunks),
                        "page": page_num
                    }
                )
                documents.append(doc)
    
    return documents

def get_available_laws(documents):
    """
    Extract unique law names from processed documents.
    
    Args:
        documents: List of processed Document objects
        
    Returns:
        List of unique law names
    """
    law_names = set()
    
    for doc in documents:
        if "law_name" in doc.metadata:
            law_names.add(doc.metadata["law_name"])
    
    return sorted(list(law_names))

def extract_article_by_number(documents, law_name, article_number):
    """
    Extract a specific article from a law.
    Handle Arabic text properly with reshaping and bidirectional support.
    
    Args:
        documents: List of processed Document objects
        law_name: Name of the law to search in
        article_number: Article number to extract
        
    Returns:
        Text of the specific article if found, None otherwise
    """
    article_marker = f"[ARTICLE_{article_number}]"
    
    relevant_chunks = []
    has_arabic = False
    
    # Find chunks containing the article
    for doc in documents:
        if doc.metadata.get("law_name") == law_name and article_marker in doc.page_content:
            relevant_chunks.append(doc)
            if doc.metadata.get("has_arabic", False):
                has_arabic = True
    
    if not relevant_chunks:
        return None
    
    # Combine chunks to get the full article
    article_text = ""
    for chunk in relevant_chunks:
        text = chunk.page_content
        
        # Extract text starting from the article marker
        start_pos = text.find(article_marker)
        if start_pos >= 0:
            # Find the next article marker if it exists
            next_article_pos = -1
            for match in re.finditer(r'\[ARTICLE_\d+\]', text[start_pos+len(article_marker):]):
                next_article_pos = start_pos + len(article_marker) + match.start()
                break
            
            if next_article_pos >= 0:
                article_text += text[start_pos:next_article_pos] + " "
            else:
                article_text += text[start_pos:] + " "
    
    # Clean up the article marker
    if has_arabic:
        article_label = f"المادة {article_number}" 
    else:
        article_label = f"Article {article_number}"
    
    cleaned_text = article_text.replace(article_marker, article_label)
    
    return cleaned_text.strip()
