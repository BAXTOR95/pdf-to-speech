import os
import PyPDF2


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

            # Extract text
            for page in reader.pages:
                text += page.extract_text() if page.extract_text() else ""

            # Extract metadata
            if reader.metadata:
                doc_info = reader.metadata
                # Check different ways metadata might be stored
                if '/Title' in doc_info and doc_info['/Title']:
                    metadata['title'] = doc_info['/Title']
                if '/Author' in doc_info and doc_info['/Author']:
                    metadata['author'] = doc_info['/Author']

                # Fallback to filename if title is not found
                if not metadata['title']:
                    metadata['title'] = os.path.splitext(os.path.basename(pdf_path))[0]

                # Default author if not found
                if not metadata['author']:
                    metadata['author'] = "Unknown Author"
            else:
                # Default metadata if not present
                metadata['title'] = os.path.splitext(os.path.basename(pdf_path))[0]
                metadata['author'] = "Unknown Author"

            return text, metadata
    except Exception as e:
        print(f"Failed to read {pdf_path}: {str(e)}")
        return "", metadata
