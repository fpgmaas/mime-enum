# src/mime_enum/api.py (or core.py)
from __future__ import annotations

import re
from pathlib import Path

# Import the generated enum + maps
from .mimetype import MimeType, _ALIASES, _EXT_TO_MIME

_PARAM_RE = re.compile(r"\s*;.*$")


def _strip_params(value: str) -> str:
    return _PARAM_RE.sub("", value).strip().lower()


def parse(value: str) -> MimeType:
    """Parse a MIME type string to a MimeType enum.
    
    Performs strict parsing with the following behavior:
    
    - Strips parameters (e.g., 'application/json; charset=utf-8' becomes 'application/json')
    - Normalizes known aliases to their canonical form
    - Case-insensitive matching
    - Raises ValueError for unknown MIME types
    
    Args:
        value: The MIME type string to parse (e.g., 'application/json')
        
    Returns:
        The corresponding MimeType enum value
        
    Raises:
        ValueError: If the MIME type is empty, malformed, or unknown
        
    Examples:
        >>> parse('application/json')
        MimeType.APPLICATION_JSON
        >>> parse('application/json; charset=utf-8')
        MimeType.APPLICATION_JSON
        >>> parse('text/json')  # alias normalization
        MimeType.APPLICATION_JSON
    """
    if not value:
        raise ValueError("Empty MIME string")
    core = _strip_params(value)
    if core in _ALIASES:
        return _ALIASES[core]
    try:
        return MimeType(core)
    except ValueError as exc:
        raise ValueError(f"Unknown MIME type: {value!r}") from exc


def try_parse(value: str) -> MimeType | None:
    """Parse a MIME type string, returning None for unknown types.
    
    Similar to parse() but returns None instead of raising ValueError
    for unknown or empty MIME type strings.
    
    Args:
        value: The MIME type string to parse (e.g., 'application/json')
        
    Returns:
        The corresponding MimeType enum value, or None if unknown/empty
        
    Examples:
        >>> try_parse('application/json')
        MimeType.APPLICATION_JSON
        >>> try_parse('unknown/type')
        None
        >>> try_parse('')
        None
    """
    if not value:
        return None
    core = _strip_params(value)
    if core in _ALIASES:
        return _ALIASES[core]
    try:
        return MimeType(core)
    except ValueError:
        return None


def from_extension(ext: str) -> MimeType | None:
    """Get MIME type from a file extension.
    
    Performs case-insensitive lookup of MIME types by file extension.
    Handles extensions with or without leading dot.
    
    Args:
        ext: File extension (e.g., 'json', '.json', 'PDF', '.PDF')
        
    Returns:
        The corresponding MimeType enum value, or None if extension is unknown
        
    Note:
        This function only looks at the file extension and does NOT examine
        actual file content. Files can have incorrect or missing extensions,
        making this method unreliable for security-critical applications.
        
        For content-based MIME type detection, consider using packages like:
        
        - `python-magic` (libmagic wrapper)
        - `filetype` (pure Python file type detection)
        
    Examples:
        >>> from_extension('json')
        MimeType.APPLICATION_JSON
        >>> from_extension('.pdf')
        MimeType.APPLICATION_PDF
        >>> from_extension('unknown')
        None
    """
    if not ext:
        return None

    token = ext.lstrip(".").lower()
    return _EXT_TO_MIME.get(token)


def from_path(path: str | Path) -> MimeType | None:
    """Get MIME type from a file path or filename.
    
    Extracts the file extension from the path and looks up the
    corresponding MIME type. Uses the last extension for compound
    extensions (e.g., 'file.tar.gz' uses '.gz').
    
    Args:
        path: File path or filename (str or Path object)
        
    Returns:
        The corresponding MimeType enum value, or None if no extension
        or unknown extension
        
    Warning:
        This function is purely extension-based and does NOT read or examine
        the actual file content. This can be unreliable because:
        
        - Files may have incorrect extensions (e.g., .txt file containing JSON)
        - Files may be renamed with wrong extensions
        - Files without extensions will return None
        - Malicious files can masquerade with fake extensions
        
        For accurate MIME type detection based on file signatures/magic bytes,
        use content-based detection libraries like `python-magic` or `filetype`.
        
    Examples:
        >>> from_path('/tmp/document.pdf')
        MimeType.APPLICATION_PDF
        >>> from_path('data.json')
        MimeType.APPLICATION_JSON
        >>> from_path('file_without_extension')
        None
    """
    if not path:
        return None

    p = Path(path)
    if not p.suffix:
        return None

    return from_extension(p.suffix)
