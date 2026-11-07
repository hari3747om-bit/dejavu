"""The brain: takes an alert, (optionally) uses memory, asks the LLM for advice."""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

import memory

load_dotenv()
llm = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

SYSTEM = """You are an on-call incident response assistant.
Return ONLY valid JSON in this shape:
{"summary": "one sentence",
 "hypotheses": [{"cause": "...", "fix": "...", "confidence": 0-100,
                 "evidence": "which past memory supports this, or 'none'"}],
 "skip": ["fixes known NOT to work, based on memory"]}
Rules: if memories are provided, ground your answer in them and NEVER suggest
a fix that memory says failed. If no memory matches, say so in 'evidence' and
give general advice. Max 3 hypotheses, best first."""


def _ask_llm(user_prompt, retries=3):
    """Call the LLM and retry if the JSON comes back broken."""
    last = ""
    for _ in range(retries):
        try:
            resp = llm.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": user_prompt + last}],
                temperature=0.2,
            )
            text = resp.choices[0].message.content.strip()
            text = text.removeprefix("```json").removeprefix("```").removesuffix("```")
            return json.loads(text)
        except Exception as e:
            last = f"\n\nYour previous reply was invalid ({e}). Reply with JSON only."
    return {"summary": "LLM failed to return valid JSON", "hypotheses": [], "skip": []}


def triage(alert, use_memory=True):
    """Returns (advice_dict, memories_used)."""
    memories = []
    prompt = f"ALERT\nService: {alert['service']}\nError: {alert['error']}\n"
    if use_memory:
        memories = memory.recall(f"{alert['service']} {alert['error']}")
        if memories:
            prompt += "\nPAST MEMORIES:\n" + "\n".join(f"- {m}" for m in memories)
        else:
            prompt += "\nPAST MEMORIES: none found."
    else:
        prompt += "\nYou have no memory of past incidents."
    return _ask_llm(prompt), memories


def record_outcome(alert, fix, outcome, notes=""):
    """The learning step: save whether a suggestion worked."""
    memory.remember(
        f"Incident {alert['id']} in {alert['service']} (symptom: {alert['error']}). "
        f"Suggested fix '{fix}'. OUTCOME: {outcome}. {notes}",
        context="engineer feedback",
    )


def close_incident(alert, root_cause, resolution):
    memory.remember(
        f"Incident {alert['id']} in {alert['service']} resolved. Symptom: {alert['error']}. "
        f"Root cause: {root_cause}. Fix that WORKED: {resolution}.",
        context="past incident",
    )
