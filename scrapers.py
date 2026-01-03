import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

UA = {"User-Agent": "Mozilla/5.0"}

def get_soup(url: str):
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")

def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def scrape_ibps_so(url):
    soup = get_soup(url)
    items = []
    for a in soup.select("a[href]"):
        title = clean(a.get_text())
        href = a.get("href")
        if title and any(k in title.lower() for k in ["notification","admit","result","interview","corrigendum","window"]):
            items.append({"title": title, "date": "", "link": urljoin(url, href)})
    return items

def scrape_sbi_careers(url):
    soup = get_soup(url)
    items = []
    for a in soup.select("a[href]"):
        title = clean(a.get_text())
        href = a.get("href")
        if "recruitment.sbi.bank.in" in href:
            items.append({"title": title, "date": "", "link": href})
    return items

def scrape_ssc_notices(url):
    soup = get_soup(url)
    items = []
    for tr in soup.select("table tr"):
        tds = [clean(td.get_text()) for td in tr.select("td")]
        if len(tds) >= 3:
            a = tr.select_one("a[href]")
            if a:
                items.append({"title": " | ".join(tds), "date": tds[0], "link": urljoin(url, a["href"])})
    return items

def scrape_mppsc_whats_new(url):
    soup = get_soup(url)
    items = []
    for a in soup.select("a[href]"):
        title = clean(a.get_text())
        if "Dated" in title:
            items.append({"title": title, "date": "", "link": urljoin(url, a["href"])})
    return items

def scrape_uppsc_notifications(url):
    soup = get_soup(url)
    items = []
    for tr in soup.select("table tr"):
        tds = [clean(td.get_text()) for td in tr.select("td")]
        if len(tds) >= 4:
            a = tr.select_one("a[href]")
            if a:
                items.append({"title": " | ".join(tds), "date": "", "link": urljoin(url, a["href"])})
    return items

def scrape_mpsc_adv_notifications(url):
    soup = get_soup(url)
    items = []
    for tr in soup.select("table tr"):
        tds = [clean(td.get_text()) for td in tr.select("td")]
        if len(tds) >= 2:
            a = tr.select_one("a[href]")
            if a:
                items.append({"title": " | ".join(tds), "date": "", "link": urljoin(url, a["href"])})
    return items

def scrape_mpesb_hindi_home(url):
    soup = get_soup(url)
    items = []
    for a in soup.select("a[href]"):
        title = clean(a.get_text())
        if any(k in title for k in ["सूचना","परीक्षा","भर्ती","परिणाम","उत्तर"]):
            items.append({"title": title, "date": "", "link": urljoin(url, a["href"])})
    return items

def scrape_careers360_upcoming(url):
    soup = get_soup(url)
    items = []
    for tr in soup.select("table tr"):
        tds = [clean(td.get_text()) for td in tr.select("td")]
        if len(tds) >= 3:
            a = tr.select_one("a[href]")
            if a:
                items.append({"title": " | ".join(tds), "date": "", "link": a["href"]})
    return items

SCRAPER_MAP = {
    "ibps_so": scrape_ibps_so,
    "sbi_careers": scrape_sbi_careers,
    "ssc_notices": scrape_ssc_notices,
    "mppsc_whats_new": scrape_mppsc_whats_new,
    "uppsc_notifications": scrape_uppsc_notifications,
    "mpsc_adv_notifications": scrape_mpsc_adv_notifications,
    "mpesb_hindi_home": scrape_mpesb_hindi_home,
    "careers360_upcoming": scrape_careers360_upcoming,
}
