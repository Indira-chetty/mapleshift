"""
MapleShift: run with   python app.py   then open http://127.0.0.1:5000
"""
from pathlib import Path
import os
import uuid
from datetime import date

from flask import Flask, redirect, render_template, request, session, url_for

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from core import engine
from core.engine import (LIST_NAME, LIST_URL, PASSAGES, FX_NOTE, analyse, answer_question,
                         build_checklist, match_item, parse_invoice)
from core.help import find_expert_help
from core.importer import parse_table, read_table
from core.i18n import LANGS, t

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hackathon-demo-key")

APP_NAME = "MapleShift"
STORE = {}  # session id -> {"rows", "answers", "name"}  (in memory: fine for a demo)
PASSAGE_BY_ID = {p["id"]: p for p in PASSAGES}


def _sid():
    if "sid" not in session:
        session["sid"] = uuid.uuid4().hex
    return session["sid"]


def _current():
    data = STORE.get(_sid())
    if not data:
        return None
    items, summary = analyse(data["rows"], data["answers"])
    return data, items, summary


@app.context_processor
def globals_for_templates():
    return {"app_name": APP_NAME, "list_name": LIST_NAME, "list_url": LIST_URL,
            "fx": engine.USD_TO_CAD, "fx_note": FX_NOTE, "has_results": _sid() in STORE,
            "today": date.today().strftime("%B %d, %Y"),
            "logo_svg": (Path(__file__).parent / "templates" / "_logo.html").read_text(encoding="utf-8").strip()}


@app.template_filter("money")
def money(v):
    return f"${v:,.2f}"


# ---- Pages --------------------------------------------------------------------
@app.get("/")
def home():
    return render_template("home.html", active="home")


@app.get("/check")
def check():
    return render_template("check.html", active="check", tab=request.args.get("tab", "invoice"))


@app.context_processor
def samples_for_templates():
    return {"samples": SAMPLES}


@app.post("/check/invoice")
def check_invoice():
    f = request.files.get("invoice")
    if not f or not f.filename:
        return render_template("check.html", active="check", tab="invoice",
                               error="Choose a CSV file first, or try the sample invoice.")
    if not f.filename.lower().endswith((".csv", ".xlsx", ".xlsm")):
        return render_template("check.html", active="check", tab="invoice",
                               error="Upload a .csv or .xlsx file. PDF invoices are coming next.")
    try:
        rows, problems, source = parse_table(read_table(f.filename, f.read()))
    except Exception:
        rows, problems, source = [], ["We couldn't open that file. Try saving it again as .xlsx or .csv."], ""
    if not rows:
        return render_template("check.html", active="check", tab="invoice",
                               error=problems[0] if problems else "We couldn't find any items in that file.")
    label = f"{f.filename} ({source})" if source and source != "Table" else f.filename
    STORE[_sid()] = {"rows": rows, "answers": {}, "name": label, "problems": problems}
    return redirect(url_for("results"))


# Sample invoices: real tariff codes, made-up businesses.
SAMPLES = {
    "bakery": ("sample_invoice.csv", "Maple & Crumb Bakery", "Toronto bakery-café", "croissant"),
    "boutique": ("sample_boutique.csv", "Queen West Threads", "Clothing boutique", "shirt"),
    "contractor": ("sample_contractor.csv", "Northview Renovations", "Home renovation contractor", "hammer"),
    "salon": ("sample_salon.csv", "Lumière Beauty Studio", "Hair and beauty salon", "sparkles"),
    "quickbooks": ("sample_quickbooks_export.xlsx", "Northview Renovations", "QuickBooks Online export (.xlsx)", "file-spreadsheet"),
}


