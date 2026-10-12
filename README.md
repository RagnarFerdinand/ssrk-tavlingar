# SSRK prov

Kommande prov för Svenska Spaniel och Retrieverklubben (SSRK). Webbapp i `docs/` (GitHub Pages),
skrapare i `scraper/` och en nattlig GitHub Action (`.github/workflows/uppdatera.yml`) som sparar
`docs/data/tavlingar.json`.

## Källa
SKK Start: `https://skkstart.se/events?federation_id=5` (id 5 = Svenska Spaniel och Retrieverklubben).
Serverrenderad HTML, 10 prov per sida. Skraparen läser alla sidor och lämnar filen orörd om inga prov hittas
(t.ex. om sidan ändrats).

## Öppet
- Skraparen läser HTML och kan gå sönder om SKK Start ändrar layouten.
- Plats och klubb är fritext från SKK Start ("inom avd" betyder att provet hålls inom avdelningen).
