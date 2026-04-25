import csv
import io
import os
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import database as db
import ai

app = FastAPI(title="Flight Design — Business Intelligence Hub")
templates = Jinja2Templates(directory="templates")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

db.init_db()


# ── helpers ──────────────────────────────────────────────────────────────────

def _parse_upload(content: bytes) -> list[dict]:
    text = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def _require_data(request: Request):
    """Redirect to upload page if no data loaded yet."""
    if not db.is_data_loaded():
        return RedirectResponse("/", status_code=302)
    return None


# ── onboarding ────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/load-demo")
async def load_demo():
    db.seed_mock_data()
    return RedirectResponse("/dashboard", status_code=302)


@app.post("/upload")
async def upload_csvs(
    projects: UploadFile = File(None),
    time_entries: UploadFile = File(None),
    invoices: UploadFile = File(None),
    contracts: UploadFile = File(None),
    calendar: UploadFile = File(None),
):
    files = {}
    mapping = {
        "projects": projects,
        "time_entries": time_entries,
        "invoices": invoices,
        "contracts": contracts,
        "calendar_events": calendar,
    }
    for table, upload in mapping.items():
        if upload and upload.filename:
            content = await upload.read()
            files[table] = _parse_upload(content)

    if not files:
        db.seed_mock_data()
    else:
        db.seed_from_uploads(files)

    return RedirectResponse("/dashboard", status_code=302)


@app.get("/reset")
async def reset():
    import sqlite3
    conn = db.get_conn()
    conn.execute("UPDATE session SET loaded=0 WHERE id=1")
    for t in ["projects","time_entries","invoices","contracts","calendar_events"]:
        conn.execute(f"DELETE FROM {t}")
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=302)


# ── dashboard ─────────────────────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    redirect = _require_data(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/dashboard-data", response_class=HTMLResponse)
async def dashboard_data(request: Request):
    stats = db.get_dashboard_stats()
    projects = db.fetch_all("projects")
    invoices = db.fetch_all("invoices")
    contracts = db.fetch_all("contracts")
    alert = ai.dashboard_alert(stats, projects, invoices, contracts)
    return templates.TemplateResponse("partials/dashboard_data.html", {
        "request": request,
        "stats": stats,
        "alert": alert,
        "projects": projects,
        "invoices": invoices,
    })


# ── capacity ──────────────────────────────────────────────────────────────────

@app.get("/capacity", response_class=HTMLResponse)
async def capacity_page(request: Request):
    redirect = _require_data(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("capacity.html", {"request": request})


@app.get("/api/capacity-data", response_class=HTMLResponse)
async def capacity_data(request: Request):
    projects = db.fetch_all("projects")
    time_entries = db.fetch_all("time_entries")
    calendar = db.fetch_all("calendar_events")
    insight = ai.capacity_insight(projects, time_entries, calendar)
    active = [p for p in projects if p["status"] != "Completed"]
    return templates.TemplateResponse("partials/capacity_data.html", {
        "request": request,
        "projects": active,
        "insight": insight,
        "calendar": calendar,
    })


# ── chat ──────────────────────────────────────────────────────────────────────

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    redirect = _require_data(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("chat.html", {"request": request})


class ChatRequest(BaseModel):
    question: str


@app.post("/api/chat", response_class=HTMLResponse)
async def chat(request: Request):
    form = await request.form()
    question = form.get("question", "").strip()
    if not question:
        return HTMLResponse("<p class='text-gray-400 italic'>Please type a question.</p>")
    projects = db.fetch_all("projects")
    time_entries = db.fetch_all("time_entries")
    invoices = db.fetch_all("invoices")
    contracts = db.fetch_all("contracts")
    calendar = db.fetch_all("calendar_events")
    answer = ai.chat_response(question, projects, time_entries, invoices, contracts, calendar)
    return templates.TemplateResponse("partials/chat_bubble.html", {
        "request": request,
        "question": question,
        "answer": answer,
    })


# ── smart actions ─────────────────────────────────────────────────────────────

@app.get("/actions", response_class=HTMLResponse)
async def actions_page(request: Request):
    redirect = _require_data(request)
    if redirect:
        return redirect
    projects = db.fetch_all("projects")
    contracts = db.fetch_all("contracts")
    pending_contracts = [c for c in contracts if c["status"] == "Pending"]
    active_projects = [p for p in projects if p["status"] != "Completed"]
    return templates.TemplateResponse("actions.html", {
        "request": request,
        "active_projects": active_projects,
        "pending_contracts": pending_contracts,
    })


@app.post("/api/action/invoice", response_class=HTMLResponse)
async def action_invoice(request: Request):
    form = await request.form()
    project_id = int(form.get("project_id", 0))
    projects = db.fetch_all("projects")
    time_entries = db.fetch_all("time_entries")
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return HTMLResponse("<p class='text-red-500'>Project not found.</p>")
    entries = [e for e in time_entries if int(e["project_id"]) == project_id]
    draft = ai.draft_invoice(project, entries)
    return templates.TemplateResponse("partials/action_result.html", {
        "request": request,
        "label": f"Invoice Draft — {project['name']}",
        "draft": draft,
    })


@app.post("/api/action/followup", response_class=HTMLResponse)
async def action_followup(request: Request):
    form = await request.form()
    contract_id = int(form.get("contract_id", 0))
    contracts = db.fetch_all("contracts")
    contract = next((c for c in contracts if c["id"] == contract_id), None)
    if not contract:
        return HTMLResponse("<p class='text-red-500'>Contract not found.</p>")
    draft = ai.draft_contract_followup(contract)
    return templates.TemplateResponse("partials/action_result.html", {
        "request": request,
        "label": f"Follow-up Email — {contract['client']}",
        "draft": draft,
    })


@app.post("/api/action/briefing", response_class=HTMLResponse)
async def action_briefing(request: Request):
    projects = db.fetch_all("projects")
    invoices = db.fetch_all("invoices")
    contracts = db.fetch_all("contracts")
    calendar = db.fetch_all("calendar_events")
    draft = ai.weekly_briefing(projects, invoices, contracts, calendar)
    return templates.TemplateResponse("partials/action_result.html", {
        "request": request,
        "label": "Weekly Briefing",
        "draft": draft,
    })
