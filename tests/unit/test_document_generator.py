from typing import List

import os

from document import config
from document.domain import model
from document.domain import document_generator


def test_document_generator_for_english_with_interleaving_by_book() -> None:
    filename = "en-ulb-wa-jud_en-tn-wa-jud.html"
    filepath = os.path.join(config.get_output_dir(), filename)
    if os.path.isfile(filepath):
        os.remove(filepath)
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.book
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="jud"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="jud"
        )
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()
    assert doc_gen._document_request_key
    assert os.path.isfile(
        os.path.join(config.get_working_dir(), "en-ulb-wa-jud_en-tn-wa-jud.html")
    )


def test_document_generator_for_english_with_interleaving_by_verse() -> None:
    filename = "en-ulb-wa-jud_en-tn-wa-jud.html"
    filepath = os.path.join(config.get_output_dir(), filename)
    if os.path.isfile(filepath):
        os.remove(filepath)
    assembly_strategy_kind: model.AssemblyStrategyEnum = model.AssemblyStrategyEnum.verse
    resource_requests: List[model.ResourceRequest] = []
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="ulb-wa", resource_code="jud"
        )
    )
    resource_requests.append(
        model.ResourceRequest(
            lang_code="en", resource_type="tn-wa", resource_code="jud"
        )
    )
    document_request = model.DocumentRequest(
        assembly_strategy_kind=assembly_strategy_kind,
        resource_requests=resource_requests,
    )

    doc_gen = document_generator.DocumentGenerator(
        document_request, config.get_working_dir(), config.get_output_dir(),
    )
    doc_gen.run()
    assert doc_gen._document_request_key
    assert os.path.isfile(
        os.path.join(config.get_working_dir(), "en-ulb-wa-jud_en-tn-wa-jud.html")
    )