import schedule
import time
from datetime import datetime, timezone, timedelta
import csv
import os
import requests

DATA_FILE = "investing_oil.csv"

# Zmienne środowiskowe (Railway, lokalne .env)
MOCK_VOLUME = os.environ.get("MOCK_VOLUME", "0.0")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

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
    UWAGA: Ta wersja używa mock danych, ponieważ Investing.com ładuje dane dynamicznie
    i Railway nie obsługuje przeglądarek (Playwright, Selenium itp).
    
    Aby zaktualizować dane:
    1. Otwórz https://pl.investing.com/commodities/crude-oil w przeglądarce
    2. Znajdź pole "Wolumen"
    3. Skopiuj wartość (np. 77.626)
    4. Zmień MOCK_VOLUME na tę wartość
    5. Uruchom scraper ponownie
    """
    # Sprawdzenie czy jesteśmy w sesji handlowej ropy
    if not is_oil_trading_session():
        print(f"⏸️  Poza sesją handlową ropy (UTC-5: pon-pią 9:00-14:30)")
        return
    
    try:
        print(f"🔄 Scrapowanie Investing.com ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})...")
        print(f"  📊 Wolumen: {MOCK_VOLUME} (dane mock)")
        print("-" * 50)
        
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "volume": MOCK_VOLUME
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
    print("   Tryb: MOCK (dane ręcznie aktualizowane)")
    print("="*50)
    
    job()
    schedule.every().hour.at(":00").do(job)  # Co godzinę o :00
    schedule.every().hour.at(":30").do(job)  # Co godzinę o :30
    
    while True:
        schedule.run_pending()
        time.sleep(60)
