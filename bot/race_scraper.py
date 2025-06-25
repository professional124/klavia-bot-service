
# race_scraper.py
# Extracts and formats race text from Klavia.io

from bs4 import BeautifulSoup

def extract_race_text(html: str) -> str:
    '''
    Takes HTML from the #typing-text element and returns clean text to type.
    It handles nested spans, line breaks, boost-words, etc.
    '''
    soup = BeautifulSoup(html, "html.parser")
    text_div = soup.find("div", {"id": "typing-text"})
    if not text_div:
        return ""

    output = ""
    for element in text_div.descendants:
        if element.name == "br" or "newline-indicator" in element.get("class", []):
            output += "\n"
        elif element.string:
            output += element.string
    return output.strip()
