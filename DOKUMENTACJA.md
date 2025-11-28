# 📊 DOKUMENTACJA SCRAPERA - Investing.com Oil Volume

## 🎯 Cel Projektu
Scraper zbiera dane o wolumenie ropy naftowej z serwisu Investing.com (`https://pl.investing.com/commodities/crude-oil`) co **30 minut** (o pełnych godzinach :00 i :30) i zapisuje je do bazy danych Supabase oraz lokalnego pliku CSV.

---

## 🏗️ Architektura Systemu

```
┌─────────────────────────────────────────────────────────┐
│                    RAILWAY.APP (Cloud)                  │
│  - Hosting: 24/7 bez przerw                             │
│  - Python 3.11                                          │
│  - Schedule library (job scheduler)                     │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌────────────────┐  ┌──────────────────┐
│  Supabase DB   │  │  CSV File        │
│  (investing_oil)│  │ (investing_oil.csv)
│                │  │                  │
│ - timestamp    │  │ - timestamp      │
│ - volume       │  │ - volume         │
│ - created_at   │  │ - created_at     │
└────────────────┘  └──────────────────┘
```

---

## 📁 Struktura Projektu

```
crawl4ai-scraper/
├── scraper.py              # Główny skrypt scrapera
├── requirements.txt        # Zależności Python
├── Procfile               # Konfiguracja Railway
├── .git/                  # Git repository
├── README.md              # Instrukcje
└── DOKUMENTACJA.md        # Ta dokumentacja
```

---

## ⚙️ Technologia

| Komponenta | Wersja | Rola |
|-----------|--------|------|
| **Python** | 3.11 | Język programowania |
| **Railway** | - | Hosting (24/7) |
| **Supabase** | - | Baza danych PostgreSQL |
| **Schedule** | 3.10+ | Job scheduler (every().hour.at()) |
| **Requests** | 2.28+ | HTTP requests |
| **Git** | - | Version control (GitHub) |

---

## 🔧 Konfiguracja

### Zmienne Środowiskowe (Railway)

W Railway → Variables dodaj:

```
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_KEY = your-anon-key-here
MOCK_VOLUME = 77.626
```

ℹ️ Nie commituj wrażliwych danych! Użyj `.env` lokalnie i zmiennych środowiskowych na Railway.

### Mock Data (Lokalna Konfiguracja)

Pobierz aktualną wartość z: https://pl.investing.com/commodities/crude-oil

---

## 📊 Schemat Bazy Danych

### Tabela: `investing_oil`

```sql
CREATE TABLE investing_oil (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  timestamp TIMESTAMP NOT NULL,
  volume TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Kolumny:**
- `id` - Unikalny identyfikator (auto-increment)
- `timestamp` - Data i czas pobrania danych (format: YYYY-MM-DD HH:MM:SS)
- `volume` - Wolumen ropy naftowej (tekst, np. "77.626")
- `created_at` - Data utworzenia rekordu w BD

**Przykładowy rekord:**
```json
{
  "id": 1,
  "timestamp": "2025-11-28 16:00:00",
  "volume": "77.626",
  "created_at": "2025-11-28 15:59:59"
}
```

---

## 🔄 Flow Danych

```
1. Railway scheduler → job() uruchamiany o :00 i :30 każdej godziny
        ↓
2. scrape_investing_data() tworzy dict z timestamp + volume
        ↓
3. save_to_csv(data) → zapisuje do investing_oil.csv
        ↓
4. send_to_webhook(data) → wysyła JSON do Supabase API
        ↓
