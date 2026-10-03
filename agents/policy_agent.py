from google import genai
from dotenv import load_dotenv

from knowledge_base.retriever import retrieve_policy

import os


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def policy_agent(query: str):

    print("\n📚 RAG Policy Agent")

    results = retrieve_policy(
        query,
        top_k=3
    )

    if not results:

        return {
            "answer": "No relevant policy information found.",
            "sources": []
        }

    context = "\n\n".join(
        [
            f"Source: {result['source']}\n"
            f"{result['content']}"
            for result in results
        ]
    )

    prompt = f"""
You are the CivicPulse Municipal Policy Agent.

Answer the user's question using ONLY the
provided policy context.

Do not invent municipal rules.

If the answer is not available in the context,
clearly say that the policy information was not found.

Policy Context:
{context}

User Question:
{query}

Provide a concise and factual answer.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    sources = list(
        dict.fromkeys(
            result["source"]
            for result in results
        )
    )

    print("\nAnswer:")
    print(response.text)

    print("\nSources:")
    for source in sources:
        print(f"- {source}")

    return {
        "answer": response.text,
        "sources": sources
    }


if __name__ == "__main__":

    question = input(
        "\nAsk CivicPulse a policy question: "
    )

    policy_agent(question)