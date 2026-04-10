#!/usr/bin/env python3
"""Generate src/mime_enum/mimetype.py from the upstream mimeData.json dataset
plus local additions in mimeDataExtras.json.

The pipeline reads like a book:

    1. load upstream + extras JSON
    2. validate extras can be merged without shadowing or conflict
    3. normalize merged data into Entry records and alias/ext lookup tables
    4. validate Python enum member names are unique
    5. render the target module
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

IN = Path("mimeData.json")
EXTRAS = Path("mimeDataExtras.json")
OUT = Path("src/mime_enum/mimetype.py")

# Convenient short aliases for commonly used verbose MIME types.
SIMPLE_ALIASES = {
    "APPLICATION_DOCX": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "APPLICATION_XLSX": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "APPLICATION_PPTX": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "APPLICATION_DOTX": "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
    "APPLICATION_XLTX": "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
    "APPLICATION_POTX": "application/vnd.openxmlformats-officedocument.presentationml.template",
    "APPLICATION_PPSX": "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
    "APPLICATION_SLDX": "application/vnd.openxmlformats-officedocument.presentationml.slide",
}


@dataclass(frozen=True)
class Entry:
    mime: str
    extensions: tuple[str, ...]


def main() -> None:
    upstream = json.loads(IN.read_text())
    extras = json.loads(EXTRAS.read_text()) if EXTRAS.exists() else []

    validate_extras(upstream, extras)
    entries, alias_to_target, ext_to_mime = normalize(upstream + extras)
    validate_member_names(entries)

    OUT.write_text(render_module(entries, alias_to_target, ext_to_mime))
    print(f"Wrote {OUT}")


# ---- validation ------------------------------------------------------------


def validate_extras(upstream: list[dict], extras: list[dict]) -> None:
    """Fail loud on duplicates, shadowing, or extension conflicts so the
    generator can't silently drop or override entries when merging."""
    if not extras:
        return
    _forbid_duplicate_extras(extras)
    _forbid_upstream_shadowing(upstream, extras)
    _forbid_extension_collisions(upstream, extras)


def _forbid_duplicate_extras(extras: list[dict]) -> None:
    names = [mime_name(item) for item in extras if mime_name(item)]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise ValueError(f"Duplicate entries inside {EXTRAS}: {dupes}")


def _forbid_upstream_shadowing(upstream: list[dict], extras: list[dict]) -> None:
    upstream_names = {mime_name(item) for item in upstream if mime_name(item)}
    extras_names = {mime_name(item) for item in extras if mime_name(item)}
    shadowed = sorted(extras_names & upstream_names)
    if shadowed:
        raise ValueError(
            f"Extras entries already exist upstream: {shadowed}. Remove them from {EXTRAS} or extend {IN} instead."
        )


def _forbid_extension_collisions(upstream: list[dict], extras: list[dict]) -> None:
    owner_by_ext: dict[str, str] = {}
    for item in upstream:
        for ext in file_types(item):
            owner_by_ext.setdefault(ext, mime_name(item))

    for item in extras:
        for ext in file_types(item):
            if ext in owner_by_ext:
                raise ValueError(
                    f"Extension {ext!r} in extras entry {mime_name(item)!r} "
                    f"is already claimed upstream by {owner_by_ext[ext]!r}."
                )


def validate_member_names(entries: list[Entry]) -> None:
    """Two MIME strings may sanitize to the same Python identifier
    (e.g. 'foo-bar' and 'foo.bar' both collapse to FOO_BAR), which would
    silently alias enum members or break class creation."""
    seen: dict[str, str] = {}
    for entry in entries:
        member = sanitize_member_name(entry.mime)
        if member in seen:
            raise ValueError(f"Member name {member!r} collides between {seen[member]!r} and {entry.mime!r}")
        seen[member] = entry.mime


# ---- normalization ---------------------------------------------------------


def normalize(
    items: list[dict],
) -> tuple[list[Entry], dict[str, str], dict[str, str]]:
    """Turn raw JSON items into Entry records plus alias and extension lookups.

    Entries are returned sorted by MIME for stable emission, while the
    extension→canonical-MIME resolution walks entries in first-seen order
    so that appending to mimeDataExtras.json yields a minimal diff.
    """
    extensions_by_mime: dict[str, set[str]] = {}
    aliases_by_mime: dict[str, set[str]] = defaultdict(set)

    for item in items:
        mime = mime_name(item)
        if not mime:
            continue
        extensions_by_mime.setdefault(mime, set()).update(file_types(item))
        aliases_by_mime[mime].update(aliases_of(item, mime))

    entries_in_order = [Entry(mime=mime, extensions=tuple(sorted(exts))) for mime, exts in extensions_by_mime.items()]

    ext_to_mime = _resolve_extension_owners(entries_in_order)
    alias_to_target = _invert_alias_map(aliases_by_mime)
    entries_sorted = sorted(entries_in_order, key=lambda e: e.mime)
    return entries_sorted, alias_to_target, ext_to_mime