5. Supabase INSERT → nowy rekord w tabeli investing_oil
```

---

## 📝 Funkcje Główne

### `scrape_investing_data()`
**Cel:** Pobiera dane i przygotowuje payload do wysłania

**Parametry:** Brak

**Zwraca:** Nic (zapisuje dane poprzez `save_to_csv()` i `send_to_webhook()`)

**Pseudo-kod:**
```python
1. Print info o scrapowaniu
2. Utwórz dict: {"timestamp": current_time, "volume": MOCK_VOLUME}
3. Zapisz do CSV
4. Wyślij do Supabase
5. Obsłuż błędy
```

---

### `save_to_csv(data)`
**Cel:** Zapisuje dane do lokalnego pliku CSV

**Parametry:**
- `data` (dict) - {"timestamp": str, "volume": str}

**Zwraca:** Nic

**Plik:** `investing_oil.csv`

**Format CSV:**
```
timestamp,volume
2025-11-28 15:49:38,77.626
2025-11-28 16:00:00,77.626
```

---

### `send_to_webhook(data)`
**Cel:** Wysyła dane do Supabase za pośrednictwem REST API

**Parametry:**
- `data` (dict) - {"timestamp": str, "volume": str}

**Zwraca:** Nic

**Endpoint:** `{SUPABASE_URL}/rest/v1/investing_oil`

**Nagłówki HTTP:**
```
apikey: {SUPABASE_KEY}
Content-Type: application/json
Prefer: return=minimal
```

**Payload JSON:**
```json
{
  "timestamp": "2025-11-28 16:00:00",
  "volume": "77.626"
}
```

**Odpowiedzi:**
- `201` ✅ - Sukces, dane zapisane
- `401` ❌ - Błąd autoryzacji (złe API key)
- `400` ❌ - Błąd schematu (złe pole w payload)

---

### `job()`
**Cel:** Wrapper do uruchomienia scrapera z schedulera

**Parametry:** Brak

**Zwraca:** Nic

**Uruchamiane przez:**
```python
schedule.every().hour.at(":00").do(job)
schedule.every().hour.at(":30").do(job)
```

---

## 🔐 Bezpieczeństwo

### Row Level Security (RLS) w Supabase

```sql
ALTER TABLE investing_oil ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public inserts" ON investing_oil
  FOR INSERT
  WITH CHECK (true);
```

**Co to robi:**
- Zezwala na INSERT z publicznego API
- Bezpieczna autoryzacja poprzez `apikey` w nagłówku
- Nie zawiera wrażliwych danych

---

## 🚀 Deployment & Scheduling

### Railway Configuration

**Plik: `Procfile`**
```
worker: python scraper.py
```

**Co to robi:**
- Railway czyta ten plik
- Uruchamia `python scraper.py` na starcie
- Utrzymuje proces 24/7

### Harmonogram Wykonania

| Czas | Akcja |
|------|-------|
| 00:00 | Scraper uruchamia się |
| XX:00 | 🔄 Pobiera dane (job #1) |
| XX:30 | 🔄 Pobiera dane (job #2) |
| Każdy 60 sekund | Sprawdza czy wykonać zaplanowane joby |

**Przykład dzisiaj (28 XI 2025):**
- 15:00 - scraper zbiera dane
- 15:30 - scraper zbiera dane
- 16:00 - scraper zbiera dane
- 16:30 - scraper zbiera dane
- ...i tak co 30 minut

---

## 📋 Logi i Debugowanie

### Logi Railway

Dostępne w: Railway Dashboard → Logs

**Przykładowe logi:**
```
🚀 SCRAPER INVESTING.COM URUCHOMIONY!
   Start: 2025-11-28 15:49:38
   Źródło: https://pl.investing.com/commodities/crude-oil
   Zbieranie: o równych godzinach (:00 i :30)
   Tryb: MOCK (dane ręcznie aktualizowane)
==================================================
🔄 Scrapowanie Investing.com (2025-11-28 15:49:38)...
  📊 Wolumen: 77.626 (dane mock)
--------------------------------------------------
✅ Dane zapisane do investing_oil.csv
✅ Dane wysłane do Supabase: 201
```

### Możliwe Błędy

| Błąd | Przyczyna | Rozwiązanie |
|------|-----------|------------|
| `❌ Błąd Supabase: HTTPSConnectionPool` | Błędny URL Supabase | Sprawdź SUPABASE_URL w Railway Variables |
| `❌ Błąd Supabase: No API key found` | Błędny format nagłówka | Używaj `apikey` zamiast `Authorization` |
| `⚠️ Supabase zwrócił: 401` | Złe API key | Regeneruj anon key w Supabase Settings |
| `⚠️ Supabase zwrócił: 400` | Błędne pole w payload | Sprawdzić czy payload ma `volume` zamiast `est_volume` |
| `❌ Błąd przy zapisywaniu` | Permissions do pliku CSV | Na Railway sprawdź storage |

---

## 🔄 Aktualizacja Danych

### Ręczna Zmiana Wolumenu

1. Otwórz `scraper.py` na GitHub
2. Edytuj linię:
```python
MOCK_VOLUME = "77.626"  # ← Zmień tę wartość
```
3. Kliknij "Commit changes"
4. Railway automatycznie redeploy'uje scraper
5. Następny job będzie zbierać nową wartość

### Pobieranie Aktualnego Wolumenu

1. Wejdź na https://pl.investing.com/commodities/crude-oil
2. Szukaj pola **"Wolumen"**
3. Skopiuj wartość (np. 77.626)
4. Wklej do `MOCK_VOLUME`

---

## 📊 Wyświetlanie Danych na Stronie

### Query do Supabase

```javascript
// Pobierz ostatnie 10 rekordów
const response = await fetch(
  '{SUPABASE_URL}/rest/v1/investing_oil?order=created_at.desc&limit=10',
  {
    headers: {
      'apikey': '{SUPABASE_KEY}',
      'Content-Type': 'application/json'
    }
  }
);

