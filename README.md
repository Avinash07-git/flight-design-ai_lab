# ✈️ Flight Design — Business Intelligence Hub

> AI-powered business intelligence for freelance design studios.
> Built at the PNP Foundation SMB Innovation Sprint Hackathon · April 2026.

---

## What It Does

Connects a design studio's fragmented tool stack (Airtable, Harvest, QuickBooks, Dropbox Sign, Google Calendar) into one AI-powered dashboard.

| Screen | What It Does |
|---|---|
| 🏠 Dashboard | Unified view of projects, invoices, and an AI morning brief |
| 📊 Capacity | Chart of hours estimated vs logged, AI overbooking warning |
| 💬 Ask Your Business | Chat with your own business data in plain English |
| ⚡ Smart Actions | AI drafts invoice descriptions, follow-up emails, weekly briefings |

---

## Quick Start

### 1. Clone & install

```bash
git clone <your-repo-url>
cd FlightDesign-AI
uv venv && uv pip install fastapi "uvicorn[standard]" jinja2 python-multipart google-generativeai
```

> Don't have `uv`? Use `pip install ...` with the same package list.

### 2. Set your Gemini API key

Get a free key at: https://aistudio.google.com/apikey

```bash
export GEMINI_API_KEY="your-key-here"
```

### 3. Run

```bash
uvicorn main:app --port 8765 --reload
```

Open **http://localhost:8765** in your browser.

### 4. Load data

- Click **"⚡ Use Demo Data"** to explore instantly with Ariana's mock business data
- Or upload your own CSVs exported from your tools

---

## Uploading Your Own Data

Export CSVs from your tools and upload on the onboarding screen:

| CSV | Export From | Required Columns |
|---|---|---|
| Projects | Airtable | id, name, client, budget_usd, estimated_hours, logged_hours, status, deadline, hourly_rate |
| Time Entries | Harvest | id, project_id, date, hours, description |
| Invoices | QuickBooks | id, invoice_number, client, project, amount_usd, status, issue_date, due_date |
| Contracts | Dropbox Sign | id, client, project, status, sent_date, signed_date |
| Calendar | Google Calendar | id, title, client, date, start_time, duration_hours, type |

Any missing files are filled automatically with demo data.

---

## Tech Stack

- **Backend:** Python + FastAPI
- **Frontend:** HTMX + Tailwind CSS
- **Charts:** Chart.js
- **Database:** SQLite
- **AI:** Google Gemini (1.5 Flash)

---

## Project Structure

```
FlightDesign-AI/
├── main.py           # FastAPI app + all routes
├── database.py       # SQLite setup, seeder, queries
├── ai.py             # Gemini prompts for all features
├── mock_data/        # Sample CSVs for demo
├── templates/        # HTMX + Jinja2 HTML templates
│   └── partials/     # HTMX partial responses
└── pyproject.toml
```

---

## Notes

- No data leaves your machine except to the Gemini API
- The app is read + draft only — it does not send emails or modify any external tool
- Works for any freelance studio, not just Flight Design — just upload your own CSVs
