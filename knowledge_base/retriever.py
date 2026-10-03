import os
import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chroma_db"
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_collection(
    name="civicpulse_policies"
)


def retrieve_policy(query: str, top_k: int = 3):

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    retrieved_documents = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved_documents.append({
            "content": document,
            "source": metadata.get("source"),
            "chunk": metadata.get("chunk"),
            "distance": round(float(distance), 4)
        })

    return retrieved_documents


if __name__ == "__main__":

    query = input(
        "\nEnter your policy question: "
    )

    results = retrieve_policy(query)

    print("\n🔎 Retrieved Policy Information\n")

    for index, result in enumerate(results, start=1):

        print(f"--- Result {index} ---")
        print(f"Source: {result['source']}")
        print(f"Chunk: {result['chunk']}")
        print(f"Distance: {result['distance']}")
        print(f"\n{result['content']}\n")