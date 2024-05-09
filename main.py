import os
import sys
import argparse
from tqdm import tqdm
from pdf_reader import extract_text_and_metadata_from_pdf
from text_to_speech import text_to_speech


def setup_directory(path):
    """Creates the directory if it does not exist.

    Args:
        path (str): The directory path.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def pdf_to_speech(pdf_path, output_audio_file, format='mp3', user_metadata=None):
    """Converts a PDF file into a speech audio file."""
    text, extracted_metadata = extract_text_and_metadata_from_pdf(pdf_path)

    # Prefer user-provided metadata over extracted
    metadata = extracted_metadata
    if user_metadata:
        if user_metadata['title']:
            metadata['title'] = user_metadata['title']
        if user_metadata['author']:
            metadata['author'] = user_metadata['author']

    if text:
        text_to_speech(
            text, output_file=output_audio_file, format=format, metadata=metadata
        )
        print(
            f"Successfully converted {os.path.basename(pdf_path)} to speech and saved as {os.path.basename(output_audio_file)}."
        )
    else:
        print("No text found in the PDF.")


def process_multiple_files(files, output_dir, format='mp3', user_metadata=None):
    for pdf_file in tqdm(files, desc="Processing PDFs", unit="file"):
        pdf_path = os.path.join('input_files', pdf_file)
        output_audio_file = os.path.join(
            output_dir, os.path.splitext(pdf_file)[0] + f'.{format}'
        )
        pdf_to_speech(
            pdf_path, output_audio_file, format=format, user_metadata=user_metadata
        )


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to Speech")
    parser.add_argument(
        'pdf_files',
        nargs='*',
        help="The names of input PDF files in the 'input_files' directory.",
    )
    parser.add_argument(
        '-f',
        '--format',
        type=str,
        choices=['mp3', 'wav', 'ogg'],
        default='mp3',
        help="The audio format of the output files.",
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help="Process all PDFs in the 'input_files' directory.",
    )
    parser.add_argument(
        '--title', type=str, help="Specify the title for the audio metadata."
    )
    parser.add_argument(
        '--author', type=str, help="Specify the author for the audio metadata."
    )

    args = parser.parse_args()

    input_dir = 'input_files'
    output_dir = 'output_files'
    setup_directory(input_dir)
    setup_directory(output_dir)

    user_metadata = {'title': args.title, 'author': args.author}

    if args.all:
        all_pdfs = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        process_multiple_files(
            all_pdfs, output_dir, format=args.format, user_metadata=user_metadata
        )
    elif args.pdf_files:
        process_multiple_files(
            args.pdf_files, output_dir, format=args.format, user_metadata=user_metadata
        )
    else:
        print(
            "No PDF files specified. Use --all to process all PDFs in the 'input_files' directory."
        )
