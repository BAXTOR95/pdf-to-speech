import os
import PyPDF2
import logging

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


def extract_text_and_metadata_from_pdf(pdf_path):
    """Extracts text and metadata from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The text content of the PDF file.
    """
    text = ""
    metadata = {'title': None, 'author': None}
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text_content = page.extract_text()
                if text_content:
                    text += text_content

            doc_info = reader.metadata or {}
            metadata['title'] = doc_info.get(
                '/Title', os.path.splitext(os.path.basename(pdf_path))[0]
            )
            metadata['author'] = doc_info.get('/Author', 'Unknown Author')

    except Exception as e:
        logging.error(f"Failed to read {pdf_path}: {e}", exc_info=True)
        return "", {
            'title': os.path.splitext(os.path.basename(pdf_path))[0],
            'author': 'Unknown Author',
        }

    logging.info(f"Extracted metadata for {pdf_path}: {metadata}")
    return text, metadata
