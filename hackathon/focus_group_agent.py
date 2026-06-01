from typing import List

from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from overrides import override

from phoenix.client import Client as PhoenixClient
from phoenix.otel import register as register_phoenix_otel

from pydantic import BaseModel, Field

from hackathon.agent import BaseAgent


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
        return "google-rapid-hackathon"

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

        opt: FocusGroupOpt = self.model.invoke(
            system_prompt,
            config=RunnableConfig(
                run_name="create_focus_group",
            ),
        )
        assert opt is not None

        assert len(opt.personas) == persona_count
        return opt
