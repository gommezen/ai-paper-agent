# src/llm_extract.py  — OpenAI SDK ≥ 1.0, project-aware, graceful fallback

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
# OpenAI SDK (new)
from openai import AuthenticationError, BadRequestError, OpenAI, RateLimitError
from pydantic import ValidationError

from .schema import ArticleSummary
from .utils import unique_sorted_pages

load_dotenv()  # read .env if present

TEMPLATE_SYSTEM = (
    "You are an academic summarization assistant. "
    "Return ONLY valid JSON that matches the provided JSON schema. "
    "Include short, clear bullet points and page numbers (1-indexed) for evidence."
)


# what is this block doing?
# Build a user prompt with paper metadata and available sections
# If title/citation missing, use placeholders
# List available sections
# Instruct to fill all fields succinctly, leaving empty strings/[] if unknown
# Return the constructed prompt as a single string
#
def _build_user_prompt(metadata: Dict[str, Any], sections: Dict[str, str]) -> str:
    title = metadata.get("title") or "Unknown Title"
    citation = metadata.get("citation") or ""
    p = [f"Paper: {title}", f"Citation: {citation}", "Sections provided:"]
    for k in sections.keys():
        p.append(f"- {k}")
    p.append(
        "Fill all template fields succinctly. If unknown, leave empty strings and [] for pages."
    )
    return "\n".join(p)


def _fwe():
    return {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "evidence_pages": {"type": "array", "items": {"type": "integer"}},
        },
        "required": ["text", "evidence_pages"],
        "additionalProperties": False,
    }


def _schema_json():
    # Define properties once
    props = {
        "citation": {"type": "string"},
        "about_main_questions": _fwe(),
        "about_purpose": _fwe(),
        "about_theory": _fwe(),
        "methods_design": _fwe(),
        "methods_data_sources": _fwe(),
        "methods_sample": _fwe(),
        "methods_instruments": _fwe(),
        "analysis_type": _fwe(),
        "analysis_techniques": _fwe(),
        "analysis_validation": _fwe(),
        "results_core": _fwe(),
        "results_surprising": _fwe(),
        "results_contributions": _fwe(),
        "results_limitations": _fwe(),
        "future_gaps": _fwe(),
        "future_extensions": _fwe(),
        "future_your_ideas": _fwe(),
    }

    # REQUIRED must include EVERY key
    required = list(props.keys())

    return {
        "type": "object",
        "properties": props,
        "required": required,
        "additionalProperties": False,
    }


def _mock_output(metadata: Dict[str, Any]) -> Dict[str, Any]:
    citation = metadata.get("citation", "")

    def mk(txt=""):
        return {"text": txt, "evidence_pages": []}

    return {
        "citation": citation,
        "about_main_questions": mk(""),
        "about_purpose": mk("%"),
        "about_theory": mk(""),
        "methods_design": mk(""),
        "methods_data_sources": mk(""),
        "methods_sample": mk(""),
        "methods_instruments": mk(""),
        "analysis_type": mk(""),
        "analysis_techniques": mk(""),
        "analysis_validation": mk(""),
        "results_core": mk(""),
        "results_surprising": mk(""),
        "results_contributions": mk(""),
        "results_limitations": mk(""),
        "future_gaps": mk(""),
        "future_extensions": mk(""),
        "future_your_ideas": mk(""),
    }


def _read_structured_or_json(resp, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prefer SDK-parsed structured output (message.parsed). Fall back to raw content->json.
    On empty/invalid content, return mock so pipeline continues.
    """
    msg = resp.choices[0].message
    parsed = getattr(msg, "parsed", None)

    if parsed is not None:
        return parsed

    content = (msg.content or "").strip()
    if not content:
        print("⚠️ Model returned empty content; falling back to mock output.")
        return _mock_output(metadata)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("⚠️ JSON decode failed. First 200 chars:\n", content[:200])
        print("   Falling back to mock output.")
        return _mock_output(metadata)


def extract_with_llm(
    metadata: Dict[str, Any], sections: Dict[str, str]
) -> Dict[str, Any]:
    """
    Uses OpenAI SDK ≥ 1.0. Supports project-scoped keys (sk-proj-…) via OPENAI_PROJECT.
    Falls back to mock (empty fields) on missing key or API errors so the pipeline still completes.
    """
    # Manual offline override
    if os.getenv("FORCE_MOCK", "").strip() == "1":
        print("ℹ️ FORCE_MOCK=1 — returning mock output.")
        return _mock_output(metadata)

    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip()
    # Some models reject temperature overrides; keep available but don't force
    temp_env = (os.getenv("TEMPERATURE") or "").strip()
    temperature = None
    if temp_env not in ("", "1", "1.0"):
        try:
            temperature = float(temp_env)
        except ValueError:
            temperature = None

    project_id = (os.getenv("OPENAI_PROJECT") or "").strip() or None

    if not api_key:
        print("⚠️ No OPENAI_API_KEY found — returning mock output.")
        return _mock_output(metadata)

    # Initialize client (project-aware; harmless if project_id is None)
    client = OpenAI(api_key=api_key, project=project_id)

    user_prompt = _build_user_prompt(metadata, sections)
    schema = _schema_json()

    try:
        kwargs = {
            "model": model,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "article_summary_schema",
                    "schema": schema,
                    "strict": True,
                },
            },
            "messages": [
                {"role": "system", "content": TEMPLATE_SYSTEM},
                +{"role": "user", "content": user_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "sections": sections,
                            "instructions": (
                                "Return a JSON object strictly matching the schema. "
                                "Bullet points welcome. Provide evidence page numbers as a list of integers."
                            ),
                        }
                    ),
                },
            ],
            "max_completion_tokens": 1200,
        }
        # Only pass temperature if user requested a non-default and model might support it
        if temperature is not None:
            kwargs["temperature"] = temperature

        resp = client.chat.completions.create(**kwargs)
        data = _read_structured_or_json(resp, metadata)

    except BadRequestError as e:
        # Common causes: unsupported params (e.g., temperature) or token budget
        print("⚠️ OpenAI BadRequestError:", str(e))
        # Minimal retry: drop temperature & max_completion_tokens to appease stricter models
        try:
            resp = client.chat.completions.create(
                model=model,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "article_summary_schema",
                        "schema": schema,
                        "strict": True,
                    },
                },
                messages=[
                    {"role": "system", "content": TEMPLATE_SYSTEM},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "sections": sections,
                                "instructions": (
                                    "Return a JSON object strictly matching the schema. "
                                    "Bullet points welcome. Provide evidence page numbers as a list of integers."
                                ),
                            }
                        ),
                    },
                ],
            )
            data = _read_structured_or_json(resp, metadata)
        except Exception as e2:
            print("⚠️ Retry also failed:", type(e2).__name__, "-", str(e2))
            print("   Falling back to mock output.")
            return _mock_output(metadata)

    except (AuthenticationError, RateLimitError) as e:
        # Auth/billing errors → continue in mock mode so exports still happen
        print("⚠️ LLM call failed:", type(e).__name__, "-", str(e))
        print("   Falling back to mock output so the pipeline can continue.")
        return _mock_output(metadata)

    # Validate with Pydantic and normalize pages
    try:
        _ = ArticleSummary(**data)
    except ValidationError as e:
        raise RuntimeError(f"LLM returned invalid schema: {e}")

    for k, v in data.items():
        if isinstance(v, dict) and "evidence_pages" in v:
            v["evidence_pages"] = unique_sorted_pages(
                [int(p) for p in v["evidence_pages"] if isinstance(p, (int, float))]
            )
    return data
