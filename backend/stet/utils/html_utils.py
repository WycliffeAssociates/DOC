from bs4 import BeautifulSoup, NavigableString

def clean_chapter_html(chapter: str) -> str:
    verse_dict: dict[str, str] = {}
    soup = BeautifulSoup(chapter, "html.parser")
    for verse_span in soup.find_all("span", class_="verse"):
        # Remove footnote callers
        for caller in verse_span.find_all("sup", class_="caller"):
            caller.decompose()
        # Fix spacing issue for poetry divs
        for poetry_div in verse_span.find_all(
            "div", class_=lambda c: c and c.startswith("poetry-")
        ):
            poetry_div.insert_before(NavigableString(" "))
    return str(soup)
