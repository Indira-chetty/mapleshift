"""
AI helpers via OpenRouter. Two jobs only, both with fallbacks:

1. pick_candidate(): when keyword matching is unsure, the AI may choose ONE of the
   official candidates we already found. It can never invent a code or a rate.
2. web_help(): live web search for experts (OpenRouter ':online' models).

Put your key in a .env file:   OPENROUTER_API_KEY=sk-or-...
Never paste the key into code or commit .env to GitHub.
"""
import json
import os
import urllib.request

URL = "https://openrouter.ai/api/v1/chat/completions"


def _model():
    return os.getenv("OPENROUTER_MODEL", "anthropic/claude-haiku-4.5")


def enabled():
    return bool(os.getenv("OPENROUTER_API_KEY"))


def _chat(messages, model, timeout=25):
    body = json.dumps({"model": model, "messages": messages, "temperature": 0}).encode()
    req = urllib.request.Request(URL, data=body, headers={
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "X-Title": "MapleShift",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def pick_candidate(description, candidates):
    """Return the hs_code the AI picks from candidates, or None. Never raises."""
    if not enabled() or not candidates:
        return None
    options = "\n".join(f"{c['hs_code']}: {c['heading_text']} — {c['description']}" for c in candidates)
    prompt = (f"Product on an invoice: \"{description}\"\n\nOfficial list entries:\n{options}\n\n"
              "Reply with ONLY the tariff item code of the entry that clearly describes this product, "
              "or NONE if none clearly fits. Do not guess.")
    try:
        data = _chat([{"role": "user", "content": prompt}], _model())
        answer = data["choices"][0]["message"]["content"].strip().split()[0].strip(".,")
        valid = {c["hs_code"] for c in candidates}
        return answer if answer in valid else None   # anything else is ignored
    except Exception:
        return None


def web_help(system_prompt, question):
    """Returns (text, sources) or (None, []) on any failure."""
    if not enabled():
        return None, []
    try:
        data = _chat([{"role": "system", "content": system_prompt},
                      {"role": "user", "content": question}], _model() + ":online", timeout=40)
        msg = data["choices"][0]["message"]
        sources, seen = [], set()
        for a in msg.get("annotations") or []:
            u = (a.get("url_citation") or {})
            if u.get("url") and u["url"] not in seen:
                seen.add(u["url"])
                sources.append({"title": u.get("title") or u["url"], "url": u["url"],
                                "what": "Found by live search", "icon": "search"})
        text = (msg.get("content") or "").strip()
        if not text or not sources:
            return None, []          # no sources = we don't trust it
        return text, sources[:6]
    except Exception:
        return None, []
