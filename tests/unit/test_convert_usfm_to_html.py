import os
import pytest

from document.domain import parsing, model
from document.utils.file_utils import read_file

USFM_RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "test_data",
)


# @pytest.mark.datafiles(USFM_RESOURCE_DIR)
# def test_convert_usfm_to_html(datafiles: list[str]) -> None:
def test_convert_usfm_to_html() -> None:
    # usfm_resource_dir = str(datafiles)
    with open(f"{USFM_RESOURCE_DIR}/50-EPH.usfm", "r") as fi:
        content = fi.read()
        parsing.convert_usfm_chapter_to_html(content, "working_temp/foo")
        with open("working_temp/foo.html") as fi_result:
            result_content = fi_result.read()
            assert 'class="verse"' in result_content
