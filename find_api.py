import requests
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("🔍 Szukanie API endpoint CME...\n")

# Spróbuj różne potencjalne API endpoints
urls = [
    "https://www.cmegroup.com/api/v1/markets/energy/crude-oil/light-sweet-crude.json",
    "https://www.cmegroup.com/api/market-data/crude-oil/light-sweet-crude",
    "https://www.cmegroup.com/trading/market-data/crude-oil/light-sweet-crude",
    "https://www.cmegroup.com/markets/settlements/crude-oil/light-sweet-crude",
]

for url in urls:
    try:
        print(f"Próbuję: {url}")
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            print(f"✓ Status 200!")
            if 'json' in response.headers.get('content-type', '').lower():
                print(f"✓ JSON Response!")
                data = response.json()
                print(json.dumps(data, indent=2)[:500])
                print("\n" + "="*60)
            else:
                print(f"Zawartość: {response.text[:200]}")
        else:
            print(f"✗ Status {response.status_code}\n")
    except Exception as e:
        print(f"✗ Błąd: {e}\n")

# Pobierz pełną stronę i szukaj JSON w kodzie
print("\n🔍 Szukanie JSON w kodzie strony...\n")
try:
    response = requests.get(
        "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html",
        headers=HEADERS,
        timeout=10
    )
    
    # Szukaj "settl" lub "volume" w response
    if 'settl' in response.text.lower():
        print("✓ Znaleziono 'settl' w stronie")
        idx = response.text.lower().find('settl')
        print(f"Kontekst: ...{response.text[max(0, idx-100):idx+200]}...\n")
    
    # Szukaj window.__INITIAL_STATE__ lub podobnych zmiennych
    if 'window.__' in response.text or '__INITIAL_STATE__' in response.text:
        print("✓ Znaleziono window.__ variables")
        idx = response.text.find('window.__')
        if idx > -1:
            print(f"Znaleziono na pozycji: {idx}")
    
    # Szukaj konkretnych liczb z poprzedniego screenshota
    if '228' in response.text:
        print("✓ Znaleziono '228' (EST. VOLUME) w stronie!")
    if '1,890' in response.text:
        print("✓ Znaleziono '1,890' (PRIOR DAY OI) w stronie!")
        
except Exception as e:
    print(f"✗ Błąd: {e}")

print("\n💾 Zapisywanie pełnej strony do scraper_page.html")
with open('scraper_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("✓ Możesz go otworzyć i przeszukać CTRL+F")
