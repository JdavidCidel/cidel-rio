import requests
from bs4 import BeautifulSoup
import json

headers = {"User-Agent": "Mozilla/5.0"}

#parsing FINTRAC
def parse_fintrac_article(url):
    #Fetch + parse all
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # scope main article
    content_area = soup.find("main", {"property": "mainContentOfPage"})
    if not content_area:
        #fall back
        content_area = soup.find(id="wb-cont") or soup


    #Extract paragraphs and headers
    desired_elements = content_area.find_all(["h1","h2", "h3", "h4", "h5", "p"])
    texts = []
    for element in desired_elements:
        text = element.get_text(strip=True)
        if not text:
            continue
        #Stop for glossary
        if element.name in ("h1", "h2", "h3") and text.strip().lower() == "glossary":
            break
        texts.append(text)

        #join texts to single string
        full_text = "\n\n".join(texts)


    return full_text

def parse_osfi_article(url):
    #Fetch + parse all
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # scope main article
    content_area = soup.find("main", {"property": "mainContentOfPage"})
    if not content_area:
        #fall back
        content_area = soup.find(id="wb-cont") or soup


    #Extract paragraphs and headers
    desired_elements = content_area.find_all(["h1","h2", "h3", "h4", "h5", "p"])
    texts = []
    for element in desired_elements:
        text = element.get_text(strip=True)
        if not text:
            continue
        # Stop for glossary
        KEYWORDS = ("glossary", "appendix", "annex", "footnote")

        if element.name in ("h1", "h2", "h3") \
                and any(kw in text.strip().lower() for kw in KEYWORDS):
            # break out, skip the rest
            break
        texts.append(text)

        #join texts to single string
        full_text = "\n\n".join(texts)


    return full_text

def parse_osc_article(url):
    #Fetch + parse all
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Scope main content area
    content_area = soup.find("div",class_="newsRelease__editorContent")
    if not content_area:
        content_area = soup.find("article", class_="newsRelease") or soup

    #Gather headers and paragraphs
    elements = content_area.find_all(["h1","h2","h3,","h4","h5","p","div"])
    lines = []

    for el in elements:
        #stop at article container
        if el.name== "div" and "contacts" in el.get("class", []):
            break
        text = el.get_text(strip=True)
        if not text:
            continue
        lines.append(text)

    return "\n\n".join(lines)
