import asyncio
import schedule
import time
from datetime import datetime
import csv
import os
import json
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup

# Plik do zapisywania danych
DATA_FILE = "cme_data.csv"

def save_to_csv(data):
    """Zapisuje dane do pliku CSV"""
    file_exists = os.path.isfile(DATA_FILE)
    
    try:
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "prior_day_open_interest"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
            print(f"✅ Dane zapisane do {DATA_FILE}")
    except Exception as e:
        print(f"❌ Błąd przy zapisywaniu: {e}")

async def scrape_cme_data():
    """Zbiera dane z CME Group - Prior day open interest totals"""
    try:
        print(f"🔄 Scrapowanie CME Group ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})...")
        
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url="https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html",
                verbose=False
            )
            
            # Parsuj HTML i szukaj danych
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Szukaj div z klasą "totals-info col-sm-6"
            totals_info_divs = soup.find_all('div', class_='totals-info col-sm-6')
            
            prior_day_open_interest = None
            
            # Przejdź przez wszystkie divs i szukaj "Prior day open interest totals"
            for div in totals_info_divs:
                label = div.find('span', class_='totals-info-label')
                if label and 'Prior day open interest totals' in label.get_text():
                    value_span = div.find('span', class_='totals-info-value')
                    if value_span:
                        prior_day_open_interest = value_span.get_text().strip()
                        break
            
            # Przygotuj dane
            data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "prior_day_open_interest": prior_day_open_interest if prior_day_open_interest else "N/A"
            }
            
            print(f"📊 Prior Day Open Interest: {data['prior_day_open_interest']}")
            print("-" * 50)
            
            # Zapisz do pliku
            save_to_csv(data)
            
    except Exception as e:
        print(f"❌ Błąd podczas scrapowania: {e}")
        print(f"   Szczegóły: {str(e)}")
        print("-" * 50)

def job():
    """Funkcja uruchamiana przez scheduler"""
    asyncio.run(scrape_cme_data())

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
