"""
Expert finder. When the tool is unsure, it points people to real help
instead of guessing. Live search runs through OpenRouter if OPENROUTER_API_KEY
is set; otherwise (or on any error, timeout or rate limit) it shows the fixed
list of official resources. It never fails.
"""
from . import ai
from .engine import RESOURCES

HELP_PROMPT = """You help a small business in Ontario, Canada find real help with Canada's
counter-tariffs on US goods (effective September 8, 2026).
Search the web. For the items listed, suggest where to get help, in this order:
1. Official Government of Canada or Ontario pages
2. Licensed customs brokers or trade advisors in the Greater Toronto Area
3. Industry associations for this type of business
Rules: only mention organizations you found in the search results. Never invent names,
phone numbers or links. Never state a tariff rate. Plain, simple English. Under 180 words."""


def find_expert_help(items):
    """Returns (text_or_None, sources). text is None when we use the fixed list."""
    if not items:
        return None, RESOURCES
    question = ("My business buys these items and we're not sure how the counter-tariffs apply:\n"
                + "\n".join(f"- {i}" for i in items) + "\nWhere can I get expert or official help?")
    text, sources = ai.web_help(HELP_PROMPT, question)
    if text:
        return text, sources
    return None, RESOURCES
