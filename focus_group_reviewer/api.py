import asyncio
from uuid import uuid4

import fire
import uvicorn
from fastapi import FastAPI, UploadFile
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

from focus_group_reviewer.graph import AgentGraphBuilder
from focus_group_reviewer.nodes import GeminiAgentGraphNodes
from focus_group_reviewer.state import AgentState
from focus_group_reviewer.storage import ContentLibrary, GoogleStorageContentLibrary


class CacheVideoOpt(BaseModel):
    cache_name: str


class InvokeAgentOpt(BaseModel):
    run_id: str


class ApplicationLang:

    content_library: ContentLibrary
    graph: CompiledStateGraph[AgentState]

    tasks: dict[str, asyncio.Task]
    agent_states: dict[str, AgentState]

    def __init__(self):
        self.content_library = GoogleStorageContentLibrary()

        nodes = GeminiAgentGraphNodes()
        self.graph = AgentGraphBuilder(nodes=nodes).build()

        self.tasks = dict()
        self.agent_states = dict()

    @staticmethod
    def create_run() -> str:
        return str(uuid4())

    def cache_video(self, video: UploadFile) -> CacheVideoOpt:
        assert video.filename is not None, "video must have a filename"
        assert video.filename.endswith(".mp4"), "video must have a filename"
        cache_name = self.content_library.cache_file(
            local_filename=video.filename,
        )
        return CacheVideoOpt(cache_name=cache_name)

    def invoke_agent(self, user_prompt: str, content_cache_name: str) -> InvokeAgentOpt:
        run_id = self.create_run()
        agent_state = AgentState(
            run_id=run_id,
            content_cache_key=content_cache_name,
            user_prompt=user_prompt,
        )
        task = asyncio.create_task(
            self.graph.ainvoke(
                agent_state,
                config=RunnableConfig(
                    configurable={
                        "thread_id": run_id,
                    }
                )
            )
        )
        self.tasks[run_id] = task
        self.agent_states[run_id] = agent_state
        return InvokeAgentOpt(run_id=run_id)

    def cancel_agent(self, run_id: str) -> None:
        if run_id not in self.tasks:
            return
        self.tasks[run_id].cancel()
        del self.tasks[run_id]
        assert run_id in self.agent_states
        del self.agent_states[run_id]

    async def stream_agent_state(self, run_id: str):
        while True:
            await asyncio.sleep(1)
            if run_id not in self.tasks:
                break
            assert run_id in self.agent_states
            yield self.agent_states[run_id]

    def shutdown(self):
        print("shutting down...")
        for run_id in list(self.tasks):
            self.cancel_agent(run_id)
        assert len(self.tasks) == 0, "failed to cancel all tasks"
        assert len(self.agent_states) == 0, "failed to delete all agent states"
        print("shut down completed.")


class RemoteApplicationLang:

    api: FastAPI
    lang: ApplicationLang

    def __init__(self):
        self.api = FastAPI()
        self.lang = ApplicationLang()

    @classmethod
    def with_mapped_routes(cls):
        return cls().map_routes()

    def map_routes(self) -> "RemoteApplicationLang":

        @self.api.post("/content/cache-video")
        def cache_video(video: UploadFile) -> CacheVideoOpt:
            return self.lang.cache_video(video)

        @self.api.post("/agent/invoke")
        def invoke_agent(user_prompt: str, content_cache_name: str) -> InvokeAgentOpt:
            return self.lang.invoke_agent(user_prompt, content_cache_name)

        return self

    def serve(self, port: int) -> None:
        uvicorn.run(self.api, host="0.0.0.0", port=port)


def main(port: int = 9384) -> None:
    RemoteApplicationLang.with_mapped_routes().serve(port=port)


if __name__ == "__main__":
    fire.Fire(main)
