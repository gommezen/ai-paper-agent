# from typing import Any, Dict

from .schema import ArticleSummary


def assemble_summary(metadata: dict, sections: dict, llm_json: dict) -> ArticleSummary:
    summary = ArticleSummary(**llm_json)
    # Attach raw artifacts for transparency
    summary.raw_sections = sections
    summary.raw_llm_json = llm_json
    if not summary.citation:
        summary.citation = metadata.get("citation", "")
    return summary
