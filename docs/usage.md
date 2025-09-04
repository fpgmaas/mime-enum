# Usage Guide

This guide provides detailed examples of how to use the `mime-enum` library for various common tasks.

## Basic Usage

### Accessing MIME Types

All MIME types are available as enum members:

```python
from mime_enum import MimeType

# Common MIME types
json_type = MimeType.APPLICATION_JSON
html_type = MimeType.TEXT_HTML
pdf_type = MimeType.APPLICATION_PDF
png_type = MimeType.IMAGE_PNG

# MIME types work as strings
print(json_type)  # "application/json"
assert json_type == "application/json"  # True
```

### File Extensions

Each MIME type includes associated file extensions:

```python
# Single extension
json_extensions = MimeType.APPLICATION_JSON.extensions
print(json_extensions)  # ("json",)

# Multiple extensions
html_extensions = MimeType.TEXT_HTML.extensions
print(html_extensions)  # ("html", "htm")

# Check if a MIME type supports an extension
if "pdf" in MimeType.APPLICATION_PDF.extensions:
    print("PDF files use application/pdf MIME type")
```

## Parsing MIME Type Strings

### Strict Parsing with `parse()`

Use `parse()` when you need to ensure the MIME type is valid:

```python
from mime_enum import parse

# Basic parsing
mime_type = parse("application/json")
print(mime_type)  # MimeType.APPLICATION_JSON

# Automatically strips parameters
mime_type = parse("text/html; charset=utf-8")
print(mime_type)  # MimeType.TEXT_HTML

# Case insensitive
mime_type = parse("IMAGE/PNG")
print(mime_type)  # MimeType.IMAGE_PNG

# Handles extra whitespace
mime_type = parse("  application/pdf  ")
print(mime_type)  # MimeType.APPLICATION_PDF
```

### Alias Normalization

The library automatically normalizes common MIME type aliases:

```python
# These aliases are normalized to their canonical forms
canonical = parse("text/json")  # → MimeType.APPLICATION_JSON
canonical = parse("application/javascript")  # → MimeType.TEXT_JAVASCRIPT
canonical = parse("image/jpg")  # → MimeType.IMAGE_JPEG
```

### Error Handling with `parse()`

```python
try:
    unknown = parse("application/unknown")
except ValueError as e:
    print(f"Unknown MIME type: {e}")
    # Output: Unknown MIME type: Unknown MIME type: 'application/unknown'

try:
    empty = parse("")
except ValueError as e:
    print(f"Empty input: {e}")
    # Output: Empty input: Empty MIME string
```

### Safe Parsing with `try_parse()`

Use `try_parse()` when you want to handle unknown types gracefully:

```python
from mime_enum import try_parse

# Returns None for unknown types instead of raising
result = try_parse("application/unknown")
print(result)  # None

# Returns None for empty strings
result = try_parse("")
print(result)  # None

# Works the same as parse() for valid types
result = try_parse("application/json")
print(result)  # MimeType.APPLICATION_JSON

# Useful in conditional logic
mime_type = try_parse(user_input)
if mime_type:
    print(f"Valid MIME type: {mime_type}")
else:
    print("Unknown or invalid MIME type")
```

## File Extension Lookups

> **Important:** The functions in this section only look at file extensions and do NOT examine actual file content. Files can have incorrect extensions, making this approach unreliable for security-critical applications. For content-based MIME type detection, use libraries like `python-magic` or `filetype`.

### Basic Extension Lookup

```python
from mime_enum import from_extension

# With or without leading dot
pdf_mime = from_extension("pdf")
print(pdf_mime)  # MimeType.APPLICATION_PDF

pdf_mime = from_extension(".pdf")
print(pdf_mime)  # MimeType.APPLICATION_PDF

# Case insensitive
json_mime = from_extension("JSON")
print(json_mime)  # MimeType.APPLICATION_JSON

# Returns None for unknown extensions
unknown = from_extension("unknown")
print(unknown)  # None
```

### Common Extensions

```python
# Web file types
html_mime = from_extension("html")  # MimeType.TEXT_HTML
css_mime = from_extension("css")    # MimeType.TEXT_CSS
js_mime = from_extension("js")      # MimeType.TEXT_JAVASCRIPT

# Document types
pdf_mime = from_extension("pdf")    # MimeType.APPLICATION_PDF
doc_mime = from_extension("doc")    # MimeType.APPLICATION_MSWORD
txt_mime = from_extension("txt")    # MimeType.TEXT_PLAIN

# Image types
png_mime = from_extension("png")    # MimeType.IMAGE_PNG
jpg_mime = from_extension("jpg")    # MimeType.IMAGE_JPEG
gif_mime = from_extension("gif")    # MimeType.IMAGE_GIF

# Archive types
zip_mime = from_extension("zip")    # MimeType.APPLICATION_ZIP
tar_mime = from_extension("tar")    # MimeType.APPLICATION_X_TAR
gz_mime = from_extension("gz")      # MimeType.APPLICATION_X_GZIP
```

## File Path Analysis

> **Note:** Path-based detection only uses file extensions and never reads file content. See the disclaimer above for limitations and alternatives.

### Basic Path Lookup

```python
from mime_enum import from_path
from pathlib import Path

# Works with string paths
mime_type = from_path("/home/user/document.pdf")
print(mime_type)  # MimeType.APPLICATION_PDF

# Works with Path objects
path = Path("data/config.json")
mime_type = from_path(path)
print(mime_type)  # MimeType.APPLICATION_JSON

# Works with relative paths
mime_type = from_path("../images/photo.png")
print(mime_type)  # MimeType.IMAGE_PNG

# Cross-platform paths
mime_type = from_path("C:\\Users\\Name\\file.html")  # Windows
print(mime_type)  # MimeType.TEXT_HTML
```

### Handling Files Without Extensions

```python
# Returns None for files without extensions
no_extension = from_path("/path/to/README")
print(no_extension)  # None

# Returns None for empty paths
empty_path = from_path("")
print(empty_path)  # None
```

### Complex File Extensions

The library currently uses the last extension for compound extensions:

```python
# For compound extensions, uses the last one
tar_gz = from_path("archive.tar.gz")
print(tar_gz)  # MimeType.APPLICATION_X_GZIP (from .gz)

# If you need more sophisticated handling, extract manually
from pathlib import Path
path = Path("document.tar.gz")
if path.name.endswith('.tar.gz'):
    # Handle as tar.gz specifically
    mime_type = MimeType.APPLICATION_X_TAR  # or your preferred handling
```
