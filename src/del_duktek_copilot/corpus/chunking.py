"""Page-aware, layout-preserving chunking for extracted PDF text."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .preprocessing import DocumentMetadata, ExtractedPage

DEFAULT_MAX_CHARS = 1200
DEFAULT_OVERLAP_CHARS = 150


@dataclass(frozen=True)
class Chunk:
    text: str
    metadata: dict[str, str | int]

    def to_record(self) -> dict[str, object]:
        """Return the JSONL record expected by downstream embedding adapters."""
        return {"text": self.text, "metadata": self.metadata}


def _split_long_line(line: str, max_chars: int) -> list[str]:
    parts: list[str] = []
    remaining = line
    while len(remaining) > max_chars:
        split_at = remaining.rfind(" ", 1, max_chars + 1)
        if split_at < 1:
            split_at = max_chars
        parts.append(remaining[:split_at])
        remaining = remaining[split_at:]
    parts.append(remaining)
    return parts


def _prepare_lines(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        if len(line) > max_chars:
            lines.extend(_split_long_line(line, max_chars))
        else:
            lines.append(line)
    return lines


def chunk_page(
    page: ExtractedPage,
    document: DocumentMetadata,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
    first_chunk_index: int = 1,
) -> list[Chunk]:
    """Split one page at line boundaries and repeat a short line-aligned overlap."""
    if max_chars < 1:
        raise ValueError("max_chars must be a positive integer")
    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("overlap_chars must be non-negative and smaller than max_chars")
    if first_chunk_index < 1:
        raise ValueError("first_chunk_index must be at least 1")
    if not page.text.strip():
        raise ValueError(f"Page {page.page_number} contains no text")

    lines = _prepare_lines(page.text, max_chars)
    chunks: list[Chunk] = []
    start = 0
    previous_end = 0

    while start < len(lines):
        end = start
        size = 0
        while end < len(lines):
            line_size = len(lines[end]) + (1 if end > start else 0)
            if end > start and size + line_size > max_chars:
                break
            size += line_size
            end += 1

        if end <= previous_end:
            start = previous_end
            continue

        chunk_text = "\n".join(lines[start:end]).strip("\n")
        if chunk_text:
            chunk_index = first_chunk_index + len(chunks)
            chunk_id = (
                f"{document.document_id}-p{page.page_number:03d}"
                f"-c{chunk_index:04d}"
            )
            chunks.append(
                Chunk(
                    text=chunk_text,
                    metadata={
                        "document_id": document.document_id,
                        "source": document.source,
                        "category": document.category,
                        "source_status": document.source_status,
                        "authority_status": document.authority_status,
                        "source_file": document.source_file,
                        "document_title": document.title,
                        "page_number": page.page_number,
                        "chunk_index": chunk_index,
                        "chunk_id": chunk_id,
                    },
                )
            )

        previous_end = end
        if end >= len(lines):
            break

        previous_start = start
        start = end
        overlap_size = 0
        while start > previous_start:
            line_size = len(lines[start - 1]) + (1 if overlap_size else 0)
            if overlap_size and overlap_size + line_size > overlap_chars:
                break
            start -= 1
            overlap_size += line_size
            if overlap_size >= overlap_chars:
                break
        if start == previous_start:
            start = end

    return chunks
