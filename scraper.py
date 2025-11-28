import schedule
import time
from datetime import datetime
import csv
import os
import requests

DATA_FILE = "investing_oil.csv"

# ⚠️ DANE MOCK - Do pobrania raz lokalnie i wklejenia tutaj
# Pobierz z: https://pl.investing.com/commodities/crude-oil
# i zmień wartości poniżej
MOCK_VOLUME = "77.626"  # ← Zmień tę wartość na bieżące dane (Wolumen)

# WEBHOOK - Zmień na URL twojego webhoka do bazy danych
WEBHOOK_URL = "https://twoja-domena.com/webhook"  # ← Zmień na rzeczywisty URL

# SUPABASE CONFIG - Zmień na swoje dane
SUPABASE_URL = "https://xxx.supabase.co"  # ← Zmień na URL projektu
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # ← Zmień na anon key

# Jeśli zmienne środowiskowe są ustawione, użyj ich (Railway)
import os as os_module
SUPABASE_URL = os_module.environ.get("SUPABASE_URL", SUPABASE_URL)
SUPABASE_KEY = os_module.environ.get("SUPABASE_KEY", SUPABASE_KEY)

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
            "est_volume": data["est_volume"]
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

def job():
    scrape_investing_data()

if __name__ == "__main__":
    print("🚀 SCRAPER INVESTING.COM URUCHOMIONY!")
    print(f"   Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Źródło: https://pl.investing.com/commodities/crude-oil")
    print("   Zbieranie: o równych godzinach (:00 i :30)")
    print("   Tryb: MOCK (dane ręcznie aktualizowane)")
    print("="*50)
    
    job()
    schedule.every().hour.at(":00").do(job)  # Co godzinę o :00
    schedule.every().hour.at(":30").do(job)  # Co godzinę o :30
    
    while True:
        schedule.run_pending()
        time.sleep(60)
