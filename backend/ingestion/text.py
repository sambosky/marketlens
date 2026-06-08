"""Text utilities for ingestion: HTML→text and chunking."""

from __future__ import annotations

import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t\r\f\v]+")
_NL_RE = re.compile(r"\n{3,}")
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_HEAD_RE = re.compile(r"<head\b[^>]*>.*?</head>", re.IGNORECASE | re.DOTALL)
# Inline-XBRL hidden/header blocks carry a large dump of machine-readable facts
# that pollute the prose — drop them before stripping tags.
_IX_BLOCK_RE = re.compile(r"<ix:(header|hidden)\b[^>]*>.*?</ix:\1>", re.IGNORECASE | re.DOTALL)
# Leftover XBRL qnames (us-gaap:Foo, nvda:Bar), dimension members, padded ids.
_XBRL_QNAME_RE = re.compile(r"\b[A-Za-z][\w-]*:[A-Za-z][\w-]+\b")
_XBRL_MEMBER_RE = re.compile(r"\b[A-Za-z0-9]+(?:Member|Axis|Domain)\b")
_PADDED_ID_RE = re.compile(r"\b0\d{6,}\b")


def _strip_xbrl_noise(text: str) -> str:
    text = _XBRL_QNAME_RE.sub(" ", text)
    text = _XBRL_MEMBER_RE.sub(" ", text)
    text = _PADDED_ID_RE.sub(" ", text)
    return text


def html_to_text(raw: str) -> str:
    """Cheap HTML→text (no bs4) good enough for embeddings, with inline-XBRL
    noise stripped (modern SEC filings are inline-XBRL)."""
    text = _HEAD_RE.sub(" ", raw)
    text = _SCRIPT_STYLE_RE.sub(" ", text)
    text = _IX_BLOCK_RE.sub(" ", text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|tr|h[1-6]|li)>", "\n", text, flags=re.IGNORECASE)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text).replace("\xa0", " ")
    text = _strip_xbrl_noise(text)
    text = _WS_RE.sub(" ", text)
    text = _NL_RE.sub("\n\n", text)
    return text.strip()


def chunk_text(text: str, *, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    """Split text into overlapping character windows on whitespace boundaries."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            # back off to the last whitespace to avoid cutting mid-word
            space = text.rfind(" ", start + overlap, end)
            if space != -1 and space > start:
                end = space
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks
