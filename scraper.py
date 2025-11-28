import asyncio
import schedule
import time
from datetime import datetime
import csv
import os
from playwright.async_api import async_playwright

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

async def scrape_cme_data():
    """Zbiera dane z CME Group - EST. VOLUME z tabeli"""
    try:
        print(f"🔄 Scrapowanie CME Group ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Nawiguj do strony
            await page.goto(
                "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html",
                wait_until="networkidle",
                timeout=30000
            )
            
            # Czekaj aż tabela się załaduje
            await page.wait_for_selector('table', timeout=10000)
            
            # Czekaj chwilę żeby dane się wyrenderowały
            await page.wait_for_timeout(2000)
            
            # Znajdź kolumnę EST. VOLUME i wyciągnij pierwszą wartość
            # Szukamy w nagłówkach kolumny "EST. VOLUME"
            est_volume_value = await page.eval_on_selector_all(
                'table th',
                'elements => elements.find(el => el.textContent.includes("EST. VOLUME"))'
            )
            
            if est_volume_value:
                # Alternatywnie: szukaj w całej tabeli
                rows = await page.query_selector_all('table tbody tr')
                
                if rows:
                    # Weź pierwszy wiersz (JAN 26)
                    first_row = rows[0]
                    cells = await first_row.query_selector_all('td')
                    
                    # Znaj indeks kolumny EST. VOLUME z nagłówków
                    headers = await page.query_selector_all('table th')
                    headers_text = []
                    for header in headers:
                        text = await header.text_content()
                        headers_text.append(text.strip())
                    
                    print(f"📋 Nagłówki: {headers_text}")
                    
                    # Szukaj indeksu "EST. VOLUME"
                    est_volume_index = None
                    for i, header in enumerate(headers_text):
                        if 'EST. VOLUME' in header.upper():
                            est_volume_index = i
                            break
                    
                    if est_volume_index is not None and est_volume_index < len(cells):
                        est_volume_cell = cells[est_volume_index]
                        est_volume = await est_volume_cell.text_content()
                        est_volume = est_volume.strip()
                        
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
                        print(f"❌ Nie znaleziono kolumny EST. VOLUME (indeks: {est_volume_index}, komórek: {len(cells)})")
                        print("-" * 50)
                else:
                    print("❌ Nie znaleziono wierszy w tabeli")
                    print("-" * 50)
            else:
                print("❌ Nie znaleziono kolumny EST. VOLUME")
                print("-" * 50)
            
            await browser.close()
            
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
