import pytest

from mime_enum import (
    MimeType,
    from_extension,
    from_path,
    parse,
    try_parse,
)
from mime_enum.mimetype import _EXT_TO_MIME

# -------------------------
# Basic enum semantics
# -------------------------


def test_strenum_equality_and_str():
    assert MimeType.APPLICATION_JSON == "application/json"
    assert str(MimeType.TEXT_HTML) == "text/html"


def test_extensions_are_tuples_not_strings():
    """
    Guard-rail: the generator must emit tuples like ('ez',) not ('ez').
    If it emits plain strings, this will fail.
    """
    for mt in MimeType:
        assert isinstance(mt.extensions, tuple), f"{mt} .extensions should be tuple, got {type(mt.extensions)}"


# -------------------------
# parse() & try_parse()
# -------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        ("application/json", MimeType.APPLICATION_JSON),
        ("application/json; charset=UTF-8", MimeType.APPLICATION_JSON),  # params stripped
        (" text/html ; charset=iso-8859-1 ", MimeType.TEXT_HTML),  # whitespace + case
        ("application/javascript", MimeType.TEXT_JAVASCRIPT),  # alias -> canonical
        ("text/json", MimeType.APPLICATION_JSON),  # alias -> canonical
    ],
)
def test_parse_normalizes_and_strips_params(value, expected):
    assert parse(value) is expected


@pytest.mark.parametrize("value", ["", "application/does-not-exist", "image/unknown-type"])
def test_try_parse_unknown_returns_none(value):
    assert try_parse(value) is None


def test_parse_raises_on_unknown():
    with pytest.raises(ValueError):
        parse("application/totally-unknown")


# -------------------------
# Extension lookups
# -------------------------


@pytest.mark.parametrize(
    "ext, expected",
    [
        ("json", MimeType.APPLICATION_JSON),
        (".json", MimeType.APPLICATION_JSON),
        ("JSON", MimeType.APPLICATION_JSON),
        ("JsOn", MimeType.APPLICATION_JSON),
    ],
)
def test_from_extension_basic(ext, expected):
    assert from_extension(ext) is expected


def test_from_extension_compound_key_supported_when_in_map():
    # Your _EXT_TO_MIME includes a compound key "abw.gz" -> application/x-abiword
    assert "abw.gz" in _EXT_TO_MIME
    assert from_extension("abw.gz") is MimeType.APPLICATION_X_ABIWORD


# -------------------------
# Path lookups
# -------------------------


@pytest.mark.parametrize(
    "path, expected",
    [
        ("/tmp/report.PDF", MimeType.APPLICATION_PDF),  # noqa: S108 case-insensitive suffix
        ("C:\\x\\y\\z\\file.html", MimeType.TEXT_HTML),  # windows-ish path
        ("archive.tgz", MimeType.APPLICATION_X_GZIP),  # simple suffix, no compound logic
    ],
)
def test_from_path_simple_suffix(path, expected):
    assert from_path(path) is expected


def test_from_path_on_compound_suffix_current_behavior():
    """
    Current implementation uses Path.suffix (single suffix).
    For 'doc.abw.gz' this resolves to '.gz', so we expect gzip, NOT x-abiword.
    If you later add compound-suffix support, update this test accordingly.
    """
    assert from_path("doc.abw.gz") is MimeType.APPLICATION_X_GZIP


# -------------------------
# Map integrity (spot checks)
# -------------------------


def test_ext_map_contains_expected_examples():
    assert _EXT_TO_MIME["pdf"] is MimeType.APPLICATION_PDF
    assert _EXT_TO_MIME["zip"] in (MimeType.APPLICATION_ZIP, MimeType.APPLICATION_X_ZIP_COMPRESSED)
    assert _EXT_TO_MIME["md"] is MimeType.TEXT_MARKDOWN
    assert _EXT_TO_MIME["png"] is MimeType.IMAGE_PNG
    # sanity for alias-paired types living together
    assert "xhtml" in _EXT_TO_MIME
    assert _EXT_TO_MIME["xhtml"] is MimeType.APPLICATION_XHTML_XML
