import time
from unittest import TestCase

from fastapi import UploadFile

from focus_group_reviewer.api import ApplicationLang


class TestApplicationLang(TestCase):

    lang: ApplicationLang

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = ApplicationLang()

    def test_video_cache(self):
        """
        Elapsed time ~2.8s minutes.
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
