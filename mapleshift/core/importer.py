"""
Reads invoices and accounting exports into one clean list of rows.

Understands:
- simple tables (our sample CSVs, Xero bill exports)
- QuickBooks Online reports such as "Purchases by Product/Service Detail":
  title rows at the top, product names as GROUP HEADINGS, "Total for ..." rows.
Works with .csv and .xlsx files.
"""
import csv
import io
import re

COLUMN_ALIASES = {
    "description": ["description", "memo/description", "memo", "item description", "goods", "details"],
    "product": ["product/service", "product", "item", "item name", "inventoryitemcode", "item code"],
    "hs_code": ["hs_code", "hs code", "hs", "hts", "hts code", "tariff code", "tariff item", "tariff #", "classification"],
    "quantity": ["quantity", "qty", "units"],
    "unit_price": ["unit_price", "unit price", "unitamount", "rate", "price", "price each", "cost"],
    "amount": ["amount", "lineamount", "line amount", "total", "line total"],
    "currency": ["currency", "curr", "ccy"],
    "made_in": ["made_in", "made in", "country of origin", "origin", "coo", "country"],
    "supplier": ["supplier", "vendor", "contactname", "contact", "seller", "shipper", "name"],
}
_ALIAS = {re.sub(r"[\s_]+", " ", a.lower()): canon for canon, names in COLUMN_ALIASES.items() for a in names}


def _clean_header(h):
    return re.sub(r"[\s_]+", " ", str(h or "").strip().lower())


def _num(v):
    """'$1,234.50' -> 1234.5, '(12.00)' -> -12.0, '' -> None"""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("$", "").replace(",", "").replace("CAD", "").replace("USD", "").strip()
    if not s:
        return None
    neg = s.startswith("(") and s.endswith(")")
    try:
        n = float(s.strip("()"))
    except ValueError:
        return None
    return -n if neg else n


def read_table(filename, data):
    """Bytes of a .csv or .xlsx file -> list of rows (lists of strings)."""
    name = (filename or "").lower()
    if name.endswith((".xlsx", ".xlsm")):
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(data), data_only=True, read_only=True)
        ws = wb.worksheets[0]
        return [["" if c is None else (c if isinstance(c, (int, float)) else str(c)) for c in row]
                for row in ws.iter_rows(values_only=True)]
    text = data.decode("utf-8-sig", errors="ignore") if isinstance(data, bytes) else data
    return list(csv.reader(io.StringIO(text)))


def _find_header(table):
    """The header is the first row (in the top 25) that names a description/product AND a number column."""
    for i, row in enumerate(table[:25]):
        canon = [_ALIAS.get(_clean_header(c)) for c in row]
        if ({"description", "product"} & set(canon)) and ({"quantity", "unit_price", "amount"} & set(canon)):
            return i, canon
    return None, None


def parse_table(table):
    """Returns (rows, problems, source) where source says which layout we recognised."""
    h, canon = _find_header(table)
    if h is None:
        return [], ["We couldn't find a header row with a description and a quantity, price or amount column."], ""

    title = " ".join(str(c) for r in table[:h] for c in r if str(c).strip()).lower()
    source = "QuickBooks report" if ("product/service" in title or "purchases by" in title) else "Table"
    if "contactname" in [_clean_header(c) for c in table[h]]:
        source = "Xero export"

    # Currency written once in the invoice header ("Currency: USD") applies to every line
    header_ccy = ""
    for r in table[:h]:
        cells = [str(c).strip() for c in r if str(c).strip()]
        for k, c in enumerate(cells):
            if c.lower().rstrip(":") == "currency" and k + 1 < len(cells):
                header_ccy = cells[k + 1].upper()[:3]

    col = {}
    for idx, c in enumerate(canon):
        if c and c not in col:
            col[c] = idx

    def cell(row, key):
        idx = col.get(key)
        if idx is None or idx >= len(row):
            return ""
        return row[idx]

    rows, problems, groups = [], [], []
    for n, row in enumerate(table[h + 1:], start=h + 2):
        texts = [str(c).strip() for c in row]
        if not any(texts):
            continue
        first = next((t for t in texts if t), "")
        if first.lower().startswith("total") or first.lower().startswith("grand total"):
            # "Total for Misc" closes that group
            if groups and first.lower().startswith("total for"):
                groups.pop()
            continue
        qty, price, amount = _num(cell(row, "quantity")), _num(cell(row, "unit_price")), _num(cell(row, "amount"))
        desc = str(cell(row, "description")).strip()
        product = str(cell(row, "product")).strip()
        if re.fullmatch(r"[\d.\-#]*", product):   # a line number, not a product name
            product = ""

        # A group heading: text but no numbers (QuickBooks puts product names here)
        if qty is None and price is None and amount is None and not desc:
            label = re.sub(r"\s*\(\d+\)\s*$", "", first)
            if label and not re.match(r"^[\d/\-\.]+$", label):
                groups.append(label)
            continue

        name = product or (groups[-1] if groups else "")
        full_desc = f"{name}: {desc}" if name and desc and name.lower() not in desc.lower() else (desc or name)
        if not full_desc:
            continue
        if qty is None:
            qty = 1.0
        if price is None:
            price = (amount / qty) if (amount is not None and qty) else None
        if price is None:
            problems.append(f"Row {n}: no price or amount, so we skipped it.")
            continue
        warn = ""
        if amount is not None and abs(qty * price - amount) > 0.02 * max(abs(amount), 1):
            warn = f"Qty x price ({qty * price:,.2f}) doesn't match the amount ({amount:,.2f})."
        rows.append({
            "line": len(rows) + 1,
            "description": full_desc,
            "hs_code": str(cell(row, "hs_code")).strip(),
            "quantity": qty,
            "unit_price": price,
            "currency": (str(cell(row, "currency")).strip() or header_ccy or "CAD").upper(),
            "made_in": str(cell(row, "made_in")).strip(),
            "supplier": str(cell(row, "supplier")).strip() or "Unknown supplier",
            "warning": warn,
        })
    if not rows:
        problems.insert(0, "We found the header but no item rows under it.")
    return rows, problems, source
