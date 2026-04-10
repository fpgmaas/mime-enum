import mimetypes

from mime_enum import MimeType, try_parse


def test_mimetypes_guess_type_compatibility():
    """Test that stdlib mimetypes.guess_type matches our enum values."""
    test_cases = [
        ("test.json", MimeType.APPLICATION_JSON),
        ("test.html", MimeType.TEXT_HTML),
        ("test.pdf", MimeType.APPLICATION_PDF),
        ("test.css", MimeType.TEXT_CSS),
        ("test.js", MimeType.TEXT_JAVASCRIPT),
    ]

    for filename, expected_mime in test_cases:
        stdlib_type, _ = mimetypes.guess_type(filename)
        assert stdlib_type == str(expected_mime)


def test_mimetypes_guess_extension_compatibility():
    """Test that mimetypes.guess_extension works with our MIME types."""
    test_cases = [
        (MimeType.APPLICATION_JSON, ".json"),
        (MimeType.TEXT_HTML, ".html"),
        (MimeType.APPLICATION_PDF, ".pdf"),
    ]

    for mime_type, expected_ext in test_cases:
        guessed_ext = mimetypes.guess_extension(str(mime_type))
        assert guessed_ext == expected_ext


def test_mimetypes_office_format_aliases():
    """Test Office format aliases work with stdlib."""
    # Only test if stdlib recognizes these formats
    stdlib_type, _ = mimetypes.guess_type("document.docx")
    if stdlib_type:
        parsed_type = try_parse(stdlib_type)
        assert parsed_type is MimeType.APPLICATION_DOCX