@app.post("/check/sample")
def check_sample():
    key = request.form.get("sample", "bakery")
    file, business, _, _ = SAMPLES.get(key, SAMPLES["bakery"])
    rows, problems, source = parse_table(read_table(file, (engine.DATA / file).read_bytes()))
    if source == "QuickBooks report":
        business += " (QuickBooks export)"
    STORE[_sid()] = {"rows": rows, "answers": {}, "name": f"Sample invoice: {business}",
                     "problems": problems}
    return redirect(url_for("results"))


@app.post("/check/quick")
def check_quick():
    desc = request.form.get("description", "").strip()
    code = request.form.get("hs_code", "").strip()
    made_in = request.form.get("made_in", "").strip()
    price = request.form.get("value", "").strip()
    if not desc and not code:
        return render_template("check.html", active="check", tab="quick",
                               error="Describe the product or enter its HS code.")
    try:
        value = float(price.replace("$", "").replace(",", "")) if price else 1000.0
    except ValueError:
        value = 1000.0
    row = {"line": 1, "description": desc or code, "hs_code": code, "quantity": 1, "unit_price": value,
           "currency": request.form.get("currency", "CAD"), "made_in": made_in, "supplier": "Your supplier"}
    items, _ = analyse([row])
    return render_template("check.html", active="check", tab="quick", quick=items[0],
                           form=request.form)


@app.get("/results")
def results():
    cur = _current()
    if not cur:
        return redirect(url_for("check"))
    data, items, summary = cur
    chart = sorted([i for i in items if i["extra_cad"] > 0], key=lambda x: x["extra_cad"], reverse=True)[:6]
    unclear = {}
    for i in items:
        if i["needs_origin_question"]:
            unclear[i["supplier"]] = unclear.get(i["supplier"], 0) + 1
    warnings = [f"{i['description']}: {i['warning']}" for i in items if i.get("warning")]
    return render_template("results.html", active="results", items=items, s=summary, name=data["name"],
                           problems=data.get("problems", []) + warnings, chart=chart,
                           unclear_suppliers=unclear)


@app.post("/results/origin")
def results_origin():
    data = STORE.get(_sid())
    if data:
        line = request.form.get("line")
        data["answers"][line] = {"made_in": request.form.get("made_in", ""),
                                 "changed": request.form.get("changed", "no")}
    return redirect(url_for("results") + f"#line-{request.form.get('line')}")


@app.post("/results/origin-supplier")
def results_origin_supplier():
    data = STORE.get(_sid())
    supplier = request.form.get("supplier", "")
    if data:
        for r in data["rows"]:
            if r["supplier"] == supplier and not r.get("made_in"):
                data["answers"][str(r["line"])] = {"made_in": request.form.get("made_in", ""),
                                                   "changed": request.form.get("changed", "no")}
    return redirect(url_for("results"))


@app.get("/ask")
def ask():
    q = request.args.get("q", "").strip()
    answer = answer_question(q) if q else None
    return render_template("ask.html", active="ask", q=q, answer=answer)


@app.get("/help")
def help_page():
    items = [i for i in request.args.getlist("item") if i]
    text, sources = (None, engine.RESOURCES)
    if items:
        text, sources = find_expert_help(items)
    return render_template("help.html", active="help", items=items, text=text, sources=sources)


@app.get("/report")
def report():
    cur = _current()
    if not cur:
        return redirect(url_for("check"))
    data, items, summary = cur
    lang = request.args.get("lang", "en")
    if lang not in LANGS:
        lang = "en"
    steps = build_checklist(items, summary)
    used = []
    for s in steps:
        if s["source"] not in used:
            used.append(s["source"])
    return render_template("report.html", active="report", items=items, s=summary, name=data["name"],
                           steps=steps, lang=lang, langs=LANGS, tr=lambda k, **v: t(lang, k, **v),
                           sources=[PASSAGE_BY_ID[x] for x in used if x in PASSAGE_BY_ID])


@app.get("/reset")
def reset():
    STORE.pop(_sid(), None)
    return redirect(url_for("check"))


if __name__ == "__main__":
    app.run(debug=True)
