from unittest import TestCase

from hackathon.focus_group_agent import FocusGroupAgent


class TestFocusGroupAgent(TestCase):

    def test_create_system_prompt(self):
        agent = FocusGroupAgent()
        agent.initialize()

        with open("./templates/hackathon/create_focus_group_system_prompt.hbs", "r") as f:
            system_prompt = f.read()

        version = agent.create_system_prompt(
            name="hackathon-create-focus-group-persona",
            description="System prompt to create focus group personas",
            system_prompt=system_prompt,
        )
        assert version is not None

        print("version = ", version)

    def test_create_focus_group(self):
        agent = FocusGroupAgent()
        agent.initialize()

        focus_group_opt = agent.create_focus_group(
            focus_group_description=(
                "Create a diverse focus group of STEM college students who will review a video from different student "
                "perspectives.Include students across different majors, years, goals, technical confidence levels, "
                "learning styles, campus contexts, and levels of skepticism.The group should include people who care "
                "about clarity, practical usefulness, credibility, pacing, accessibility, visual explanation quality, "
                "and whether the video would hold their attention.Avoid making the personas differ only by major or "
                "demographics; each persona should have distinct motivations, constraints, and evaluation criteria."

            ),
            persona_count=4,
        )
        assert focus_group_opt is not None

        print(focus_group_opt.model_dump_json(indent=2))
