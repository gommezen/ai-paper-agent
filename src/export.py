import json
from pathlib import Path

import pandas as pd

from .schema import ArticleSummary


def export_markdown(summary: ArticleSummary, out_dir: str, stem: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, f"{stem}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_markdown(summary))
    return md_path


def render_markdown(s: ArticleSummary) -> str:
    def block(title, fw):
        pages = ", ".join(str(p) for p in (fw.evidence_pages or []))
        pages_str = f" _(pp. {pages})_" if pages else ""
        return f"### {title}\n{fw.text}{pages_str}\n\n"

    parts = [f"# Article Summary\n\n**Citation:** {s.citation}\n\n---\n"]
    parts.append(block("1) What is it about — Main questions", s.about_main_questions))
    parts.append(block("1) Purpose / aim", s.about_purpose))
    parts.append(block("1) Theory / key concepts", s.about_theory))

    parts.append(block("2) Methods — Research design", s.methods_design))
    parts.append(block("2) Methods — Data sources", s.methods_data_sources))
    parts.append(block("2) Methods — Sample/participants", s.methods_sample))
    parts.append(block("2) Methods — Instruments/tools", s.methods_instruments))

    parts.append(block("3) Analysis — Type", s.analysis_type))
    parts.append(block("3) Analysis — Techniques/frameworks", s.analysis_techniques))
    parts.append(block("3) Analysis — Validation/reliability", s.analysis_validation))

    parts.append(block("4) Results — Core findings", s.results_core))
    parts.append(block("4) Results — Surprising results", s.results_surprising))
    parts.append(block("4) Results — Contributions", s.results_contributions))
    parts.append(block("4) Results — Limitations", s.results_limitations))

    parts.append(block("5) Future — Gaps", s.future_gaps))
    parts.append(block("5) Future — Extensions", s.future_extensions))
    parts.append(block("5) Future — Your ideas", s.future_your_ideas))

    return "".join(parts)


def export_csv_row(summary: ArticleSummary, csv_path: str, stem: str) -> str:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    row = {
        "id": stem,
        "citation": summary.citation,
        "about_main_questions": summary.about_main_questions.text,
        "methods_design": summary.methods_design.text,
        "analysis_type": summary.analysis_type.text,
        "results_core": summary.results_core.text,
        "future_gaps": summary.future_gaps.text,
    }
    df = pd.DataFrame([row])
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_all = pd.concat([df_existing, df], ignore_index=True)
    else:
        df_all = df
    df_all.to_csv(csv_path, index=False)
    return csv_path


def export_json(summary: ArticleSummary, out_dir: str, stem: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{stem}.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(summary.model_dump_json(indent=2))
    return path