def _invert_alias_map(aliases_by_mime: dict[str, set[str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for target, aliases in aliases_by_mime.items():
        for alias in aliases:
            result.setdefault(alias, target)  # first-write-wins on dup alias
    return result


def _resolve_extension_owners(entries: list[Entry]) -> dict[str, str]:
    candidates: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        for ext in entry.extensions:
            candidates[ext].append(entry.mime)
    return {ext: _choose_canonical(mimes) for ext, mimes in candidates.items()}


def _choose_canonical(mimes: list[str]) -> str:
    """When several MIME types share an extension, prefer a non-vendor one."""
    non_vendor = [m for m in mimes if "/vnd." not in m]
    return (non_vendor or mimes)[0]


# ---- rendering -------------------------------------------------------------


def render_module(
    entries: list[Entry],
    alias_to_target: dict[str, str],
    ext_to_mime: dict[str, str],
) -> str:
    lines: list[str] = list(MODULE_HEADER)
    lines += _render_members(entries)
    lines += _render_simple_aliases(entries)
    lines += _render_alias_dict(alias_to_target)
    lines += _render_ext_dict(ext_to_mime)
    return "\n".join(lines) + "\n"


def _render_members(entries: list[Entry]) -> list[str]:
    lines = [f"    {sanitize_member_name(e.mime)} = ('{e.mime}', {py_tuple(e.extensions)})" for e in entries]
    lines.append("")
    return lines


def _render_simple_aliases(entries: list[Entry]) -> list[str]:
    known = {e.mime for e in entries}
    out = ["    # Convenient aliases for commonly used MIME types with verbose names"]
    for alias_name, target_mime in sorted(SIMPLE_ALIASES.items()):
        if target_mime not in known:
            continue
        target_member = sanitize_member_name(target_mime)
        if alias_name == target_member:
            continue
        out.append(f"    {alias_name} = {target_member}")
    out.append("")
    return out


def _render_alias_dict(alias_to_target: dict[str, str]) -> list[str]:
    lines = ["_ALIASES: dict[str, MimeType] = {"]
    for alias, target in sorted(alias_to_target.items()):
        lines.append(f"    '{alias}': MimeType('{target}'),")
    lines += ["}", ""]
    return lines


def _render_ext_dict(ext_to_mime: dict[str, str]) -> list[str]:
    lines = ["_EXT_TO_MIME: dict[str, MimeType] = {"]
    for ext, mime in sorted(ext_to_mime.items()):
        lines.append(f"    '{ext}': MimeType('{mime}'),")
    lines += ["}", ""]
    return lines


# ---- JSON field helpers ----------------------------------------------------


def mime_name(item: dict) -> str:
    return str(item.get("name") or "").strip().lower()


def file_types(item: dict) -> list[str]:
    return [strip_dot(e) for e in item.get("fileTypes") or [] if e]


def aliases_of(item: dict, mime: str) -> set[str]:
    links = item.get("links") or {}
    result: set[str] = set()
    for key in ("deprecates", "alternativeTo"):
        for alias in links.get(key) or []:
            a = str(alias).strip().lower()
            if a and a != mime:
                result.add(a)
    return result


def strip_dot(ext: str) -> str:
    return ext.lstrip(".").lower()


def sanitize_member_name(mime: str) -> str:
    """'application/vnd.hp-jlyt' -> 'APPLICATION_VND_HP_JLYT'"""
    name = re.sub(r"[^A-Za-z0-9]+", "_", mime.upper()).strip("_")
    if not name or name[0].isdigit():
        name = "MIME_" + name
    return name


def py_tuple(items: tuple[str, ...]) -> str:
    if not items:
        return "()"
    if len(items) == 1:
        return f"('{items[0]}',)"  # note the trailing comma
    return "(" + ", ".join(f"'{e}'" for e in items) + ")"


# ---- static module template ------------------------------------------------

MODULE_HEADER: tuple[str, ...] = (
    "# Auto-generated by scripts/generate_mimetypes.py — DO NOT EDIT.",
    "# Data source: mimetype-io (https://github.com/patrickmccallum/mimetype-io)",
    "",
    "from __future__ import annotations",
    "from enum import StrEnum",
    "",
    "",
    "class MimeType(StrEnum):",
    '    """MIME type enumeration with associated file extensions.',
    "    ",
    "    Auto-generated enum containing standard MIME types as string values.",
    "    Each enum member has an associated `.extensions` attribute containing",
    "    a tuple of common file extensions for that MIME type.",
    "    ",
    "    The enum values are the official MIME type strings (e.g., 'application/json'),",
    "    and can be used directly as strings in HTTP headers, content-type detection,",
    "    and other applications.",
    "    ",
    "    Attributes:",
    "        extensions: Tuple of file extensions associated with this MIME type",
    "        ",
    "    Examples:",
    "        >>> MimeType.APPLICATION_JSON",
    "        'application/json'",
    "        >>> MimeType.APPLICATION_JSON.extensions",
    "        ('json',)",
    "        >>> str(MimeType.TEXT_HTML)",
    "        'text/html'",
    '    """',
    "",
    "    def __new__(cls, value: str, extensions: tuple[str, ...] = ()):  # type: ignore[override]",
    "        obj = str.__new__(cls, value)",
    "        obj._value_ = value",
    "        obj.extensions = extensions",
    "        return obj",
    "",
)


if __name__ == "__main__":
    main()
