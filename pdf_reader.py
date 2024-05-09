import os
import fitz  # PyMuPDF
import re
import logging

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


def extract_text_and_metadata_from_pdf(pdf_path, segment_by_chapter=False):
    """Extracts text and metadata from a PDF file, optionally segmenting by chapters.

    Args:
        pdf_path (str): The path to the PDF file.
        segment_by_chapter (bool): Whether to segment the text by chapters.

    Returns:
        list: A list of text segments from the PDF file.
    """
    text_segments = []
    metadata = {'title': None, 'author': None}

    try:
        doc = fitz.open(pdf_path)
        metadata['title'] = doc.metadata.get(
            'title', os.path.splitext(os.path.basename(pdf_path))[0]
        )
        metadata['author'] = doc.metadata.get('author', 'Unknown Author')

        if segment_by_chapter:
            chapters = extract_chapters(doc)
            text_segments.extend(chapters)
        else:
            # Extract text from the entire document
            full_text = "\n".join(page.get_text() for page in doc)
            text_segments.append(full_text)

    except Exception as e:
        logging.error(f"Failed to read {pdf_path}: {e}", exc_info=True)
        return [], {
            'title': os.path.splitext(os.path.basename(pdf_path))[0],
            'author': 'Unknown Author',
        }

    logging.info(f"Extracted {len(text_segments)} segments from {pdf_path}")
    return text_segments, metadata


def extract_chapters(doc):
    """Extract chapters from the PDF using text block positions and headings.

    Args:
        doc (fitz.Document): The PDF document object.

    Returns:
        list: A list of chapters extracted as strings.
    """
    chapters = []
    current_chapter = ""
    chapter_pattern = re.compile(r'(chapter|section|part)\s+\d+', re.IGNORECASE)

    for page in doc:
        blocks = page.get_text("blocks")
        for b in sorted(
            blocks, key=lambda b: (b[1], b[0])
        ):  # Sort blocks by their vertical position, then horizontal
            block_text = b[4].strip()
            if block_text and chapter_pattern.match(block_text.lower()):
                if current_chapter:
                    chapters.append("\n".join(current_chapter).strip())
                    current_chapter = []
            current_chapter.append(block_text)

        # Append the last formed chapter
        if current_chapter:
            chapters.append("\n".join(current_chapter).strip())
            current_chapter = []

    return chapters
