from phoenix.otel import register as register_phoenix

from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent


# No need to configure API key since Phoenix is running locally.
register_phoenix(
    project_name="arize_phoenix_playground",
    auto_instrument=True,
)


@tool
def get_recent_alerts() -> str:
    """Return recent infrastructure and third-party service alerts."""
    return """
Recent alerts:
- 10:04 UTC: Authentication provider latency increased sharply.
- 10:06 UTC: OAuth callback requests returning intermittent 503 errors.
- 10:07 UTC: New user sign-in completion rate dropped by 38%.
"""


@tool
def search_recent_deployments() -> str:
    """Return recent application deployments related to onboarding."""
    return """
Recent deployments:
- 09:42 UTC: web-onboarding v1.18.2 deployed.
- Change: invite acceptance route migrated from /accept-invite to /join.
- Known symptom: old email invite links may redirect to a missing route.
"""


@tool
def get_customer_reports() -> str:
    """Return recent customer complaints related to onboarding."""
    return """
Recent customer reports:
- Existing users can log in normally.
- Some invited users see a blank page after clicking invite links.
- Some new users report login timing out after accepting an invite.
"""


TOOLS = [
    get_recent_alerts,
    search_recent_deployments,
    get_customer_reports,
]

SYSTEM_PROMPT = """
You are an incident triage engineer.

Your job is to identify likely causes of an onboarding incident using available tools.

Rules:
- Do not conclude after checking only one source.
- Inspect alerts, recent deployments, and customer reports before diagnosing.
- Separate confirmed evidence from hypotheses.
- Return:
  1. probable causes,
  2. supporting evidence,
  3. immediate mitigation,
  4. next debugging step.
"""


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

agent = create_agent(
    model=model,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
)


def run_incident(question: str):
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
