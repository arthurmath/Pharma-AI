# Question réponse humain - chatbot (schema langgraph)

from typing import Annotated, Literal, Optional # = Union[T, None]
from typing_extensions import TypedDict
from pprint import pprint
from prompts import syst_promptV0

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model("openai:gpt-4.1-mini") # anthropic:claude-3-5-sonnet-latest


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    presciptions: Annotated[str, add_messages]




def human(state: State) -> State:
    message = input("\nUSER: ")
    return {"messages": [{"role": "user", "content": message}]}


def chatbot(state: State) -> State:
    response = llm.invoke(state["messages"])
    print("\n\nCHATBOT:", response.content, "\n\n")
    return {"messages": [{"role": "ai", "content": response.content}]}


def route_chat_exit(state: State) -> Literal["chatbot", "__end__"]:
    # Check if the last message from the user contains "exit"
    last_message = state["messages"][-1]
    if last_message.content.lower() in ["exit", "q", "quitter"]:
        return END
    else:
        return "chatbot"
    
    




graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("human", human)

graph_builder.add_edge(START, "human")
graph_builder.add_edge("chatbot", "human")
graph_builder.add_conditional_edges("human", route_chat_exit)

graph = graph_builder.compile()


# # Save the graph as a PNG file
# graph_png = graph.get_graph().draw_mermaid_png()
# with open("images/grapheV0.png", "wb") as f:
#     f.write(graph_png)



def call_agent(messages: Optional[list]):
    initial_state = {"messages": []}
    if messages:
        initial_state["messages"].append({"role": "user", "content": messages})
    state = graph.invoke(initial_state)
    return state["messages"][-1].content





if __name__ == "__main__":
    
    initial_state = {"messages": [{"role": "system", "content": syst_promptV0}]}
    state = graph.invoke(initial_state)
    
    print("\n\n\n")
    pprint(state)