import re
from typing import Optional


def is_valid_int(text: str) -> bool:
    try:
        int(text)
        return True
    except ValueError:
        return False


def extract_chapter_and_beyond(text: str) -> Optional[str]:
    # Regular expression to match "<chapter_num>:<verse_num> [comment]"
    match = re.search(r"\d+:\d+(\s*\(\*\*?\))?$", text)
    if match:
        return match.group()
    return None
