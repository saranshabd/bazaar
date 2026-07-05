import abc

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import Runnable
from langgraph.types import Send
from overrides import override

from focus_group_reviewer.prompt_manager import PromptManager
from focus_group_reviewer.state import AgentInput, AgentState, PersonaAgentState, ContentReview, ContentReviewOptMixin


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

    model: Runnable
    prompt_manager: PromptManager

    def __init__(
        self, model_name: str = "gemini-3.5-flash", temperature: float = 0.2
    ):
        self.model = (
            ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
            )
            .with_structured_output(
                AgentInput,
                method="json_schema",
            )
        )

        self.prompt_manager = PromptManager()

    @staticmethod
    def prepare_input_prompt_version_id():
        return "UHJvbXB0VmVyc2lvbjox"

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

        agent_input = self.model.invoke(prompt)
        assert agent_input is not None
        state.agent_input = agent_input

        return state

    @override
    def create_focus_group(self, state: AgentState) -> AgentState:
        return state

    @override
    def fan_out_reviewers(self, state: AgentState) -> list[Send]:
        return [
            Send(
                node="review_content",
                arg=PersonaAgentState(
                    **state.model_dump(), persona_id="sample_persona_id"
                ),
            )
        ]

    @override
    def review_content(self, state: PersonaAgentState) -> ContentReviewOptMixin:
        return ContentReviewOptMixin(
            reviews=[
                ContentReview(persona_id=state.persona_id, answers=[], annotations=[]),
            ]
        )

    @override
    def eval_reviews(self, state: AgentState) -> AgentState:
        return state
