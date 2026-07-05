from focus_group_reviewer.nodes import GeminiAgentGraphNodes
from focus_group_reviewer.prompt_manager import PromptManager
from focus_group_reviewer.state import AgentInput, Question


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
