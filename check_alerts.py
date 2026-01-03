import os, json, hashlib, re
from telegram import send_telegram_message
from sources import SOURCES, AGGREGATOR
from scrapers import SCRAPER_MAP

STORE_FILE = "dedupe_store.json"

ALLOW = ["notification","admit","result","cut","answer","schedule","application","interview","dv","corrigendum"]
BLOCK = ["syllabus","eligibility","pattern","tips","preparation","complete detail"]

def ok(title):
    t = title.lower()
    if any(b in t for b in BLOCK): return False
    return any(a in t for a in ALLOW)

def load():
    if not os.path.exists(STORE_FILE):
        return {"posted_ids": []}
    return json.load(open(STORE_FILE))

def save(d): json.dump(d, open(STORE_FILE,"w"), indent=2)

def hid(exam,title,link): 
    return hashlib.sha256(f"{exam}{title}{link}".encode()).hexdigest()

def post(bot, chat, text):
    send_telegram_message(bot, chat, text)

def run():
    bot = os.environ["TELEGRAM_BOT_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    agg = os.environ.get("AGGREGATOR_MODE","off")=="on"

    store = load()
    seen = set(store["posted_ids"])

    for src in SOURCES:
        fn = SCRAPER_MAP[src["kind"]]
        for it in fn(src["url"]):
            if not ok(it["title"]): continue
            h = hid(src["exam"], it["title"], it["link"])
            if h in seen: continue
            seen.add(h)
            post(bot, chat, f"🚨 <b>{src['exam']} ALERT</b>\n{it['title']}\n{it['link']}")
            break

    if agg:
        fn = SCRAPER_MAP[AGGREGATOR["kind"]]
        for it in fn(AGGREGATOR["url"]):
            if not ok(it["title"]): continue
            h = hid("AGG", it["title"], it["link"])
            if h in seen: continue
            seen.add(h)
            post(bot, chat, f"🟡 <b>Possible Update</b>\n{it['title']}\n{it['link']}\nVerify on official site")
            break

    store["posted_ids"] = list(seen)
    save(store)

if __name__ == "__main__":
    run()
