# MapleShift

Shift the cost. Keep the margin.

Upload a supplier invoice and see what Canada's counter-tariffs on US goods
(effective Sept 8, 2026) cost you, how sure we are about each number, and what to do next.

## Run it (Windows, VS Code terminal)

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env        (then open .env and paste your OpenRouter key)
    python app.py

Open http://127.0.0.1:5000 and click "Try a sample invoice".
The app works without a key too: AI features fall back to rules and official links.

## Pages

| Page | What it does |
|---|---|
| Home | Landing page: pitch, how it works, features, trust, future vision |
| Check | Upload a CSV or Excel file (including QuickBooks and Xero exports), use a sample, or check one item |
| Results | Totals, cost chart, item table, Origin Detective, supplier comparison |
| Ask | Answers quoted only from official Finance Canada text |
| Get help | Expert finder: live search (OpenRouter) or official fallback list |
| Report | Printable report in English, French, Punjabi, Mandarin |

## Where things live

    app.py              routes for every page
    core/importer.py    reads CSV/Excel, Xero bills, QuickBooks grouped reports
    core/engine.py      parse -> match -> origin -> calculate -> checklist  (no AI in the math)
    core/ai.py          OpenRouter: pick from official candidates only; live expert search
    core/help.py        expert finder with fallback
    core/i18n.py        preset translations (numbers are never translated)
    data/tariffs.csv    rows from the official Finance Canada list
    data/passages.json  quotable official passages (backgrounder + news release)
    data/sample_invoice.csv   demo invoice (real codes, made-up business)
    data/resources.json official help links

## Before the demo

1. **Full tariff list:** data/tariffs.csv has 84 real rows copied from the official list.
   Replace it with your full 629-row tariffs.csv (needs columns hs_code, description,
   rate_percent; heading_text optional; rename "hs_heading" to "heading_text" if needed).
2. **Exchange rate:** set USD_TO_CAD in core/engine.py to the Bank of Canada rate for today.

## The honesty rules

- Rates come only from tariffs.csv. Math is plain Python.
- The AI may only choose among codes we already found; anything else is ignored.
- Every result is labelled Verified, Estimated, or Needs review.
- Unsure items go to a human expert, never a guess.

## QuickBooks Online exports

Reports > "Purchases by Product/Service Detail" > Export > Export to Excel, then upload the .xlsx.
The importer skips the title rows and "Total for ..." rows, and uses the product group
headings as the product name. QuickBooks has no HS code or country of origin, so the tool
matches by description and asks once per supplier where their goods are made.
data/sample_quickbooks_export.xlsx copies that real layout (from the QuickBooks Canada test drive).
