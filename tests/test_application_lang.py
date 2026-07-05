import asyncio
import time
from unittest import IsolatedAsyncioTestCase
import os
import pytest

from fastapi import UploadFile

from focus_group_reviewer.api import ApplicationLang
from focus_group_reviewer.nodes import GeminiAgentGraphNodes
from focus_group_reviewer.state import AgentState


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
            os.environ.get("FGR_CONTENT_CACHE_NAME") or "cachedContents/duhx4ijd5mlq9djal3bl0uz6zwx14g6f430wqmm6"
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
