"""CivicPulse - AI Policy & Bylaw Assistant Page
Interactive conversational interface backed by the CivicPulse RAG Policy Agent.
"""

from typing import Any, Dict, List
import streamlit as st

from app.api_client import api_client
from app.components.cards import hero_header, policy_notice_card
from app.config import SAMPLE_POLICY_PROMPTS


def render_assistant_page():
    """Renders the policy RAG assistant chat interface."""
    hero_header(
        title="Municipal Policy & RAG Assistant",
        subtitle="Ask questions regarding municipal bylaws, grievance SLAs, ward escalation trees, and citizen charters.",
        tag="INTELLIGENT KNOWLEDGE AGENT"
    )

    # Mandatory Synthetic Policy Notice
    policy_notice_card()

    # Initialize chat history in session state
    if "assistant_messages" not in st.session_state:
        st.session_state["assistant_messages"] = [
            {
                "role": "assistant",
                "content": "Hello! I am your **CivicPulse Municipal Policy Agent**. You can ask me about municipal resolution SLAs, escalation procedures, grievance categories, or department responsibilities. How can I assist you today?",
                "sources": []
            }
        ]

    # Quick Prompt Chips
    st.markdown("##### 💡 Suggested Questions")
    chip_cols = st.columns(len(SAMPLE_POLICY_PROMPTS))
    selected_prompt = None

    for i, prompt in enumerate(SAMPLE_POLICY_PROMPTS):
        with chip_cols[i]:
            # Shortened label for button
            short_label = prompt[:35] + "..."
            if st.button(short_label, key=f"chip_{i}", use_container_width=True, help=prompt):
                selected_prompt = prompt

    st.markdown("---")

    # Render Chat History
    for msg in st.session_state["assistant_messages"]:
        role = msg.get("role", "assistant")
        with st.chat_message(role):
            st.markdown(msg.get("content", ""))
            sources = msg.get("sources", [])
            if sources:
                with st.expander(f"📚 Retrieved Citations & Sources ({len(sources)})", expanded=False):
                    for idx, s in enumerate(sources, 1):
                        doc_text = s if isinstance(s, str) else s.get("text") or s.get("content") or str(s)
                        metadata = s.get("metadata") if isinstance(s, dict) else {}
                        meta_str = f" | {metadata}" if metadata else ""
                        st.markdown(f"**Source {idx}:** {doc_text}{meta_str}")

    # Chat Input
    user_query = st.chat_input("Ask a question about municipal policies or resolution SLAs...")
    if selected_prompt:
        user_query = selected_prompt

    if user_query:
        # Append and display user query
        st.session_state["assistant_messages"].append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Call RAG Backend
        with st.chat_message("assistant"):
            with st.spinner("🤖 Consulting municipal policy embeddings & citizen charters..."):
                response_data, error = api_client.query_policy(user_query)

            if error:
                err_msg = f"⚠️ I encountered an error querying the policy agent: {error}"
                st.error(err_msg)
                st.session_state["assistant_messages"].append({
                    "role": "assistant",
                    "content": err_msg,
                    "sources": []
                })
            elif response_data:
                answer = response_data.get("answer", "No policy answer generated.")
                sources = response_data.get("sources", [])
                st.markdown(answer)

                if sources:
                    with st.expander(f"📚 Retrieved Citations & Sources ({len(sources)})", expanded=False):
                        for idx, s in enumerate(sources, 1):
                            doc_text = s if isinstance(s, str) else s.get("text") or s.get("content") or str(s)
                            st.markdown(f"**Source {idx}:** {doc_text}")

                st.session_state["assistant_messages"].append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

    # Clear Chat Action
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Conversation History", type="secondary"):
        st.session_state["assistant_messages"] = [
            {
                "role": "assistant",
                "content": "Conversation history cleared. Feel free to ask any municipal policy question!",
                "sources": []
            }
        ]
        st.rerun()
