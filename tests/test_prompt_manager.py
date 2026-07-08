import json
import os

import pytest

from agent.nodes import GeminiAgentGraphNodes
from agent.prompt_manager import PromptManager
from agent.state import AgentInput, Persona, Question

pytestmark = pytest.mark.skipif(
    os.environ.get("BAZAAR_RUN_INTEGRATION_TESTS") != "1",
    reason="prompt manager tests call an external prompt registry",
)


def test_set_prepare_input_prompt():
    prompt_manager = PromptManager()
    version_id = prompt_manager.set(
        name="prepare-input",
        description=(
            "System prompt that compiles the user's free-text focus-group request into the structured "
            "AgentInput (focus group description, persona count, questions with stable ids, and reviewer "
            "guidance) consumed by the rest of the focus-group review pipeline."
        ),
        template_path="./templates/prepare_input.hbs",
    )
    assert version_id is not None and len(version_id) > 0
    print(version_id)


def test_get_prepare_input_prompt():
    prompt_manager = PromptManager()
    sample_user_prompt = "This is a sample user prompt for testing purposes."
    prompt = prompt_manager.get(
        version_id=GeminiAgentGraphNodes.prepare_input_prompt_version_id(),
        user_prompt=sample_user_prompt,
    )
    assert prompt is not None and len(prompt) > 0
    print(prompt)


def test_set_create_focus_group_prompt():
    prompt_manager = PromptManager()
    version_id = prompt_manager.set(
        name="create-focus-group",
        description=(
            "System prompt that synthesizes a diverse focus group of personas from the structured "
            "AgentInput brief (focus group description, persona count, questions, and reviewer "
            "guidance). Returns a PersonasList of Persona entries, each with id, name, bio, and "
            "demographics, that the subsequent review_content step will fan out over."
        ),
        template_path="./templates/create_focus_group.hbs",
    )
    assert version_id is not None and len(version_id) > 0
    print(version_id)


def test_get_create_focus_group_prompt():
    prompt_manager = PromptManager()
    sample_agent_input = AgentInput(
        focus_group_description="Young adults aged 18-30 who are fans of prestige TV dramas",
        persona_count=4,
        questions=[
            Question(id="q1", question="Would you watch the next episode?"),
            Question(id="q2", question="What was the most memorable scene and why?"),
            Question(id="q3", question="Rate the overall pilot on a scale of 1-10."),
        ],
        review_guidance="Be critical but constructive; focus on dialogue, character development, and pacing.",
    )
    prompt = prompt_manager.get(
        version_id=GeminiAgentGraphNodes.create_focus_group_prompt_version_id(),
        agent_input=sample_agent_input.model_dump_json(indent=2),
    )
    assert prompt is not None and len(prompt) > 0
    print(prompt)


def test_set_review_content_prompt():
    prompt_manager = PromptManager()
    version_id = prompt_manager.set(
        name="review-content",
        description=(
            "System prompt that has a single focus-group persona review the cached video and "
            "produce a structured ContentReview. Receives the persona (id, name, bio, "
            "demographics), the reviewer guidance, and the list of questions (with stable ids) "
            "the persona must answer. Returns a ContentReview with one QuestionResponse per "
            "question (matching question_ids) and 5-10 timestamped Annotations."
        ),
        template_path="./templates/review_content.hbs",
    )
    assert version_id is not None and len(version_id) > 0
    print(version_id)


def test_get_review_content_prompt():
    prompt_manager = PromptManager()
    sample_persona = Persona(
        id="persona_1",
        name="Maya Chen",
        bio=(
            "Maya is 24, a graduate student in film studies living in a major city. "
            "She watches prestige dramas closely and cares about dialogue, character "
            "arcs, and pacing."
        ),
        demographics="female, 24, urban, graduate student",
    )
    sample_questions = [
        Question(id="q1", question="Would you watch the next episode?"),
        Question(id="q2", question="What was the most memorable scene and why?"),
        Question(id="q3", question="Rate the overall pilot on a scale of 1-10."),
    ]
    prompt = prompt_manager.get(
        version_id=GeminiAgentGraphNodes.review_content_prompt_version_id(),
        persona=sample_persona.model_dump_json(indent=2),
        review_guidance="Be critical but constructive; focus on dialogue, character development, and pacing.",
        questions=json.dumps(
            [q.model_dump(mode="json") for q in sample_questions],
            indent=2
        ),
    )
    assert prompt is not None and len(prompt) > 0
    print(prompt)
