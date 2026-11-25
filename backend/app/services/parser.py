import io
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def parse_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extracts text from raw PDF bytes using pdfplumber with PyPDF fallback.
    """
    text_content = []
    
    # Try pdfplumber for layout awareness
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text(layout=True)
                if extracted:
                    text_content.append(extracted)
        if text_content:
            return "\n".join(text_content)
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}. Falling back to PyPDF.")

    # Fallback to PyPDF
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_content.append(extracted)
        return "\n".join(text_content)
    except Exception as e:
        logger.error(f"PyPDF extraction also failed: {e}")
        return ""

def clean_text(text: str) -> str:
    """
    Normalizes whitespace and removes unprintable control characters.
    """
    cleaned = re.sub(r"[\r\t]", " ", text)
    cleaned = re.sub(r" +", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)
    return cleaned.strip()

def semantic_section_chunker(raw_text: str, candidate_id: str) -> List[Dict[str, Any]]:
    """
    Chunks a resume by semantic sections rather than arbitrary character counts.
    Produces 4-8 high-cohesion chunks with attached metadata.
    """
    cleaned = clean_text(raw_text)
    
    # Standard resume section delimiters
    section_patterns = [
        ("EXPERIENCE", r"(?i)\b(work experience|professional experience|employment history|experience)\b"),
        ("PROJECTS", r"(?i)\b(projects|technical projects|key projects)\b"),
        ("SKILLS", r"(?i)\b(technical skills|skills|technologies|competencies)\b"),
        ("EDUCATION", r"(?i)\b(education|academic background|qualifications)\b"),
        ("CERTIFICATIONS", r"(?i)\b(certifications|licenses|certifications & achievements)\b")
    ]
    
    chunks = []
    lines = cleaned.split("\n")
    current_section = "SUMMARY"
    current_lines = []
    
    for line in lines:
        matched_section = None
        for sec_name, pattern in section_patterns:
            if re.match(pattern, line.strip()):
                matched_section = sec_name
                break
                
        if matched_section:
            if current_lines:
                chunk_text = "\n".join(current_lines).strip()
                if len(chunk_text) > 30:
                    chunks.append({
                        "candidate_id": candidate_id,
                        "section": current_section,
                        "content": chunk_text
                    })
                current_lines = []
            current_section = matched_section
        else:
            current_lines.append(line)
            
    # Add final buffer
    if current_lines:
        chunk_text = "\n".join(current_lines).strip()
        if len(chunk_text) > 30:
            chunks.append({
                "candidate_id": candidate_id,
                "section": current_section,
                "content": chunk_text
            })
            
    # Fallback if no sections detected
    if not chunks and cleaned:
        chunks.append({
            "candidate_id": candidate_id,
            "section": "FULL_RESUME",
            "content": cleaned
        })
        
    logger.info(f"Generated {len(chunks)} semantic section chunks for candidate {candidate_id}.")
    return chunks
