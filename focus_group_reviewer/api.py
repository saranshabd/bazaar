import fire
import uvicorn
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from focus_group_reviewer.storage import ContentLibrary, GoogleStorageContentLibrary


class CacheVideoOpt(BaseModel):
    cache_name: str


class ApplicationLang:

    content_library: ContentLibrary

    def __init__(self):
        self.content_library = GoogleStorageContentLibrary()

    def cache_video(self, video: UploadFile) -> CacheVideoOpt:
        assert video.filename is not None, "video must have a filename"
        assert video.filename.endswith(".mp4"), "video must have a filename"
        cache_name = self.content_library.cache_file(
            local_filename=video.filename,
        )
        return CacheVideoOpt(cache_name=cache_name)


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

        @self.api.post("/content/upload-video")
        def cache_video(video: UploadFile) -> CacheVideoOpt:
            return self.lang.cache_video(video)

        return self

    def serve(self, port: int) -> None:
        uvicorn.run(self.api, host="0.0.0.0", port=port)


def main(port: int = 9384) -> None:
    RemoteApplicationLang.with_mapped_routes().serve(port=port)


if __name__ == "__main__":
    fire.Fire(main)
