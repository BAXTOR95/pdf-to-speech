# PDF to Speech Converter

This tool converts PDF documents into spoken audio files using Google's Text-to-Speech (TTS) API. It's designed to be flexible and powerful, allowing batch processing, interactive selection, and resume capabilities.

## Features

- **Batch Processing**: Convert all PDFs in a directory to audio files automatically.
- **Interactive Mode**: Select specific PDFs to convert via a simple interactive prompt.
- **Resume Capability**: Pick up processing where you left off, skipping over already processed files.
- **Segmentation**: Split large PDFs into manageable segments based on chapters or sections.
- **Customizable Output**: Choose from multiple audio formats and specify metadata like title and author.
- **Language Detection**: Automatically detect the language of the text to optimize TTS.
- **Logging**: Detailed logs for monitoring and debugging the processing workflow.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.6 or higher
- Pip (Python package installer)

## Installation

First, clone the repository:

```bash
git clone https://github.com/BAXTOR95/pdf-to-speech.git
cd pdf-to-speech
```

Then, install the required Python libraries:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Conversion

Convert all PDFs in the `input_files` directory to MP3 audio files:

```bash
python main.py --all
```

### Interactive Mode

Selectively convert PDFs by choosing them interactively:

```bash
python main.py --interactive
```

### Resume Processing

Resume a previous processing session, skipping already processed files:

```bash
python main.py --resume
```

### Convert Specific Files

Convert specific PDF files:

```bash
python main.py file1.pdf file2.pdf file3.pdf
```

### Segment by Chapters

Convert PDFs and segment them by chapters:

```bash
python main.py --all --segment-by-chapter
```

### Specify Output Format

Convert PDFs to a specific audio format (MP3, WAV, or OGG):

```bash
python main.py --all -f wav
```

### Set Metadata

Specify title and author metadata for the audio files:

```bash
python main.py --all --title "Example Title" --author "Author Name"
```

### Set Language

Override automatic language detection:

```bash
python main.py --all --language en
```

## Directory Structure

- `input_files/`: Place your PDFs here before processing.
- `output_files/`: Audio files are saved in this directory after processing.
- `progress.txt`: Tracks the progress of processed files (used with `--resume`).

## Modules and Functions

- **`pdf_reader.py`**: Contains functions to extract text and metadata from PDFs.
- **`text_to_speech.py`**: Handles the conversion of text to speech using Google TTS.
- **`main.py`**: The main script to run conversions, handling command-line arguments and processing logic.

## Customization

You can modify the script to suit your needs:

- Change the `chapter_pattern` in `pdf_reader.py` to match different chapter styles.
- Adjust the TTS properties in `text_to_speech.py` for different voices or speeds.

## Troubleshooting

- **Missing PDFs**: Ensure all PDFs are in the `input_files` directory.
- **Permission Issues**: Make sure you have read and write permissions for the directories.
- **Dependency Errors**: Run `pip install -r requirements.txt` to ensure all dependencies are installed.

## Contributing

Feel free to fork the repository, make your changes, and create a pull request with your improvements.

## Authors

- **Brian Arriaga** - _Initial work_ - [BAXTOR95](https://github.com/BAXTOR95)
