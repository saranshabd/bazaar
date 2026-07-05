from focus_group_reviewer.nodes import GeminiAgentGraphNodes
from focus_group_reviewer.prompt_manager import PromptManager


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
