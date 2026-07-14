from langgraph.graph import StateGraph, START, END

from nodes.creative_director import creative_director
from nodes.image_generator import image_generator

from state import CreativeState


builder = StateGraph(CreativeState)

builder.add_node("creative_director", creative_director)
builder.add_node("image_generator", image_generator)

builder.add_edge(START, "creative_director")
builder.add_edge("creative_director", "image_generator")
builder.add_edge("image_generator", END)

creative_graph = builder.compile()