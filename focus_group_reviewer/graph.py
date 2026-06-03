from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph

from focus_group_reviewer.nodes import AgentGraphNodes
from focus_group_reviewer.state import AgentState


class AgentGraphBuilder:

    def __init__(self, nodes: AgentGraphNodes):
        self.nodes = nodes

    def build(self) -> CompiledStateGraph[AgentState]:
        builder = StateGraph(AgentState)
        self.add_nodes_(builder)
        builder.set_entry_point("upload_video")
        self.add_edges_(builder)
        checkpointer = MemorySaver()
        graph = builder.compile(checkpointer=checkpointer)
        return graph

    def add_nodes_(self, builder: StateGraph[AgentState]):
        builder.add_node("upload_video", self.nodes.upload_video)
        builder.add_node("prepare_input", self.nodes.prepare_input)
        builder.add_node("create_focus_group", self.nodes.create_focus_group)
        builder.add_node("review_content", self.nodes.review_content)
        builder.add_node("eval_reviews", self.nodes.eval_reviews)

    def add_edges_(self, builder: StateGraph[AgentState]):
        builder.add_edge("upload_video", "prepare_input")
        builder.add_edge("prepare_input", "create_focus_group")
        builder.add_conditional_edges(
            "create_focus_group",
            self.nodes.fan_out_reviewers,
            ["review_content"],
        )
        builder.add_edge("review_content", "eval_reviews")
        builder.add_edge("eval_reviews", END)
