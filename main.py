import os
import argparse
import logging
import sys
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


def select_files_interactively(input_dir):
    """Allow users to select PDF files interactively from a given directory.

    Args:
        input_dir (str): Directory to list PDF files from.

    Returns:
        list: Selected PDF file names.
    """
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    for i, file in enumerate(pdf_files):
        print(f"{i + 1}: {file}")

    selections = input(
        "Enter the numbers of the PDFs you want to process (e.g., 1 3 5): "
    )
    selected_indices = map(int, selections.split())
    selected_files = [pdf_files[i - 1] for i in selected_indices]
    return selected_files


def save_progress(progress_file, processed_files):
    """Saves the list of processed files to a progress file.

    Args:
        progress_file (str): The path to the progress file.
        processed_files (list): A list of processed file names.
    """
    with open(progress_file, 'w') as file:
        for item in processed_files:
            file.write(f"{item}\n")


def load_progress(progress_file):
    """Loads the list of processed files from a progress file.

    Args:
        progress_file (str): The path to the progress file.

    Returns:
        list: A list of processed file names.
    """
    if not os.path.exists(progress_file):
        return []
    with open(progress_file, 'r') as file:
        processed_files = [line.strip() for line in file.readlines()]
    return processed_files


def clear_progress(progress_file):
    """Clears the progress file to reset processing state.

    Args:
        progress_file (str): The path to the progress file.

    Returns:
        None
    """
    if os.path.exists(progress_file):
        os.remove(progress_file)
        logging.info(f"Cleared progress file {progress_file}")


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
    progress_file='progress.txt',
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
    processed_files = load_progress(progress_file)

    # Only process files that have not been completed yet
    files_to_process = [f for f in files if f not in processed_files]

    if not files_to_process:
        logging.info("No new files to process. All selected files have been processed.")
        return

    for pdf_file in tqdm(files_to_process, desc="Processing PDFs", unit="file"):
        pdf_path = os.path.join('input_files', pdf_file)
        pdf_to_speech(
            pdf_path,
            output_dir,
            format=format,
            user_metadata=user_metadata,
            language=language,
            segment_by_chapter=segment_by_chapter,
        )

        # Save each file to progress after processing
        processed_files.append(pdf_file)
        save_progress(progress_file, processed_files)

    # Clear the progress file after successfully processing all files
    clear_progress(progress_file)


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
        '--interactive', action='store_true', help="Select PDF files interactively."
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
    parser.add_argument(
        '--resume',
        action='store_true',
        help="Resume processing from the last saved progress.",
    )

    args = parser.parse_args()

    input_dir = 'input_files'
    output_dir = 'output_files'
    setup_directory(input_dir)
    setup_directory(output_dir)

    user_metadata = {
        k: v for k, v in [('title', args.title), ('author', args.author)] if v
    }
    progress_file = 'progress.txt'  # Define the path to the progress file

    # Determine which files to process
    if args.interactive:
        args.pdf_files = select_files_interactively(input_dir)

    if args.resume:
        if not os.path.exists(progress_file):
            logging.error(
                "Progress file does not exist. Cannot resume without progress data."
            )
            sys.exit(1)
        if args.all:
            all_pdfs = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        else:
            # Load progress and determine unprocessed files
            processed_pdfs = load_progress(progress_file)
            all_pdfs = [
                f
                for f in os.listdir(input_dir)
                if f.lower().endswith('.pdf') and f not in processed_pdfs
            ]
    elif args.all:
        all_pdfs = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    else:
        all_pdfs = args.pdf_files

    if all_pdfs:
        process_multiple_files(
            all_pdfs,
            output_dir,
            format=args.format,
            user_metadata=user_metadata,
            language=args.language,
            segment_by_chapter=args.segment_by_chapter,
            progress_file=progress_file,
        )
    else:
        logging.warning(
            "No PDF files specified. Use --all, --interactive, or list specific files to process."
        )
