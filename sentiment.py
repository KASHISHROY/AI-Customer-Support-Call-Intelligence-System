# sentiment.py
# ---------------------------------------------------------
# What this file does:
# Reads a transcript JSON file → detects sentiment → 
# updates the JSON with the sentiment result
# ---------------------------------------------------------

from transformers import pipeline   # gives us ready-made AI models
import json                          # lets us read and write JSON files
import os                            # lets us work with files and folders


# ---------------------------------------------------------
# STEP 1: Load the sentiment analysis model
# ---------------------------------------------------------
# We are using a pre-trained model from HuggingFace.
# "pre-trained" means someone already trained this AI on
# millions of text examples. We just USE it, we don't train it.
#
# Model name: "distilbert-base-uncased-finetuned-sst-2-english"
# - distilbert = a lightweight version of BERT (a famous AI model)
# - uncased = it doesn't care about CAPITAL vs lowercase letters
# - finetuned-sst-2 = it was specifically trained on sentiment data
# - english = works on English text
#
# First time running: downloads ~250MB model (one-time only)
# After that: loads from your computer instantly
# ---------------------------------------------------------

def load_sentiment_model():
    """
    Loads and returns the HuggingFace sentiment analysis pipeline.
    Think of this as hiring a sentiment expert who is already trained.
    """
    print("Loading sentiment analysis model...")
    print("(First time: downloads ~250MB — please wait)")
    
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    
    print("Model loaded successfully!")
    return sentiment_pipeline


# ---------------------------------------------------------
# STEP 2: Analyze the sentiment of a piece of text
# ---------------------------------------------------------

def analyze_sentiment(sentiment_pipeline, text):
    """
    Takes a piece of text and returns the sentiment.
    
    Input:  "I am very frustrated with your product"
    Output: "negative"
    
    The model returns a label (POSITIVE/NEGATIVE) and a 
    confidence score (0 to 1, where 1 = 100% confident).
    """
    
    # The model has a token limit — it can only read ~512 words at once
    # Customer calls can be long, so we trim to first 512 characters
    # This is enough to detect the overall sentiment
    trimmed_text = text[:512]
    
    # Run the text through the AI model
    # result looks like: [{'label': 'NEGATIVE', 'score': 0.9978}]
    result = sentiment_pipeline(trimmed_text)
    
    # result is a list with one item, so we take [0] to get that item
    label = result[0]["label"]   # 'POSITIVE' or 'NEGATIVE'
    score = result[0]["score"]   # confidence: 0.0 to 1.0
    
    # Convert to lowercase for cleaner storage
    # 'POSITIVE' → 'positive'
    # 'NEGATIVE' → 'negative'
    sentiment = label.lower()
    
    # Round score to 2 decimal places (e.g. 0.9978 → 1.0)
    confidence = round(score * 100, 2)  # convert to percentage
    
    return sentiment, confidence


# ---------------------------------------------------------
# STEP 3: Read transcript JSON, update it, save it back
# ---------------------------------------------------------

def update_json_with_sentiment(json_file_path, sentiment, confidence):
    """
    Opens an existing transcript JSON file,
    adds the sentiment result into it,
    and saves it back to the same file.
    
    Before:
    { "sentiment": null }
    
    After:
    { "sentiment": "negative", "confidence": "97.80%" }
    """
    
    # Open and read the existing JSON file
    with open(json_file_path, "r") as f:
        data = json.load(f)   # loads JSON into a Python dictionary
    
    # Update the sentiment field (was null, now has a value)
    data["sentiment"] = sentiment
    data["confidence"] = f"{confidence}%"
    
    # Write the updated dictionary back to the same file
    with open(json_file_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"JSON updated successfully: {json_file_path}")


# ---------------------------------------------------------
# STEP 4: Main function — ties everything together
# ---------------------------------------------------------

def main():
    print("=" * 50)
    print("  AI Call Analyzer — Day 2: Sentiment Analysis")
    print("=" * 50)
    
    # --- Find all JSON files in the transcripts/ folder ---
    transcripts_folder = "transcripts"
    
    # Get list of all .json files in transcripts folder
    json_files = [
        f for f in os.listdir(transcripts_folder)
        if f.endswith(".json")
    ]
    
    # If no JSON files found, tell the user and stop
    if not json_files:
        print("\nNo transcript JSON files found in transcripts/ folder.")
        print("Please run transcribe.py first to generate a transcript.")
        return
    
    # Show available transcript files
    print("\nTranscript files found:")
    for i, f in enumerate(json_files):
        print(f"  [{i}] {f}")
    
    # Ask user which file to analyze
    choice = int(input("\nEnter the number of the file to analyze: "))
    chosen_file = json_files[choice]
    json_path = os.path.join(transcripts_folder, chosen_file)
    
    # --- Read the transcript text from the JSON file ---
    with open(json_path, "r") as f:
        data = json.load(f)
    
    transcript_text = data["transcript"]
    
    print(f"\nTranscript loaded:")
    print(f"  \"{transcript_text[:100]}...\"")  # show first 100 chars
    
    # --- Load model and analyze ---
    sentiment_pipeline = load_sentiment_model()
    sentiment, confidence = analyze_sentiment(sentiment_pipeline, transcript_text)
    
    # --- Show result on screen ---
    print("\n--- SENTIMENT RESULT ---")
    print(f"  Sentiment  : {sentiment.upper()}")
    print(f"  Confidence : {confidence}%")
    print("------------------------")
    
    # --- Update the JSON file ---
    update_json_with_sentiment(json_path, sentiment, confidence)
    
    # --- Final confirmation ---
    print("\nFinal JSON content:")
    with open(json_path, "r") as f:
        print(json.dumps(json.load(f), indent=2))


# Only run main() if this file is executed directly
if __name__ == "__main__":
    main()