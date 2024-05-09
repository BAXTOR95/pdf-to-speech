from gtts import gTTS
from langdetect import detect, DetectorFactory
from pydub import AudioSegment
from mutagen.id3 import ID3, TIT2, TPE1, TRCK, TALB
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
import os
import logging

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)


# Ensure consistent language detection
DetectorFactory.seed = 0


def detect_language(text):
    """Detects the language of the given text.

    Args:
        text (str): The text to detect the language of.

    Returns:
        str: The language code of the detected language.
    """
    try:
        return detect(text)
    except:
        logging.warning("Language detection failed, defaulting to English.")
        return 'en'  # Default to English if language detection fails


def text_to_speech(
    text, output_file='output.mp3', format='mp3', metadata=None, language=None
):
    """Converts text to speech and saves it to an MP3 file.

    Args:
        text (str): The text to convert to speech.
        output_file (str): The path to save the output MP3 file.
        format (str): The format of the output file (e.g., 'mp3', 'wav').
        metadata (dict): Metadata to include in the output file.

    Returns:
        str: The path to the saved MP3 file.
    """
    # Detect the language of the text
    language = language or detect_language(
        text[:500]
    )  # Use provided language or detect, check only the first 500 characters for efficiency
    logging.info(f"Using language: {language}")

    max_chunk_size = 3000  # Safe chunk size for gTTS
    chunks = [text[i : i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]

    combined = AudioSegment.empty()

    # Process each chunk
    for i, chunk in enumerate(chunks):
        tts = gTTS(text=chunk, lang=language, slow=False)
        chunk_file = f"{output_file[:-len(format)-1]}_chunk_{i+1}.{format}"
        tts.save(chunk_file)

        audio = (
            AudioSegment.from_mp3(chunk_file)
            if format == 'mp3'
            else AudioSegment.from_file(chunk_file, format=format)
        )
        combined += audio
        os.remove(chunk_file)

    # Export combined audio to the specified format
    combined.export(output_file, format=format)

    # If the format is MP3, we can add ID3 tags using Mutagen
    if format == 'mp3' and metadata:
        audio = MP3(output_file, ID3=ID3)
        audio.tags.add(TIT2(encoding=3, text=metadata.get('title', 'Unknown Title')))
        audio.tags.add(TPE1(encoding=3, text=metadata.get('author', 'Unknown Author')))
        audio.save()
    elif format == 'ogg' and metadata:
        audio = OggVorbis(output_file)
        audio['title'] = metadata.get('title', 'Unknown Title')
        audio['artist'] = metadata.get('author', 'Unknown Author')
        audio.save()

    logging.info(f"Saved speech to {output_file}")
    return output_file
