# 🌉 MindBridge

A private AI journaling companion built with Streamlit. Write freely, receive thoughtful reflective questions powered by Groq, and track your mood over time.

---

## Features

- **Journal page** — write a free-form entry and get 3 AI-generated reflective questions (not advice, not diagnosis — just deeper thinking)
- **Insights page** — visualize your mood over time with a sentiment chart and browse your last 5 entries
- **Local-first** — all entries are stored in a local SQLite database, never sent anywhere except the Groq API for reflection

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/mindBridge.git
cd mindBridge
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

### 3. Add your Groq API key

Copy the example secrets file and fill in your key:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then edit `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_your_key_here"
```

Get a free API key at [console.groq.com](https://console.groq.com).

### 4. Run the app

```bash
streamlit run app.py
```

---

## Project Structure

```
mindBridge/
├── app.py                        # Full Streamlit application
├── requirements.txt              # Python dependencies
├── .gitignore
├── .streamlit/
│   ├── secrets.toml              # Your API key (git-ignored)
│   └── secrets.toml.example     # Safe template to commit
└── journal.db                    # SQLite database (auto-created, git-ignored)
```

---

## Stack

| Layer | Tool |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| AI | [Groq](https://groq.com) — `llama-3.3-70b-versatile` |
| Sentiment | [TextBlob](https://textblob.readthedocs.io) |
| Storage | SQLite (Python stdlib) |

---

## Privacy

Your journal entries are stored locally in `journal.db` on your machine. The only data sent externally is the text of each entry to the Groq API for generating reflective questions.
