# AI Paper Agent — Starter Repo

A minimal, extensible agent for **reading academic articles**, **auto-filling a structured template**, and **exporting** to Markdown/CSV — with **page-anchored citations**.

> Works locally in VS Code or Jupyter. Uses PyMuPDF for parsing; optional ChatGPT extraction via the OpenAI API (falls back to simple heuristics if no API key).

---

## Features

- 🧭 **Template-first extraction** (About, Methods & Data, Analysis, Results, Future Work)
- 📄 **Page-anchored evidence** (`evidence_pages` per field)
- 🧩 Modular pipeline (`parse → section → LLM extract → assemble → export`)
- 📦 **Batch mode**: drop a folder of PDFs → summaries + a master CSV
- 🧪 **Mock mode** when `OPENAI_API_KEY` is missing (runs without network)

---

## Quickstart

```bash
# 1) Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Configure env (optional for real LLM extraction)
cp .env.example .env
# then edit .env and add your key

# 4) Run a single PDF (sample provided)
python -m src.batch data/sample --out_dir outputs

# 5) Open the demo notebook
jupyter notebook notebooks/01_single_pdf_demo.ipynb
```

Outputs will appear in:
- `outputs/summaries/<paper_name>.md`
- `outputs/csv/master_table.csv` (one row per paper)

---

## Configuration

Create `.env` (or edit environment variables):

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-mini
TEMPERATURE=0.0
```

You can also set these via command line flags.

---

## Pipeline

1. **Parse**: `PyMuPDF` loads text page-by-page and creates a page map.
2. **Section**: simple heuristics to segment Abstract/Intro/Methods/Results/Discussion/Conclusion/Refs.
3. **Extract**: prompts the LLM with **strict JSON schema** (see `schema.py`). If no key, uses mock extractor.
4. **Assemble**: merges fields into your **Article Summary Template** (+ page evidence).
5. **Export**: Markdown note (Obsidian/Notion-friendly) + CSV row; saves raw JSON too.

---

## Your Template (used in exports)

See `src/schema.py` for the canonical schema and `notebooks/01_single_pdf_demo.ipynb` for a rendered template.
A filled example for *How People Use ChatGPT (2025)* is included in the notebook.

---

## Extending

- Add new fields to `Schema` in `src/schema.py`.
- Customize prompts in `src/llm_extract.py`.
- Improve sectioning by swapping in GROBID or science-parse.
- Add integrations (Zotero/Notion) in `src/export.py`.

---

## License

MIT
