# Interleaved Resource Generator API otherwise known as DOC

A DocumentRequest, composed of ResourceRequests, and a few other
values, is submitted to the API. The API then uses that information
to fetch assets associated with each Resource and interleaves said
assets according to the assembly strategy chosen. It also builds
interlinking between assets within the document as appropriate and
then translates the assets into an HTML document. Finally the API
generates a PDF, ePub, or Docx from the HTML document if requested.

Each Resource is composed of lang_code, resource_type, and
resource_code.

There are over hundreds lang_codes, several different resource_types, and
at least 66 resource_codes.

There are a few different assembly strategies available and a few
layout strategies available.

In this way, the API can produce multi-language, multi-book,
multi-resource PDFs assembled according to the resources, assembly
strategy, and assembly laytout combinations chosen.
