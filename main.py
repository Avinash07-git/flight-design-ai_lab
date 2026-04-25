import csv
import io
import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database as db
import ai

app = FastAPI(title="Flight Design — Business Intelligence Hub")
templates = Jinja2Templates(directory="templates")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

db.init_db()


# ── helpers ───────────────────────────────────────────────────────────────────

def _parse_upload(content: bytes) -> list[dict]:
    text = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def _require_data(request: Request):
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
    employees: UploadFile = File(None),
    projects: UploadFile = File(None),
    schedule: UploadFile = File(None),
):
    files: dict[str, list[dict]] = {}
    mapping = {
        "employees": employees,
        "projects": projects,
        "schedule": schedule,
    }
    for key, upload in mapping.items():
        if upload and upload.filename:
            content = await upload.read()
            files[key] = _parse_upload(content)

    if not files:
        db.seed_mock_data()
    else:
        db.seed_from_uploads(files)

    return RedirectResponse("/dashboard", status_code=302)


@app.get("/reset")
async def reset():
    conn = db.get_conn()
    conn.execute("UPDATE session SET loaded=0 WHERE id=1")
    for t in ["employees", "projects", "schedule"]:
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
    stats            = db.get_dashboard_stats()
    capacity_data    = db.get_capacity_data()
    projects         = db.get_projects_summary()
    rev_by_emp       = db.get_revenue_by_employee()
    rev_by_client    = db.get_revenue_by_client()
    rev_by_service   = db.get_revenue_by_service()
    weekly_trend     = db.get_weekly_revenue_trend()
    health           = db.compute_studio_health(stats, capacity_data, rev_by_service, rev_by_client)

    # Derived KPIs
    blended_rate   = round(stats["total_revenue"] / stats["total_hours_logged"]) \
                     if stats["total_hours_logged"] else 0
    avg_utilization = round(
        sum(e["utilization_pct"] for e in capacity_data) / len(capacity_data)
    ) if capacity_data else 0
    active_projects = [p for p in projects if p["actual_hours"] > 0]

    alert = ai.dashboard_alert(stats, capacity_data, projects, rev_by_client, rev_by_service)
    return templates.TemplateResponse("partials/dashboard_data.html", {
        "request":         request,
        "stats":           stats,
        "health":          health,
        "alert":           alert,
        "weekly_trend":    weekly_trend,
        "rev_by_emp":      rev_by_emp,
        "rev_by_client":   rev_by_client[:10],
        "rev_by_service":  rev_by_service,
        "capacity_data":   capacity_data,
        "projects":        active_projects,
        "blended_rate":    blended_rate,
        "avg_utilization": avg_utilization,
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
    capacity_data = db.get_capacity_data()
    cap_trend     = db.get_weekly_capacity_pct()
    insight       = ai.capacity_insight(capacity_data)
    return templates.TemplateResponse("partials/capacity_data.html", {
        "request":       request,
        "capacity_data": capacity_data,
        "cap_trend":     cap_trend,
        "insight":       insight,
    })


# ── chat ──────────────────────────────────────────────────────────────────────

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    redirect = _require_data(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/api/chat", response_class=HTMLResponse)
async def chat(request: Request):
    form = await request.form()
    question = form.get("question", "").strip()
    if not question:
        return HTMLResponse("<p class='text-gray-400 italic'>Please type a question.</p>")
    employees = db.fetch_all("employees")
    projects = db.get_projects_summary()
    schedule = db.fetch_all("schedule")
    answer = ai.chat_response(question, employees, projects, schedule)
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
    return templates.TemplateResponse("actions.html", {"request": request})


@app.post("/api/action/briefing", response_class=HTMLResponse)
async def action_briefing(request: Request):
    stats = db.get_dashboard_stats()
    capacity_data = db.get_capacity_data()
    projects = db.get_projects_summary()
    draft = ai.weekly_briefing(stats, capacity_data, projects)
    return templates.TemplateResponse("partials/action_result.html", {
        "request": request,
        "label": "Weekly Briefing",
        "draft": draft,
    })


@app.post("/api/action/capacity-report", response_class=HTMLResponse)
async def action_capacity_report(request: Request):
    capacity_data = db.get_capacity_data()
    draft = ai.capacity_violation_report(capacity_data)
    return templates.TemplateResponse("partials/action_result.html", {
        "request": request,
        "label": "Capacity Violation Report",
        "draft": draft,
    })


@app.post("/api/action/budget-report", response_class=HTMLResponse)
async def action_budget_report(request: Request):
    projects = db.get_projects_summary()
    draft = ai.project_budget_report(projects)
    return templates.TemplateResponse("partials/action_result.html", {
        "request": request,
        "label": "Project Budget Status Report",
        "draft": draft,
    })
