import os
import sqlite3
from datetime import datetime

import streamlit as st
from groq import Groq
from textblob import TextBlob

DB_PATH = "journal.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS entries "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "created_at TEXT NOT NULL, "
        "content TEXT NOT NULL, "
        "sentiment REAL NOT NULL)"
    )
    con.commit()
    con.close()

def save_entry(content, sentiment):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO entries (created_at, content, sentiment) VALUES (?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), content, sentiment),
    )
    con.commit()
    con.close()

def fetch_entries():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT created_at, content, sentiment FROM entries ORDER BY id DESC"
    ).fetchall()
    con.close()
    return rows

def sentiment_label(score):
    if score >= 0.3:
        return "Positive", "#4ade80", "😊"
    if score <= -0.3:
        return "Negative", "#f87171", "😔"
    return "Neutral", "#94a3b8", "😐"

def sentiment_bar_html(score):
    pct = int((score + 1) / 2 * 100)
    label, color, _ = sentiment_label(score)
    return f"""
    <div style="margin:4px 0 12px 0;">
      <div style="display:flex;justify-content:space-between;font-size:0.72rem;
                  color:#94a3b8;margin-bottom:4px;">
        <span>Negative</span><span>Neutral</span><span>Positive</span>
      </div>
      <div style="background:#1e293b;border-radius:99px;height:8px;overflow:hidden;">
        <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#6366f1,{color});
                    border-radius:99px;transition:width 0.6s ease;"></div>
      </div>
    </div>"""

init_db()

