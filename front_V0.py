import streamlit as st
from prompts import syst_promptV0
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model("openai:gpt-4.1-mini", temperature=0) 

def call_llm(messages: list):
    response = llm.invoke(messages)
    return response.content





# Titre de l'application
st.title("🧠 EPOIA")


# Initialisation de la session pour le chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": syst_promptV0},
        {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider aujourd'hui ?"}
    ]


# Affichage de la conversation
st.subheader("💬 Conversation")
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])




# Saisie utilisateur
user_input = st.chat_input("Posez votre question ici...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Le LLM réfléchit..."):
            response = call_llm(st.session_state.messages)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})




# streamlit run front_V0.py
