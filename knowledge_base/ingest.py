import os
import chromadb
from sentence_transformers import SentenceTransformer


KNOWLEDGE_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(KNOWLEDGE_BASE_DIR, "chroma_db")

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_or_create_collection(
    name="civicpulse_policies"
)


def chunk_text(text, chunk_size=800, overlap=100):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def ingest_documents():

    documents = []
    metadatas = []
    ids = []

    for filename in os.listdir(KNOWLEDGE_BASE_DIR):

        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(
            KNOWLEDGE_BASE_DIR,
            filename
        )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

        chunks = chunk_text(text)

        for index, chunk in enumerate(chunks):

            documents.append(chunk)

            metadatas.append({
                "source": filename,
                "chunk": index
            })

            ids.append(
                f"{filename}_{index}"
            )

    if documents:

        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    unique_sources = set(
        metadata["source"]
        for metadata in metadatas
    )

    print("\n✅ RAG ingestion completed")
    print(
        f"Documents processed: {len(unique_sources)}"
    )
    print(
        f"Chunks stored: {len(documents)}"
    )
    print(
        f"ChromaDB location: {CHROMA_DIR}"
    )


if __name__ == "__main__":
    ingest_documents()