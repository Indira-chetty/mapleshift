"""
The one engine every page uses.

    invoice rows -> parse -> match -> origin check -> calculate -> checklist

Rule we never break: AI and translation never touch numbers.
Rates come from data/tariffs.csv, math is plain Python.
"""
import csv
import io
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# ---- Settings you may need to change ---------------------------------------
LIST_URL = ("https://www.canada.ca/en/department-finance/news/2026/08/"
            "list-of-products-from-the-united-states-subject-to-counter-tariffs-"
            "effective-september-8-2026.html")
LIST_NAME = "Finance Canada list, effective Sept 8, 2026 (updated Aug 26, 2026)"
# Update this with the Bank of Canada rate for the day you demo:
# https://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/
USD_TO_CAD = 1.40
FX_NOTE = "approximate rate, update with today's Bank of Canada rate"


# ---- Loading data ------------------------------------------------------------
def load_tariffs():
    rows = []
    with open(DATA / "tariffs.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            code = r["hs_code"].strip()
            rows.append({
                "hs_code": code,
                "digits": re.sub(r"\D", "", code),
                "heading_text": r.get("heading_text", "").strip(),
                "description": r["description"].strip(),
                "rate": float(str(r["rate_percent"]).replace("%", "").strip()),
            })
    return rows


def load_json(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


TARIFFS = load_tariffs()
PASSAGES = load_json("passages.json")
RESOURCES = load_json("resources.json")


# ---- Parsing an invoice ------------------------------------------------------
def parse_invoice(text, filename="invoice.csv"):
    """CSV text or file bytes -> (rows, problems). See core/importer.py."""
    from .importer import read_table, parse_table
    data = text.encode() if isinstance(text, str) else text
    rows, problems, _ = parse_table(read_table(filename, data))
    return rows, problems


# ---- Matching ----------------------------------------------------------------
# Everyday words -> words used in the official list.
SYNONYMS = {
    "cup": "cups", "cups": "cups", "plate": "plates", "plates": "plates",
    "napkin": "serviettes", "napkins": "serviettes", "serviette": "serviettes", "serviettes": "serviettes",
    "box": "boxes cartons", "boxes": "boxes cartons", "carton": "cartons",
    "bag": "bags sacks", "bags": "bags sacks",
    "jar": "jars", "jars": "jars", "bottle": "bottles", "bottles": "bottles",
    "container": "kitchenware", "containers": "kitchenware", "kitchen": "kitchenware",
    "dough": "doughs mixes", "mix": "mixes", "mixes": "mixes",
    "lumber": "sawn", "2x4": "sawn", "drywall": "plaster boards", "gypsum": "plaster",
    "lipstick": "lip make-up", "mascara": "eye make-up", "eyeliner": "eye make-up",
    "nail": "manicure", "perfume": "perfumes", "cologne": "toilet waters",
    "tshirt": "t-shirts", "tee": "t-shirts", "sweater": "pullovers jerseys", "hoodie": "pullovers jerseys",
    "jacket": "anoraks wind-jackets", "coat": "overcoats", "rug": "carpets", "rugs": "carpets",
    "notebook": "note books", "notebooks": "note books", "binder": "binders", "envelope": "envelopes",
    "rebar": "bars rods deformations", "galvanized": "zinc", "galvanised": "zinc",
    "flooring": "floor coverings", "vinyl": "vinyl", "carpeting": "carpets", "charcoal": "charcoal", "tissue": "tissues",
}
STOP = {"sheet", "sheets", "roll", "rolls", "kit", "kits", "regular", "coil", "framing", "of", "the", "and", "or", "a", "an", "for", "with", "other", "in", "to", "lb", "kg", "oz",
        "ml", "bulk", "pack", "case", "pails", "pail", "blocks", "block", "printed", "new"}


def _stem(w):
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("es") and w[:-2].endswith(("x", "ch", "sh")):
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    return w


def _words(text):
    """Meaningful words only: sizes like 3/4in, 4x8, 18v or 20 are dropped (unless we know them)."""
    out = []
    for w in re.findall(r"[a-z0-9\-]+", text.lower()):
        if w in STOP or len(w) < 3:
            continue
        if any(ch.isdigit() for ch in w) and w not in SYNONYMS:
            continue
        out.append(w)
    return out


def _tokens(text, expand=False):
    """Stemmed words. expand=True also adds the official-list synonyms (used for user text only)."""
    out = set()
    for w in _words(text):
        out.add(_stem(w))
        if expand:
            out.update(_stem(x) for x in SYNONYMS.get(w, "").split())
    return out


for _t in TARIFFS:
    _t["tokens"] = _tokens(_t["heading_text"] + " " + _t["description"])
    _t["desc_tokens"] = _tokens(_t["description"])


@dataclass
class Match:
    status: str            # listed | not_listed | unsure
    confidence: str        # Verified | Estimated | Needs review
    method: str            # how we found it, in plain words
    row: dict = None
    candidates: list = field(default_factory=list)


def match_by_code(code):
    digits = re.sub(r"\D", "", code)
    if len(digits) < 4:
        return None
    exact = [t for t in TARIFFS if t["digits"][:8] == digits[:8]] if len(digits) >= 8 else []
    if exact:
        return Match("listed", "Verified", "Exact tariff item match", exact[0])
    six = [t for t in TARIFFS if t["digits"][:6] == digits[:6]]
    if six:
        rates = {t["rate"] for t in six}
        if len(rates) == 1:
            return Match("listed", "Estimated",
                         "Same 6-digit group on the list; confirm the full code", six[0], six[:5])
        return Match("unsure", "Needs review",
                     "This group has items at different rates; the full code decides", six[0], six[:5])
    four = [t for t in TARIFFS if t["digits"][:4] == digits[:4]]
    if four:
        return Match("unsure", "Needs review",
                     "Same product heading is on the list, but not this exact code", four[0], four[:5])
    return Match("not_listed", "Verified", "This code is not on the counter-tariff list")


def match_by_words(description):
    """Keyword match against the official descriptions.
    This is the spot to plug in an AI classifier later: let it pick ONLY
    from these candidates, never invent a code or a rate."""
    words = _words(description)
    if not words:
        return Match("unsure", "Needs review", "Not enough detail to match")
    groups = [{_stem(w)} | {_stem(x) for x in SYNONYMS.get(w, "").split()} for w in words]
    scored = []
    for t in TARIFFS:
        hit_groups = sum(1 for g in groups if g & t["tokens"])
        if hit_groups:
            desc_hits = sum(1 for g in groups if g & t["desc_tokens"])
            scored.append((hit_groups / len(groups), hit_groups + desc_hits, t))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if not scored or scored[0][0] < 0.34:
        return Match("unsure", "Needs review",
                     "No clear match on the list; a broker should confirm the code",
                     None, [x[2] for x in scored[:3]])
    best_share, best_score, best = scored[0]
    tied = [x[2] for x in scored if x[0] == best_share and x[1] == best_score]
    cands = [x[2] for x in scored[:4]]
    same_rate = len({t["rate"] for t in tied}) == 1
    if best_share >= 0.5 and (len(tied) == 1 or same_rate):
        return Match("listed", "Estimated", "Matched by product description (no HS code given)", best, cands)
    return Match("unsure", "Needs review", "Several possible matches; a broker should confirm", best, cands)


_AI_CACHE = {}


def match_item(description, hs_code=""):
    if hs_code.strip():
        m = match_by_code(hs_code)
        if m:
            return m
    m = match_by_words(description)
    if m.status == "unsure" and m.candidates:
        # Ask the AI to choose among OUR candidates only (cached, so it runs once per item).
        from . import ai
        if description not in _AI_CACHE:
            _AI_CACHE[description] = ai.pick_candidate(description, m.candidates)
        code = _AI_CACHE[description]
        chosen = next((c for c in m.candidates if c["hs_code"] == code), None)
        if chosen:
            return Match("listed", "Estimated", "AI picked this from the official list; confirm the code",
                         chosen, m.candidates)
    return m


# ---- Origin (Origin Detective) --------------------------------------------------
US_NAMES = {"us", "usa", "u.s.", "u.s.a.", "united states", "united states of america", "america"}


def origin_status(made_in, changed_in_us=None):
    """us | not_us | unclear. Surtax only applies to goods made in the US."""
    m = (made_in or "").strip().lower()
    if not m or m in {"unknown", "not sure", "?", "dont know", "don't know"}:
        return "unclear"
    if m in US_NAMES:
        return "us"
    if changed_in_us == "yes":
        return "unclear"   # made elsewhere but transformed in the US: a broker must decide
    return "not_us"


# ---- Calculation --------------------------------------------------------------
def to_cad(amount, currency):
    return amount * USD_TO_CAD if currency == "USD" else amount


def analyse(rows, origin_answers=None):
    """Run every invoice row through the engine. origin_answers: {line: {made_in, changed}}"""
    origin_answers = origin_answers or {}
    items = []
    for r in rows:
        ans = origin_answers.get(str(r["line"]), {})
        made_in = ans.get("made_in") or r["made_in"]
        origin = origin_status(made_in, ans.get("changed"))
        m = match_item(r["description"], r["hs_code"])
        value = round(to_cad(r["quantity"] * r["unit_price"], r["currency"]), 2)
        rate = m.row["rate"] if (m.row and m.status != "not_listed") else 0.0

        if m.status == "not_listed":
            effect, extra, confidence = "not_affected", 0.0, m.confidence
            reason = m.method
        elif origin == "not_us":
            effect, extra, confidence = "not_affected", 0.0, "Estimated"
            reason = f"Made in {made_in}, so the US surtax should not apply (confirm with proof of origin)"
        elif m.status == "listed" and origin == "us":
            effect, extra, confidence = "affected", round(value * rate / 100, 2), m.confidence
            reason = m.method
        else:  # unsure match, or origin unclear
            effect, extra, confidence = "at_risk", round(value * rate / 100, 2), "Needs review"
            reason = m.method if m.status == "unsure" else "We don't know where this was made"

        items.append({
            **r,
            "made_in": made_in,
            "origin": origin,
            "value_cad": value,
            "rate": rate,
            "extra_cad": extra,
            "effect": effect,
            "confidence": confidence,
            "reason": reason,
            "match_code": m.row["hs_code"] if m.row else "",
            "match_desc": (m.row["heading_text"] + " — " + m.row["description"]) if m.row else "",
            "candidates": [{"hs_code": c["hs_code"], "description": c["description"], "rate": c["rate"]}
                           for c in m.candidates],
            "needs_origin_question": origin == "unclear" and m.status != "not_listed",
            "match_status": m.status,
            # Toupee rule: the gold TARIFF badge goes ONLY on US-origin lines that are on the list
            "tariff_badge": origin == "us" and m.status == "listed" and rate > 0,
            "changed_in_us": ans.get("changed") == "yes",
        })
        items[-1]["advice"] = expert_advice(items[-1]) if confidence == "Needs review" else None

    total = sum(i["value_cad"] for i in items)
    confirmed = sum(i["extra_cad"] for i in items if i["effect"] == "affected")
    possible = sum(i["extra_cad"] for i in items if i["effect"] == "at_risk")
    summary = {
        "invoice_total": round(total, 2),
        "confirmed_extra": round(confirmed, 2),
        "possible_extra": round(possible, 2),
        "share_pct": round((confirmed / total * 100) if total else 0, 1),
        "n_items": len(items),
        "n_affected": sum(1 for i in items if i["effect"] == "affected"),
        "n_at_risk": sum(1 for i in items if i["effect"] == "at_risk"),
        "n_clear": sum(1 for i in items if i["effect"] == "not_affected"),
        "fx": USD_TO_CAD,
        "n_badged": sum(1 for i in items if i["tariff_badge"]),
    }
    return items, summary


# ---- Expert advice when data is missing (rules, not AI) ---------------------------
def expert_advice(item):
    """For an unsure item: what's missing, who can fill the gap, and what to send them.
    Plain rules only, so nothing here can be invented."""
    desc = item["description"]
    missing, who, docs = [], [], []

    if not item.get("hs_code"):
        missing.append("Your invoice has no HS code (the product's customs number), so we matched by description only.")
        who.append(("Your supplier", "They should put the HS code on every commercial invoice."))
    if item.get("match_status") == "unsure" and item["candidates"]:
        rates = sorted({int(c["rate"]) for c in item["candidates"]})
        missing.append(f"It could match {len(item['candidates'])} items on the official list"
                       + (f", taxed at different rates ({', '.join(str(r) + '%' for r in rates)})." if len(rates) > 1 else "."))
        who.append(("A licensed customs broker", "Only the exact 10-digit code decides the rate."))
    elif item.get("match_status") == "unsure":
        missing.append("We couldn't find this product on the official list. It may not be affected, but we won't assume that.")
        who.append(("A licensed customs broker", "They can classify the product and confirm it is not on the list."))
    if item.get("origin") == "unclear" and not item.get("changed_in_us"):
        missing.append("We don't know where it was made. The surtax only applies to goods made in the US.")
        who.append(("Your supplier", "Ask for the country of origin, or a CUSMA certification of origin."))
        docs.append("Certificate or statement of origin from the supplier")
    if item.get("changed_in_us"):
        missing.append("It was made outside the US but changed in the US. Special origin rules decide if it counts as US-made.")
        who.append(("A licensed customs broker", "They apply the origin (marking) rules to your product."))
    if item.get("warning"):
        missing.append("The numbers on this line don't add up: " + item["warning"])
        who.append(("Your bookkeeper", "Check the quantity and price before relying on this cost."))

    docs += ["The invoice with this item", "A product spec sheet or photo"]
    # remove duplicate contacts, keep order
    seen, who_unique = set(), []
    for w in who:
        if w[0] not in seen:
            seen.add(w[0]); who_unique.append(w)

    codes = ", ".join(c["hs_code"] for c in item["candidates"][:3])
    to_supplier = (f"Hi, for \"{desc}\" on our recent invoice, could you send us the HS code and "
                   f"the country where it was made? We need it for Canada's counter-tariffs. Thank you.")
    to_broker = (f"Could you confirm the Canadian tariff classification for \"{desc}\" and whether it is on "
                 f"Finance Canada's counter-tariff list effective Sept 8, 2026?"
                 + (f" Possible codes we found: {codes}." if codes else ""))
    return {"missing": missing, "who": who_unique, "docs": docs,
            "to_supplier": to_supplier, "to_broker": to_broker,
            "at_stake": item["extra_cad"]}


# ---- Action checklist (rules, not AI) ---------------------------------------------
def build_checklist(items, summary):
    """Each step: key (for translation), values to fill in, and the source passage."""
    steps = []
    affected = [i for i in items if i["effect"] == "affected"]
    at_risk = [i for i in items if i["effect"] == "at_risk"]
    unclear_origin = [i for i in items if i["origin"] == "unclear" and i["effect"] == "at_risk"]
    review = [i for i in at_risk if i not in unclear_origin]

    by_supplier = {}
    for i in affected:
        by_supplier.setdefault(i["supplier"], []).append(i["description"])
    for sup, names in by_supplier.items():
        steps.append({"key": "proof_of_origin", "vals": {"supplier": sup, "n": len(names)},
                      "items": names, "source": "BG-2"})
    if affected:
        top = sorted(affected, key=lambda x: x["extra_cad"], reverse=True)[:3]
        steps.append({"key": "compare_suppliers", "vals": {},
                      "items": [t["description"] for t in top], "source": "NR-9"})
    if unclear_origin:
        steps.append({"key": "confirm_origin", "vals": {},
                      "items": [i["description"] for i in unclear_origin], "source": "BG-2"})
    if review:
        steps.append({"key": "broker_review", "vals": {},
                      "items": [i["description"] for i in review], "source": "BG-5"})
    if summary["confirmed_extra"] > 0:
        steps.append({"key": "review_prices",
                      "vals": {"amount": f"${summary['confirmed_extra']:,.2f}", "pct": summary["share_pct"]},
                      "items": [], "source": "BG-1"})
        steps.append({"key": "remission", "vals": {}, "items": [], "source": "NR-8"})
        steps.append({"key": "support_programs", "vals": {}, "items": [], "source": "NR-2"})
    steps.append({"key": "in_transit", "vals": {}, "items": [], "source": "BG-4"})
    return steps


# ---- Ask about the tariffs (answers only from official passages) --------------------
QUESTION_STOP = STOP | {"what", "when", "does", "do", "is", "are", "can", "how", "will", "my", "much",
                        "i", "we", "our", "this", "that", "apply", "tariff", "tariffs", "counter", "affected",
                        "get", "there", "any", "which", "goods", "products", "product", "canada", "u.s",
                        "made", "from", "shipped", "buy", "sell", "import", "imports", "importing", "mexico",
                        "china", "states", "united", "business", "businesses", "small", "start", "help"}
QUESTION_SYNONYMS = {
    "start": "effective september", "begin": "effective september", "when": "effective",
    "date": "effective september", "transit": "transit", "shipped": "transit", "way": "transit",
    "help": "support supports liquidity", "support": "support supports", "money": "liquidity investment",
    "loan": "liquidity bdc", "cash": "cash-flow liquidity", "workers": "workers", "employees": "workers",
    "origin": "originating marked", "made": "originating marked", "american": "originating",
    "rate": "per cent", "rates": "per cent", "percent": "per cent", "much": "per cent",
    "relief": "remission relief", "exemption": "remission relief transit", "exempt": "remission transit",
    "list": "list", "code": "tariff item", "codes": "tariff item", "why": "objective protect",
    "steel": "steel", "cheese": "cheese dairy", "dairy": "dairy", "furniture": "furniture",
    "clothing": "clothing apparel", "clothes": "clothing apparel",
}


def answer_question(question):
    raw = [w for w in re.findall(r"[a-z0-9\-]+", question.lower())]
    words = set()
    for w in raw:
        if w in QUESTION_SYNONYMS:
            words.update(QUESTION_SYNONYMS[w].split())
        if w not in QUESTION_STOP and len(w) > 2:
            words.add(w)
    scored = []
    for p in PASSAGES:
        text = p["text"].lower()
        hits = sum(1 for w in words if w in text or (w.endswith("s") and w[:-1] in text))
        if hits:
            scored.append((hits, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    passages = [p for _, p in scored[:3]]

    # If the question names a specific product, look it up on the list too.
    products = []
    for w in raw:
        if w in QUESTION_STOP or len(w) < 4:
            continue
        toks = _tokens(w, expand=True)
        hits = [t for t in TARIFFS if toks & t["tokens"]]
        if 0 < len(hits) <= 12:
            for t in hits[:3]:
                if t["hs_code"] not in [x["hs_code"] for x in products]:
                    products.append({"hs_code": t["hs_code"], "rate": t["rate"],
                                     "description": t["heading_text"] + " — " + t["description"]})
    return {"passages": passages, "products": products[:4]}
