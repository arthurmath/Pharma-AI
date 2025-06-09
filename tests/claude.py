import streamlit as st
import openai
from datetime import datetime
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()




# Configuration de la page
st.set_page_config(
    page_title="Chat avec LLM",
    page_icon="🤖",
    layout="wide"
)

# Titre de l'application
st.title("🤖 Chat avec LLM")

# Configuration de l'API OpenAI
def setup_openai():
    """Configuration de l'API OpenAI"""
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")
    
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input(
            "Clé API OpenAI", 
            value=st.session_state.openai_api_key,
            type="password",
            help="Entrez votre clé API OpenAI"
        )
        
        if api_key:
            st.session_state.openai_api_key = api_key
            openai.api_key = api_key
        
        model = st.selectbox(
            "Modèle",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
            index=0
        )
        st.session_state.model = model
        
        # Bouton pour vider la conversation
        if st.button("🗑️ Vider la conversation"):
            st.session_state.messages = []
            st.rerun()

# Configuration
# setup_openai()

# Initialisation de l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fonction pour obtenir une réponse du LLM
def get_llm_response(messages, model="gpt-3.5-turbo"):
    """Obtient une réponse du LLM"""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur: {str(e)}"
    


llm = init_chat_model("openai:gpt-4.1-mini", temperature=0)

def call_llm(messages: list):
    response = llm.invoke(messages)
    return response.content



# Interface principal
col1, col2 = st.columns([3, 1])

with col1:
    # Affichage de l'historique des messages
    st.subheader("💬 Conversation")
    
    # Conteneur pour les messages avec défilement
    messages_container = st.container()
    
    with messages_container:
        if st.session_state.messages:
            for i, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    # Message utilisateur
                    with st.chat_message("user"):
                        st.write(message["content"])
                        st.caption(f"Envoyé à {message.get('timestamp', 'heure inconnue')}")
                else:
                    # Message assistant
                    with st.chat_message("assistant"):
                        st.write(message["content"])
                        st.caption(f"Reçu à {message.get('timestamp', 'heure inconnue')}")
        else:
            st.info("Commencez une conversation en tapant un message ci-dessous!")

with col2:
    st.subheader("📊 Statistiques")
    total_messages = len(st.session_state.messages)
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    
    st.metric("Total messages", total_messages)
    st.metric("Messages utilisateur", user_messages)
    st.metric("Réponses assistant", assistant_messages)

# Zone de saisie pour nouveau message
st.markdown("---")
st.subheader("✍️ Nouveau message")

# Formulaire pour envoyer un message
with st.form("message_form", clear_on_submit=True):
    user_input = st.text_area(
        "Votre message:",
        placeholder="Tapez votre message ici...",
        height=100,
        key="user_message_input"
    )
    
    col_send, col_clear = st.columns([1, 4])
    
    with col_send:
        submit_button = st.form_submit_button("📤 Envoyer", use_container_width=True)
    
    if submit_button and user_input.strip():
        if not st.session_state.get("openai_api_key"):
            st.error("Veuillez configurer votre clé API OpenAI dans la barre latérale.")
        else:
            # Ajouter le message utilisateur
            timestamp = datetime.now().strftime("%H:%M:%S")
            user_message = {
                "role": "user",
                "content": user_input.strip(),
                "timestamp": timestamp
            }
            st.session_state.messages.append(user_message)
            
            # Préparer les messages pour l'API (sans timestamps)
            api_messages = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in st.session_state.messages
            ]
            
            # Obtenir la réponse du LLM
            with st.spinner("🤔 Le LLM réfléchit..."):
                response = call_llm(api_messages)
            
            # Ajouter la réponse de l'assistant
            timestamp = datetime.now().strftime("%H:%M:%S")
            assistant_message = {
                "role": "assistant",
                "content": response,
                "timestamp": timestamp
            }
            st.session_state.messages.append(assistant_message)
            
            # Recharger la page pour afficher les nouveaux messages
            st.rerun()

# # Instructions dans la barre latérale
# with st.sidebar:
#     st.markdown("---")
#     st.subheader("ℹ️ Instructions")
#     st.markdown("""
#     1. **Configurez votre clé API OpenAI** en haut de cette barre latérale
#     2. **Choisissez un modèle** (gpt-3.5-turbo recommandé pour commencer)
#     3. **Tapez votre message** dans la zone de texte en bas
#     4. **Cliquez sur Envoyer** pour obtenir une réponse
    
#     💡 **Astuce**: La conversation est mémorisée pendant votre session!
#     """)
    
#     st.markdown("---")
#     st.subheader("🔧 Fonctionnalités")
#     st.markdown("""
#     - ✅ Mémoire de conversation
#     - ✅ Horodatage des messages
#     - ✅ Statistiques en temps réel
#     - ✅ Interface intuitive
#     - ✅ Choix du modèle LLM
#     """)

# # Footer
# st.markdown("---")
# st.markdown("*Développé avec Streamlit et OpenAI API*")