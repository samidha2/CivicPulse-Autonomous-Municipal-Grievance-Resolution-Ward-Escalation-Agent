from agents.orchestrator import build_civicpulse_graph


def main():

    print("\n" + "=" * 60)
    print("CIVICPULSE AGENTIC WORKFLOW TEST")
    print("=" * 60)

    graph = build_civicpulse_graph()

    complaint_id = int(
        input("\nEnter Complaint ID to process: ")
    )

    initial_state = {
        "complaint_id": complaint_id
    }

    print("\n🚀 Starting CivicPulse Agent...\n")

    result = graph.invoke(
        initial_state
    )

    print("\n" + "=" * 60)
    print("FINAL AGENT STATE")
    print("=" * 60)

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )

    print("\n" + "=" * 60)
    print("✅ Agent workflow completed")
    print("=" * 60)


if __name__ == "__main__":
    main()