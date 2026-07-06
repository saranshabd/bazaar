import abc
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import Runnable
from langgraph.types import Send
from overrides import override
from pydantic import BaseModel

from focus_group_reviewer.prompt_manager import PromptManager
from focus_group_reviewer.state import AgentInput, AgentState, PersonaAgentState, ContentReview, ContentReviewOptMixin, PersonasList


class AgentGraphNodes(abc.ABC):

    @abc.abstractmethod
    def prepare_input(self, state: AgentState) -> AgentState:
        """Construct `AgentInput` from the original user prompt."""

    @abc.abstractmethod
    def create_focus_group(self, state: AgentState) -> AgentState:
        """Create the focus group and all the personas from the description."""

    @abc.abstractmethod
    def fan_out_reviewers(self, state: AgentState) -> list[Send]:
        """Fan out `review_content` nodes for all the personas to review the content video separately."""

    @abc.abstractmethod
    def review_content(self, state: PersonaAgentState) -> ContentReviewOptMixin:
        """Focus group persona (with the given person_id) reviews the video content and prepares `ContentReview`"""

    @abc.abstractmethod
    def eval_reviews(self, state: AgentState) -> AgentState:
        """Evaluate the quality of persona reviews of the content."""


class GeminiAgentGraphNodes(AgentGraphNodes):

    _model_name: str
    _temperature: float
    prompt_manager: PromptManager

    def __init__(
        self, model_name: str = "gemini-3.5-flash", temperature: float = 0.2
    ):
        self._model_name = model_name
        self._temperature = temperature

        self.prompt_manager = PromptManager()

    def _typed_model(
        self,
        T: type[BaseModel],
        model_kwargs: dict = dict(),
    ) -> Runnable:
        return (
            ChatGoogleGenerativeAI(
                model=self._model_name,
                temperature=self._temperature,
                **model_kwargs,
            )
            .with_structured_output(
                T,
                method="json_schema",
            )
        )

    @staticmethod
    def prepare_input_prompt_version_id():
        return "UHJvbXB0VmVyc2lvbjox"

    @staticmethod
    def create_focus_group_prompt_version_id():
        return "UHJvbXB0VmVyc2lvbjoz"

    @staticmethod
    def review_content_prompt_version_id():
        return "UHJvbXB0VmVyc2lvbjo1"

    @override
    def prepare_input(self, state: AgentState) -> AgentState:
        """
        This node prepares the input for the rest of the graph. It processes the user prompt
        to figure out the questions to ask, personas to create and reviewer guidance for the
        personas.

        This is the most crucial part of the graph since the self-improving loop will rewrite
        only this part of the graph.
        """

        prompt = self.prompt_manager.get(
            self.prepare_input_prompt_version_id(),
            user_prompt=state.user_prompt,
        )

        agent_input = self._typed_model(AgentInput).invoke(prompt)
        assert agent_input is not None
        state.agent_input = agent_input

        return state

    @override
    def create_focus_group(self, state: AgentState) -> AgentState:
        assert state.agent_input is not None

        prompt = self.prompt_manager.get(
            self.create_focus_group_prompt_version_id(),
            agent_input=state.agent_input.model_dump_json(indent=2),
        )

        personas_opt = self._typed_model(PersonasList).invoke(prompt)
        assert personas_opt is not None
        state.personas = personas_opt.personas

        return state

    @override
    def fan_out_reviewers(self, state: AgentState) -> list[Send]:
        return [
            Send(
                node="review_content",
                arg=PersonaAgentState(
                    **state.model_dump(), persona_id=persona.id
                ),
            )
            for persona in state.personas
        ]

    @override
    def review_content(self, state: PersonaAgentState) -> ContentReviewOptMixin:
        persona = next(p for p in state.personas if p.id == state.persona_id)

        assert state.agent_input is not None

        prompt = self.prompt_manager.get(
            self.review_content_prompt_version_id(),
            persona=persona.model_dump_json(indent=2),
            review_guidance=state.agent_input.review_guidance,
            questions=json.dumps(
                [
                    question.model_dump(mode="json")
                    for question in state.agent_input.questions
                ],
                indent=2,
            ),
        )

        content_review = (
            self._typed_model(
                ContentReview,
                model_kwargs={
                    "cached_content": state.content_cache_key,
                }
            )
            .invoke(prompt)
        )
        assert content_review is not None

        return ContentReviewOptMixin(reviews=[content_review])

    @override
    def eval_reviews(self, state: AgentState) -> AgentState:
        return state
