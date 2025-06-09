# 1er LLM propose une liste de médicaments (peu fiable) puis verification avec l'API BDPM

from typing import Annotated, Literal, List, Optional # = Union[T, None]
from typing_extensions import TypedDict
from pprint import pprint
from prompts import *
from pydantic import BaseModel, Field

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model("openai:gpt-4.1-mini", temperature=0) # anthropic:claude-3-5-sonnet-latest



class Source(BaseModel):
    medicament: str
    lien: str
    texte: str
    


class State(TypedDict):
    messages: Annotated[str, add_messages]
    prescriptions: List[str]
    sources: List[Source]
    

    
class Medicaments(BaseModel):
    message_type: List[str] = Field(
        ...,
        description="Liste des médicaments recommandés pour ces symptomes, les chaînes de caractères ne doivent contenir que les noms des médicaments prescrits."
    )
    
    



def presciption_llm(state: State) -> State:
    # print("\n\nSTATE PRESCRIPTION : ")
    # pprint(state)
    # print("\n\n")
    
    llm_st = llm.with_structured_output(Medicaments)

    result = llm_st.invoke([
        {"role": "system", "content": syst_promptV1_pres},
        {"role": "user", "content": state["messages"][-1].content}
    ])
    # print("\nPRESCRIPTIONS LLM:", result.message_type, "\n\n")
    return {"prescriptions": result.message_type}



def verification_api(state: State) -> State:
    # print("\n\nSTATE VERIFICATION : ")
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



def requete(nom_medicament: str) -> str:
    """ Fonction pour récupérer les informations sur le médicament """
    
    selecteur_lien = 'a[href*="extrait.php?specid="]'
    selecteur_text = 'p.AmmCorpsTexte'
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver-137"))
    driver.get("https://base-donnees-publique.medicaments.gouv.fr")

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
        print("-" * 40 + "\n")
            
        return url, "\n".join(p.text for p in paragraphes)

    except Exception as e:
        print("❌ Erreur médicament :", nom_medicament)
        return url, "None"

    finally:
        driver.quit()

    
    
    
def confirmation_llm(state: State) -> State:
    # print("\n\nSTATE CONFIRMATION : ")
    # pprint(state)
    # print("\n\n")
    
    prompt = (syst_promptV1_conf,
        "Symptomes : " + state["messages"][-1].content + "\n\n",
        "Prescriptions : " + str(state["prescriptions"]) + "\n\n", # Necessaire ??
        "Informations : "
    )
    prompt = ''.join(prompt)
    for source in state["sources"]:
        prompt += source.medicament + " : " + source.texte + "\n"
        
    prompt = ''.join(prompt)
    # print("\nPROMPT : \n", prompt)
    
    response = llm.invoke([{"role": "system", "content": prompt}])
    
    # print("CONFIRMATION LLM:", response.content, "\n\n")
    return {"messages": [{"role": "ai", "content": ''.join(response.content)}]}





graph_builder = StateGraph(State)

graph_builder.add_node("prescription", presciption_llm)
graph_builder.add_node("verification", verification_api)
graph_builder.add_node("confirmation", confirmation_llm)

graph_builder.add_edge(START, "prescription")
graph_builder.add_edge("prescription", "verification")
graph_builder.add_edge("verification", "confirmation")
graph_builder.add_edge("confirmation", END)

graph = graph_builder.compile()


# Save the graph as a PNG file
graph_png = graph.get_graph().draw_mermaid_png()
with open("images/grapheV1.png", "wb") as f:
    f.write(graph_png)





def call_agent(prompt: str):
    initial_state = {"messages": [{"role": "user", "content": prompt}]}
    # print("INITIAL STATE :\n")
    # pprint(initial_state)
    print("\n\n")
    
    state = graph.invoke(initial_state)
    pprint(state)
    
    final_message = state["messages"][-1].content
    liens = [source.lien for source in state["sources"]]
    
    return final_message, liens




if __name__ == "__main__":
    prompt = "J'ai mal à la tête depuis deux jours et je me sens un peu fiévreux. Que me recommandez-vous ?"
    reponse, liens = call_agent(prompt)
    
    print("\n\n", ''.join(reponse), "\n")
    
    
    


