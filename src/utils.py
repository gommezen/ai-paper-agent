import re
from typing import List


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def unique_sorted_pages(pages: List[int]) -> List[int]:
    return sorted(sorted(set([p for p in pages if isinstance(p, int) and p > 0])))
