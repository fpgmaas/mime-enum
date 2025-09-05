# mime-enum

[![Release](https://img.shields.io/github/v/release/fpgmaas/mime-enum)](https://img.shields.io/github/v/release/fpgmaas/mime-enum)
[![Build status](https://img.shields.io/github/actions/workflow/status/fpgmaas/mime-enum/main.yml?branch=main)](https://github.com/fpgmaas/mime-enum/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/fpgmaas/mime-enum/branch/main/graph/badge.svg)](https://codecov.io/gh/fpgmaas/mime-enum)
[![License](https://img.shields.io/github/license/fpgmaas/mime-enum)](https://img.shields.io/github/license/fpgmaas/mime-enum)

**A type-safe Python library for working with MIME types and file extensions.**

The `mime-enum` package provides a comprehensive enumeration of MIME types with their associated file extensions. It offers a clean, type-safe API for parsing MIME type strings, looking up MIME types by file extension, and working with file paths.


## Installation

Install using pip:

```bash
pip install mime-enum
```

Or using uv:

```bash
uv add mime-enum
```

## Quick Start

The `mime-enum` library provides three key capabilities: type-safe MIME type access, flexible string parsing, and file extension lookups.

### Type-Safe MIME Types

Access MIME types as strongly-typed enum values with full IDE support:

```python
from mime_enum import MimeType

# Enum values work as strings with autocompletion and type checking
json_mime = MimeType.APPLICATION_JSON
print(json_mime)  # "application/json"
print(json_mime.extensions)  # ("json",)

```

### Convenient Aliases

For commonly used MIME types with verbose names, convenient aliases are provided:

```python
# Microsoft Office formats - use short aliases instead of verbose names
docx = MimeType.APPLICATION_DOCX  # vs APPLICATION_VND_OPENXMLFORMATS_OFFICEDOCUMENT_WORDPROCESSINGML_DOCUMENT
xlsx = MimeType.APPLICATION_XLSX  # vs APPLICATION_VND_OPENXMLFORMATS_OFFICEDOCUMENT_SPREADSHEETML_SHEET
pptx = MimeType.APPLICATION_PPTX  # vs APPLICATION_VND_OPENXMLFORMATS_OFFICEDOCUMENT_PRESENTATIONML_PRESENTATION

# String representation shows the full MIME type
print(docx)  # "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
print(xlsx)  # "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
print(pptx)  # "application/vnd.openxmlformats-officedocument.presentationml.presentation"

# All aliases point to the same enum instances
assert MimeType.APPLICATION_DOCX is MimeType.APPLICATION_VND_OPENXMLFORMATS_OFFICEDOCUMENT_WORDPROCESSINGML_DOCUMENT

# Available aliases: DOCX, XLSX, PPTX, DOTX, XLTX, POTX, PPSX, SLDX
```

### Flexible String Parsing

Parse real-world MIME type strings with automatic parameter stripping and alias normalization:

```python
from mime_enum import parse, try_parse

# Strips parameters automatically
mime_type = parse("application/json; charset=utf-8")
print(mime_type)  # MimeType.APPLICATION_JSON

# Normalizes common aliases to canonical forms
canonical = parse("text/json")  # → MimeType.APPLICATION_JSON
canonical = parse("application/javascript")  # → MimeType.TEXT_JAVASCRIPT

# Safe parsing returns None instead of raising exceptions
unknown = try_parse("application/unknown")
print(unknown)  # None
```

### File Extension Lookups

Detect MIME types from file extensions and paths:

```python
from mime_enum import from_extension, from_path

# Look up by extension (with or without dot, case-insensitive)
pdf_mime = from_extension(".pdf")  # MimeType.APPLICATION_PDF
json_mime = from_extension("JSON")  # MimeType.APPLICATION_JSON

# Detect from complete file paths
mime_type = from_path("/path/to/document.pdf")  # MimeType.APPLICATION_PDF
```

> **Note:** These functions only examine file extensions, not actual file content. For content-based detection, consider `python-magic` or `filetype` packages.

For detailed usage examples, see the [Usage Guide](usage.md).

For complete API documentation, see the [API Reference](api.md).
