# 💰 WealthLens MX — AI-Powered Personal Finance Dashboard

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![AI Powered](https://img.shields.io/badge/AI-Groq%20%7C%20LLaMA%203.3-FF6B35?style=for-the-badge&logo=anthropic&logoColor=white)](https://groq.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**A full-stack AI financial advisor for Mexican investors — tracks CEDEs, stocks, crypto & goals with live LLM-powered insights.**

[🚀 Live Demo](https://wealthlens-mx.onrender.com) · [📖 API Docs](#api-reference) · [🐛 Report Bug](https://github.com/crinatarajan/wealthlens-mx/issues) · [✨ Request Feature](https://github.com/crinatarajan/wealthlens-mx/issues)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **AI Financial Advisor** | LLM-powered chat using Groq (LLaMA 3.3 70B) with your real portfolio context |
| 📊 **Smart Dashboard** | Dynamic KPIs, income/expense charts, and asset allocation donut |
| 🏦 **CEDE Rate Tracker** | Live Mexican bank deposit rates (Banregio, Inbursa, Banbajío, HSBC, Santander) |
| 📈 **Market Data** | Real-time stock prices via Yahoo Finance (MX + US markets) |
| 🪙 **Crypto Tracker** | Live BTC, ETH, SOL prices in MXN via CoinGecko |
| 🎯 **Goal Tracking** | Visual progress tracking for financial goals with deadlines |
| 💬 **AI Chat History** | Persistent conversation history stored in SQLite |
| 📥 **Transaction Import** | CSV/Excel import with auto-categorization |
| 🔒 **Auth System** | Secure login with hashed passwords (Werkzeug) |
| 🌐 **Bilingual** | Full English & Spanish support (EN/ES) |
| 🔌 **REST API** | 8+ documented endpoints with interactive testing dashboard |

---

## 🖥️ Screenshots

### 📊 Financial Dashboard
![Dashboard](screenshots/01_dashboard.png)
*KPI cards, income vs expenses chart, asset allocation donut, and recent transactions*

### 💼 Portfolio Breakdown
![Portfolio](screenshots/02_portfolio.png)
*Full asset table across CEDEs, stocks (MX + US), crypto, and FIBRAs*

### 📈 Market Data
![Market Data](screenshots/03_market_data.png)
*Live Mexican bank CEDE rates, stock prices via Yahoo Finance, and crypto via CoinGecko*

### 🧠 AI Financial Analysis
![AI Analysis](screenshots/04_ai_analysis.png)
*LLM-generated health score, insights, and ranked recommendations — refreshable on demand*

### 💬 AI Advisor Chat
![AI Chat](screenshots/05_ai_advisor.png)
*Conversational advisor with full portfolio context, suggested questions, and quick chips*

### 🔌 API Dashboard
![API Endpoints](screenshots/06_api_dashboard.png)
*Interactive endpoint explorer with one-click testing and live JSON responses*

---

## 🏗️ Architecture

```
wealthlens-mx/
│
├── app.py                    # Flask backend — all routes & AI logic
├── wealthlens_demo.html      # Standalone HTML demo (no backend needed)
├── requirements.txt          # Python dependencies (pinned versions)
├── .env.example              # Environment variable template
├── .gitignore                # Excludes .env, *.db, uploads/, venv/
│
├── templates/
│   ├── wealthlens_demo.html  # Main dashboard UI
│   ├── api_dashboard.html    # API explorer
│   ├── login.html
│   └── register.html
│
├── tests/
│   └── test_api.py           # Pytest suite for all API routes
│
└── uploads/                  # User-uploaded CSV/Excel files (gitignored)
```

### Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask 2.x, SQLite (WAL mode) |
| **AI Layer** | Groq API (LLaMA 3.3 70B) — swappable to DeepSeek or Ollama |
| **Market Data** | Yahoo Finance API (stocks), CoinGecko (crypto) |
| **Auth** | Werkzeug password hashing, Flask sessions |
| **Frontend** | Vanilla JS, CSS custom properties, Playfair Display + DM Sans |
| **CI** | GitHub Actions (lint + test on every push) |

---

## ⚡ Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/crinatarajan/wealthlens-mx.git
cd wealthlens-mx
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required — get a free key at console.groq.com
GROQ_API_KEY=gsk_your_key_here

# Required — generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-random-secret-here

# Optional — override AI model
AI_MODEL=llama-3.3-70b-versatile

# Optional — swap to DeepSeek or Ollama (see AI Configuration below)
# AI_BASE_URL=https://api.deepseek.com/v1/chat/completions
```

### 5. Run the app

```bash
python app.py
```

Open http://localhost:5000 — register an account and start tracking!

> **No API key?** Open `wealthlens_demo.html` directly in your browser for a fully interactive demo without any backend.

---

## 🔌 API Reference

All endpoints require authentication (session cookie). Base URL: `http://localhost:5000`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | Health check, AI gateway status, version |
| `GET` | `/api/wealth/summary` | Total assets, goals, 30-day cash flow |
| `GET` | `/api/market/deposits` | CEDE rates from Mexican banks |
| `GET` | `/api/market/stocks?symbols=SPY,AMXL.MX` | Stock prices via Yahoo Finance |
| `GET` | `/api/market/crypto?ids=bitcoin,ethereum` | Crypto prices in USD & MXN |
| `POST` | `/api/ai/dashboard` | AI-generated financial report (JSON) |
| `POST` | `/api/chat` | AI advisor chat with context |
| `GET` | `/api/chat/history` | Stored conversation history |

**Example — AI Chat:**

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is my biggest financial risk?"}'
```

**Example Response:**

```json
{
  "ok": true,
  "answer": "Based on your portfolio, your biggest risk is crypto concentration at 17%...",
  "demo": false
}
```

---

## 🤖 AI Configuration

WealthLens uses an **OpenAI-compatible gateway** — swap providers with one `.env` change:

| Provider | Speed | Cost | `.env` setting |
|---|---|---|---|
| **Groq** *(default)* | ⚡ Ultra-fast | Free tier | `AI_BASE_URL=https://api.groq.com/openai/v1/chat/completions` |
| **DeepSeek** | Fast | Very cheap | `AI_BASE_URL=https://api.deepseek.com/v1/chat/completions` |
| **Ollama** *(local)* | Moderate | Free | `AI_BASE_URL=http://localhost:11434/v1/chat/completions` |
| **OpenRouter** | Variable | Pay-per-use | `AI_BASE_URL=https://openrouter.ai/api/v1/chat/completions` |

---

## 🗄️ Database Schema

The SQLite database is **auto-created on first run** (`wealthlens.db`). It is excluded from version control via `.gitignore`.

```
users          — Auth, currency preference, language (EN/ES)
assets         — Portfolio holdings with MXN value
goals          — Financial goals with progress tracking
transactions   — Income & expense ledger (CSV importable)
budgets        — Monthly category limits
recurring      — Subscription & recurring income tracking
alerts         — Smart financial alerts
chat_history   — AI conversation history
```

---

## 🚀 Deployment

### Render (free tier)

1. Push to GitHub
2. New Web Service → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variables (`GROQ_API_KEY`, `SECRET_KEY`) in the Render dashboard

### Railway

```bash
railway init
railway add
railway up
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
```

---

## 🗺️ Roadmap

- [ ] Plaid/Belvo bank account sync (open banking)
- [ ] PDF statement parsing with AI categorization
- [ ] Push notifications for goal milestones
- [ ] Multi-currency rebalancing calculator
- [ ] Tax optimization module (ISR/SAT Mexico)
- [ ] Mobile PWA support
- [ ] Live FX rate fetching (replace static rates)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Natarajan Narayanan**

- LinkedIn: https://www.linkedin.com/in/natrajnarayan/
- GitHub: [@crinatarajan](https://github.com/crinatarajan)
- Email: crinatarajan@gmail.com

---

Built with ❤️ and ☕ · If this helped you, please ⭐ the repo!
