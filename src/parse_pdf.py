import fitz  # PyMuPDF


class PDFDoc:
    def __init__(self, path: str):
        self.path = path
        self.doc = fitz.open(path)
        self.pages = [p.get_text("text") for p in self.doc]  # simple text mode
        # Build a quick map of page index -> text
        self.page_map = {i + 1: self.pages[i] for i in range(len(self.pages))}

    def num_pages(self) -> int:
        return len(self.pages)

    def get_page_text(self, page_number: int) -> str:
        return self.page_map.get(page_number, "")

    def get_all_text(self) -> str:
        return "\n".join(self.pages)

    def close(self):
        self.doc.close()
