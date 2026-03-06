import json, os
from datetime import datetime
from whisper_transcriber import transcribe
from sentiment_model import analyze

RESULTS_FOLDER = "data/results"

def run_analysis(audio_path: str) -> dict:
    audio_filename = os.path.basename(audio_path)

    # ── Check if this file was already analyzed ──
    # If a result already exists for this audio file, return it
    # instead of running Whisper again
    existing = _find_existing_result(audio_filename)
    if existing:
        return existing

    # ── Run fresh analysis ──
    transcript_text = transcribe(audio_path)
    sentiment_result = analyze(transcript_text)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    result = {
        "call_file":  audio_filename,
        "transcript": transcript_text,
        "sentiment":  sentiment_result["sentiment"],
        "confidence": sentiment_result["confidence"],
        "timestamp":  timestamp
    }

    os.makedirs(RESULTS_FOLDER, exist_ok=True)

    # ── Save with fixed filename (not timestamp) ──
    # Using audio filename means same file = same JSON = no duplicates
    base_name   = os.path.splitext(audio_filename)[0]
    output_path = os.path.join(RESULTS_FOLDER, f"{base_name}.json")

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


def _find_existing_result(audio_filename: str):
    """
    Checks if a result JSON already exists for this audio file.
    Returns the result dict if found, None if not.
    """
    base_name   = os.path.splitext(audio_filename)[0]
    result_path = os.path.join(RESULTS_FOLDER, f"{base_name}.json")

    if os.path.exists(result_path):
        with open(result_path, "r") as f:
            return json.load(f)
    return None


def load_all_results() -> list:
    results = []
    if not os.path.exists(RESULTS_FOLDER):
        return results
    for filename in os.listdir(RESULTS_FOLDER):
        if filename.endswith(".json"):
            with open(os.path.join(RESULTS_FOLDER, filename)) as f:
                results.append(json.load(f))
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return results


def get_audio_files(audio_folder="data/audio") -> list:
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder, exist_ok=True)
        return []
    valid = (".wav", ".mp3", ".m4a", ".ogg", ".flac")
    return [f for f in os.listdir(audio_folder) if f.lower().endswith(valid)]