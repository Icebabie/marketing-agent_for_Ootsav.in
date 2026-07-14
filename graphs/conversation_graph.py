from langgraph.graph import StateGraph, START, END

from state import State
from nodes.brain import brain


builder = StateGraph(State)

builder.add_node("brain", brain)

builder.add_edge(START, "brain")
builder.add_edge("brain", END)

graph = builder.compile()