const data = await response.json();
console.log(data);
```

ℹ️ Zastąp `{SUPABASE_URL}` i `{SUPABASE_KEY}` swoimi zmiennymi środowiskowymi.

### API Endpoint

```
GET https://xqlvexlvvxpkolqrcoxd.supabase.co/rest/v1/investing_oil
```

**Query Parameters:**
- `order=created_at.desc` - Sortuj po dacie malejąco
- `limit=10` - Pobierz ostatnie 10 rekordów
- `select=timestamp,volume` - Pobierz tylko te kolumny

---

## 🎯 Przypadki Użycia

### Monitorowanie Wolumenu w Realtime
```python
# Na stronie pokazuj ostatnią wartość
SELECT volume FROM investing_oil ORDER BY created_at DESC LIMIT 1
```

### Analiza Historyczna
```python
# Pokażaj wszystkie dane z ostatnich 24 godzin
SELECT * FROM investing_oil 
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at ASC
```

### Export Danych
```python
# Pobierz CSV z historyą
wget https://raw.githubusercontent.com/oprlab/cme_scrap/main/investing_oil.csv
```

---

## 🔧 Utrzymanie i Skalowanie

### Zmiana Harmonogramu

Zmień z co 30 minut na inny interwał:

```python
# Co 1 godzinę
schedule.every(1).hour.do(job)

# Co 15 minut
schedule.every(15).minutes.do(job)

# Codziennie o 9:00
schedule.every().day.at("09:00").do(job)

# Co poniedziałek o 10:00
schedule.every().monday.at("10:00").do(job)
```

### Dodanie Nowego Pola Danych

1. Edytuj `scraper.py`:
```python
data = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "volume": MOCK_VOLUME,
    "price": MOCK_PRICE,  # ← Nowe pole
}
```

2. Dodaj kolumnę w Supabase:
```sql
ALTER TABLE investing_oil ADD COLUMN price TEXT;
```

3. Aktualizuj CSV fieldnames:
```python
writer = csv.DictWriter(f, fieldnames=["timestamp", "volume", "price"])
```

---

## 📚 Przydatne Linki

- **Investing.com Oil:** https://pl.investing.com/commodities/crude-oil
- **Supabase Dashboard:** https://supabase.com
- **Railway Dashboard:** https://railway.app
- **GitHub Repository:** https://github.com/oprlab/cme_scrap
- **Schedule Library Docs:** https://schedule.readthedocs.io/

---

## ❓ FAQ

**P: Czy mogę zmienić źródło danych z Investing.com na inne?**
A: Tak, zmień `MOCK_VOLUME` na dane z innego źródła i zmień URL w komentarzu.

**P: Jak długo będą przechowywane dane w Supabase?**
A: Bezterminowo, chyba że ręcznie usuniesz. Supabase ma límity storage w planie free.

**P: Czy scraper zahamuje się jeśli Railway będzie offline?**
A: Nie, ale będzie przeskakiwać joby. Po powrocie w line, weźmie się do roboty.

**P: Czy mogę wyświetlić dane na wielu stronach?**
A: Tak, każda strona może query'ować ten sam Supabase endpoint.

**P: Czy dane są szyfrowane?**
A: Tak, Supabase używa SSL/TLS do transmisji. Dane w BD to PostgreSQL default encryption.

---

## 🎓 Architektura Edukacyjna

To projekt demonstracyjny pokazujący:
- ✅ Cloud hosting (Railway)
- ✅ Job scheduling (Schedule library)
- ✅ REST API integration (Supabase)
- ✅ Data persistence (CSV + Database)
- ✅ CI/CD deployment (GitHub → Railway)
- ✅ Error handling & logging
- ✅ Mock data pattern (dla ograniczeń środowiska)

---

**Ostatnia aktualizacja:** 28.11.2025
**Status:** ✅ Produkcyjny (działający 24/7)
