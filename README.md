# AI Customer Call Analyzer

> A fully local, zero-cost AI system that transforms raw customer support call recordings into structured business insights — built in 4 days.

---

## What Is This Project?

In many companies, thousands of customer support calls are recorded every day. Managers do not have time to listen to every call. Important insights — customer frustration, complaint patterns, satisfaction levels — remain buried inside audio files.

This system solves that problem automatically:

- ️ Converts audio calls into text
- Analyzes the emotion behind the words
- Displays insights in an interactive dashboard
- Stores all results locally — no cloud, no cost

---

## Live Pipeline

```
Customer Call Audio (.wav / .mp3)
 ↓
 Whisper AI (Speech → Text)
 ↓
 RoBERTa AI (Text → Sentiment)
 ↓
 JSON Result Saved Locally
 ↓
 Streamlit Dashboard
```

---

## Features

- **Upload audio** directly from the dashboard
- **Auto transcription** using OpenAI Whisper
- **Sentiment detection** — POSITIVE, NEGATIVE, or NEUTRAL
- **Confidence score** shown for every result
- **Analytics page** with call counts and bar chart
- **Color coded results** — Green / Red / Yellow
- **100% local** — no API keys, no internet needed after setup

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.12 | Core language |
| OpenAI Whisper | Speech to text (local AI model) |
| RoBERTa (HuggingFace) | Sentiment analysis (local AI model) |
| Streamlit | Web dashboard |
| PyTorch | AI engine powering both models |
| FFmpeg | Audio file processing |

---

## Project Structure

```
call-analyzer/
│
├── dashboard.py ← Streamlit web UI (4 pages)
├── analyzer.py ← Pipeline coordinator
├── whisper_transcriber.py ← Speech to text module
├── sentiment_model.py ← Sentiment detection module
├── transcribe.py ← Day 1 CLI transcription script
├── sentiment.py ← Day 2 CLI sentiment script
│
├── data/
│ ├── audio/ ← Upload audio files here
│ └── results/ ← JSON results saved here
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Setup Instructions

### Step 1 — Make sure Python is installed
```bash
py --version
```
Should show Python 3.12.x

### Step 2 — Install all packages
```bash
py -m pip install openai-whisper
py -m pip install torch
py -m pip install transformers
py -m pip install streamlit
py -m pip install pandas
```

### Step 3 — Install FFmpeg (required for audio processing)
```bash
winget install ffmpeg
```
Close and reopen terminal after this.

### Step 4 — Create required folders
```bash
mkdir data\audio
mkdir data\results
```

### Step 5 — Run the dashboard
```bash
py -m streamlit run dashboard.py
```

Your browser will open at `http://localhost:8501`

---

## How To Use

1. Open the dashboard in your browser
2. Go to **Home** page
3. Upload a `.wav` or `.mp3` call recording
4. Click **Analyze Call**
5. Wait for Whisper to transcribe + AI to detect sentiment
6. See the result — sentiment, confidence, full transcript
7. Go to **Analytics** to see summary across all calls

---

## Dashboard Pages

| Page | What It Shows |
|------|--------------|
| Home | Upload audio or select existing, click Analyze |
| ️ Call Library | All uploaded recordings with Analyze / Delete buttons |
| Result | Sentiment badge, confidence score, full transcript |
| Analytics | Total calls, sentiment breakdown, bar chart, recent calls table |

---

## Sentiment Labels

| Label | Meaning | Color |
|-------|---------|-------|
| POSITIVE | Customer is happy or satisfied | Green |
| NEGATIVE | Customer is frustrated or upset | Red |
| NEUTRAL | Customer is calm, just asking a question | Yellow |

---

## Development Journey

This project was built in 4 days, 1 hour per day.

### Day 1 — Speech to Text
Built `transcribe.py` using OpenAI Whisper.
Audio files → transcript saved as JSON.

**Key learning:** Whisper needs FFmpeg as a helper to open audio files. Installed via `winget install ffmpeg`.

### Day 2 — Sentiment Analysis
Built `sentiment.py` using HuggingFace DistilBERT.
Transcript JSON → sentiment label added to same JSON.

**Key learning:** Pre-trained models from HuggingFace can be used without any training. Just download and run.

### Day 3 — Streamlit Dashboard
Built `dashboard.py` that reads all transcript JSONs and displays them.
Sidebar for call selection, color coded sentiment badges.

**Key learning:** Streamlit lets you build real interactive web apps using only Python — no HTML or CSS needed (though you can add custom CSS for styling).

### Day 4 — Full Pipeline + Professional UI
Rebuilt the entire system with clean separation of concerns.
Split into `whisper_transcriber.py`, `sentiment_model.py`, `analyzer.py`, `dashboard.py`.
Added upload button, analyze button, analytics page, and professional dark UI.

**Key learning:** Real software separates each job into its own file. One file = one responsibility. This makes it easier to debug and improve.

---

## Problems Faced & How They Were Solved

| Problem | Cause | Solution |
|---------|-------|---------|
| `No module named whisper` | Wrong Python being used | Used `py -m pip install` instead of `pip install` |
| FFmpeg not found | Not installed on Windows | `winget install ffmpeg` |
| All results showing NEGATIVE | DistilBERT only knows movie reviews | Switched to RoBERTa trained on real customer text |
| Duplicate JSON files | Timestamp in filename = new file each time | Fixed filename to `audio_name.json` so same file overwrites |

---

## Models Used

### OpenAI Whisper (base)
- Trained on 680,000 hours of multilingual audio
- Runs 100% locally after one-time download (~150MB)
- Supports .wav, .mp3, .m4a, .ogg, .flac

### Cardiff RoBERTa Sentiment
- Trained on real social and customer text
- Returns POSITIVE, NEGATIVE, NEUTRAL natively
- Runs 100% locally after one-time download (~500MB)

---

## Requirements

```
openai-whisper
torch
transformers
streamlit
pandas
ffmpeg (system dependency)
```

---

## Important Notes

- First run will download AI models (~650MB total) — one time only
- After download, everything works offline
- All data stays on your computer — nothing is sent anywhere
- Use `py -m streamlit run dashboard.py` (not `streamlit run`) on Windows

---

*Built with 0 rupees. Runs locally. No cloud. No APIs. Just AI.*