st.set_page_config(page_title="MindBridge", page_icon="🌉", layout="centered")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Lora:ital,wght@0,400;1,400&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .stApp { background: #0f172a; color: #e2e8f0; }

  section[data-testid="stSidebar"] {
    background: #0d1526;
    border-right: 1px solid #1e293b;
  }

  section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

  .stRadio > label { font-size: 0.8rem; color: #64748b !important; letter-spacing: 0.08em; text-transform: uppercase; }
  .stRadio div[role="radiogroup"] label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 0.92rem !important;
    transition: all 0.2s;
  }
  .stRadio div[role="radiogroup"] label:hover { background: #1e293b; border-color: #334155; }

  .brand {
    font-family: 'Lora', serif;
    font-size: 2.4rem;
    font-weight: 400;
    background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    margin-bottom: 2px;
  }
  .brand-sub {
    font-size: 0.85rem;
    color: #475569;
    letter-spacing: 0.04em;
    margin-bottom: 2rem;
  }

  .card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
  }
  .card-sm {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 14px;
    transition: border-color 0.2s;
  }
  .card-sm:hover { border-color: #6366f1; }

  .section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 10px;
  }
  .question-num {
    font-size: 0.7rem;
    font-weight: 600;
    color: #6366f1;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
  }
  .question-text {
    font-family: 'Lora', serif;
    font-size: 1.05rem;
    color: #e2e8f0;
    line-height: 1.55;
    font-style: italic;
  }
  .entry-date {
    font-size: 0.75rem;
    color: #475569;
    margin-bottom: 6px;
  }
  .entry-snippet {
    font-size: 0.92rem;
    color: #94a3b8;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .pill {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 2px 10px;
    border-radius: 99px;
    margin-left: 8px;
    vertical-align: middle;
  }
  .stat-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
  }
  .stat-val {
    font-size: 1.8rem;
    font-weight: 600;
    color: #e2e8f0;
    line-height: 1;
  }
  .stat-lbl {
    font-size: 0.72rem;
    color: #475569;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  textarea { background: #0f172a !important; color: #e2e8f0 !important; border: 1px solid #334155 !important; border-radius: 12px !important; font-size: 1rem !important; }
  textarea:focus { border-color: #6366f1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important; }

  .stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
    font-size: 0.92rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    transition: opacity 0.2s, transform 0.15s;
    width: 100%;
  }
  .stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }
  .stButton > button:active { transform: translateY(0); }

  .stSuccess { background: #052e16; border: 1px solid #166534; border-radius: 10px; color: #4ade80; }
  .stError   { background: #1c0a09; border: 1px solid #7f1d1d; border-radius: 10px; }

  .stSpinner > div { border-top-color: #6366f1 !important; }

  div[data-testid="stMetric"] { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 14px 18px; }
  div[data-testid="stMetric"] label { color: #475569 !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
  div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 1.6rem !important; }

  div[data-testid="stExpander"] {
    background: #1e293b;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    overflow: hidden;
  }
  div[data-testid="stExpander"] summary { font-size: 0.88rem; color: #94a3b8; padding: 10px 16px; }

  [data-testid="stDecoration"] { display: none; }
  footer { display: none; }
  #MainMenu { display: none; }
  header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand">MindBridge</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">Your private AI journaling companion</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="margin-bottom:1.5rem;"><span style="font-family:Lora,serif;font-size:1.2rem;color:#818cf8;">🌉 MindBridge</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("", ["✏️  Journal", "📊  Insights"], label_visibility="collapsed")
    st.markdown("<hr style='border-color:#1e293b;margin:24px 0;'>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.75rem;color:#334155;line-height:1.6;">Your entries are stored<br>locally and never shared.</div>', unsafe_allow_html=True)

page = page.split("  ")[1]

if page == "Journal":
    st.markdown('<div class="section-label">New Entry</div>', unsafe_allow_html=True)

    with st.container():
        entry = st.text_area(
            "",
            placeholder="What's on your mind today? Write freely — this is your space…",
            height=220,
            label_visibility="collapsed",
        )
        col_btn, col_gap = st.columns([1, 3])
        with col_btn:
            submitted = st.button("Reflect →")

    if submitted:
        if not entry.strip():
            st.error("Please write something before submitting.")
        else:
            api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
            if not api_key:
                st.error("GROQ_API_KEY not found. Add it to .streamlit/secrets.toml or set it as an environment variable.")
            else:
                with st.spinner("Thinking…"):
                    client = Groq(api_key=api_key)
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a thoughtful journaling companion. "
                                    "Given a journal entry, respond with exactly 3 short, "
                                    "open-ended reflective questions that help the writer "
                                    "think deeper. No advice, no diagnosis, no commentary — "
                                    "only the 3 questions, each on its own line, numbered."
                                ),
                            },
                            {"role": "user", "content": entry},
                        ],
                    )
                    raw = response.choices[0].message.content.strip()

                lines = [l.strip() for l in raw.splitlines() if l.strip()]
                questions = []
                for line in lines:
                    for prefix in ["1.", "2.", "3.", "1)", "2)", "3)"]:
                        if line.startswith(prefix):
                            questions.append(line[len(prefix):].strip())
                            break
                    else:
                        if len(questions) < 3:
                            questions.append(line)
                questions = questions[:3]

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-label">Reflective Questions</div>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                for i, q in enumerate(questions, 1):
                    st.markdown(
                        f'<div style="margin-bottom:{"20px" if i < len(questions) else "0"};">'
                        f'<div class="question-num">QUESTION {i}</div>'
                        f'<div class="question-text">{q}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown('</div>', unsafe_allow_html=True)

                sentiment = TextBlob(entry).sentiment.polarity
                label, color, emoji = sentiment_label(sentiment)

                save_entry(entry, sentiment)

                st.markdown('<div class="section-label">Mood Snapshot</div>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="display:flex;align-items:center;margin-bottom:10px;">'
                    f'<span style="font-size:1.8rem;margin-right:12px;">{emoji}</span>'
                    f'<span style="font-size:1.1rem;font-weight:500;color:{color};">{label}</span>'
                    f'<span style="margin-left:8px;font-size:0.85rem;color:#475569;">({sentiment:+.2f})</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(sentiment_bar_html(sentiment), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.success("Entry saved to your journal.")

if page == "Insights":
    rows = fetch_entries()

    if not rows:
        st.markdown('<div class="card" style="text-align:center;padding:48px 28px;">'
                    '<div style="font-size:2.5rem;margin-bottom:12px;">📖</div>'
                    '<div style="color:#475569;font-size:0.95rem;">No entries yet.<br>Head to the Journal page to get started.</div>'
                    '</div>', unsafe_allow_html=True)
    else:
        scores = [r[2] for r in rows]
        avg = sum(scores) / len(scores)
        best = max(scores)
        avg_label, avg_color, avg_emoji = sentiment_label(avg)

        st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Entries", len(rows))
        with c2:
            st.metric("Avg Mood", f"{avg:+.2f}")
        with c3:
            st.metric("Best Entry", f"{best:+.2f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Mood Over Time</div>', unsafe_allow_html=True)

        chart_rows = list(reversed(rows))
        chart_data = {"Sentiment": [r[2] for r in chart_rows]}
        st.line_chart(chart_data, color="#6366f1")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Recent Entries</div>', unsafe_allow_html=True)

        for created_at, content, sentiment in rows[:5]:
            label, color, emoji = sentiment_label(sentiment)
            snippet = content[:220] + ("…" if len(content) > 220 else "")
            with st.expander(f"{emoji}  {created_at}  ·  {label} ({sentiment:+.2f})"):
                st.markdown(sentiment_bar_html(sentiment), unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-size:0.93rem;color:#94a3b8;line-height:1.7;">{snippet}</div>',
                    unsafe_allow_html=True,
                )
