import os
import argparse
import logging
from tqdm import tqdm
from pdf_reader import extract_text_and_metadata_from_pdf
from text_to_speech import text_to_speech


# Set up basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


def setup_directory(path):
    """Creates the directory if it does not exist.

    Args:
        path (str): The directory path.
    """
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Created directory {path}")


def pdf_to_speech(
    pdf_path,
    output_dir,
    format='mp3',
    user_metadata=None,
    language=None,
    segment_by_chapter=False,
):
    """Converts a PDF file to speech by extracting text and converting it to speech.

    Args:
        pdf_path (str): The path to the PDF file.
        output_dir (str): The directory to save the output audio files.
        format (str): The format of the output audio files (e.g., 'mp3', 'wav').
        user_metadata (dict): Additional metadata to include in the audio files.
        language (str): The language for text-to-speech conversion.
        segment_by_chapter (bool): Whether to segment the text by chapters.

    Returns:
        None
    """
    text_segments, extracted_metadata = extract_text_and_metadata_from_pdf(
        pdf_path, segment_by_chapter=segment_by_chapter
    )

    metadata = {**extracted_metadata, **(user_metadata or {})}
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

    # Decide how to name the output files based on the number of segments
    if len(text_segments) == 1:
        # Single segment: use the PDF base name directly
        output_audio_file = os.path.join(output_dir, f"{base_filename}.{format}")
        text_to_speech(
            text_segments[0],
            output_file=output_audio_file,
            format=format,
            metadata=metadata,
            language=language,
        )
        logging.info(
            f"Converted {os.path.basename(pdf_path)} to speech as {os.path.basename(output_audio_file)}."
        )
    else:
        # Multiple segments: append segment index to the base name
        for i, segment in enumerate(
            tqdm(
                text_segments, desc="Converting text segments to speech", unit="segment"
            )
        ):
            output_audio_file = os.path.join(
                output_dir, f"{base_filename}_segment_{i+1}.{format}"
            )
            if segment.strip():  # Ensure segment is not just whitespace
                text_to_speech(
                    segment,
                    output_file=output_audio_file,
                    format=format,
                    metadata=metadata,
                    language=language,
                )
                logging.info(
                    f"Converted segment {i+1} of {os.path.basename(pdf_path)} to speech as {os.path.basename(output_audio_file)}."
                )
            else:
                logging.warning(
                    f"Segment {i+1} of {pdf_path} is empty and was skipped."
                )


def process_multiple_files(
    files,
    output_dir,
    format='mp3',
    user_metadata=None,
    language=None,
    segment_by_chapter=False,
):
    """Processes multiple PDF files to convert them to speech.

    Args:
        files (list): A list of PDF file names.
        output_dir (str): The directory to save the output audio files.
        format (str): The format of the output audio files (e.g., 'mp3', 'wav').
        user_metadata (dict): Additional metadata to include in the audio files.
        language (str): The language for text-to-speech conversion.
        segment_by_chapter (bool): Whether to segment the text by chapters.

    Returns:
        None
    """
    for pdf_file in tqdm(files, desc="Processing PDFs", unit="file"):
        pdf_path = os.path.join('input_files', pdf_file)
        pdf_to_speech(
            pdf_path,
            output_dir,
            format=format,
            user_metadata=user_metadata,
            language=language,
            segment_by_chapter=segment_by_chapter,
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
    parser.add_argument(
        '--language',
        type=str,
        help="Specify the language for text-to-speech conversion.",
    )
    parser.add_argument(
        '--segment-by-chapter',
        action='store_true',
        help="Segment the text by chapters or sections if possible.",
    )

    args = parser.parse_args()

    input_dir = 'input_files'
    output_dir = 'output_files'
    setup_directory(input_dir)
    setup_directory(output_dir)

    user_metadata = {
        k: v for k, v in [('title', args.title), ('author', args.author)] if v
    }

    if args.all:
        all_pdfs = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        process_multiple_files(
            all_pdfs,
            output_dir,
            format=args.format,
            user_metadata=user_metadata,
            language=args.language,
            segment_by_chapter=args.segment_by_chapter,
        )
    elif args.pdf_files:
        process_multiple_files(
            args.pdf_files,
            output_dir,
            format=args.format,
            user_metadata=user_metadata,
            language=args.language,
            segment_by_chapter=args.segment_by_chapter,
        )
    else:
        logging.warning(
            "No PDF files specified. Use --all to process all PDFs in the 'input_files' directory."
        )
