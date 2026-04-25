# 🐶 AVI RAMP-UP FILE — Flight Design AI Hub
> Read this first in any new session. Everything important is here.

---

## THE EVENT
| Field | Detail |
|---|---|
| **Event** | PNP Foundation SMB Innovation Sprint Hackathon |
| **Date** | Saturday, April 25, 2026 |
| **Time** | 9:00 AM – 9:00 PM (12 hours) |
| **Location** | Plug and Play Tech Center HQ, Sunnyvale, CA |
| **Track** | Track 1 — AI & Data Transformation |
| **Submission deadline** | 6:30 PM hard deadline on Cerebral Valley |
| **Judging expo** | ~7:30 PM — 3 min pitch + 1 min Q&A |

---

## THE BUSINESS WE ARE SOLVING FOR
**Flight Design** — brand/graphic design studio
**Owner:** Ariana Wolf, Oakland, CA

**Her problem:** 5 disconnected tools with no unified view
| Tool | What It Holds |
|---|---|
| Airtable | Project management |
| Harvest | Time tracking |
| QuickBooks | Invoices & payments |
| Dropbox Sign | Contracts & signatures |
| Google Calendar | Scheduling |

She is the human glue manually reconciling all of them every day.

---

## WHAT WE BUILT: Flight Design Business Intelligence Hub

**One-line pitch:**
> "Ariana opens one dashboard instead of 5 apps — and an AI tells her exactly what needs her attention today."

### 4 Screens:
| Screen | What It Does |
|---|---|
| 🏠 Dashboard | Stat cards (active projects, overdue invoices, unsigned contracts, over-budget) + AI Morning Brief |
| 📊 Capacity | Chart.js bar chart of estimated vs logged hours per project + AI overbooking warning |
| 💬 Ask Your Business | Chat with your own business data in plain English via Gemini |
| ⚡ Smart Actions | Buttons that generate ready-to-copy invoice descriptions, follow-up emails, weekly briefings |

### What AI Can and CANNOT Do:
- ✅ Answer questions about her data
- ✅ Spot over-budget projects
- ✅ Predict capacity overload
- ✅ Draft invoice text, follow-up emails, weekly briefings
- ❌ Cannot book meetings, send emails, or take any real-world action
- Phase 2 roadmap = live OAuth integrations

### Scalability answer for judges:
> "Any SMB uploads CSVs exported from their own tools — app works immediately. Under 5 minutes, no developer needed."

---

## TECH STACK
| Component | Technology |
|---|---|
| Backend | Python + FastAPI |
| Frontend | HTMX + Tailwind CSS |
| Charts | Chart.js |
| Database | SQLite |
| AI | Google Gemini (`models/gemini-2.5-flash`) |
| Config | python-dotenv (.env file) |

---

## PROJECT LOCATION
```
/Users/a0a0kbv/Downloads/Code Puppy/FlightDesign-AI/
```

### File Structure:
```
FlightDesign-AI/
├── main.py               # FastAPI app + all routes
├── database.py           # SQLite setup, seeder, queries
├── ai.py                 # Gemini prompts for all 4 features
├── .env                  # GEMINI_API_KEY lives here (not in git)
├── .env.example          # Template for new users
├── mock_data/            # 5 demo CSVs (projects, time_entries,
│                         # invoices, contracts, calendar)
├── templates/
│   ├── base.html         # Sidebar layout
│   ├── upload.html       # Onboarding / CSV upload screen
│   ├── dashboard.html
│   ├── capacity.html
│   ├── chat.html
│   ├── actions.html
│   └── partials/         # HTMX partial responses
└── pyproject.toml
```

---

## HOW TO RUN
```bash
cd "/Users/a0a0kbv/Downloads/Code Puppy/FlightDesign-AI"
uvicorn main:app --port 8765 --reload
```
Open: **http://localhost:8765**

- `.env` file already exists with Gemini API key
- Click **"⚡ Use Demo Data"** or upload real CSVs
- Server must stay running in that terminal

### If port 8765 is busy:
```bash
lsof -ti:8765 | xargs kill -9
```

---

## GEMINI API KEY
- Stored in `.env` file in project root
- Model in use: `models/gemini-2.5-flash` (only model with working quota)
- `gemini-1.5-flash` and `gemini-2.0-flash-lite` return 404/429 for this key
- Key has been exposed in chat twice — remind Avinash to revoke after hackathon

---

## GITHUB REPO
**https://github.com/Avinash07-git/flight-design-ai_lab**

---

## CURRENT STATUS (as of ~2:00 PM)
- ✅ All 4 screens built and working
- ✅ Mock data seeded and loading
- ✅ Gemini AI working (gemini-2.5-flash)
- ✅ Code pushed to GitHub
- ⏳ Avinash's team fetching real CSV data to replace mock data
- ⏳ Business Health Score feature (suggested, not yet built)
- ⏳ Demo prep and pitch practice
- ⏳ Cerebral Valley submission (deadline 6:30 PM)

---

## NEXT THINGS TO BUILD (priority order)
1. **Real CSV data upload** — Avinash's team fetching actual Flight Design data. When CSVs arrive, check column names match and fix if needed.
2. **Business Health Score** — Single AI-generated score (0-100) front and centre on dashboard. One number judges immediately understand.
3. **Demo prep** — Practice 3-min walkthrough, write pitch script.

---

## BUSINESS HEALTH SCORE (not built yet — next feature)
Visual concept:
```
Flight Design Health Score
        62 / 100
    ████████████░░░░░░░
  ⚠️ 1 overdue invoice · 2 projects over budget
     2 unsigned contracts · capacity at 87%
```
- Gemini calculates score from all table data
- Add to dashboard as a hero card above stat cards
- Judges will remember this

---

## JUDGING CRITERIA
| Criteria | Weight | Our Strategy |
|---|---|---|
| SMB Impact & Problem Fit | 25% | Named real business, exact real problem |
| Feasibility & Pilot Ready | 25% | CSV upload = live tomorrow |
| Technical Execution | 20% | 4 working modules, real AI, real UI |
| Usability & Design | 15% | One click per action |
| Demo & Clarity | 15% | Before/after is obvious |

---

## 3-MINUTE PITCH STRUCTURE
1. **Hook (15s):** "Ariana runs a design studio in Oakland. Every morning she opens 5 different apps just to understand her own business."
2. **Problem (30s):** Fragmented tools, no unified view, zero insight
3. **Solution (30s):** One dashboard — AI reads everything, tells her what matters
4. **Demo (90s):** Dashboard → Capacity → Ask AI → Smart Actions
5. **Impact (15s):** "5 hours a week saved. Every invoice, contract, and deadline in one place."

## Q&A PREP
| Judge Asks | Avinash Says |
|---|---|
| "Can it take actions?" | "Phase 1 is intelligence and drafting. Phase 2 roadmap is live OAuth — post hackathon build." |
| "How does it scale to other SMBs?" | "Any SMB uploads their own CSVs — under 5 minutes, no setup." |
| "Why not just use a spreadsheet?" | "A spreadsheet can't tell you you're about to be overbooked next week or draft your invoice for you." |
| "What does it cost to run?" | "Gemini API costs pennies per query. Under $5/month for a studio this size." |

---

## ONE LINE TO START A NEW SESSION
> "Avi, read AVI_RAMPUP.md in the FlightDesign-AI folder and let's continue building."
