"""Hämtar kommande SSRK-prov från SKK Start och skriver docs/data/tavlingar.json.

Källa: https://skkstart.se/events?federation_id=5 (id 5 = Svenska Spaniel och
Retrieverklubben). Sidan är serverrenderad HTML med 10 prov per sida.
"""
import html
import json
import re
import time
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

BAS = "https://skkstart.se/events"
SSRK_ID = 5
UT = Path(__file__).resolve().parent.parent / "docs" / "data" / "tavlingar.json"
MANAD = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"])}
MANAD_EN = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def hamta(sida):
    url = f"{BAS}?federation_id={SSRK_ID}&date_from={date.today().isoformat()}&page={sida}"
    req = urllib.request.Request(url, headers={"User-Agent": "ssrk-tavlingar (GitHub Pages-app)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def datum(s):
    """'28 sep - 31 okt, 2026' / '01 - 31 okt, 2026' / '10 okt, 2026' -> (start, slut) ISO."""
    delar = [d.strip() for d in s.split(" - ")]
    tolk = []
    for d in delar:
        m = re.match(r"(\d{1,2})(?: ([a-zåäö]{3}))?(?:,? (\d{4}))?$", d, re.I)
        tolk.append(list(m.groups()) if m else [None, None, None])
    dag, man, ar = tolk[-1]
    for t in reversed(tolk):  # fyll i månad/år baklänges från slutdatumet
        t[1] = t[1] or man
        t[2] = t[2] or ar
        man, ar = t[1], t[2]
    iso = [f"{int(t[2]):04d}-{MANAD[t[1].lower()]:02d}-{int(t[0]):02d}" for t in tolk]
    return iso[0], iso[-1]


def anmalan(s):
    """'Jul 29 2026' -> '2026-07-29'."""
    m = re.search(r"([A-Za-z]{3}) (\d{1,2}) (\d{4})", s)
    return f"{m[3]}-{MANAD_EN[m[1].lower()]:02d}-{int(m[2]):02d}" if m else ""


def rader(h):
    ut = []
    for rad in re.split(r'<div\s+class=\s*"flex-table-row\s+flex-table-row-striped', h)[1:]:
        celler = {}
        for k in ("event", "date", "location", "federation", "start-registration-date",
                  "last-registration-date", "fee"):
            m = re.search(rf'class="flex-table-cell {k}[^"]*">(.*?)(?=<div class="flex-table-cell|\Z)', rad, re.S)
            celler[k] = m.group(1) if m else ""
        m = re.search(r'href="https://skkstart.se/events/(\d+)".*?#\d+ –\s*<strong>(.*?)</strong>\s*<br>(.*?)</a>',
                      celler["event"], re.S)
        if not m:
            continue
        fed = [text(x) for x in re.split(r"<br\s*/?>", celler["federation"]) if text(x)]
        start, slut = datum(text(celler["date"]))
        ut.append({
            "id": m[1],
            "namn": text(m[2]),
            "klasser": [k.strip() for k in text(m[3]).split(",") if k.strip()],
            "datum": start,
            "slutdatum": slut,
            "plats": text(celler["location"]),
            "klubb": fed[1] if len(fed) > 1 else "",
            "anmalan_start": anmalan(text(celler["start-registration-date"])),
            "anmalan_slut": anmalan(text(celler["last-registration-date"])),
            "avgift": text(celler["fee"]),
            "url": f"https://skkstart.se/events/{m[1]}",
        })
    return ut


def main():
    alla, sett = [], set()
    for sida in range(1, 60):
        ny = [r for r in rader(hamta(sida)) if r["id"] not in sett]
        if not ny:
            break
        sett.update(r["id"] for r in ny)
        alla += ny
        time.sleep(1)
    if not alla:
        raise SystemExit("Inga prov hittades – sidan kan ha ändrats. Behåller gamla filen.")
    alla.sort(key=lambda t: (t["datum"], t["id"]))
    UT.write_text(json.dumps({
        "uppdaterad": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "tavlingar": alla,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(alla)} prov")


if __name__ == "__main__":
    main()
