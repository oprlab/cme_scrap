# 🥇 Gold Scraper - CNBC

Niezależny scraper do zbierania danych o wolumenie złota z CNBC.

## 📁 Struktura

```
gold-scraper/
├── gold_scraper.py          # Główny skrypt scrapera
├── requirements.txt         # Dependencje Python
├── SUPABASE_SETUP.sql      # SQL do stworzenia tabeli
└── README.md               # Ten plik
```

## 🎯 Co robi?

- Scrapuje **wolumen złota** z: `https://www.cnbc.com/quotes/@GC.1`
- Element HTML: `<div class="QuoteStrip-volume">149,887</div>`
- Wysyła do **Supabase** do tabeli `investing_gold`
- Uruchamiany **co 30 minut** w dni robocze (pon–pią)
- **Tryb jednorazowy** - bez pętli, bez schedula

## 🔧 Zmienne środowiskowe

Używa tych samych zmiennych co oil scraper:
- `SUPABASE_URL` - URL Supabase REST API
- `SUPABASE_KEY` - API key do Supabase

Ustaw je na Railway w: **Settings → Variables**

## 📊 Format danych

```json
{
  "timestamp": "2025-11-30 17:00:00",
  "volume": "149887"
}
```

## 🚀 Wdrożenie na Railway

1. **Stwórz tabelę w Supabase:**
   - Zaloguj się na https://supabase.com/
   - Przejdź do SQL Editor
   - Skopiuj zawartość `SUPABASE_SETUP.sql`
   - Kliknij Run

2. **Dodaj Cron Schedule w Railway:**
   - Przejdź do https://railway.app/
   - Przejdź do projektu
   - Kliknij **"Create"** → **"Cron Job"**
   - Ustawienia:
     - **Command**: `python gold-scraper/gold_scraper.py`
     - **Cron schedule**: `0,30 * * * 1-5` (co 30 min, pon–pią)
     - **Memory**: 256 MB (wystarczy)
   - Kliknij Create

3. **Gotowe!** ✅

## 📝 Testowanie lokalnie

```bash
cd gold-scraper
pip install -r requirements.txt
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
python gold_scraper.py
```

## ⚠️ Ważne

- **Nie modyfikuj** istniejącego `scraper.py` (ropę)
- Złoto jest **całkowicie niezależnym** skryptem
- Działa tylko w **dni robocze** (pon–pią)

## 🔍 Debugowanie

Logi dostępne na Railway w: **Logs** sekcji

Szukaj:
- `🔄 Scrapowanie CNBC Złoto` - start
- `✅ Dane wysłane do Supabase` - sukces
- `⚠️` - warnings
- `❌` - błędy
