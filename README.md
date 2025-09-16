# AI Paper Agent

[![CI - Summarizer](https://github.com/<gommezen>/<ai-paper-agent>/actions/workflows/ci.yml/badge.svg)](https://github.com/<gommezen>/<ai-paper-agent>/actions/workflows/ci.yml)

An **AI-powered pipeline** for summarizing academic PDFs into structured Markdown, JSON, and CSV — with page-anchored evidence and a reproducible CI/CD flow.

---

## 📚 Table of Contents
- [✨ Features](#-features)
- [🚀 Quickstart](#-quickstart)
- [⚙️ Configuration](#️-configuration)
- [🛠️ Pipeline](#️-pipeline)
- [📑 Template](#-template)
- [🔧 Extending](#-extending)
- [✅ Continuous Integration](#-continuous-integration)
- [📜 License](#-license)

---

## ✨ Features
- 🧭 **Template-first extraction**: About, Methods, Analysis, Results, Future
- 📄 **Page-anchored evidence**: each field links back to source pages
- 📦 **Batch mode**: process a folder of PDFs at once
- 🔒 **Mock mode**: runs without API key (offline safe)
- ✅ **CI-ready**: GitHub Actions runs linting, pytest, and pipeline with `data/sample/sample.pdf`

---

## 🚀 Quickstart

```bash
# 1) Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Configure environment (optional for real LLM extraction)
cp .env.example .env
# edit .env and add your API key + project ID if needed

# 4) Run pipeline on the sample PDF
python -m src.batch data/sample --out_dir outputs

# 5) Explore in Jupyter
jupyter notebook notebooks/01_single_pdf_demo.ipynb
```

Outputs will appear in:

outputs/summaries/<paper_name>.md

outputs/csv/master_table.csv (one row per paper)

outputs/summaries/<paper_name>.json (raw structured output)

---

⚙️ Configuration

Create `.env` (or edit environment variables):

```
OPENAI_API_KEY=sk-...        # your API key (use GitHub Secrets in CI)
OPENAI_PROJECT=proj_...      # optional: project-scoped keys
OPENAI_MODEL=gpt-4.1-mini    # or gpt-5-mini if available
TEMPERATURE=1
```

In CI/CD, keys are injected via GitHub Secrets — never commit them to .env.

---

🛠️ Pipeline

1. Parse: PyMuPDF loads text page-by-page
2. Section: heuristics split into Abstract / Methods / Results / Conclusion
3. Extract: prompts the LLM with strict JSON schema (schema.py)
4. Assemble: merges fields into structured Article Summary Template
5. Export: saves Markdown, JSON, and appends to master CSV

---

📑 Template

The canonical schema is in src/schema.py.
A worked example is in notebooks/01_single_pdf_demo.ipynb with data/sample/sample.pdf.

---

🔧 Extending

- Add new fields → src/schema.py
- Customize prompts → src/llm_extract.py
- Improve sectioning → integrate GROBID or science-parse
- Add new exports → extend src/export.py (Zotero, Notion, etc.)

---
✅ Continuous Integration

- Linting with flake8
- Tests with pytest (tests/test_basic.py included)
- Full pipeline run on data/sample/sample.pdf
- Outputs uploaded as GitHub Action artifacts
---

📜 License

MIT
