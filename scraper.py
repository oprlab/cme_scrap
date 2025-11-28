import schedule
import time
from datetime import datetime
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Plik do zapisywania danych
DATA_FILE = "cme_data.csv"

def save_to_csv(data):
    """Zapisuje dane do pliku CSV"""
    file_exists = os.path.isfile(DATA_FILE)
    
    try:
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "est_volume"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
            print(f"✅ Dane zapisane do {DATA_FILE}")
    except Exception as e:
        print(f"❌ Błąd przy zapisywaniu: {e}")

def scrape_cme_data():
    """Zbiera dane z CME Group - EST. VOLUME z tabeli"""
    driver = None
    try:
        print(f"🔄 Scrapowanie CME Group ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})...")
        
        # Konfiguracja opcji Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Uruchom driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Nawiguj do strony
        driver.get("https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html")
        
        # Czekaj aż tabela się załaduje
        wait = WebDriverWait(driver, 15)
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        
        # Czekaj na tym aby dane się wyrenderowały
        time.sleep(2)
        
        # Znajdź wszystkie nagłówki
        headers = driver.find_elements(By.CSS_SELECTOR, "table th")
        headers_text = [h.text.strip() for h in headers]
        
        print(f"📋 Nagłówki: {headers_text}")
        
        # Szukaj indeksu "EST. VOLUME"
        est_volume_index = None
        for i, header in enumerate(headers_text):
            if 'EST. VOLUME' in header.upper():
                est_volume_index = i
                break
        
        if est_volume_index is not None:
            # Znajdź pierwszy wiersz (JAN 26)
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            
            if rows:
                first_row = rows[0]
                cells = first_row.find_elements(By.TAG_NAME, "td")
                
                if est_volume_index < len(cells):
                    est_volume = cells[est_volume_index].text.strip()
                    
                    # Przygotuj dane
                    data = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "est_volume": est_volume
                    }
                    
                    print(f"📊 EST. VOLUME: {data['est_volume']}")
                    print("-" * 50)
                    
                    # Zapisz do pliku
                    save_to_csv(data)
                else:
                    print(f"❌ Indeks kolumny poza zakresem: {est_volume_index} >= {len(cells)}")
                    print("-" * 50)
            else:
                print("❌ Nie znaleziono wierszy w tabeli")
                print("-" * 50)
        else:
            print("❌ Nie znaleziono kolumny EST. VOLUME")
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Błąd podczas scrapowania: {e}")
        print(f"   Szczegóły: {str(e)}")
        print("-" * 50)
    finally:
        if driver:
            driver.quit()

def job():
    """Funkcja uruchamiana przez scheduler"""
    scrape_cme_data()

if __name__ == "__main__":
    print("🚀 SCRAPER CME GROUP URUCHOMIONY!")
    print(f"   Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Strona: https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html")
    print("   Dane: EST. VOLUME z tabeli")
    print("   Zbieranie: co 30 minut")
    print("   Plik z danymi: cme_data.csv")
    print("="*50)
    
    # Uruchom pierwszą scrapowanie od razu
    job()
    
    # Ustaw scheduler - uruchamiaj co 30 minut
    schedule.every(30).minutes.do(job)
    
    # Główna pętla
    while True:
        schedule.run_pending()
        time.sleep(60)  # Sprawdzaj co minutę

if __name__ == "__main__":
    print("🚀 SCRAPER CME GROUP URUCHOMIONY!")
    print(f"   Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Strona: https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html")
    print("   Dane będą zbierane co 30 minut")
    print("   Plik z danymi: cme_data.csv")
    print("="*50)
    
    # Uruchom pierwszą scrapowanie od razu
    job()
    
    # Ustaw scheduler - uruchamiaj co 30 minut
    schedule.every(30).minutes.do(job)
    
    # Główna pętla
    while True:
        schedule.run_pending()
        time.sleep(60)  # Sprawdzaj co minutę
