import streamlit as st
from main_V3 import call_llm, call_agent, extraction_llm, model_selection



# Configuration de la page
st.set_page_config(
page_title="EPOIA - Assistant Médical",
    page_icon="🧑‍⚕️",
    layout="wide"
)


# Titre de l'application
st.title("🧠 EPOIA")


# Initialisation de la session pour le chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider aujourd'hui ?"}]
if "model" not in st.session_state:
    st.session_state.model = "GPT-4o"
    
    

with st.sidebar:
    st.header("🎚️ Configuration")
    
    model = st.selectbox(
        "Modèle",
        ["GPT-4o", "GPT-4.1", "Claude-3.5"],
        index=0
    ), 
    st.session_state.model = model
    
    # Bouton pour vider la conversation
    if st.button("🗑️ Nouvelle conversation"):
        st.session_state.messages = []
        st.rerun()
        

    st.markdown("---")
    st.subheader("ℹ️ Fonctionnement")
    st.markdown("""
    1. **Indiquez les symptomes** et les spécificités du patient
    2. **Répondez aux question supplémentaires** si nécessaire.
    3. **Proposition des médicaments à prescrire** par l'IA
    4. **Vérification avec la BDPM** pour confirmer les presciptions
    5. **Optionnel :** Choisissez un modèle de raisonnement pour les cas cliniques complexes
    6. **Consultez les sources** pour chaque médicament proposé
    7. **Posez d'autres questions** si nécessaire
    8. **Utilisez le bouton "Nouvelle conversation"** pour recommencer
    """)
    
    st.markdown("---")


llm = model_selection(st.session_state.model[0])


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
    with st.chat_message("user"):
        st.markdown(user_input)


    with st.spinner("Le LLM réfléchit..."):
        reponse = call_llm(st.session_state.messages, llm)
    
    
    st.session_state.messages.append({"role": "assistant", "content": reponse})
    with st.chat_message("assistant"):
        st.markdown(reponse)
        
        booleen, list_medics = extraction_llm(reponse, llm)
        
        if booleen:
            print("\n\n######## CALL AGENT ######## \n\n")
        
            confirmation, liens = call_agent(st.session_state.messages, list_medics)
            st.markdown(f"\n\nVérification : \n\n" + confirmation)

            # Génère les petits numéros de référence cliquables
            ref_links = ""
            for i, link in enumerate(liens):
                ref_links += f"-{list_medics[i].capitalize()} : [({i+1})]({link}) \n"

            # Affiche la réponse enrichie avec les références
            st.markdown("\n\nSources : \n" + ref_links, unsafe_allow_html=True)

    




# streamlit run front_V3.py