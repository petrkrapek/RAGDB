# Skript pro zpracování a vektorizaci JSON dat s uložením do Qdrant DB.
# Copyright (C) 2025 Petr Krapek
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import json
import uuid
import openai
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import CollectionStatus

# Načtení proměnných prostředí ze souboru .env
load_dotenv()

# --- 1. Konfigurace ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "moje_qdrant_kolekce"
JSON_FILE_PATH = "data/data.json"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

if not all([OPENAI_API_KEY, QDRANT_URL]):
    raise ValueError("Chybí API klíče nebo URL. Ujistěte se, že máte správně nastavený .env soubor.")

print("Konfigurace načtena.")

# --- 2. Příprava dat ---
try:
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        documents_data = json.load(f)

    texts_to_vectorize = [item['text'] for item in documents_data]

    # Původní ID uložíme do payloadu, Qdrant dostane nová UUID
    payloads_to_add = [
        {"author": item["author"], "original_text": item["text"], "original_id": item["id"]}
        for item in documents_data
    ]
    # Vygenerujeme nová, platná UUID pro Qdrant
    document_ids = [str(uuid.uuid4()) for _ in documents_data]

    print(f"Načteno {len(texts_to_vectorize)} dokumentů a jejich payloadů z {JSON_FILE_PATH}.")

except FileNotFoundError:
    print(f"Chyba: Soubor {JSON_FILE_PATH} nebyl nalezen.")
    exit()
except (json.JSONDecodeError, KeyError) as e:
    print(f"Chyba v JSON souboru: {e}.")
    exit()

# --- 3. Generování Embeddings pomocí OpenAI ---
try:
    print(f"Generuji embeddings pomocí modelu '{EMBEDDING_MODEL}'...")
    client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client_openai.embeddings.create(
        input=texts_to_vectorize,
        model=EMBEDDING_MODEL
    )
    vectors = [item.embedding for item in response.data]
    print(f"Vygenerováno {len(vectors)} vektorů.")
except Exception as e:
    print(f"Došlo k chybě při generování embeddings: {e}")
    exit()

# --- 4. Připojení a vložení dat do Qdrant DB ---
try:
    print(f"Připojuji se ke Qdrant DB na adrese '{QDRANT_URL}'...")
    client_qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print("Úspěšně připojeno ke Qdrant.")

    # Moderní způsob vytvoření/ověření kolekce
    try:
        collection_info = client_qdrant.get_collection(collection_name=COLLECTION_NAME)
        print(f"Kolekce '{COLLECTION_NAME}' již existuje a je připravena.")
    except Exception:
        print(f"⏳ Kolekce '{COLLECTION_NAME}' neexistuje. Vytvářím...")
        client_qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=EMBEDDING_DIMENSION, distance=models.Distance.COSINE),
        )
        print(f"Kolekce '{COLLECTION_NAME}' vytvořena.")

    print("Vkládám/aktualizuji body...")

    client_qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=models.Batch(
            ids=document_ids,
            vectors=vectors,
            payloads=payloads_to_add
        ),
        wait=True
    )

    print("Hotovo! Data byla úspěšně nahrána do Qdrant DB.")

    count_info = client_qdrant.get_collection(collection_name=COLLECTION_NAME)
    print(f"Počet záznamů v kolekci: {count_info.points_count}")

except Exception as e:
    print(f"Došlo k chybě při komunikaci s Qdrant DB: {e}")
