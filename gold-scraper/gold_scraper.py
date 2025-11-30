from datetime import datetime, timezone
import os
import requests
from bs4 import BeautifulSoup
import re

# Zmienne środowiskowe (Railway)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Walidacja Supabase
if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  SUPABASE_URL lub SUPABASE_KEY nie jest ustawiony!")

def send_to_supabase(data):
    """Wysyła dane do Supabase (tabela: investing_gold)"""
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
        
        url = f"{SUPABASE_URL}/rest/v1/investing_gold"
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"✅ Dane wysłane do Supabase: {response.status_code}")
        else:
            print(f"⚠️ Supabase zwrócił: {response.status_code}")
            print(f"   Odpowiedź: {response.text}")
    except Exception as e:
        print(f"❌ Błąd Supabase: {e}")

def scrape_gold_volume():
    """Scrapeuje wolumen złota z CNBC.com używając BeautifulSoup"""
    try:
        print("  🌐 Pobieranie strony CNBC...")
        
        # Headers aby nie zostać zablokowanym
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Pobierz stronę
        response = requests.get(
            "https://www.cnbc.com/quotes/@GC.1",
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Szukaj elementu class="QuoteStrip-volume"
        volume_element = soup.find('div', class_='QuoteStrip-volume')
        
        if volume_element:
            # Wyciągnij tekst
            volume_text = volume_element.get_text()
            print(f"  📝 Znaleziony tekst: {volume_text}")
            
            # Wyciągnij liczbę (usuń przecinki)
            volume_clean = volume_text.replace(",", "").strip()
            
            # Walidacja czy to liczba
            if volume_clean.isdigit():
                print(f"  ✅ Wyodrębniony wolumen: {volume_clean}")
                return volume_clean
            else:
                print(f"  ⚠️  Tekst nie jest liczbą: {volume_clean}")
                return None
        
        print("  ⚠️  Element class='QuoteStrip-volume' nie znaleziony")
        return None
            
    except Exception as e:
        print(f"⚠️  Błąd przy scrapeowaniu: {e}")
        return None

def scrape_gold_data():
    """
    Scrapuje wolumen złota z CNBC.com przy użyciu BeautifulSoup.
    Zbiera TYLKO dane ze strony - bez mock danych!
    """
    # Sprawdzenie czy dzisiaj jest dzień roboczy (pon-pią)
    if not is_business_day():
        print(f"⏸️  Dzisiaj nie jest dzień roboczy (tylko pon–pią). Nic nie robimy.")
        return
    
    try:
        print(f"🔄 Scrapowanie CNBC Złoto ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})...")
        
        # Scrapeuj stronę
        volume = scrape_gold_volume()
        
        if not volume:
            print(f"  ⚠️  Nie udało się pobrać wolumenu ze strony")
            return
        
        print(f"  📊 Wolumen (ze strony): {volume}")
        print("-" * 50)
        
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "volume": volume
        }
        
        send_to_supabase(data)
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        print("-" * 50)

def is_business_day():
    """
    Sprawdza czy dzisiaj jest dzień roboczy (poniedziałek-piątek).
    Używa UTC.
    """
    now_utc = datetime.now(timezone.utc)
    weekday_utc = now_utc.weekday()  # 0=pon, 4=pią, 5=sob, 6=nie
    
    # Tylko pon-pią (0-4)
    return 0 <= weekday_utc <= 4

if __name__ == "__main__":
    print("🚀 SCRAPER CNBC ZŁOTO – TRYB JEDNORAZOWY")
    print(f"   Czas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Źródło: https://www.cnbc.com/quotes/@GC.1")
    print(f"   SUPABASE: {'✅ Configured' if SUPABASE_URL and SUPABASE_KEY else '❌ Not configured'}")
    print("="*50)
    
    scrape_gold_data()
    
    print("🔚 Złoto – skrypt zakończony.")
