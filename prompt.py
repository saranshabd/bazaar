from phoenix.client import Client
from phoenix.client.types import PromptVersion

client = Client(base_url="http://localhost:6006")


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


def get_system_prompt(version_id: str) -> str:
    prompt = client.prompts.get(
        prompt_version_id=version_id,
    )
    return prompt.format(sdk="openai")["messages"][0]["content"]


def register_system_prompt() -> None:
    prompt_version = client.prompts.create(
        name="incident-triage-system-prompt",
        version=PromptVersion(
            [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                }
            ],
            model_name="gemini-2.5-flash",
            model_provider="GOOGLE"
        ),
        prompt_description="System prompt for the onboarding incident triage agent",
    )
    print(prompt_version)


if __name__ == "__main__":
    register_system_prompt()
