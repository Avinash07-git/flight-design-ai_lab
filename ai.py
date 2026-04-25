import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

MODELS_TO_TRY = [
    "models/gemini-2.5-flash",
    "models/gemini-2.0-flash-001",
    "models/gemini-2.0-flash",
]


def _get_model(model_name: str):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


def ask(prompt: str) -> str:
    if not os.environ.get("GEMINI_API_KEY"):
        return "⚠️ No API key set. Add GEMINI_API_KEY to your .env file and restart."
    last_error = ""
    for model_name in MODELS_TO_TRY:
        try:
            model = _get_model(model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            last_error = str(e)
            if "404" in last_error or "not found" in last_error.lower():
                continue
            if "429" in last_error:
                continue
    return "⚠️ AI unavailable right now — please check your Gemini API key quota."


# ── Dashboard ─────────────────────────────────────────────────────────────────

def dashboard_alert(stats: dict, capacity_data: list[dict], projects: list[dict],
                    rev_by_client: list[dict] | None = None,
                    rev_by_service: list[dict] | None = None) -> str:
    over_cap    = [e for e in capacity_data if e["over_capacity"]]
    over_budget = [p for p in projects if p["actual_hours"] > p["hours_budget"] and p["hours_budget"] > 0]
    blended     = round(stats["total_revenue"] / stats["total_hours_logged"]) if stats.get("total_hours_logged") else 0
    top_client  = rev_by_client[0] if rev_by_client else {}
    top_service = rev_by_service[0] if rev_by_service else {}
    prompt = f"""
You are a sharp business advisor for Flight Design, a brand and graphic design studio owned by Ariana Wolf in Oakland, CA.

STUDIO SNAPSHOT (13-week period):
- Total billed: ${stats['total_revenue']:,.0f}
- Blended rate: ${blended}/hr across {stats['total_employees']} staff
- {stats['total_projects']} active projects, {stats['over_budget_projects']} over hours budget
- Top client: {top_client.get('client','—')} at {top_client.get('pct',0)}% of revenue
- Top service: {top_service.get('service','—')} at {top_service.get('pct',0)}% of revenue

CAPACITY ALERTS ({len(over_cap)} staff with violation weeks):
{chr(10).join(f"- {e['name']}: {e['violation_weeks']} of {e['total_weeks']} weeks over {e['allowed_hours_week']}h/wk contracted" for e in over_cap)}

OVER-BUDGET PROJECTS:
{chr(10).join(f"- {p['name']} ({p['client']}): {p['actual_hours']:.1f}h vs {p['hours_budget']:.0f}h budget" for p in over_budget) or 'None'}

Write a 2-sentence morning brief for Ariana. Lead with the single most urgent operational issue using real names and numbers. Second sentence: one quick win she can act on today. Warm, direct, no bullet points.
"""
    return ask(prompt)


# ── Capacity ──────────────────────────────────────────────────────────────────

def capacity_insight(capacity_data: list[dict]) -> str:
    prompt = f"""
You are a business analyst for Flight Design, a brand design studio run by Ariana Wolf in Oakland, CA.

EMPLOYEE CAPACITY ANALYSIS (contracted vs actual average weekly hours):
{json.dumps(capacity_data, indent=2)}

Write 3–4 sentences analysing the team's capacity situation. Be specific:
1. Which employees are the most overextended and by how much
2. Whether subcontractors vs core staff show different patterns
3. One concrete action Ariana should take immediately

Be direct and practical. No bullet points — write as a paragraph.
"""
    return ask(prompt)


# ── Chat ──────────────────────────────────────────────────────────────────────

def chat_response(question: str, employees: list[dict], projects: list[dict],
                  schedule: list[dict]) -> str:
    # Summarise schedule to avoid token bloat — group by employee + project
    from collections import defaultdict
    summary: dict = defaultdict(lambda: {"hours": 0.0, "amount": 0.0})
    for row in schedule:
        key = f"{row['employee_name']} → {row['project']}"
        summary[key]["hours"] += row.get("hours", 0)
        summary[key]["amount"] += row.get("amount", 0)

    prompt = f"""
You are a smart business assistant for Flight Design, a brand design studio owned by Ariana Wolf in Oakland, CA.
Answer the question using ONLY the data provided. Be concise, specific, and helpful.
If the data doesn't contain enough information to answer, say so honestly.

EMPLOYEES (name, type, bill rate, capacity %):
{json.dumps([{"name": e["name"], "type": e["employee_type"], "rate": e["bill_rate"], "capacity_pct": e["capacity_pct"]} for e in employees], indent=2)}

PROJECTS (name, client, service, hours budget, budget USD):
{json.dumps([{"name": p["name"], "client": p["client"], "service": p["service"], "hours_budget": p["hours_budget"], "budget_usd": p["budget_usd"]} for p in projects], indent=2)}

SCHEDULE SUMMARY (employee → project: total hours, total billed):
{json.dumps([{"assignment": k, "hours": round(v["hours"],1), "billed": v["amount"]} for k, v in summary.items()], indent=2)}

QUESTION: {question}

Answer in plain English. Use specific names and numbers. Keep it under 120 words.
"""
    return ask(prompt)


# ── Smart Actions ─────────────────────────────────────────────────────────────

def weekly_briefing(stats: dict, capacity_data: list[dict], projects: list[dict]) -> str:
    over_cap = [e for e in capacity_data if e["over_capacity"]]
    over_budget = [p for p in projects if p["actual_hours"] > p["hours_budget"] and p["hours_budget"] > 0]
    prompt = f"""
You are a smart business assistant generating a weekly briefing for Ariana Wolf of Flight Design.

BUSINESS STATS: {json.dumps(stats, indent=2)}
OVER-CAPACITY EMPLOYEES: {json.dumps(over_cap, indent=2)}
OVER-BUDGET PROJECTS: {json.dumps(over_budget, indent=2)}
ALL PROJECTS SUMMARY: {json.dumps(projects[:20], indent=2)}

Generate a weekly briefing with these bold sections:
1. **Top 3 Priorities** — specific and actionable for this week
2. **Capacity Alerts** — which team members are overextended and by how much
3. **Budget Watch** — which projects are over hours budget
4. **Revenue Snapshot** — total billed, avg per project, quick win to improve cash flow

Use bold headers. Be specific with names and numbers. Keep each section to 1–2 sentences.
"""
    return ask(prompt)


def capacity_violation_report(capacity_data: list[dict]) -> str:
    over_cap = [e for e in capacity_data if e["over_capacity"]]
    prompt = f"""
You are a business operations analyst for Flight Design, a brand design studio owned by Ariana Wolf.

EMPLOYEES EXCEEDING CONTRACTED CAPACITY:
{json.dumps(over_cap, indent=2)}

Write a concise capacity violation report that:
1. Names each overextended employee with their contracted hours/week vs actual average
2. Flags the top 2–3 most severe cases
3. Recommends whether Ariana should renegotiate contracts, hire more staff, or reduce project load

Format as a professional memo. Use bold for employee names. Keep it under 150 words.
"""
    return ask(prompt)


def project_budget_report(projects: list[dict]) -> str:
    over_budget = [p for p in projects if p["actual_hours"] > p["hours_budget"] and p["hours_budget"] > 0]
    on_track = [p for p in projects if 0 < p["actual_hours"] <= p["hours_budget"]]
    prompt = f"""
You are a project manager analyst for Flight Design, a brand design studio owned by Ariana Wolf in Oakland, CA.

OVER-BUDGET PROJECTS (hours logged exceed budgeted hours):
{json.dumps(over_budget, indent=2)}

ON-TRACK PROJECTS (sample):
{json.dumps(on_track[:10], indent=2)}

Write a concise project budget status report:
1. List each over-budget project with client name, hours over budget, and estimated cost impact at $175/hr avg
2. Highlight which client relationship is most at risk
3. Give one immediate recommendation

Format professionally with bold project names. Under 150 words.
"""
    return ask(prompt)
