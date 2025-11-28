import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Pobierz stronę
print("📥 Pobieranie strony...")
response = requests.get(
    "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html",
    headers=HEADERS,
    timeout=10
)
response.raise_for_status()

# Parsuj HTML
soup = BeautifulSoup(response.content, 'html.parser')

print("\n" + "="*60)
print("🔍 SZUKANIE ELEMENTÓW 'TOTALS-INFO'")
print("="*60)

# Szukaj wszystkich divów zawierających "totals" w klasie
all_divs_with_totals = soup.find_all('div', class_=lambda x: x and 'totals' in x.lower())
print(f"\n✓ Znalezione divy z 'totals': {len(all_divs_with_totals)}")

for i, div in enumerate(all_divs_with_totals[:5]):  # Pokaż pierwsze 5
    print(f"\n--- DIV #{i+1} ---")
    print(f"Klasy: {div.get('class')}")
    print(f"Zawartość:")
    print(div.prettify()[:500])  # Pokaż pierwsze 500 znaków

print("\n" + "="*60)
print("🔍 SZUKANIE WSZYSTKICH SPANÓW Z ETYKIETAMI")
print("="*60)

# Szukaj spanów zawierających "interest"
all_spans = soup.find_all('span')
interest_spans = [s for s in all_spans if 'interest' in s.get_text().lower()]

print(f"\n✓ Znalezione spany z 'interest': {len(interest_spans)}")
for i, span in enumerate(interest_spans[:10]):
    print(f"\n--- SPAN #{i+1} ---")
    print(f"Tekst: {span.get_text()[:100]}")
    print(f"Klasy: {span.get('class')}")
    print(f"Parent: {span.parent.name}, classes: {span.parent.get('class')}")

print("\n" + "="*60)
print("🔍 SZUKANIE 'PRIOR DAY OPEN INTEREST'")
print("="*60)

# Szukaj całego tekstu
text_content = soup.get_text()
if 'Prior day open interest' in text_content:
    print("✓ Znaleziono tekst 'Prior day open interest' na stronie!")
    idx = text_content.find('Prior day open interest')
    print(f"Kontekst: ...{text_content[max(0, idx-50):idx+150]}...")
else:
    print("✗ Tekst 'Prior day open interest' NIE znaleziony na stronie!")

print("\n" + "="*60)
print("💾 Zapisywanie pełnego HTML do pliku debug.html")
print("="*60)

with open('debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("✓ Plik debug.html został zapisany - możesz go otworzyć w przeglądarce")
