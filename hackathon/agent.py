from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from phoenix.client import Client as PhoenixClient
from phoenix.client.__generated__.v1 import PromptMessage
from phoenix.client.types import PromptVersion

import constants


class BaseAgent(ABC):

    def __init__(self, client: PhoenixClient | None = None):
        self.client = client
        if self.client is None:
            self.client = PhoenixClient(base_url=constants.PHOENIX_CLIENT_URL)

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def project_name(self) -> str:
        ...

    @abstractmethod
    def system_prompt_version(self) -> str:
        ...

    def system_prompt(
        self,
        variables: Mapping[str, Any] | None = None,
    ) -> str:
        prompt = self.client.prompts.get(
            prompt_version_id=self.system_prompt_version(),
        )
        assert prompt is not None
        prompt = prompt.format(sdk="openai", variables=dict(variables or {}))
        return prompt["messages"][0]["content"]

    def create_system_prompt(self, name: str, description: str, system_prompt: str) -> str:
        prompt_version = self.client.prompts.create(
            name=name,
            version=PromptVersion(
                [
                    PromptMessage(
                        role="system",
                        content=system_prompt,
                    ),
                ],
                model_name="gemini-3.5-flash",
                model_provider="GOOGLE",
            ),
            prompt_description=description,
        )
        return prompt_version.id


