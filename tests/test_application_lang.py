import asyncio
import time
from unittest import IsolatedAsyncioTestCase
import os
import pytest

from fastapi import UploadFile

from focus_group_reviewer.api import ApplicationLang
from focus_group_reviewer.nodes import GeminiAgentGraphNodes
from focus_group_reviewer.state import (
    AgentInput,
    AgentState,
    ContentReviewOptMixin,
    Persona,
    PersonaAgentState,
    PersonasList,
    Question,
)


class TestApplicationLang(IsolatedAsyncioTestCase):

    lang: ApplicationLang

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = ApplicationLang()

    def test_video_cache(self):
        """
        Elapsed time ~2.8 minutes.
        Total token count 141,008.
        """

        filename = "./focus_group_reviewer/artifacts/FRIENDS_Pilot.mp4"
        with open(filename, "rb") as f:
            start = time.perf_counter()
            opt = self.lang.cache_video(
                video=UploadFile(
                    filename=filename,
                    file=f,
                )
            )
            elapsed_time = time.perf_counter() - start

        assert opt is not None

        print(f"opt: '{opt}'")
        print(f"elapsed_time: {elapsed_time}s")

        total_token_count = self.lang.content_library.peek_cache(opt.cache_name)
        assert total_token_count is not None, (
            f"Failed to verify '{opt.cache_name}' cache in the content library."
        )
        print(f"total_token_count: {total_token_count}")

    @property
    def user_prompt(self):
        return (
            "I want feedback from young adults aged 18-30 who are fans of prestige TV dramas like Succession "
            "and The Bear. They should be critical viewers who pay attention to dialogue, character development, "
            "and pacing. Ask them: would they watch the next episode? What was the most memorable scene and why? "
            "Rate the overall pilot on a scale of 1-10."
        )

    @property
    def content_cache_name(self) -> str:
        value = (
            os.environ.get("FGR_CONTENT_CACHE_NAME") or "cachedContents/3wp9c9ojtqbk7l3afft8xybavlk6l43g1gt5rld9"
        )
        assert len(value) > 0
        return value

    @pytest.mark.asyncio
    async def test_invoke_agent(self):
        opt = self.lang.invoke_agent(self.user_prompt, self.content_cache_name)
        assert opt is not None

        print(f"opt: {opt.model_dump_json(indent=2)}")

        async def delayed_shutdown(for_seconds: int):
            await asyncio.sleep(for_seconds)
            self.lang.shutdown()

        delay_in_seconds = int(os.environ.get("FGR_DELAY_IN_SECONDS") or 10)
        shutdown_task = asyncio.create_task(
            delayed_shutdown(for_seconds=delay_in_seconds)
        )

        async for agent_state in self.lang.stream_agent_state(run_id=opt.run_id):
            print(agent_state)

        await shutdown_task

    def test_prepare_input(self):
        agent_state = AgentState(
            run_id=self.lang.create_run(),
            user_prompt=self.user_prompt,
            content_cache_key=self.content_cache_name,
        )

        nodes = GeminiAgentGraphNodes()
        updated_agent_state = nodes.prepare_input(agent_state)

        assert updated_agent_state.agent_input is not None
        print(updated_agent_state.agent_input.model_dump_json(indent=2))

    def test_create_focus_group(self):
        agent_state = AgentState(
            run_id=self.lang.create_run(),
            user_prompt=self.user_prompt,
            content_cache_key=self.content_cache_name,
            agent_input=AgentInput(
                focus_group_description="Young adults aged 18-30 who are fans of prestige TV dramas",
                persona_count=4,
                questions=[
                    Question(id="q1", question="Would you watch the next episode?"),
                    Question(id="q2", question="What was the most memorable scene and why?"),
                    Question(id="q3", question="Rate the overall pilot on a scale of 1-10."),
                ],
                review_guidance="Be critical but constructive; focus on dialogue, character development, and pacing.",
            )
        )

        nodes = GeminiAgentGraphNodes()
        updated_agent_state = nodes.create_focus_group(agent_state)

        assert agent_state.agent_input is not None
        assert (
            len(updated_agent_state.personas) == agent_state.agent_input.persona_count
        )

        personas = PersonasList(personas=updated_agent_state.personas)
        print(personas.model_dump_json(indent=2))

    def test_review_content(self):
        personas = [
            Persona(
                id="persona_1",
                name="Maya Chen",
                bio=(
                    "Maya is 24, a graduate student in film studies living in a major city. "
                    "She watches prestige dramas closely and cares about dialogue, character "
                    "arcs, and pacing. She notices when scenes earn their length and when they "
                    "drag, and she has strong opinions about whether a pilot hooks her."
                ),
                demographics="female, 24, urban, graduate student",
            )
        ]
        agent_state = PersonaAgentState(
            run_id=self.lang.create_run(),
            user_prompt=self.user_prompt,
            content_cache_key=self.content_cache_name,
            agent_input=AgentInput(
                focus_group_description="Young adults aged 18-30 who are fans of prestige TV dramas",
                persona_count=1,
                questions=[
                    Question(id="q1", question="Would you watch the next episode?"),
                    Question(id="q2", question="What was the most memorable scene and why?"),
                    Question(id="q3", question="Rate the overall pilot on a scale of 1-10."),
                ],
                review_guidance="Be critical but constructive; focus on dialogue, character development, and pacing.",
            ),
            personas=personas,
            persona_id="persona_1",
        )

        nodes = GeminiAgentGraphNodes()
        opt = nodes.review_content(agent_state)

        assert isinstance(opt, ContentReviewOptMixin)
        assert len(opt.reviews) == 1

        review = opt.reviews[0]
        assert review.persona_id == agent_state.persona_id

        assert agent_state.agent_input is not None

        expected_question_ids = {
            q.id for q in agent_state.agent_input.questions
        }
        answered_question_ids = {a.question_id for a in review.answers}
        assert answered_question_ids == expected_question_ids, (
            f"Expected answers for {expected_question_ids}, got {answered_question_ids}"
        )

        assert len(review.annotations) >= 5, (
            f"Expected at least 5 annotations, got {len(review.annotations)}"
        )
        for annotation in review.annotations:
            assert 1 <= annotation.score <= 10
            assert annotation.timestamp_sec >= 0

        print(review.model_dump_json(indent=2))
