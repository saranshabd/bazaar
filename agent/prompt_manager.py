import os
from pathlib import Path

from phoenix.client import Client as PhoenixClient
from phoenix.client.__generated__.v1 import PromptMessage
from phoenix.client.types import PromptVersion


class PromptManager:

    phoenix_client: PhoenixClient

    def __init__(self, phoenix_client_url: str | None = None):
        if phoenix_client_url is None:
            phoenix_client_url = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT")
        assert phoenix_client_url is not None

        self.phoenix_client = PhoenixClient(base_url=phoenix_client_url)

    def get(self, version_id: str, **kwargs) -> str:
        prompt = (
            self.phoenix_client.prompts.get(
                prompt_version_id=version_id,
            )
            .format(
                sdk="openai",
                variables=kwargs,
            )
        )
        prompt = prompt["messages"][0]["content"]
        return prompt

    def set(
        self, name: str, description: str, template_path: str,
    ) -> str:
        template_path = Path(template_path)
        if not template_path.exists():
            raise ValueError(f"'{template_path}' template path does not exist.")

        with open(template_path, "r") as f:
            system_prompt = f.read()

        prompt_version = self.phoenix_client.prompts.create(
            name=name,
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
            prompt_description=description,
        )

        assert prompt_version.id is not None
        return prompt_version.id
