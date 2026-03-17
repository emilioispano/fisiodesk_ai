import re
from typing import List


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_pain_scores(text: str) -> List[int]:
    t = normalize_text(text)
    matches = re.findall(r"\b([0-9]|10)\s*/\s*10\b", t)
    return [int(x) for x in matches]
