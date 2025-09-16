import argparse
import os

from tqdm import tqdm

from .assemble import assemble_summary
from .export import export_csv_row, export_json, export_markdown
from .extract_sections import split_into_sections
from .llm_extract import extract_with_llm
from .parse_pdf import PDFDoc


def process_pdf(pdf_path: str, out_dir: str):
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf = PDFDoc(pdf_path)
    try:
        sections = split_into_sections(pdf)
        metadata = {"title": stem, "citation": stem}
        llm_json = extract_with_llm(metadata, sections)
        summary = assemble_summary(metadata, sections, llm_json)

        md_path = export_markdown(summary, os.path.join(out_dir, "summaries"), stem)
        csv_path = export_csv_row(
            summary, os.path.join(out_dir, "csv", "master_table.csv"), stem
        )
        json_path = export_json(summary, os.path.join(out_dir, "summaries"), stem)
        return {"md": md_path, "csv": csv_path, "json": json_path}
    finally:
        pdf.close()


def main():
    parser = argparse.ArgumentParser(
        description="Batch summarize PDFs into template + exports."
    )
    parser.add_argument("input", help="PDF file or directory containing PDFs")
    parser.add_argument("--out_dir", default="outputs", help="Output base directory")
    args = parser.parse_args()

    if os.path.isdir(args.input):
        pdfs = [
            os.path.join(args.input, f)
            for f in os.listdir(args.input)
            if f.lower().endswith(".pdf")
        ]
    else:
        pdfs = [args.input]

    os.makedirs(args.out_dir, exist_ok=True)

    for pdf in tqdm(pdfs, desc="Processing PDFs"):
        try:
            result = process_pdf(pdf, args.out_dir)
            print(f"✓ {os.path.basename(pdf)} -> {result['md']}")
        except Exception as e:
            print(f"✗ Failed on {pdf}: {e}")


if __name__ == "__main__":
    main()
