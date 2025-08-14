import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from parsing import *

#using a user-agent so not denied as a bot
headers = {"User-Agent": "Mozilla/5.0"}

def scrape_fintrac_notices(limit=15, exclude_keywords=None):
    url = "https://fintrac-canafe.canada.ca/notices-avis/notices-avis-eng"
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    notices = []

    #Each notice in an <li class "li.list-group-item row">
    for row in soup.select("main li.list-group-item.row"):
        #Date is in #<span class="col-md-2">
        date_span = row.find("span", class_="col-md-2")
        if not date_span:
            continue
        date_text = date_span.get_text(strip=True)

        #Title and url in <a class="col-md-10">
        a = row.find ("a", class_="col-md-10", href=True)
        if not a:
            continue
        title = a.get_text (strip=True)
        href = a["href"].strip()

        #exclude if keywords are in title
        if exclude_keywords and any(kw.lower() in title.lower() for kw in exclude_keywords):
            continue

        # build full url
        if href.startswith("http"):
            full_url = href
        else:
            full_url = f"https://fintrac-canafe.canada.ca{href}"

        #parse whole article
        content = parse_fintrac_article(full_url)

        notices.append({
            "source": "FINTRAC",
            "title": title,
            "url": full_url,
            "date": date_text,
            "article": content,
        })

        if len(notices) >= limit:
            break

    return notices

def scrape_OSFI_notices(limit=15, article_sector=None):
    url = "https://www.osfi-bsif.gc.ca/en/guidance/guidance-library"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tbody tr")
    entries = []

    for row in rows:
        cols = row.find_all("td")
        #date, title/url, sector columns
        if len(cols) < 3:
            continue

        #extract date from column 1
        date_text = cols[0].get_text(strip=True)

        # extracting title and url from column 2
        title_tag = cols[1].find("a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        href = title_tag["href"].strip()
        full_url = f"https://www.osfi-bsif.gc.ca{href}" if href.startswith("/") else href

        # extract sectors from column 3
        sectors = [li.get_text(strip=True) for li in cols[2].find_all("li")]
        if not any(any(s.lower() in sector.lower() for s in article_sector) for sector in sectors):
            continue

        content = parse_osfi_article(full_url)

        entries.append({
            "source": "OSFI",
            "title": title,
            "date": date_text,
            "url": full_url,
            "sector": sectors,
            "article": content
        })

        # limit amount of articles
        if len(entries) >= limit:
            break

    return entries

def scrape_OSC_notices(limit=15, article_related_to=None):
    url = "https://www.osc.ca/en/news-events/news?keyword=&category%5B5036%5D=5036&category%5B5041%5D=5041&category%5B5061%5D=5061&category%5B5056%5D=5056&date%5Bmin%5D=&date%5Bmax%5D=&sort_bef_combine=field_publication_date_DESC"

    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    notices = []

    for row in soup.select("div.table-row__content"):
        # column-3 -> dates
        date_divs = row.find_all("div", class_="column-3")
        if not date_divs:
            continue
        date_text = date_divs[0].get_text(strip=True)

        #column-6 -> title and link
        title_div = row.find("div", class_="column-6")
        if not title_div:
            continue
        a = title_div.find("a", href=True)
        if not a:
            continue

        title = a.get_text(strip=True)
        href = a["href"].strip()
        full_url = f"https://www.osc.ca{href}"

        content = parse_osc_article(full_url)

        notices.append({
            "source": "OSC",
            "title": title,
            "url": full_url,
            "date": date_text,
            "article": content,
        })

        if len(notices) >= limit:
            break

    return notices


#all articles in one place
def scrape_all_articles():
    items = []
    items.extend(scrape_OSFI_notices(
        limit=15,
        article_sector=[
            "Bank Act",
            "Banks",
            "Trust and Loan Companies",
            "Trust and Loan Companies Act",
        ],
    ))
    items.extend(scrape_fintrac_notices(limit=15, exclude_keywords=["News release"]))
    items.extend(scrape_OSC_notices(limit=15))
    return items
