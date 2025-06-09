from typing import List, Optional, Annotated, Literal
from typing_extensions import TypedDict
from pprint import pprint

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.messages.tool import ToolMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode


from dotenv import load_dotenv
load_dotenv()




llm = ChatOpenAI(
    model="gpt-4.1-mini-2025-04-14", # "gpt-3.5-turbo-0125", "gpt-4o"
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)



class PharmaState(TypedDict):
    messages: Annotated[list, add_messages] # List[BaseMessage]
    patient_info: Optional[dict]
    recommendations: Optional[str]




def collect_patient_info(state: PharmaState) -> dict:
    # Extraction fictive des informations du patient
    patient_info = {
        "âge": 45,
        "pathologies": ["hypertension"],
        "traitements_en_cours": ["amlodipine"],
        "grossesse": False,
        "budget": "modéré",
        "préférences": ["phytothérapie"]
    }
    return {"patient_info": patient_info}


def analyze_needs(state: PharmaState) -> dict:
    # Analyse fictive des besoins
    needs = {
        "symptômes": ["maux de tête"],
        "préférences": state["patient_info"].get("préférences", [])
    }
    return {"needs": needs}



def recommend_products(state: PharmaState) -> dict:
    # Recommandation fictive de produits
    recommendations = "Nous recommandons le produit X pour soulager les maux de tête, compatible avec vos traitements actuels."
    return {"recommendations": recommendations}



def generate_response(state: PharmaState) -> dict:
    response = f"{state['recommendations']} N'hésitez pas à demander si vous avez d'autres questions."
    return {"messages": state["messages"] + [AIMessage(content=response)]}




builder = StateGraph(PharmaState)

builder.add_node("collect_patient_info", collect_patient_info)
builder.add_node("analyze_needs", analyze_needs)
builder.add_node("recommend_products", recommend_products)
builder.add_node("generate_response", generate_response)

builder.add_edge(START, "collect_patient_info")
builder.add_edge("collect_patient_info", "analyze_needs")
builder.add_edge("analyze_needs", "recommend_products")
builder.add_edge("recommend_products", "generate_response")
builder.add_edge("generate_response", END)

graph = builder.compile()

# Save the graph as a PNG file
graph_png = graph.get_graph().draw_mermaid_png()
with open("images/graphe_gpt.png", "wb") as f:
    f.write(graph_png)





# if __name__ == "__main__":
    
#     print("Patient :")
#     message = input("Entrez vos symptomes : ")
    
#     initial_state = {
#         "messages": [HumanMessage(content=message)],
#         "patient_info": None,
#         "recommendations": None
#     }

#     for output in graph.stream(initial_state):
#         for key, value in output.items():
#             if key == "messages":
#                 print(f"Assistant: {value[-1].content}")
                
          
#     print("---------------------------------------")        
#     final_state = graph.invoke(initial_state)

#     print("État final du graphe :")
#     pprint(final_state)
    
    
    