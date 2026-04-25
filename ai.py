import os
import json
import google.generativeai as genai

_model = None


def _get_model():
    global _model
    if _model is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel("gemini-2.0-flash")
    return _model


def ask(prompt: str) -> str:
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ AI unavailable: {str(e)}"


def capacity_insight(projects: list[dict], time_entries: list[dict], calendar: list[dict]) -> str:
    context = f"""
You are a business analyst for a freelance brand design studio called Flight Design, owned by Ariana Wolf in Oakland, CA.

ACTIVE PROJECTS:
{json.dumps([p for p in projects if p['status'] != 'Completed'], indent=2)}

TIME ENTRIES THIS WEEK:
{json.dumps(time_entries, indent=2)}

UPCOMING CALENDAR EVENTS:
{json.dumps(calendar, indent=2)}

Analyse Ariana's current capacity situation. Be specific about:
1. Which projects are over budget in hours and by how much
2. Whether she is at risk of being overbooked next week based on calendar events and active projects
3. One concrete recommendation she should act on today

Keep it to 3–4 sentences. Be direct, warm, and practical. No bullet points — write as a paragraph.
"""
    return ask(context)


def dashboard_alert(stats: dict, projects: list[dict], invoices: list[dict], contracts: list[dict]) -> str:
    context = f"""
You are a smart business assistant for Flight Design, a freelance design studio owned by Ariana Wolf.

BUSINESS SNAPSHOT:
{json.dumps(stats, indent=2)}

PROJECTS:
{json.dumps(projects, indent=2)}

INVOICES:
{json.dumps(invoices, indent=2)}

CONTRACTS:
{json.dumps(contracts, indent=2)}

Write a short 2-sentence morning alert for Ariana. Highlight the single most urgent thing she needs to do today and one positive thing happening in her business. Be warm and specific. No bullet points.
"""
    return ask(context)


def chat_response(question: str, projects: list[dict], time_entries: list[dict],
                  invoices: list[dict], contracts: list[dict], calendar: list[dict]) -> str:
    context = f"""
You are a smart business assistant for Flight Design, a freelance design studio owned by Ariana Wolf in Oakland, CA.
Answer the question using ONLY the data provided below. Be concise, specific, and helpful.
If the data doesn't contain enough information, say so honestly.

PROJECTS: {json.dumps(projects, indent=2)}
TIME ENTRIES: {json.dumps(time_entries, indent=2)}
INVOICES: {json.dumps(invoices, indent=2)}
CONTRACTS: {json.dumps(contracts, indent=2)}
CALENDAR: {json.dumps(calendar, indent=2)}

ARIANA'S QUESTION: {question}

Answer in plain English. Use specific names and numbers from the data. Keep it under 100 words.
"""
    return ask(context)


def draft_invoice(project: dict, entries: list[dict]) -> str:
    context = f"""
You are helping Ariana Wolf of Flight Design draft an invoice description for QuickBooks.

PROJECT: {json.dumps(project, indent=2)}
TIME ENTRIES: {json.dumps(entries, indent=2)}

Write a professional invoice description that summarises:
- What work was done (based on time entry descriptions)
- Total hours logged
- Rate per hour and total amount

Format it as 2-3 sentences ready to paste into QuickBooks. Do not add a subject line or greeting.
"""
    return ask(context)


def draft_contract_followup(contract: dict) -> str:
    context = f"""
You are helping Ariana Wolf of Flight Design write a short follow-up email to a client who hasn't signed their contract yet.

CONTRACT DETAILS: {json.dumps(contract, indent=2)}

Write a warm, professional, 3-sentence follow-up email. Include:
- A friendly reminder that the contract was sent
- An offer to answer any questions
- A soft call to action to sign when ready

Use first person as Ariana. Do not add a subject line — just the body. Sign off as "Ariana".
"""
    return ask(context)


def weekly_briefing(projects: list[dict], invoices: list[dict],
                    contracts: list[dict], calendar: list[dict]) -> str:
    context = f"""
You are a smart business assistant generating a weekly briefing for Ariana Wolf of Flight Design.

PROJECTS: {json.dumps(projects, indent=2)}
INVOICES: {json.dumps(invoices, indent=2)}
CONTRACTS: {json.dumps(contracts, indent=2)}
UPCOMING CALENDAR: {json.dumps(calendar, indent=2)}

Generate a weekly briefing with these sections:
1. **Top 3 Priorities** this week (specific, actionable)
2. **Money** — what's overdue, what's coming in
3. **Watch Out** — any capacity or deadline risk
4. **Quick Win** — one thing she can knock out fast today

Use bold headers. Be specific with names and numbers. Keep each section to 1–2 sentences.
"""
    return ask(context)
