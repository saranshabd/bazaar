import abc

from langgraph.types import Send
from overrides import override

from focus_group_reviewer.state import AgentState, PersonaAgentState, ContentReview, ContentReviewOptMixin


class AgentGraphNodes(abc.ABC):

    @abc.abstractmethod
    def upload_video(self, state: AgentState) -> AgentState:
        """Upload content to GCS, Gemini Files API and cache for later LLM queries."""

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

    @override
    def upload_video(self, state: AgentState) -> AgentState:
        return state

    @override
    def prepare_input(self, state: AgentState) -> AgentState:
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
