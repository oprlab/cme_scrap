import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("📥 Pobieranie strony...")
response = requests.get(
    "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html",
    headers=HEADERS,
    timeout=10
)
response.raise_for_status()

# Sprawdź czy dane są w JavaScript
print("\n🔍 Szukanie danych w JavaScript...")
if '228' in response.text or 'EST. VOLUME' in response.text:
    print("✓ Znalezione dane w HTML")
    
    # Szukaj tabeli
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Szukaj wszystkich tabel
    tables = soup.find_all('table')
    print(f"\n✓ Znalezione tabele: {len(tables)}")
    
    for i, table in enumerate(tables):
        print(f"\n--- TABELA #{i+1} ---")
        # Szukaj EST. VOLUME w nagłówkach
        headers = table.find_all('th')
        header_texts = [h.get_text().strip() for h in headers]
        print(f"Nagłówki: {header_texts}")
        
        if 'EST. VOLUME' in header_texts or 'PRIOR DAY OI' in header_texts:
            print("✓ To jest nasza tabela!")
            
            # Wyświetl pierwszych kilka wierszy
            rows = table.find_all('tr')[1:6]  # Pomiń nagłówek, weź 5 wierszy
            for j, row in enumerate(rows):
                cells = row.find_all('td')
                cell_texts = [c.get_text().strip() for c in cells]
                print(f"  Wiersz {j+1}: {cell_texts}")
else:
    print("✗ Dane nie znalezione w HTML")
    print("⚠️  Dane prawdopodobnie są ładowane dynamicznie przez JavaScript")
    print("    Potrzebujemy użyć Playwright lub Selenium")

# Zapisz HTML do przeanalizowania
print("\n💾 Zapisywanie HTML do pliku...")
with open('debug_full.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("✓ Plik debug_full.html zapisany")

# Szukaj w kodzie źródłowym dla liczb
print("\n🔍 Szukanie liczb w formacie XXX,XXX...")
numbers = re.findall(r'\d{1,3},\d{3}', response.text)
if numbers:
    print(f"✓ Znalezione liczby: {set(numbers)}")
