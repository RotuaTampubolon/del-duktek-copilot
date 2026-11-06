"""PDF extraction, text cleanup, corpus metadata, and JSONL generation."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from .chunking import (
    DEFAULT_MAX_CHARS,
    DEFAULT_OVERLAP_CHARS,
    Chunk,
    chunk_page,
)

AUTHORITY_STATUS = "referensi eksternal; bukan SOP resmi IT Del"


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class DocumentMetadata:
    document_id: str
    source_file: str
    title: str
    source: str
    category: str
    source_status: str
    authority_status: str
    page_start: int
    page_end: int


def clean_text(text: str) -> str:
    """Normalize character encoding and line endings without flattening layout."""
    normalized = unicodedata.normalize("NFC", text)
    normalized = normalized.replace("\u00a0", " ").replace("\u00ad", "")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace("\x0c", "\n")
    normalized = "".join(
        character
        for character in normalized
        if character in "\n\t" or unicodedata.category(character) != "Cc"
    )
    normalized = "\n".join(line.rstrip() for line in normalized.split("\n"))
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip("\n")


def extract_pdf_pages(pdf_path: Path) -> list[ExtractedPage]:
    """Extract and clean each page separately using pypdf's layout mode."""
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    extracted: list[ExtractedPage] = []
    for page_number, pdf_page in enumerate(reader.pages, start=1):
        text = clean_text(pdf_page.extract_text(extraction_mode="layout") or "")
        if not text:
            raise ValueError(
                f"No extractable text on page {page_number} of {pdf_path.name}"
            )
        extracted.append(ExtractedPage(page_number=page_number, text=text))
    return extracted


def load_manifest(manifest_path: Path) -> list[DocumentMetadata]:
    """Load and validate the explicit allowlist derived from the corpus audit."""
    raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if raw_manifest.get("schema_version") != 1:
        raise ValueError("Unsupported corpus manifest schema_version")

    documents: list[DocumentMetadata] = []
    seen_ids: set[str] = set()
    seen_ranges: dict[str, list[tuple[int, int]]] = {}
    for item in raw_manifest.get("documents", []):
        required_fields = (
            "document_id",
            "source_file",
            "title",
            "source",
            "category",
            "source_status",
            "page_start",
            "page_end",
        )
        missing_fields = [field for field in required_fields if field not in item]
        if missing_fields:
            raise ValueError(f"Manifest entry is missing fields: {missing_fields}")

        source_file = item["source_file"]
        if not isinstance(source_file, str) or Path(source_file).name != source_file:
            raise ValueError(f"source_file must be a filename: {source_file!r}")
        document_id = item["document_id"]
        if not isinstance(document_id, str) or not document_id.strip():
            raise ValueError("document_id must be a non-empty string")
        if document_id in seen_ids:
            raise ValueError(f"Duplicate document_id: {document_id}")
        seen_ids.add(document_id)

        page_start = item["page_start"]
        page_end = item["page_end"]
        if (
            not isinstance(page_start, int)
            or isinstance(page_start, bool)
            or not isinstance(page_end, int)
            or isinstance(page_end, bool)
            or page_start < 1
            or page_end < page_start
        ):
            raise ValueError(f"Invalid page range for {document_id}")

        ranges = seen_ranges.setdefault(source_file, [])
        if any(page_start <= end and start <= page_end for start, end in ranges):
            raise ValueError(f"Overlapping page ranges for {source_file}")
        ranges.append((page_start, page_end))

        if item["source_status"] != "Layak":
            raise ValueError(f"Document is not audit-approved: {source_file}")
        if item.get("authority_status", AUTHORITY_STATUS) != AUTHORITY_STATUS:
            raise ValueError(f"Unexpected authority_status for {document_id}")

        documents.append(
            DocumentMetadata(
                document_id=document_id,
                source_file=source_file,
                title=item["title"],
                source=item["source"],
                category=item["category"],
                source_status=item["source_status"],
                authority_status=AUTHORITY_STATUS,
                page_start=page_start,
                page_end=page_end,
            )
        )

    if not documents:
        raise ValueError("Corpus manifest contains no approved documents")
    return documents


def build_chunks(
    data_dir: Path,
    documents: list[DocumentMetadata],
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> list[Chunk]:
    """Create chunks only for files and page ranges named in the manifest."""
    pages_by_file: dict[str, list[ExtractedPage]] = {}
    chunks: list[Chunk] = []

    for document in documents:
        if document.source_file not in pages_by_file:
            pages_by_file[document.source_file] = extract_pdf_pages(
                data_dir / document.source_file
            )
        pages = pages_by_file[document.source_file]
        if document.page_end > len(pages):
            raise ValueError(
                f"{document.document_id} requests page {document.page_end}, "
                f"but {document.source_file} has {len(pages)} pages"
            )

        chunk_index = 1
        for page_number in range(document.page_start, document.page_end + 1):
            page = pages[page_number - 1]
            page_chunks = chunk_page(
                page,
                document,
                max_chars=max_chars,
                overlap_chars=overlap_chars,
                first_chunk_index=chunk_index,
            )
            chunks.extend(page_chunks)
            chunk_index += len(page_chunks)
    return chunks


def write_jsonl(chunks: list[Chunk], output_path: Path) -> None:
    """Write deterministic UTF-8 JSONL records without modifying source PDFs."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
        for chunk in chunks:
            output_file.write(
                json.dumps(chunk.to_record(), ensure_ascii=False, sort_keys=True)
            )
            output_file.write("\n")


def preprocess_corpus(
    data_dir: Path,
    manifest_path: Path,
    output_path: Path,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> list[Chunk]:
    documents = load_manifest(manifest_path)
    chunks = build_chunks(
        data_dir,
        documents,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
    )
    write_jsonl(chunks, output_path)
    return chunks


def main() -> None:
    repository_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description="Preprocess the audited PDF corpus.")
    parser.add_argument("--data-dir", type=Path, default=repository_root / "data")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repository_root / "docs/corpus-inventory/corpus-manifest.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repository_root / "data/processed/corpus_chunks.jsonl",
    )
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    parser.add_argument("--overlap-chars", type=int, default=DEFAULT_OVERLAP_CHARS)
    arguments = parser.parse_args()

    chunks = preprocess_corpus(
        arguments.data_dir,
        arguments.manifest,
        arguments.output,
        max_chars=arguments.max_chars,
        overlap_chars=arguments.overlap_chars,
    )
    print(f"Generated {len(chunks)} chunks from the audit-approved corpus.")
    print(f"Output: {arguments.output}")


if __name__ == "__main__":
    main()
