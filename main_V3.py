# Version deployee sur Streamlit

from typing import Annotated, Literal, List, Optional # = Union[T, None]
from typing_extensions import TypedDict
from pprint import pprint
from prompts import *
from pydantic import BaseModel, Field

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

from dotenv import load_dotenv
load_dotenv()


def model_selection(name: str):
    match name:
        case "GPT-4o": 
            model = "openai:gpt-4o"
        case "GPT-4.1":
            model = "openai:gpt-4.1-mini"
        case "Claude-3.5":
            model = "anthropic:claude-3-5-sonnet-latest"
        case _:
            model = "openai:gpt-4o"
    llm = init_chat_model(model, temperature=0)
    return llm

llm = model_selection("openai:gpt-4o")


class Source(BaseModel):
    medicament: str
    lien: str
    texte: str
    

class State(TypedDict):
    messages: Annotated[str, add_messages]
    prescriptions: List[str] # Liste des médicaments prescrits
    confirmation_msg: str
    sources: List[Source]
    

class Extract(BaseModel):
    bool_medics: bool = Field(
        ...,
        description="'True' si des médicaments ont été recommandés dans les prescriptions, 'False' s'il n'y a pas de médicaments prescrits."
    )
    list_medics: List[str] = Field(
        ...,
        description="Liste des médicaments recommandés pour les symptomes entrés, les chaînes de caractères ne doivent contenir que les noms des médicaments prescrits."
    )
    
    
    


def call_llm(messages: List[dict], llm) -> str:
    prompt = [{"role": "system", "content": syst_promptV2_pres}]
    prompt.extend(messages)
    response = llm.invoke(prompt)
    
    print("---------CALL LLM PROMPT :---------\n\n", prompt, "\n\n")
    print("---------CALL LLM RESPONSE :---------\n\n", response.content, "\n\n")
    return response.content




def extraction_llm(last_msg: str, llm) -> tuple[bool, List[str]]:
    
    llm_st = llm.with_structured_output(Extract)
        
    prompt = [
        {"role": "system", "content": syst_promptV2_extraction},
        {"role": "user", "content": last_msg}
    ]

    result = llm_st.invoke(prompt)
    print("---------EXTRACTION LLM PROMPT :---------\n\n", prompt, "\n\n")
    print("---------EXTRACTION LLM RESULT :---------\n\n", result.bool_medics, result.list_medics, "\n\n")
    return result.bool_medics, result.list_medics







def verification_api(state: State) -> State:
    print("VERIFICATION API : \n")
    # pprint(state)
    # print("\n\n")
    
    descriptions = []
    for medicament in state["prescriptions"]:
        # Création d'un objet Sources pour chaque médicament
        lien, texte = requete(medicament)
        source = Source(medicament=medicament, lien=lien, texte=texte)
        descriptions.append(source)
    
    # print("\n\nVérification des prescriptions :", descriptions, "\n\n")    
    return {"sources": descriptions}




def get_driver():
    options = Options()
    options.add_argument("--headless")  # Mode sans interface graphique
    options.add_argument("--no-sandbox")  # Recommandé sur les serveurs
    options.add_argument("--disable-dev-shm-usage")  # Évite certains crashes
    options.add_argument("--disable-gpu")  # Optionnel
    return webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=options)




def requete(nom_medicament: str) -> tuple[str, str]:
    """ Fonction pour récupérer les informations sur le médicament """
    
    selecteur_lien = 'a[href*="extrait.php?specid="]'
    selecteur_text = 'p.AmmCorpsTexte'
    driver = get_driver()
    driver.get("https://base-donnees-publique.medicaments.gouv.fr")
    
    if len(liste := nom_medicament.split(' ')) > 0 :
        nom_medicament = liste[0]  # On ne prend que le premier mot du nom du médicament s'il contient plusieur mots

    # Recherche du médicament
    champ_recherche = driver.find_element(By.NAME, "txtCaracteres")
    champ_recherche.send_keys(nom_medicament)
    champ_recherche.send_keys("\n")

    try:
        # Attente le chargement des liens et extraction
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selecteur_lien)))
        lien = driver.find_elements(By.CSS_SELECTOR, selecteur_lien)[0]
        
        # Aller sur la page du 1er médicament trouvé
        url = lien.get_attribute("href")
        driver.get(url)

        # Attente le chargement des textes et extraction
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selecteur_text)))
        paragraphes = driver.find_elements(By.CSS_SELECTOR, selecteur_text)

        for i, p in enumerate(paragraphes, start=1):
            print(f"Paragraphe {i} :")
            print(p.text)
        print("-" * 40)
        print("\n")
            
        return url, "\n".join(p.text for p in paragraphes)

    except Exception as e:
        print("❌ Erreur médicament :", nom_medicament)
        return "None", "None"

    finally:
        driver.quit()


    
    
def confirmation_llm(state: State) -> State:
    print("\n\n-------------STATE CONFIRMATION : -------------")
    pprint(state)
    print("\n\n")
    
    prompt = syst_promptV2_conf + "\n\nSymptomes : "
    
    for message in state["messages"]:
        if type(message) is HumanMessage:
            prompt += message.content + "\n\n"
         
    prompt += "Prescriptions : " + str(state["prescriptions"]) + "\n\nInformations : \n"
        
    for source in state["sources"]:
        prompt += source.medicament + " : " + source.texte + "\n"
        
    prompt = ''.join(prompt)
    
    response = llm.invoke([{"role": "system", "content": prompt}])
    
    
    print("-----------CONFIRMATION LLM PROMPT :--------- \n", prompt, "\n\n")
    print("-----------CONFIRMATION LLM RESPONSE :---------\n", response.content, "\n\n")
    
    return {"confirmation_msg": [{"role": "assistant", "content": ''.join(response.content)}]}





graph_builder = StateGraph(State)

graph_builder.add_node("extraction", extraction_llm)
graph_builder.add_node("verification", verification_api)
graph_builder.add_node("confirmation", confirmation_llm)

graph_builder.add_edge(START, "verification")
graph_builder.add_edge("verification", "confirmation")
graph_builder.add_edge("confirmation", END)

graph = graph_builder.compile()


# # Save the graph as a PNG file
# graph_png = graph.get_graph().draw_mermaid_png()
# with open("images/grapheV2.png", "wb") as f:
#     f.write(graph_png)





def call_agent(messages: List[dict], list_medics: List[str]) -> tuple[str, List[str]]:
    initial_state = {"messages": messages, "prescriptions": list_medics, "confirmation_msg": [], "sources": []}
    print("\n-------INITIAL STATE :-------\n")
    pprint(initial_state)
    print("\n\n")
    
    state = graph.invoke(initial_state)
    print("--------FINAL STATE :--------\n")
    pprint(state)
    print("\n-----------------------------\n")
    
    # message = state["messages"][-1].content
    confirmation = state["confirmation_msg"][-1]["content"]
    liens = [source.lien for source in state["sources"]]
    
    return confirmation, liens




if __name__ == "__main__":
    messages = [
        {"role": "user", "content": "J'ai mal à la tête depuis deux jours et je me sens un peu fiévreux. Que me recommandez-vous ?"},
        {"role": "assistant", "content": "Vous pourriez essayer de prendre du Doliprane ou de l'Ibuprofène pour soulager vos symptômes."}
    ]
    list_medics = ["Doliprane", "Ibuprofène"]
    
    reponse, liens = call_agent(messages, list_medics)
    
    print("\n\n", ''.join(reponse), "\n")
    
    
    


