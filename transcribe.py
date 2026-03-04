# transcribe.py
# ---------------------------------------------------------
# What this file does:
# Takes an audio file → runs Whisper on it → saves the text
# ---------------------------------------------------------

import whisper          # the speech-to-text AI
import os               # helps us work with files and folders
import json             # helps us save results neatly
from datetime import datetime  # helps us record when analysis was done

def transcribe_audio(audio_file_path):
    """
    This function takes a path to an audio file,
    runs Whisper on it, and returns the transcript as text.
    """

    # STEP 1: Load the Whisper model
    # "base" = small and fast model, good for beginners
    # Other options: "tiny" (faster, less accurate), "small", "medium", "large"
    print("Loading Whisper model... (first time takes 1-2 minutes to download)")
    model = whisper.load_model("base")
    print("Model loaded!")

    # STEP 2: Run transcription
    # Whisper reads the audio file and converts speech → text
    print(f"Transcribing: {audio_file_path}")
    result = model.transcribe(audio_file_path)

    # STEP 3: Extract the text from the result
    transcript_text = result["text"]

    return transcript_text


def save_transcript(audio_filename, transcript_text):
    """
    Saves the transcript as a .txt file inside the /transcripts folder.
    Also saves a .json file with metadata (filename, date, text).
    """

    # Create a clean name for our output file
    base_name = os.path.splitext(audio_filename)[0]  # removes .mp3 or .wav
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"{base_name}_{timestamp}"

    # Save as plain text
    txt_path = os.path.join("transcripts", f"{output_name}.txt")
    with open(txt_path, "w") as f:
        f.write(transcript_text)

    # Save as JSON (useful when we connect everything on Day 4)
    json_path = os.path.join("transcripts", f"{output_name}.json")
    metadata = {
        "audio_file": audio_filename,
        "transcript": transcript_text,
        "timestamp": timestamp,
        "sentiment": None  # we'll fill this in on Day 2
    }
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nTranscript saved!")
    print(f"  Text file: {txt_path}")
    print(f"  JSON file: {json_path}")

    return json_path


def main():
    """
    Main function — this runs when you execute the script.
    It asks you which audio file to transcribe.
    """
    print("=" * 50)
    print("  AI Call Analyzer — Day 1: Transcription")
    print("=" * 50)

    # List audio files available in the audio_files/ folder
    audio_folder = "audio_files"
    files = [f for f in os.listdir(audio_folder)
             if f.endswith((".mp3", ".wav", ".m4a", ".ogg"))]

    if not files:
        print("\nNo audio files found in the audio_files/ folder.")
        print("Please add a .mp3 or .wav file there and run again.")
        return

    # Show the user what files are available
    print("\nAudio files found:")
    for i, f in enumerate(files):
        print(f"  [{i}] {f}")

    # Ask user to pick one
    choice = int(input("\nEnter the number of the file to transcribe: "))
    chosen_file = files[choice]
    audio_path = os.path.join(audio_folder, chosen_file)

    # Run transcription
    transcript = transcribe_audio(audio_path)

    # Show result on screen
    print("\n--- TRANSCRIPT ---")
    print(transcript)
    print("------------------")

    # Save to file
    save_transcript(chosen_file, transcript)


# This line means: only run main() if we execute this file directly
# (not when it's imported by another file on Day 4)
if __name__ == "__main__":
    main()