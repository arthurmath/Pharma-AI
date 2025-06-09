import streamlit as st
from main_V1 import call_agent




# Titre de l'application
st.title("🧠 EPOIA")


# Initialisation de la session pour le chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider aujourd'hui ?"}]


# Affichage de la conversation
st.subheader("💬 Conversation")
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


# Saisie utilisateur
user_input = st.chat_input("Posez votre question ici...")


# Traitement du message
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    print(st.session_state.messages[-1])
    
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Le LLM réfléchit..."):
            response, liens = call_agent(st.session_state.messages[-1]['content'])

            # Génère les petits numéros de référence cliquables
            ref_links = ""
            for i, link in enumerate(liens, 1):
                ref_links += f"\n[<sup>({i})</sup>]({link}) "

            # Affiche la réponse enrichie avec les références
            st.markdown(response + "\n\nSources : " + ref_links, unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": response})




# streamlit run front_V1.py