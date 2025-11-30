-- ========================================
-- SQL do stworzenia tabeli dla złota na Supabase
-- ========================================

-- 1. Stwórz tabelę 'investing_gold'
CREATE TABLE IF NOT EXISTS investing_gold (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    volume TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. Dodaj index na timestamp (dla szybszego wyszukiwania)
CREATE INDEX IF NOT EXISTS idx_investing_gold_timestamp ON investing_gold(timestamp DESC);

-- 3. Włącz Row Level Security (RLS) - opcjonalnie, dla bezpieczeństwa
ALTER TABLE investing_gold ENABLE ROW LEVEL SECURITY;

-- 4. Dodaj policy dla insertu (aby Railway mógł wpisywać dane)
-- WAŻNE: Zastąp 'YOUR_API_KEY' rzeczywistym kluczem
CREATE POLICY "Allow insert from API key" ON investing_gold
    FOR INSERT
    WITH CHECK (true);

-- 5. Opcjonalnie: Dodaj policy dla select (aby móc czytać dane)
CREATE POLICY "Allow select for all" ON investing_gold
    FOR SELECT
    USING (true);

-- ========================================
-- Jak to wdrożyć w Supabase:
-- ========================================
-- 1. Zaloguj się na https://supabase.com/
-- 2. Przejdź do swojego projektu
-- 3. Kliknij "SQL Editor" (lewe menu)
-- 4. Kliknij "+ New Query"
-- 5. Skopiuj cały kod z tego pliku
-- 6. Kliknij "Run" (Ctrl+Enter)
-- 7. Gotowe! Tabela 'investing_gold' jest stworzonym

-- ========================================
-- Testowanie:
-- ========================================
-- Aby zobaczyć dane:
SELECT * FROM investing_gold ORDER BY timestamp DESC LIMIT 10;

-- Aby usunąć test data:
-- DELETE FROM investing_gold WHERE timestamp > NOW() - INTERVAL '1 hour';
