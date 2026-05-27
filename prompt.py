from phoenix.client import Client
from phoenix.client.types import PromptVersion
from phoenix.client.__generated__.v1 import PromptMessage

import constants

client = Client(base_url=constants.PHOENIX_CLIENT_URL)


def get_system_prompt_text(version_id: str) -> str:
    prompt = client.prompts.get(
        prompt_version_id=version_id,
    )
    return prompt.format(sdk="openai")["messages"][0]["content"]


def get_judge_prompt(version_id: str, question: str, agent_response: str) -> str:
    prompt = (
        client.prompts.get(
            prompt_version_id=version_id,
        )
        .format(
            sdk="openai",
            variables={
                "user_question": question,
                "agent_response": agent_response,
            }
        )
    )
    prompt = prompt["messages"][0]["content"]
    return prompt


def register_system_prompt(template_path: str) -> None:
    with open(template_path, "r") as f:
        system_prompt = f.read()

    prompt_version = client.prompts.create(
        name="incident-triage-system-prompt",
        version=PromptVersion(
            [
                PromptMessage(
                    role="system",
                    content=system_prompt,
                ),
            ],
            model_name="gemini-3.5-flash",
            model_provider="GOOGLE"
        ),
        prompt_description="System prompt for the onboarding incident triage agent",
    )
    print(prompt_version)


def register_judge_system_prompt(template_path: str) -> None:
    with open(template_path, "r") as f:
        judge_prompt = f.read()

    prompt_version = client.prompts.create(
        name="incident-triage-judge-system-prompt",
        version=PromptVersion(
            [
                PromptMessage(
                    role="system",
                    content=judge_prompt,
                ),
            ],
            model_name="gemini-3.5-flash",
            model_provider="GOOGLE",
        ),
        prompt_description="System prompt for the incident triage response-judge agent",
    )
    print(prompt_version)


if __name__ == "__main__":
    # register_system_prompt(
    #     template_path="./templates/system_prompt.hbs",
    # )
    register_judge_system_prompt(
        template_path="templates/judge_prompt.hbs"
    )
