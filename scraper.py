import asyncio
import schedule
import time
from datetime import datetime
import csv
import os
from crawl4ai import AsyncWebCrawler

# Plik do zapisywania danych
DATA_FILE = "scraped_data.csv"

def save_to_csv(data):
    """Zapisuje dane do pliku CSV"""
    file_exists = os.path.isfile(DATA_FILE)
    
    try:
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "url", "title", "content_length"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
            print(f"✅ Dane zapisane do {DATA_FILE}")
    except Exception as e:
        print(f"❌ Błąd przy zapisywaniu: {e}")

async def scrape_data():
    """Zbiera dane ze strony"""
    try:
        print(f"🔄 Scrapowanie ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})...")
        
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url="https://www.nbcnews.com/business",
                verbose=False
            )
            
            # Przygotuj dane
            data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "url": "https://www.nbcnews.com/business",
                "title": result.title if result.title else "N/A",
                "content_length": len(result.markdown.raw_markdown) if result.markdown else 0
            }
            
            print(f"📰 Tytuł: {data['title']}")
            print(f"📊 Rozmiar: {data['content_length']} znaków")
            print(f"✨ Zawartość (pierwsze 300 znaków):")
            print(result.markdown.raw_markdown[:300])
            print("-" * 50)
            
            # Zapisz do pliku
            save_to_csv(data)
            
    except Exception as e:
        print(f"❌ Błąd podczas scrapowania: {e}")
        print("-" * 50)

def job():
    """Funkcja uruchamiana przez scheduler"""
    asyncio.run(scrape_data())

if __name__ == "__main__":
    print("🚀 SCRAPER URUCHOMIONY!")
    print(f"   Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Dane będą zbierane co 30 minut")
    print("   Plik z danymi: scraped_data.csv")
    print("="*50)
    
    # Uruchom pierwszą scrapowanie od razu
    job()
    
    # Ustaw scheduler - uruchamiaj co 30 minut
    schedule.every(30).minutes.do(job)
    
    # Główna pętla
    while True:
        schedule.run_pending()
        time.sleep(60)  # Sprawdzaj co minutę
