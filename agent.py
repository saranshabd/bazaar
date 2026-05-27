from phoenix.otel import register as register_phoenix_otel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent, AgentState
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from openinference.instrumentation import using_prompt_template, capture_span_context

from judge import evaluate_agent_response
from prompt import get_system_prompt_text
from tools import agent_tools
import constants

register_phoenix_otel(
    project_name=constants.PROJECT_NAME,
    auto_instrument=True,
)

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
)

system_prompt_version = constants.AgentPrompts["GOOD"]
system_prompt = get_system_prompt_text(version_id=system_prompt_version)

agent = create_agent(
    model=model,
    tools=agent_tools(),
    system_prompt=system_prompt,
)


def run_incident(question: str):
    with using_prompt_template(
        template=system_prompt,
        version=system_prompt_version,
        variables={}
    ):
        with capture_span_context() as capture:
            opt = agent.invoke(
                Command(
                    update=AgentState(
                        messages=[
                            HumanMessage(content=question)
                        ]
                    )
                )
            )

            span_id = capture.get_first_span_id()
            assert span_id is not None

    agent_response = opt["messages"][-1].content[0]["text"]
    print("\n========== AGENT RESPONSE ==========")
    print(agent_response)

    evaluate_agent_response(span_id, question, agent_response)
    print("Agent response judged.")


if __name__ == "__main__":
    run_incident(
        "New users cannot complete onboarding today. Investigate the incident, "
        "identify the probable cause, and recommend the immediate response."
    )
