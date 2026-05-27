from phoenix.client import Client
from phoenix.client.types import PromptVersion
from phoenix.client.__generated__.v1 import PromptMessage

client = Client(base_url="http://localhost:6006")


RegisteredPromptVersions = {
    "GOOD": "UHJvbXB0VmVyc2lvbjo0",
    "BAD": "UHJvbXB0VmVyc2lvbjoz",
}


def get_system_prompt_text(version_id: str) -> str:
    prompt = client.prompts.get(
        prompt_version_id=version_id,
    )
    return prompt.format(sdk="openai")["messages"][0]["content"]


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
            model_name="gemini-2.5-flash",
            model_provider="GOOGLE"
        ),
        prompt_description="System prompt for the onboarding incident triage agent",
    )
    print(prompt_version)


if __name__ == "__main__":
    register_system_prompt(
        template_path="./templates/system_prompt.j2",
    )
