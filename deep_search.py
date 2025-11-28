import requests
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("🔍 Szukanie danych w atrybutach HTML...\n")

resp = requests.get(
    "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html",
    headers=headers,
    timeout=15
)

html = resp.text

# Szukaj data-* atrybutów
print("1️⃣ Szukanie data- atrybutów...")
data_attrs = re.findall(r'data-([a-z-]+)=["\']([^"\']*)["\']', html, re.IGNORECASE)
if data_attrs:
    for attr, value in data_attrs[:10]:
        if '228' in value or 'volume' in value.lower():
            print(f"  ✓ {attr} = {value[:100]}")

# Szukaj JSON bloku
print("\n2️⃣ Szukanie JSON bloków...")
json_blocks = re.findall(r'<script[^>]*type=["\']application/json["\']>(.+?)</script>', html, re.DOTALL)
if json_blocks:
    print(f"  ✓ Znaleziono {len(json_blocks)} JSON bloków")
    for i, block in enumerate(json_blocks[:3]):
        try:
            data = json.loads(block)
            print(f"    Blok {i}: {json.dumps(data, indent=2)[:200]}")
        except:
            print(f"    Blok {i}: {block[:100]}")

# Szukaj React props
print("\n3️⃣ Szukanie React props...")
react_data = re.findall(r'<div[^>]*id=["\']root["\'][^>]*>.*?<script', html, re.DOTALL)
if react_data:
    print(f"  ✓ Znaleziono React DOM")

# Szukaj konkretnego stringa
print("\n4️⃣ Szukanie konkretnych stringów...")
if '228,285' in html:
    print("  ✓ Znaleziono '228,285' w HTML!")
    idx = html.find('228,285')
    print(f"    Kontekst: ...{html[max(0, idx-100):idx+150]}...")
elif '228' in html:
    print("  ✓ Znaleziono '228' w HTML")
    idx = html.find('228')
    print(f"    Kontekst: ...{html[max(0, idx-100):idx+150]}...")
else:
    print("  ✗ '228' nie znaleziono")

# Szukaj konkretnego HTML struktury
print("\n5️⃣ Szukanie <table>...")
tables = re.findall(r'<table[^>]*>.*?</table>', html, re.DOTALL)
print(f"  Znalezione tabele: {len(tables)}")
if tables:
    for i, table in enumerate(tables[:2]):
        print(f"    Tabela {i}: {len(table)} znaków")
        if '228' in table:
            print(f"      ✓ Zawiera '228'!")
            print(f"      Fragment: {table[:300]}")

# Najpowszechniejszy trick - szukaj w całym tekście
print("\n6️⃣ Szukanie wszystkich liczb w formacie XXX,XXX...")
all_numbers = re.findall(r'\d{1,3},\d{3}(?:,\d{3})*', html)
print(f"  Znalezione liczby: {sorted(set(all_numbers))}")

print("\n" + "="*60)
print("💾 Zapisywanie page_analysis.txt...")
with open('page_analysis.txt', 'w', encoding='utf-8') as f:
    f.write(f"Wielkość HTML: {len(html)} znaków\n")
    f.write(f"Liczby znalezione: {sorted(set(all_numbers))}\n")
    f.write(f"\nPierwsze 5000 znaków:\n{html[:5000]}")

print("✓ Zapisano")
