import schedule
import time
from datetime import datetime, timezone, timedelta
import csv
import os
import requests
from playwright.sync_api import sync_playwright

DATA_FILE = "investing_oil.csv"

# Zmienne środowiskowe (Railway, lokalne .env)
MOCK_VOLUME = os.environ.get("MOCK_VOLUME", None)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Walidacja Supabase
if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  SUPABASE_URL lub SUPABASE_KEY nie jest ustawiony!")

def scrape_investing_volume():
    """Scrapeuje wolumen ropy z Investing.com"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            page = browser.new_page()
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            page.goto("https://pl.investing.com/commodities/crude-oil", timeout=60000, wait_until="networkidle")
            
            # Czekaj na załadowanie elementów
            page.wait_for_timeout(2000)
            
            # Szukaj data-test="volume"
            try:
                volume_element = page.locator('[data-test="volume"]')
                volume_text = volume_element.text_content()
                
                # Wyciągnij liczbę z teksty
                import re
                match = re.search(r'[\d]+[\.,][\d]+', volume_text)
                if match:
                    volume = match.group(0).replace(",", ".")
                    browser.close()
                    return volume
            except Exception as e:
                print(f"  ⚠️  Selektor volume nie znaleziony: {e}")
            
            browser.close()
            return None
            
    except Exception as e:
        print(f"⚠️  Błąd przy scrapeowaniu: {e}")
        return None

def save_to_csv(data):
    file_exists = os.path.isfile(DATA_FILE)
    try:
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "volume"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        print(f"✅ Dane zapisane do {DATA_FILE}")
    except Exception as e:
        print(f"❌ Błąd przy zapisywaniu: {e}")

def send_to_webhook(data):
    """Wysyła dane do Supabase"""
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        payload = {
            "timestamp": data["timestamp"],
            "volume": data["volume"]
        }
        
        url = f"{SUPABASE_URL}/rest/v1/investing_oil"
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"✅ Dane wysłane do Supabase: {response.status_code}")
        else:
            print(f"⚠️ Supabase zwrócił: {response.status_code}")
            print(f"   Odpowiedź: {response.text}")
    except Exception as e:
        print(f"❌ Błąd Supabase: {e}")

def scrape_investing_data():
    """
    Scrapuje wolumen ropy z Investing.com przy użyciu Playwright.
    Jeśli scrapeowanie nie uda się, używa MOCK_VOLUME jako fallback.
    """
    # Sprawdzenie czy jesteśmy w sesji handlowej ropy
    if not is_oil_trading_session():
        print(f"⏸️  Poza sesją handlową ropy (UTC-5: pon-pią 9:00-14:30)")
        return
    
    try:
        print(f"🔄 Scrapowanie Investing.com ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})...")
        
        # Próbuj scrapeować stronę
        volume = scrape_investing_volume()
        
        if volume:
            print(f"  📊 Wolumen (ze strony): {volume}")
        elif MOCK_VOLUME:
            print(f"  📊 Wolumen (mock fallback): {MOCK_VOLUME}")
            volume = MOCK_VOLUME
        else:
            print(f"  ⚠️  Nie udało się pobrać wolumenu i brak MOCK_VOLUME")
            return
        
        print("-" * 50)
        
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "volume": volume
        }
        
        save_to_csv(data)
        send_to_webhook(data)
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        print("-" * 50)

def is_oil_trading_session():
    """
    Sprawdza czy jesteśmy w sesji handlowej ropy.
    Sesja UTC-5: poniedziałek-piątek 9:00-14:30
    Konwersja do UTC: od poniedziałku 14:00 do soboty 19:30 (UTC)
    """
    # Pobieramy aktualny czas w UTC
    now_utc = datetime.now(timezone.utc)
    
    # Dzień tygodnia (0=poniedziałek, 6=niedziela)
    weekday_utc = now_utc.weekday()
    hour_utc = now_utc.hour
    minute_utc = now_utc.minute
    
    # Sesja w UTC-5: pon-pią 9:00-14:30 = pon 14:00 UTC do sob 19:30 UTC
    is_session = False
    
    if weekday_utc == 0:  # Poniedziałek
        is_session = (hour_utc > 14) or (hour_utc == 14 and minute_utc >= 0)
    elif 1 <= weekday_utc <= 4:  # Wtorek-piątek
        is_session = True
    elif weekday_utc == 5:  # Sobota
        is_session = (hour_utc < 19) or (hour_utc == 19 and minute_utc <= 30)
    
    return is_session

def job():
    scrape_investing_data()

if __name__ == "__main__":
    print("🚀 SCRAPER INVESTING.COM URUCHOMIONY!")
    print(f"   Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Źródło: https://pl.investing.com/commodities/crude-oil")
    print("   Zbieranie: o równych połówkach godziny (:00 i :30)")
    print("   Sesja: poniedziałek-piątek, UTC-5: 9:00-14:30")
    print("   Tryb: LIVE (automatyczne scrapowanie + fallback MOCK)")
    print(f"   SUPABASE: {'✅ Configured' if SUPABASE_URL and SUPABASE_KEY else '❌ Not set'}")
    print("="*50)
    
    # Nie uruchamiamy job() od razu - czekamy na schedule
    schedule.every().hour.at(":00").do(job)  # Co godzinę o :00
    schedule.every().hour.at(":30").do(job)  # Co godzinę o :30
    
    while True:
        schedule.run_pending()
        time.sleep(60)
