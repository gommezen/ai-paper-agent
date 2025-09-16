import re
from typing import Dict

from .parse_pdf import PDFDoc

SECTION_HEADINGS = [
    "abstract",
    "introduction",
    "background",
    "methods",
    "methodology",
    "data",
    "materials and methods",
    "analysis",
    "results",
    "findings",
    "discussion",
    "limitations",
    "conclusion",
    "conclusions",
    "acknowledgments",
    "references",
]


def split_into_sections(pdf: PDFDoc) -> Dict[str, str]:
    text = pdf.get_all_text()
    # Construct a regex to capture headings
    pattern = (
        r"(?im)^\s*(" + "|".join([re.escape(h) for h in SECTION_HEADINGS]) + r")\s*$"
    )
    # Find all headings with positions
    positions = [(m.group(1).lower(), m.start()) for m in re.finditer(pattern, text)]
    if not positions:
        # Fall back to naive chunks
        n = pdf.num_pages()
        return {
            "abstract_or_intro": "\n".join(pdf.pages[: min(2, n)]),
            "body": "\n".join(pdf.pages[min(2, n) : max(n - 1, 2)]),
            "conclusion": pdf.pages[-1] if n > 0 else "",
        }

    # Add end marker
    positions.append(("__END__", len(text)))
    sections = {}
    for i in range(len(positions) - 1):
        name, start = positions[i]
        _, end = positions[i + 1]
        content = text[start:end].strip()
        sections[name] = content
    return sections
