"""This module provides custom domain exceptions."""

from typing import final


@final
class InvalidDocumentRequestException(Exception):
    def __init__(self, message: str):
        self.message: str = message


@final
class ResourceAssetFileNotFoundError(Exception):
    """Raised when no supported resource asset URL could be found."""

    def __init__(self, message: str):
        self.message: str = message


@final
class NoSharedResourcesError(Exception):
    """Raised when two languages either have no shared books, no shared resource types, or both."""

    def __init__(self, message: str):
        self.message: str = message


@final
class NoBooksError(Exception):
    """Raised a language has no books."""

    def __init__(self, message: str):
        self.message: str = message


@final
class MissingChapterMarkerError(Exception):
    """Raised when USFM source chapter has no chapter, e.g., \\c 1, marker."""

    def __init__(self, message: str):
        self.message: str = message
