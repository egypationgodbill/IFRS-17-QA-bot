import os
from embedchain import App
import streamlit as st

st.set_page_config(page_title="IFRS 17 QA Bot", page_icon="📊")

with st.sidebar:
    st.header("IFRS 17 QA Bot")
    st.markdown(
        "A specialized assistant for actuaries and finance professionals "
        "to explore IFRS 17 Insurance Contracts standard."
    )
    st.divider()
    huggingface_access_token = st.text_input(
        "Hugging Face Token", key="chatbot_api_key", type="password"
    )
    "[Get Hugging Face Access Token](https://huggingface.co/settings/tokens)"
    st.divider()
    st.subheader("Add Knowledge Source")
    st.markdown(
        "Use `/add <url>` in the chat to add a PDF or webpage to the knowledge base.\n\n"
        "**Suggested sources:**\n"
        "- IASB IFRS 17 standard documents\n"
        "- Actuarial society guidance notes\n"
        "- Regulatory implementation papers"
    )

st.title("📊 IFRS 17 QA Bot")
st.caption("An AI assistant for actuaries to explore IFRS 17 Insurance Contracts")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm your IFRS 17 assistant, here to help actuaries and finance "
                "professionals navigate the IFRS 17 Insurance Contracts standard.\n\n"
                "I can help you with:\n"
                "- **Core IFRS 17 concepts** – GMM, PAA, VFA measurement models\n"
                "- **CSM (Contractual Service Margin)** calculations and amortisation\n"
                "- **Risk adjustment** for non-financial risk\n"
                "- **Discount rates** and financial assumptions\n"
                "- **Transition approaches** – full retrospective, modified, fair value\n"
                "- **Presentation and disclosure** requirements\n\n"
                "You can also teach me new material using `/add <url>` – for example, "
                "`/add https://www.ifrs.org/issued-standards/list-of-standards/ifrs-17-insurance-contracts/`\n\n"
                "What would you like to know about IFRS 17?"
            ),
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about IFRS 17..."):
    if not st.session_state.chatbot_api_key:
        st.error("Please enter your Hugging Face Access Token in the sidebar.")
        st.stop()

    os.environ["HUGGINGFACE_ACCESS_TOKEN"] = st.session_state.chatbot_api_key
    app = App.from_config(config_path="config.yaml")

    if prompt.startswith("/add"):
        with st.chat_message("user"):
            st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
        source = prompt.replace("/add", "").strip()
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Adding to knowledge base...")
            app.add(source)
            msg = f"Added **{source}** to the knowledge base! You can now ask questions about it."
            message_placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.stop()

    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("Thinking...")
        full_response = ""

        for response in app.chat(prompt):
            msg_placeholder.empty()
            full_response += response

        msg_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
