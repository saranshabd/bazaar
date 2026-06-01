from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any
from typing import List

from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from overrides import override

from phoenix.client import Client as PhoenixClient
from phoenix.client.__generated__.v1 import PromptMessage
from phoenix.client.types import PromptVersion
from phoenix.otel import register as register_phoenix_otel

from pydantic import BaseModel, Field

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


class FocusGroupPersona(BaseModel):
    system_prompt: str = Field(
        description=(
            "The complete system prompt for one persona review agent. It should "
            "define the persona's identity, audience perspective, evaluation "
            "priorities, tone, blind spots, and the way they should review and "
            "score a video while staying in character."
        )
    )
    name: str = Field(
        description=(
            "A short, human-readable persona name that clearly distinguishes this "
            "reviewer from the other focus group members."
        )
    )


class FocusGroupOpt(BaseModel):
    personas: List[FocusGroupPersona] = Field(
        description=(
            "The full set of generated focus group personas. The list must match "
            "the requested persona count and should be intentionally diverse "
            "across motivations, context, expertise, constraints, and likely "
            "reactions to the video."
        )
    )


class FocusGroupAgent(BaseAgent):

    def __init__(
        self,
        gemini_model: str = "gemini-3.5-flash",
        temperature: float = 0,
        client: PhoenixClient | None = None,
    ):
        super().__init__(client=client)

        self.model = (
            ChatGoogleGenerativeAI(
                model=gemini_model,
                temperature=temperature,
            )
            .with_structured_output(
                FocusGroupOpt,
                method="json_schema",
            )
        )

    @override
    def initialize(self) -> None:
        register_phoenix_otel(
            project_name=self.project_name(),
            auto_instrument=True,
        )

    @override
    def project_name(self) -> str:
        return "create_persona_agent"

    @override
    def system_prompt_version(self) -> str:
        return "UHJvbXB0VmVyc2lvbjo3"

    def create_focus_group(
        self,
        focus_group_description: str,
        persona_count: int,
    ) -> FocusGroupOpt:
        assert persona_count > 0

        system_prompt = self.system_prompt(
            variables={
                "focus_group_description": focus_group_description,
                "persona_count": str(persona_count),
            },
        )

        opt: FocusGroupOpt = self.model.invoke(system_prompt)
        assert opt is not None

        assert len(opt.personas) == persona_count
        return opt
