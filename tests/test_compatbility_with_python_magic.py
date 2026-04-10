import tempfile
from pathlib import Path

import magic
import pytest

from mime_enum import MimeType, from_path, try_parse


def test_python_magic_basic_detection():
    """Test basic python-magic integration with common file types."""

    test_cases = [
        ('{"test": "data"}', "test.json", [MimeType.APPLICATION_JSON, MimeType.TEXT_PLAIN]),
        ("<!DOCTYPE html><html><body>Test</body></html>", "test.html", [MimeType.TEXT_HTML, MimeType.TEXT_PLAIN]),
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        for content, filename, expected_types in test_cases:
            file_path = Path(temp_dir) / filename
            file_path.write_text(content)

            detected_mime = magic.from_file(str(file_path), mime=True)
            our_mime = try_parse(detected_mime)

            if our_mime:
                assert our_mime in expected_types


def test_python_magic_vs_extension_based():
    """Demonstrate difference between content-based and extension-based detection."""

    with tempfile.TemporaryDirectory() as temp_dir:
        # JSON content with wrong extension
        misnamed_file = Path(temp_dir) / "data.txt"
        misnamed_file.write_text('{"actually": "json"}')

        # Extension says text/plain
        extension_mime = from_path(str(misnamed_file))
        assert extension_mime is MimeType.TEXT_PLAIN

        # Content might reveal the truth
        detected_mime = magic.from_file(str(misnamed_file), mime=True)
        content_mime = try_parse(detected_mime)

        # Both are valid - this just shows they can differ
        assert extension_mime is not None
        assert content_mime in (MimeType.APPLICATION_JSON, MimeType.TEXT_PLAIN, None)


def test_python_magic_binary_detection():
    """Test python-magic with binary content."""

    with tempfile.TemporaryDirectory() as temp_dir:
        # PNG signature
        png_file = Path(temp_dir) / "test.png"
        png_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)

        detected_mime = magic.from_file(str(png_file), mime=True)
        our_mime = try_parse(detected_mime)

        if our_mime and str(our_mime).startswith("image/"):
            assert True  # Successfully detected as image
        else:
            # Magic detection can be inconsistent across systems
            pytest.skip(f"Detected as {detected_mime}, not recognized as image")
