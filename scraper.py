import schedule
import time
from datetime import datetime
import csv
import os
import asyncio
from pyppeteer import launch

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
    browser = None
    try:
        print(f"🔄 Scrapowanie ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})...")
        
        # Uruchom przeglądarke
        browser = await launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.newPage()
        
        # Nawiguj do strony z timeoutem
        await page.goto(
            "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html",
            waitUntil='networkidle2',
            timeout=30000
        )
        
        # Czekaj na tabelę
        await page.waitForSelector('table', timeout=15000)
        await page.waitFor(2000)  # Czekaj aby dane się wyrenderowały
        
        # Wyciągnij dane za pomocą JavaScript
        data_js = await page.evaluate("""
            () => {
                let table = document.querySelector('table');
                if (!table) return null;
                
                // Znajdź nagłówki
                let headers = [];
                let headerElements = table.querySelectorAll('th');
                headerElements.forEach(h => {
                    headers.push(h.textContent.trim());
                });
                
                // Znajdź indeks EST. VOLUME
                let estVolumeIndex = headers.findIndex(h => h.toUpperCase().includes('EST. VOLUME'));
                
                if (estVolumeIndex === -1) return null;
                
                // Znajdź pierwszy wiersz w tbody
                let rows = table.querySelectorAll('tbody tr');
                if (rows.length === 0) {
                    rows = table.querySelectorAll('tr');
                }
                
                if (rows.length > 0) {
                    let cells = rows[0].querySelectorAll('td');
                    if (estVolumeIndex < cells.length) {
                        return {
                            headers: headers,
                            estVolume: cells[estVolumeIndex].textContent.trim()
                        };
                    }
                }
                return null;
            }
        """)
        
        if data_js and data_js['estVolume']:
            print(f"📋 Nagłówki: {data_js['headers']}")
            print(f"📊 EST. VOLUME: {data_js['estVolume']}")
            print("-" * 50)
            
            data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "est_volume": data_js['estVolume']
            }
            save_to_csv(data)
        else:
            print("❌ Nie znaleziono danych w tabeli")
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        print("-" * 50)
    finally:
        if browser:
            await browser.close()

def job():
    """Funkcja uruchamiana przez scheduler"""
    asyncio.run(scrape_cme_data())

if __name__ == "__main__":
    print("🚀 SCRAPER CME GROUP URUCHOMIONY!")
    print(f"   Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Zbieranie: co 30 minut")
    print("="*50)
    
    job()
    schedule.every(30).minutes.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
