import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("🔍 Szukanie CME API endpoints...\n")

# Spróbuj znaleźć API przez različne metody
urls_to_try = [
    # GraphQL endpoints
    "https://www.cmegroup.com/graphql",
    "https://api.cmegroup.com/graphql",
    
    # REST API
    "https://www.cmegroup.com/api/settlement/CL/latest",
    "https://www.cmegroup.com/api/settlement/CL",
    "https://www.cmegroup.com/api/market-data/CL",
    
    # Data endpoints
    "https://www.cmegroup.com/data/api/settlement/CL",
    "https://api.cmegroup.com/settlement/CL",
    
    # Market data
    "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude/quotes.json",
    "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude/settlements.json",
]

for url in urls_to_try:
    try:
        print(f"Próbuję: {url}")
        resp = requests.get(url, headers=headers, timeout=5)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  ✓ Sukces!")
            print(f"  Content-Type: {resp.headers.get('content-type')}")
            print(f"  Rozmiar: {len(resp.text)} bajtów")
            if 'json' in resp.headers.get('content-type', '').lower():
                try:
                    data = resp.json()
                    print(f"  JSON: {json.dumps(data, indent=2)[:300]}")
                except:
                    print(f"  Tekst: {resp.text[:200]}")
            print()
    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout\n")
    except Exception as e:
        print(f"  ✗ Błąd: {e}\n")

# Pobierz główną stronę i szukaj API calls
print("\n" + "="*60)
print("🔍 Szukanie API calls w kodzie strony...\n")

try:
    resp = requests.get(
        "https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html",
        headers=headers,
        timeout=10
    )
    
    html = resp.text
    
    # Szukaj fetch() calls
    fetch_urls = re.findall(r"fetch\(['\"]([^'\"]+)['\"]", html)
    if fetch_urls:
        print(f"✓ Znalezione fetch URLs: {fetch_urls}")
    
    # Szukaj XMLHttpRequest calls
    xhr_urls = re.findall(r"(?:url|path|endpoint)['\"]?\s*:\s*['\"]([^'\"]*api[^'\"]*)['\"]", html, re.IGNORECASE)
    if xhr_urls:
        print(f"✓ Znalezione API URLs: {set(xhr_urls)}")
    
    # Szukaj JSON w window. variables
    json_vars = re.findall(r"window\.__[A-Z_]+=(\{[^}]+\})", html)
    if json_vars:
        print(f"✓ Znalezione window variables")
        for var in json_vars[:2]:
            print(f"  {var[:200]}")
    
    # Szukaj konkretnych danych
    if '"228' in html or "'228" in html:
        print("✓ Znaleziono '228' w HTML")
        idx = html.find("228")
        print(f"  Kontekst: ...{html[max(0, idx-50):idx+100]}...")
    
    # Zapisz HTML
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\n💾 Zapisano page_source.html - możesz go przeanalizować")
    
except Exception as e:
    print(f"✗ Błąd: {e}")

print("\n" + "="*60)
print("💡 Jeśli nic nie znaleziono, dane są ładowane dynamicznie.")
print("   Trzeba będzie użyć Playwright/Pyppeteer albo znaleźć inny sposób.")
