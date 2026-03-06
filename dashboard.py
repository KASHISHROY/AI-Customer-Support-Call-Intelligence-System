# dashboard.py
# ---------------------------------------------------------
# What this file does:
# The entire Streamlit web interface.
# Has 4 pages: Home, Calls, Analysis Result, Analytics
# Users never see JSON files — only clean UI.
# ---------------------------------------------------------

import streamlit as st
import os
import shutil
import pandas as pd
from analyzer import run_analysis, load_all_results, get_audio_files

# ── PAGE CONFIG ─────────────────────────────────────────
# Must be the very first Streamlit command
st.set_page_config(
    page_title="CallSense AI",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ──────────────────────────────────────────
# Streamlit allows injecting raw CSS using st.markdown
# unsafe_allow_html=True lets us write real HTML/CSS
st.markdown("""
<style>
    /* Import a sharp, technical font */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

    /* ── Global Reset ── */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
        background-color: #0a0a0f;
        color: #e8e8f0;
    }

    /* ── Main background ── */
    .stApp {
        background: #0a0a0f;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #0f0f1a;
        border-right: 1px solid #1e1e2e;
    }

    /* ── Hide Streamlit default header and footer ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Cards ── */
    .card {
        background: #12121e;
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 24px;
        margin: 12px 0;
        transition: border-color 0.2s;
    }
    .card:hover { border-color: #3d3d6b; }

    /* ── Metric cards ── */
    .metric-card {
        background: #12121e;
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-number {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 42px;
        font-weight: 600;
        line-height: 1;
        margin: 8px 0;
    }
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #6666aa;
    }

    /* ── Sentiment badges ── */
    .badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-family: 'IBM Plex Mono', monospace;
    }
    .badge-positive { background: #0d2e1a; color: #30d158; border: 1px solid #30d158; }
    .badge-negative { background: #2e0d0d; color: #ff453a; border: 1px solid #ff453a; }
    .badge-neutral  { background: #2e2a0d; color: #ffd60a; border: 1px solid #ffd60a; }

    /* ── Page title ── */
    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #e8e8f0;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    .page-subtitle {
        font-size: 14px;
        color: #6666aa;
        margin-bottom: 32px;
    }

    /* ── Transcript box ── */
    .transcript-box {
        background: #0f0f1a;
        border-radius: 10px;
        padding: 24px;
        font-size: 15px;
        line-height: 1.9;
        color: #c8c8e0;
        border-left: 3px solid #3d3d6b;
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* ── Call list items ── */
    .call-item {
        background: #12121e;
        border: 1px solid #1e1e2e;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* ── Nav items in sidebar ── */
    .nav-item {
        padding: 10px 16px;
        border-radius: 8px;
        margin: 4px 0;
        cursor: pointer;
        font-size: 14px;
        color: #8888bb;
        transition: all 0.2s;
    }
    .nav-item-active {
        background: #1e1e2e;
        color: #e8e8f0;
    }

    /* ── Divider ── */
    .divider {
        border: none;
        border-top: 1px solid #1e1e2e;
        margin: 24px 0;
    }

    /* ── Logo text ── */
    .logo {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 18px;
        font-weight: 600;
        color: #e8e8f0;
        letter-spacing: -0.5px;
    }
    .logo-accent { color: #5e5ef0; }

    /* ── Result header ── */
    .result-sentiment-block {
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        margin: 16px 0;
    }
    .result-sentiment-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 28px;
        font-weight: 600;
        letter-spacing: 2px;
        white-space: nowrap;
    }
    .result-confidence {
        font-size: 14px;
        opacity: 0.7;
        margin-top: 8px;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* Style Streamlit buttons */
    .stButton > button {
        background: #1e1e2e;
        color: #e8e8f0;
        border: 1px solid #3d3d6b;
        border-radius: 8px;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 13px;
        padding: 8px 20px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #2a2a4a;
        border-color: #5e5ef0;
        color: #fff;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #12121e;
        border: 1px dashed #3d3d6b;
        border-radius: 12px;
        padding: 8px;
    }

    /* Table styling */
    [data-testid="stDataFrame"] {
        background: #12121e;
    }
</style>
""", unsafe_allow_html=True)


# ── CONSTANTS ───────────────────────────────────────────
AUDIO_FOLDER = "data/audio"


# ── HELPER FUNCTIONS ────────────────────────────────────

def sentiment_badge(sentiment: str) -> str:
    """Returns an HTML badge for the given sentiment."""
    s = (sentiment or "unknown").lower()
    css_class = {
        "positive": "badge-positive",
        "negative": "badge-negative",
        "neutral":  "badge-neutral"
    }.get(s, "badge-neutral")

    icons = {"positive": "▲", "negative": "▼", "neutral": "●"}
    icon = icons.get(s, "●")

    return f'<span class="badge {css_class}">{icon} {s}</span>'


def sentiment_color(sentiment: str) -> str:
    """Returns hex color for sentiment."""
    return {
        "POSITIVE": "#30d158",
        "NEGATIVE": "#ff453a",
        "NEUTRAL":  "#ffd60a"
    }.get((sentiment or "").upper(), "#6666aa")


def sentiment_bg(sentiment: str) -> str:
    """Returns background color for sentiment block."""
    return {
        "POSITIVE": "#0a2018",
        "NEGATIVE": "#200a0a",
        "NEUTRAL":  "#1e1a08"
    }.get((sentiment or "").upper(), "#12121e")


def format_ts(ts: str) -> str:
    """Formats '20260304_053930' → '04 Mar 2026, 05:39 AM'"""
    try:
        from datetime import datetime
        dt = datetime.strptime(ts, "%Y%m%d_%H%M%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except:
        return ts


# ── SIDEBAR ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown('<div class="logo">📞 Call<span class="logo-accent">Sense</span></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:11px;color:#6666aa;margin-bottom:24px;">AI Customer Intelligence</div>', unsafe_allow_html=True)
        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Navigation
        st.markdown('<div style="font-size:11px;color:#6666aa;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">Navigation</div>', unsafe_allow_html=True)

        pages = {
            "🏠  Home":       "Home",
            "🎙️  Call Library": "Calls",
            "📊  Analytics":  "Analytics"
        }

        # Use session state to track current page
        if "page" not in st.session_state:
            st.session_state.page = "Home"

        for label, page_key in pages.items():
            is_active = st.session_state.page == page_key
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                # Clear result state when navigating away
                if page_key != "Result":
                    st.session_state.pop("result", None)
                st.rerun()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Quick stats in sidebar
        results = load_all_results()
        total = len(results)
        pos   = sum(1 for r in results if r.get("sentiment","").upper() == "POSITIVE")
        neg   = sum(1 for r in results if r.get("sentiment","").upper() == "NEGATIVE")
        neu   = sum(1 for r in results if r.get("sentiment","").upper() == "NEUTRAL")

        st.markdown(f"""
        <div style="font-size:11px;color:#6666aa;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">Quick Stats</div>
        <div style="display:grid;gap:8px;">
            <div style="background:#12121e;border:1px solid #1e1e2e;border-radius:8px;padding:12px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#8888bb;">Total Calls</span>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:18px;font-weight:600;">{total}</span>
            </div>
            <div style="background:#12121e;border:1px solid #1e1e2e;border-radius:8px;padding:12px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#30d158;">Positive</span>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:18px;font-weight:600;color:#30d158;">{pos}</span>
            </div>
            <div style="background:#12121e;border:1px solid #1e1e2e;border-radius:8px;padding:12px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#ff453a;">Negative</span>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:18px;font-weight:600;color:#ff453a;">{neg}</span>
            </div>
            <div style="background:#12121e;border:1px solid #1e1e2e;border-radius:8px;padding:12px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#ffd60a;">Neutral</span>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:18px;font-weight:600;color:#ffd60a;">{neu}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── PAGE 1: HOME ─────────────────────────────────────────

def page_home():
    st.markdown('<div class="page-title">Welcome to CallSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Upload a customer call recording and get instant AI-powered sentiment analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    # ── Upload new audio ──
    with col1:
        st.markdown("""
        <div class="card">
            <div style="font-size:32px;margin-bottom:12px;">⬆️</div>
            <div style="font-size:16px;font-weight:600;margin-bottom:8px;">Upload New Call</div>
            <div style="font-size:13px;color:#6666aa;margin-bottom:16px;">
                Upload a .wav or .mp3 recording to analyze
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Drop audio file here",
            type=["wav", "mp3", "m4a", "ogg"],
            label_visibility="collapsed"
        )

        if uploaded:
            # Save uploaded file to data/audio/
            os.makedirs(AUDIO_FOLDER, exist_ok=True)
            save_path = os.path.join(AUDIO_FOLDER, uploaded.name)
            with open(save_path, "wb") as f:
                f.write(uploaded.getbuffer())
            st.success(f"✅ Saved: {uploaded.name}")

            if st.button("🔍 Analyze This Call", use_container_width=True):
                _run_and_show_result(save_path)

    # ── Select existing audio ──
    with col2:
        st.markdown("""
        <div class="card">
            <div style="font-size:32px;margin-bottom:12px;">📂</div>
            <div style="font-size:16px;font-weight:600;margin-bottom:8px;">Existing Recordings</div>
            <div style="font-size:13px;color:#6666aa;margin-bottom:16px;">
                Select from previously uploaded audio files
            </div>
        </div>
        """, unsafe_allow_html=True)

        audio_files = get_audio_files(AUDIO_FOLDER)

        if not audio_files:
            st.markdown('<div style="color:#6666aa;font-size:13px;padding:16px 0;">No recordings yet. Upload one first.</div>', unsafe_allow_html=True)
        else:
            chosen = st.selectbox(
                "Select recording",
                audio_files,
                label_visibility="collapsed"
            )
            if st.button("🔍 Analyze Selected Call", use_container_width=True):
                audio_path = os.path.join(AUDIO_FOLDER, chosen)
                _run_and_show_result(audio_path)

    # ── How it works ──
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:16px;font-weight:600;margin-bottom:16px;">How It Works</div>', unsafe_allow_html=True)

    h1, h2, h3, h4 = st.columns(4)
    steps = [
        ("🎙️", "Upload Audio", "Add your .wav or .mp3 call recording"),
        ("🤖", "Whisper AI", "Converts speech to text automatically"),
        ("🧠", "DistilBERT", "Detects sentiment from the transcript"),
        ("📊", "See Results", "Instant dashboard with full analysis"),
    ]
    for col, (icon, title, desc) in zip([h1, h2, h3, h4], steps):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:28px;">{icon}</div>
                <div style="font-size:14px;font-weight:600;margin:8px 0;">{title}</div>
                <div style="font-size:12px;color:#6666aa;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def _run_and_show_result(audio_path: str):
    """
    Runs the full pipeline and shows the result.
    Used by both Home and Calls pages.
    """
    with st.spinner("🎙️ Transcribing audio with Whisper..."):
        try:
            result = run_analysis(audio_path)
            st.session_state.result = result
            st.session_state.page   = "Result"
            st.rerun()
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")


# ── PAGE 2: CALL LIBRARY ─────────────────────────────────

def page_calls():
    st.markdown('<div class="page-title">Call Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">All uploaded recordings ready for analysis</div>', unsafe_allow_html=True)

    audio_files = get_audio_files(AUDIO_FOLDER)

    if not audio_files:
        st.markdown("""
        <div class="card" style="text-align:center;padding:48px;">
            <div style="font-size:48px;margin-bottom:16px;">🎙️</div>
            <div style="font-size:16px;font-weight:600;margin-bottom:8px;">No recordings yet</div>
            <div style="font-size:13px;color:#6666aa;">Go to Home and upload a call recording to get started</div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f'<div style="font-size:13px;color:#6666aa;margin-bottom:16px;">{len(audio_files)} recording(s) available</div>', unsafe_allow_html=True)

    for audio_file in audio_files:
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"""
            <div style="padding:14px 0;">
                <div style="font-size:15px;font-weight:600;">🎵 {audio_file}</div>
                <div style="font-size:12px;color:#6666aa;margin-top:4px;font-family:'IBM Plex Mono',monospace;">
                    {os.path.join(AUDIO_FOLDER, audio_file)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("🔍 Analyze", key=f"analyze_{audio_file}", use_container_width=True):
                audio_path = os.path.join(AUDIO_FOLDER, audio_file)
                _run_and_show_result(audio_path)

        with col3:
            if st.button("🗑️ Delete", key=f"delete_{audio_file}", use_container_width=True):
                os.remove(os.path.join(AUDIO_FOLDER, audio_file))
                st.rerun()

        st.markdown('<hr style="border:none;border-top:1px solid #1e1e2e;margin:0;">', unsafe_allow_html=True)


# ── PAGE 3: ANALYSIS RESULT ──────────────────────────────

def page_result():
    result = st.session_state.get("result", None)

    if not result:
        st.warning("No result to display. Please analyze a call first.")
        if st.button("← Go Home"):
            st.session_state.page = "Home"
            st.rerun()
        return

    sentiment   = result.get("sentiment", "UNKNOWN")
    confidence  = result.get("confidence", 0)
    transcript  = result.get("transcript", "")
    call_file   = result.get("call_file", "")
    timestamp   = result.get("timestamp", "")
    color       = sentiment_color(sentiment)
    bg          = sentiment_bg(sentiment)

    # Back button
    if st.button("← Back to Library"):
        st.session_state.page = "Calls"
        st.rerun()

    st.markdown('<br>', unsafe_allow_html=True)

    # ── Main result layout ──
    left, right = st.columns([1, 2], gap="large")

    with left:
        # Big sentiment block
        emoji = {"POSITIVE": "😊", "NEGATIVE": "😠", "NEUTRAL": "😐"}.get(sentiment.upper(), "❓")

        st.markdown(f"""
        <div class="result-sentiment-block" style="background:{bg};border:1px solid {color}30;">
            <div style="font-size:56px;">{emoji}</div>
            <div class="result-sentiment-label" style="color:{color};">{sentiment}</div>
            <div class="result-confidence" style="color:{color};">
                {round(confidence * 100, 1)}% confidence
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Call metadata
        st.markdown(f"""
        <div class="card">
            <div style="font-size:11px;color:#6666aa;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">Call Details</div>
            <div style="margin-bottom:10px;">
                <div style="font-size:11px;color:#6666aa;">File</div>
                <div style="font-size:14px;font-family:'IBM Plex Mono',monospace;">{call_file}</div>
            </div>
            <div style="margin-bottom:10px;">
                <div style="font-size:11px;color:#6666aa;">Analyzed At</div>
                <div style="font-size:14px;">{format_ts(timestamp)}</div>
            </div>
            <div>
                <div style="font-size:11px;color:#6666aa;">Word Count</div>
                <div style="font-size:14px;font-family:'IBM Plex Mono',monospace;">{len(transcript.split())} words</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div style="font-size:16px;font-weight:600;margin-bottom:12px;">📄 Full Transcript</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="transcript-box" style="border-left-color:{color};">
            {transcript}
        </div>
        """, unsafe_allow_html=True)

        # Confidence bar
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:13px;color:#6666aa;margin-bottom:8px;">Confidence Score</div>', unsafe_allow_html=True)
        st.progress(confidence)
        st.markdown(f'<div style="font-size:12px;font-family:\'IBM Plex Mono\',monospace;color:{color};">{round(confidence * 100, 1)}%</div>', unsafe_allow_html=True)


# ── PAGE 4: ANALYTICS ────────────────────────────────────

def page_analytics():
    st.markdown('<div class="page-title">Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Sentiment insights across all analyzed calls</div>', unsafe_allow_html=True)

    results = load_all_results()

    if not results:
        st.markdown("""
        <div class="card" style="text-align:center;padding:48px;">
            <div style="font-size:48px;margin-bottom:16px;">📊</div>
            <div style="font-size:16px;font-weight:600;margin-bottom:8px;">No data yet</div>
            <div style="font-size:13px;color:#6666aa;">Analyze some calls first to see analytics here</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Count sentiments
    total = len(results)
    pos   = sum(1 for r in results if r.get("sentiment","").upper() == "POSITIVE")
    neg   = sum(1 for r in results if r.get("sentiment","").upper() == "NEGATIVE")
    neu   = sum(1 for r in results if r.get("sentiment","").upper() == "NEUTRAL")

    # ── Metric Cards ──
    m1, m2, m3, m4 = st.columns(4)

    metrics = [
        (total, "Total Calls",     "#5e5ef0", "#0d0d2e"),
        (pos,   "Positive",        "#30d158", "#0a2018"),
        (neg,   "Negative",        "#ff453a", "#200a0a"),
        (neu,   "Neutral",         "#ffd60a", "#1e1a08"),
    ]

    for col, (num, label, color, bg) in zip([m1, m2, m3, m4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-color:{color}30;background:{bg};">
                <div class="metric-label">{label}</div>
                <div class="metric-number" style="color:{color};">{num}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    # ── Charts row ──
    chart_col, table_col = st.columns([1, 2], gap="large")

    with chart_col:
        st.markdown('<div style="font-size:15px;font-weight:600;margin-bottom:16px;">Sentiment Distribution</div>', unsafe_allow_html=True)

        if total > 0:
            import pandas as pd

            chart_data = pd.DataFrame({
                "Sentiment": ["Positive", "Negative", "Neutral"],
                "Count":     [pos, neg, neu]
            }).set_index("Sentiment")

            st.bar_chart(
                chart_data,
                color=["#5e5ef0"],
                use_container_width=True
            )

            # Percentage breakdown
            st.markdown(f"""
            <div class="card" style="margin-top:8px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                    <span style="color:#30d158;font-size:13px;">● Positive</span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:13px;">{round(pos/total*100)}%</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                    <span style="color:#ff453a;font-size:13px;">● Negative</span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:13px;">{round(neg/total*100)}%</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:#ffd60a;font-size:13px;">● Neutral</span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:13px;">{round(neu/total*100)}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with table_col:
        st.markdown('<div style="font-size:15px;font-weight:600;margin-bottom:16px;">Recent Calls</div>', unsafe_allow_html=True)

        # Build a clean table from results
        rows = []
        for r in results[:10]:   # show last 10
            rows.append({
                "Call File":   r.get("call_file", "—"),
                "Sentiment":   r.get("sentiment", "—"),
                "Confidence":  f"{round(r.get('confidence', 0) * 100, 1)}%",
                "Analyzed At": format_ts(r.get("timestamp", ""))
            })

        df = pd.DataFrame(rows)

        # Color-code the sentiment column
        def color_sentiment(val):
            colors = {
                "POSITIVE": "color: #30d158",
                "NEGATIVE": "color: #ff453a",
                "NEUTRAL":  "color: #ffd60a"
            }
            return colors.get(val.upper(), "")

        styled_df = df.style.applymap(color_sentiment, subset=["Sentiment"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)


# ── MAIN APP ROUTER ──────────────────────────────────────

def main():
    render_sidebar()

    # Route to correct page based on session state
    page = st.session_state.get("page", "Home")

    if page == "Home":
        page_home()
    elif page == "Calls":
        page_calls()
    elif page == "Result":
        page_result()
    elif page == "Analytics":
        page_analytics()


if __name__ == "__main__":
    main()