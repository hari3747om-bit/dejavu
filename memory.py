"""Thin wrapper around Hindsight so the rest of the app stays simple."""
import os


from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()

BANK = os.getenv("MEMORY_BANK", "acme-sre")

_kwargs = {"base_url": os.getenv("HINDSIGHT_BASE_URL", "http://localhost:8888")}
if os.getenv("HINDSIGHT_API_KEY"):
    _kwargs["api_key"] = os.getenv("HINDSIGHT_API_KEY")
client = Hindsight(**_kwargs)


def remember(text, context=None, timestamp=None):
    """RETAIN: save something the agent should remember."""
    kw = {"bank_id": BANK, "content": text}
    if context:
        kw["context"] = context
    if timestamp:
        kw["timestamp"] = timestamp
    return client.retain(**kw)


def recall(query):
    """RECALL: look up relevant memories. Returns a list of memory texts."""
    results = client.recall(bank_id=BANK, query=query)
    return [r.text for r in results.results]


def reflect(question):
    """REFLECT: ask Hindsight to find patterns across all memories."""
    return client.reflect(bank_id=BANK, query=question)
