import os
import fire
from langchain_core.runnables import RunnableConfig

from phoenix.otel import register as register_phoenix_otel

from focus_group_reviewer.graph import AgentGraphBuilder
from focus_group_reviewer.nodes import GeminiAgentGraphNodes
from focus_group_reviewer.state import AgentState


def auto_instrument_phoenix_otel() -> None:
    """
    Configure auto-instrumentation for Phoenix OTEL for LangChain and VertexAI
    :return:
    """
    register_phoenix_otel(
        project_name="dev-focus-group-reviewer",
        api_key=os.environ["PHOENIX_API_KEY"],
        endpoint=os.environ["PHOENIX_COLLECTOR_ENDPOINT"] + "/v1/traces",
        auto_instrument=True,
    )


def main() -> None:
    auto_instrument_phoenix_otel()

    nodes = GeminiAgentGraphNodes()
    graph = AgentGraphBuilder(nodes=nodes).build()

    run_id = "sample_run_id"

    opt = graph.invoke(
        AgentState(
            run_id=run_id,
            user_prompt=(
                "I want feedback from young adults aged 18-30 who are fans of prestige TV dramas like Succession "
                "and The Bear. They should be critical viewers who pay attention to dialogue, character development, "
                "and pacing. Ask them: would they watch the next episode? What was the most memorable scene and why? "
                "Rate the overall pilot on a scale of 1-10."
            ),
            video_content_uri="gcs://sample_video_content",
            gemini_content_cache_key="sample_cache_key",
        ),
        config=RunnableConfig(
            configurable={
                "thread_id": run_id,
            }
        ),
    )
    print(opt)


if __name__ == "__main__":
    fire.Fire(main)
