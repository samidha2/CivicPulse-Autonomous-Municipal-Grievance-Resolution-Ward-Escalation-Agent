from langgraph.graph import StateGraph, END

from agents.state import CivicPulseState

from agents.nodes import (
    load_complaint,
    understand_complaint,
    confidence_check,
    decide_after_confidence,
    duplicate_detection_node,
    duplicate_handling_node,
    policy_agent_node,
    route_complaint_node,
    create_work_order_node,
    notify_node,
    human_review_node
)


def build_civicpulse_graph():

    workflow = StateGraph(CivicPulseState)

    # Nodes
    workflow.add_node(
        "load_complaint",
        load_complaint
    )

    workflow.add_node(
        "understand_complaint",
        understand_complaint
    )

    workflow.add_node(
        "confidence_check",
        confidence_check
    )

    workflow.add_node(
        "duplicate_detection",
        duplicate_detection_node
    )

    workflow.add_node(
        "duplicate_handling",
        duplicate_handling_node
    )

    workflow.add_node(
        "policy_agent",
        policy_agent_node
    )

    workflow.add_node(
        "route_complaint",
        route_complaint_node
    )

    workflow.add_node(
        "create_work_order",
        create_work_order_node
    )

    workflow.add_node(
        "notify",
        notify_node
    )

    workflow.add_node(
        "human_review",
        human_review_node
    )

    # Starting point
    workflow.set_entry_point(
        "load_complaint"
    )

    # Main flow
    workflow.add_edge(
        "load_complaint",
        "understand_complaint"
    )

    workflow.add_edge(
        "understand_complaint",
        "confidence_check"
    )

    # Confidence decision
    workflow.add_conditional_edges(
        "confidence_check",
        decide_after_confidence,
        {
            "duplicate_detection":
                "duplicate_detection",

            "human_review":
                "human_review"
        }
    )

    # Duplicate decision
    workflow.add_conditional_edges(
    "duplicate_detection",
    lambda state: state.get("next_action", "route_complaint"),
    {
        "DUPLICATE": "duplicate_handling",
        "ROUTE": "policy_agent",
        "route_complaint": "policy_agent"
    }
)

    # Duplicate → END
    workflow.add_edge(
        "duplicate_handling",
        END
    )

    # New complaint → Policy → Routing
    workflow.add_edge(
        "policy_agent",
        "route_complaint"
    )

    workflow.add_edge(
        "route_complaint",
        "create_work_order"
    )

    workflow.add_edge(
        "create_work_order",
        "notify"
    )

    workflow.add_edge(
        "notify",
        END
    )

    # Human review → END
    workflow.add_edge(
        "human_review",
        END
    )

    return workflow.compile()