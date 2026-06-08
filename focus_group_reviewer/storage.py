import abc
import os
import time

from google import genai
from google.genai import types
from overrides import override


class ContentLibrary(abc.ABC):

    @abc.abstractmethod
    def cache_file(self, local_filename: str) -> str:
        """Caches the uploaded content for LLM calls. Returns the cache name."""

    @abc.abstractmethod
    def peek_cache(self, cache_name: str) -> int | None:
        """
        Checks whether the file was successfully cached in the content library.

        Returns token count of the cache if found.
        """


class GoogleStorageContentLibrary(ContentLibrary):

    genai_client: genai.Client
    bucket_name: str

    def __init__(self):
        self.genai_client = genai.Client(
            project=os.environ["GCP_PROJECT_ID"],
            location=os.environ["GCS_LOCATION"],
        )

    @override
    def cache_file(self, local_filename: str) -> str:
        print(f"Creating cache for '{local_filename}'...")
        video_file = self.genai_client.files.upload(
            file=local_filename,
            config=types.UploadFileConfig(mime_type="video/mp4"),
        )
        self._wait_for_processing(video_file)

        opt = self.genai_client.caches.create(
            model="gemini-3.5-flash",
            config=types.CreateCachedContentConfig(
                contents=[video_file],
                ttl="3600s",
            ),
        )
        assert opt.name is not None
        return opt.name

    @override
    def peek_cache(self, cache_name: str) -> int | None:
        total_token_count = None
        for cache in self.genai_client.caches.list():
            if cache.name == cache_name:
                assert cache.usage_metadata is not None
                total_token_count = cache.usage_metadata.total_token_count
                break
        return total_token_count

    def _wait_for_processing(self, file: types.File) -> None:
        if file.state == types.FileState.ACTIVE:
            print(f"File '{file.name}' processing completed.")
            return
        assert file.name is not None
        print(f"Waiting for '{file.name}' to be processed...")
        file = self.genai_client.files.get(name=file.name)
        time.sleep(1)
        self._wait_for_processing(file)
