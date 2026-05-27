from phoenix.otel import register as register_phoenix_otel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from openinference.instrumentation import using_prompt_template

from prompt import get_system_prompt, RegisteredPromptVersions
from tools import agent_tools

# No need to configure API key since Phoenix is running locally.
register_phoenix_otel(
    project_name="arize_phoenix_playground",
    auto_instrument=True,
)

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

system_prompt_version = RegisteredPromptVersions["GOOD"]
system_prompt = get_system_prompt(version_id=system_prompt_version)

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
        opt = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            }
        )

    final_message = opt["messages"][-1]
    print("\n========== AGENT RESPONSE ==========")
    print(final_message)


if __name__ == "__main__":
    run_incident(
        "New users cannot complete onboarding today. Investigate the incident, "
        "identify the probable cause, and recommend the immediate response."
    )
