# Import dat do Qdrant DB

Tento projekt obsahuje Python skript pro načtení textových dat z `data.json`, vygenerování vektorových embeddings pomocí OpenAI a jejich nahrání do vektorové databáze Qdrant.

## Instalace

1.  **Klonujte repozitář (nebo vytvořte soubory ručně):**
    ```bash
    git clone [https://github.com/petrkrapek/RAGDB.git]
    cd moje-qdrant-repo
    ```

2.  **Vytvořte a aktivujte virtuální prostředí (doporučeno):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Na Windows použijte `venv\Scripts\activate`
    ```

3.  **Nainstalujte potřebné knihovny:**
    ```bash
    pip install -r requirements.txt
    ```

## Konfigurace

Skript načítá API klíče a URL ze souboru `.env`. Tento soubor není součástí repozitáře z bezpečnostních důvodů.

1.  **Vytvořte soubor `.env`** v kořenovém adresáři projektu.

2.  **Vložte do něj své klíče** v následujícím formátu:
    ```
    OPENAI_API_KEY="sk-vas-openai-klic"
    QDRANT_URL="https://vas-qdrant-cluster.cloud.qdrant.io:6333"
    QDRANT_API_KEY="vas-qdrant-klic"
    ```

## Spuštění

Po dokončení instalace a konfigurace spusťte importní skript:
```bash
python import_script.py
