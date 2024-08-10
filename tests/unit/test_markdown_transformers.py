import os

import mistune

import pytest

from document.domain import model
from document.markdown_transforms import markdown_transformer
from document.utils import tw_utils

EN_TW_RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "test_data",
    "en_tw-wa",
    "en_tw",
)

GU_TW_RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "test_data",
    "gu_tw",
    "gu_tw",
)


def test_remove_section() -> None:
    source = """# blah

## Flub:

Nullam eu ante vel est convallis dignissim.  Fusce suscipit, wisi nec facilisis facilisis, est dui fermentum leo, quis tempor ligula erat quis odio.  Nunc porta vulputate tellus.  Nunc rutrum turpis sed pede.  Sed bibendum.  Aliquam posuere.  Nunc aliquet, augue nec adipiscing interdum, lacus tellus malesuada massa, quis varius mi purus non odio.  Pellentesque condimentum, magna ut suscipit hendrerit, ipsum augue ornare nulla, non luctus diam neque sit amet urna.  Curabitur vulputate vestibulum lorem.  Fusce sagittis, libero non molestie mollis, magna orci ultrices dolor, at vulputate neque nulla lacinia eros.  Sed id ligula quis est convallis tempor.  Curabitur lacinia pulvinar nibh.  Nam a sapien.


## Picture of blah:

<a href="http://example.com"><img src="http://example.com/foo.png" ></a>

## Links:

Lorem ipsum dolor sit amet, consectetuer adipiscing elit.  Donec hendrerit tempor tellus.  Donec pretium posuere tellus.  Proin quam nisl, tincidunt et, mattis eget, convallis nec, purus.  Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.  Nulla posuere.  Donec vitae dolor.  Nullam tristique diam non turpis.  Cras placerat accumsan nulla.  Nullam rutrum.  Nam vestibulum accumsan nisl.


## Delete me:

* foo
* bar

## Keep me:

* Blatz

Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus."""

    source_expected = """# blah

## Flub:

Nullam eu ante vel est convallis dignissim.  Fusce suscipit, wisi nec facilisis facilisis, est dui fermentum leo, quis tempor ligula erat quis odio.  Nunc porta vulputate tellus.  Nunc rutrum turpis sed pede.  Sed bibendum.  Aliquam posuere.  Nunc aliquet, augue nec adipiscing interdum, lacus tellus malesuada massa, quis varius mi purus non odio.  Pellentesque condimentum, magna ut suscipit hendrerit, ipsum augue ornare nulla, non luctus diam neque sit amet urna.  Curabitur vulputate vestibulum lorem.  Fusce sagittis, libero non molestie mollis, magna orci ultrices dolor, at vulputate neque nulla lacinia eros.  Sed id ligula quis est convallis tempor.  Curabitur lacinia pulvinar nibh.  Nam a sapien.


## Keep me:

* Blatz

Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.\n"""

    source = markdown_transformer.remove_sections(
        source, ["Picture", "Links", "Delete me"]
    )
    assert source_expected == source


@pytest.mark.datafiles(EN_TW_RESOURCE_DIR)
def test_translation_word_link_alt(datafiles: list[str]) -> None:
    tw_resource_dir = str(datafiles)
    source = """## Translation Suggestions:

* It is important to translate the terms "apostle" and "disciple" in different ways.

(See also: [[rc://*/tw/dict/bible/kt/authority]], [[rc://*/tw/dict/bible/kt/disciple]])"""

    expected = """## Translation Suggestions:

* It is important to translate the terms "apostle" and "disciple" in different ways.\n\n, )\n"""
    resource_requests = [
        model.ResourceRequest(lang_code="en", resource_type="ulb", book_code="gen")
    ]
    translation_words_dict = tw_utils.translation_words_dict(tw_resource_dir)
    source = markdown_transformer.remove_sections(source)
    source = markdown_transformer.transform_tw_links(
        source, "en", resource_requests, translation_words_dict
    )
    assert expected == source


@pytest.mark.datafiles(GU_TW_RESOURCE_DIR)
def test_translation_word_link_alt_gu(datafiles: list[str]) -> None:
    tw_resource_dir = str(datafiles)
    source = """દ્રષ્ટાંતો એ એવીવાર્તાઓ છે જે નૈતિક પાઠો શીખવે છે. (જુઓ: [[rc://*/tw/dict/bible/kt/lawofmoses]])"""
    expected = """દ્રષ્ટાંતો એ એવીવાર્તાઓ છે જે નૈતિક પાઠો શીખવે છે. \n"""
    resource_requests = [
        model.ResourceRequest(lang_code="en", resource_type="ulb", book_code="gen")
    ]
    translation_words_dict = tw_utils.translation_words_dict(tw_resource_dir)
    source = markdown_transformer.remove_sections(source)
    source = markdown_transformer.transform_tw_links(
        source, "gu", resource_requests, translation_words_dict
    )
    assert expected == source


@pytest.mark.datafiles(GU_TW_RESOURCE_DIR)
def test_translation_note_link_gu(datafiles: list[str]) -> None:
    tw_resource_dir = str(datafiles)
    source = """* [ઉત્પત્તિ 4:18-19](rc://gu/tn/help/gen/04/18)
* [ઉત્પત્તિ 4:23-24](rc://gu/tn/help/gen/04/23)
* [લૂક 3:36-38](rc://gu/tn/help/luk/03/36)"""
    expected = """* ઉત્પત્તિ 4:18-19
* ઉત્પત્તિ 4:23-24
* લૂક 3:36-38\n"""
    resource_requests = [
        model.ResourceRequest(lang_code="en", resource_type="ulb", book_code="gen")
    ]
    source = markdown_transformer.remove_sections(source)
    source = markdown_transformer.transform_ta_and_tn_links(
        source, "en", resource_requests
    )
    assert expected == source
