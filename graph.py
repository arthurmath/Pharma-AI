from typing import Annotated, Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages




class State(TypedDict):
    messages: Annotated[list, add_messages]




def fonction(state: State) -> State:
    pass

def route_chat_exit(state: State) -> Literal["humain", "extraction"]:
    pass
    





graph_builder = StateGraph(State)

graph_builder.add_node("humain", fonction)
graph_builder.add_node("chatbot", fonction)
graph_builder.add_node("extraction", fonction)
graph_builder.add_node("recuperation sources", fonction)
graph_builder.add_node("confirmation", fonction)

graph_builder.add_edge(START, "humain")
graph_builder.add_edge("humain", "chatbot")
graph_builder.add_conditional_edges("chatbot", route_chat_exit)
graph_builder.add_edge("extraction", "recuperation sources")
graph_builder.add_edge("recuperation sources", "confirmation")
graph_builder.add_edge("confirmation", END)


graph = graph_builder.compile()


# Save the graph as a PNG file
graph_png = graph.get_graph().draw_mermaid_png()
with open("images/grapheV2.png", "wb") as f:
    f.write(graph_png)


