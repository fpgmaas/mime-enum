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
docx_mime = from_extension("docx")  # MimeType.APPLICATION_DOCX
xlsx_mime = from_extension("xlsx")  # MimeType.APPLICATION_XLSX
pptx_mime = from_extension("pptx")  # MimeType.APPLICATION_PPTX
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

## Convenient Aliases

### Overview

For MIME types with particularly verbose names, the library provides convenient aliases that point to the exact same enum instances. These aliases improve code readability and reduce typing while maintaining full type safety.

### Available Aliases

The library currently provides aliases for Microsoft Office Open XML formats:

```python
from mime_enum import MimeType

# Word Processing
MimeType.APPLICATION_DOCX    # Word document
MimeType.APPLICATION_DOTX    # Word template

# Spreadsheets
MimeType.APPLICATION_XLSX    # Excel spreadsheet
MimeType.APPLICATION_XLTX    # Excel template

# Presentations
MimeType.APPLICATION_PPTX    # PowerPoint presentation
MimeType.APPLICATION_POTX    # PowerPoint template
MimeType.APPLICATION_PPSX    # PowerPoint slideshow
MimeType.APPLICATION_SLDX    # PowerPoint slide
```

### Using Aliases

Aliases work identically to their verbose counterparts:

```python
# These are the exact same objects
docx_alias = MimeType.APPLICATION_DOCX
docx_full = MimeType.APPLICATION_VND_OPENXMLFORMATS_OFFICEDOCUMENT_WORDPROCESSINGML_DOCUMENT
assert docx_alias is docx_full  # True

# String representation is identical
print(docx_alias)  # "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
print(docx_full)   # "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

# Extensions are the same
print(docx_alias.extensions)  # ("docx",)
print(docx_full.extensions)   # ("docx",)
```

### Aliases in Parsing and Lookups

Aliases work seamlessly with all library functions:

```python
from mime_enum import parse, from_extension, from_path

# Extension lookup returns the alias instance
docx_mime = from_extension("docx")
print(docx_mime is MimeType.APPLICATION_DOCX)  # True

# Path lookup also returns the alias
docx_path = from_path("/documents/report.docx")
print(docx_path is MimeType.APPLICATION_DOCX)  # True

# Parsing the full MIME string returns the alias
parsed = parse("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
print(parsed is MimeType.APPLICATION_DOCX)  # True
```

### Benefits of Aliases

1. **Improved Readability**: `APPLICATION_DOCX` is much easier to read than `APPLICATION_VND_OPENXMLFORMATS_OFFICEDOCUMENT_WORDPROCESSINGML_DOCUMENT`

2. **Less Typing**: Significantly shorter to type and autocomplete

3. **Same Functionality**: All aliases point to the exact same enum instances, so they work identically in every context

4. **IDE Support**: Full autocompletion and type checking support

### Example: Working with Office Documents

```python
from mime_enum import MimeType, from_extension

def process_office_document(file_path: str):
    mime_type = from_extension(file_path)

    if mime_type is MimeType.APPLICATION_DOCX:
        return "Processing Word document"
    elif mime_type is MimeType.APPLICATION_XLSX:
        return "Processing Excel spreadsheet"
    elif mime_type is MimeType.APPLICATION_PPTX:
        return "Processing PowerPoint presentation"
    else:
        return "Unknown office document type"

# Usage
result = process_office_document("report.docx")
print(result)  # "Processing Word document"
```
