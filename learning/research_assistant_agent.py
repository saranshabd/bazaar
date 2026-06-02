from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from pydantic import BaseModel, Field
import json

from phoenix.otel import register as register_phoenix_otel

from fire import Fire

from ddgs import DDGS


class ResearchAssistantState(BaseModel):
    """
    Agent state to be shared across tool calls.
    """

    question: str
    search_results: list[str] = Field(default_factory=list)
    search_count: int = 0
    final_answer: str = ""

    @property
    def context(self) -> str:
        return "\n\n".join(self.search_results)


class ResearchAssistantAgent:

    def __init__(self, llm: BaseChatModel, max_search_results_count: int = 3):
        self.llm = llm
        self.max_search_results_count = max_search_results_count

    def web_search(self, state: ResearchAssistantState) -> ResearchAssistantState:
        """
        Look up the information on the web and add it to the state.
        """
        with DDGS() as ddgs:
            search_results = list(ddgs.text(state.question, max_results=5))
        snippets = [search_result["body"] for search_result in search_results]
        state.search_count += 1
        state.search_results += snippets
        return state

    def eval_search_results(self, state: ResearchAssistantState) -> ResearchAssistantState:
        """
        Decide if the state has enough info. This function does not do anything; the conditional edge is down below.

        This method only exists for record-keeping; the decision-making will show up in observability.
        """
        return state

    def generate_answer(self, state: ResearchAssistantState) -> ResearchAssistantState:
        """Synthesize the final answer from all the aggregated web search results."""
        opt = self.llm.invoke(
            "Answer this question using the context below. \n\n"
            f"Question: {state.question} \n\n"
            f"Context: {state.context}"
        )
        state.final_answer = opt.content
        return state

    def should_continue(self, state: ResearchAssistantState) -> str:
        """
        Conditional edge in the graph deciding whether to keep searching the web or to synthesize the final answer.
        """

        if state.search_count >= self.max_search_results_count:
            return "done"

        opt = self.llm.invoke(
            "Do we have enough information to answer the following question? \n\n"
            f"Question: {state.question} \n\n"
            f"Context so far: {state.context} \n\n"
            "Respond only with YES or NO"
        )
        opt = opt.content.upper()
        assert opt in ["YES", "NO"]

        if opt == "YES":
            return "done"
        return "retry"

    def build_app(self) -> CompiledStateGraph[ResearchAssistantState]:
        graph = StateGraph(ResearchAssistantState)

        # add nodes
        graph.add_node("web_search", self.web_search)
        graph.add_node("eval_search_results", self.eval_search_results)
        graph.add_node("generate_answer", self.generate_answer)

        # set the entrypoint
        graph.set_entry_point("web_search")

        # defining normal edges (always go here next)
        graph.add_edge("web_search", "eval_search_results")
        graph.add_edge("generate_answer", END)

        # defining conditional edge
        graph.add_conditional_edges(
            "eval_search_results",
            self.should_continue,
            {
                "retry": "web_search",
                "done": "generate_answer",
            }
        )

        app = graph.compile()
        return app


def main(
    question: str = "What are the main differences between LangChain and LangGraph?"
) -> None:
    register_phoenix_otel(
        project_name="research_assistant_agent",
        auto_instrument=True,
    )

    app = (
        ResearchAssistantAgent(
            llm=init_chat_model(model_provider="google_genai", model="gemini-2.5-flash")
        )
        .build_app()
    )

    result = app.invoke(
        ResearchAssistantState(question=question)
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    Fire(main)
