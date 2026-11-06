import json
from pathlib import Path

import pytest

from del_duktek_copilot.corpus import (
    DocumentMetadata,
    ExtractedPage,
    build_chunks,
    clean_text,
    chunk_page,
    extract_pdf_pages,
    load_manifest,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPOSITORY_ROOT / "data"
MANIFEST_PATH = REPOSITORY_ROOT / "docs/corpus-inventory/corpus-manifest.json"


def test_extract_pdf_pages_returns_page_numbered_layout_text():
    pages = extract_pdf_pages(
        DATA_DIR / "1.-Layanan-Helpdesk-Teknologi-Informasi-ok.pdf"
    )

    assert len(pages) == 3
    assert [page.page_number for page in pages] == [1, 2, 3]
    assert all(page.text.strip() for page in pages)
    assert "UNIVERSITAS GADJAH MADA" in pages[0].text
    assert "\n" in pages[0].text


def test_clean_text_preserves_structure_while_normalizing_whitespace():
    source = "  BAGIAN  \r\n\r\n\r\n1.\tLangkah\u00a0utama\x00\r\n | A     | B  \r\n"

    assert clean_text(source) == (
        "  BAGIAN\n\n1.\tLangkah utama\n | A     | B"
    )


def test_manifest_contains_only_audit_approved_documents_and_splits_sop_it():
    documents = load_manifest(MANIFEST_PATH)
    source_files = {document.source_file for document in documents}
    sop_it = [document for document in documents if document.source_file == "SOP-IT.pdf"]

    assert len(source_files) == 10
    assert len(documents) == 13
    assert sum(document.page_end - document.page_start + 1 for document in documents) == 43
    assert [(document.page_start, document.page_end) for document in sop_it] == [
        (1, 4),
        (5, 7),
        (8, 11),
        (12, 14),
    ]
    assert all(document.source_status == "Layak" for document in documents)


def test_manifest_rejects_non_layak_and_duplicate_document_id(tmp_path):
    item = {
        "document_id": "sample",
        "source_file": "sample.pdf",
        "title": "Sample",
        "source": "Sample source",
        "category": "helpdesk",
        "source_status": "Tidak layak",
        "page_start": 1,
        "page_end": 1,
    }
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"schema_version": 1, "documents": [item]}), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="not audit-approved"):
        load_manifest(manifest)

    item["source_status"] = "Layak"
    manifest.write_text(
        json.dumps({"schema_version": 1, "documents": [item, item]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate document_id"):
        load_manifest(manifest)


def test_chunk_page_preserves_page_metadata_and_line_aligned_overlap():
    document = DocumentMetadata(
        document_id="sample-document",
        source_file="sample.pdf",
        title="Sample SOP",
        source="Sample institution",
        category="helpdesk",
        source_status="Layak",
        authority_status="referensi eksternal; bukan SOP resmi IT Del",
        page_start=1,
        page_end=1,
    )
    text = "\n".join(f"Langkah {index:02d}: proses teknis." for index in range(1, 8))

    chunks = chunk_page(
        ExtractedPage(page_number=2, text=text),
        document,
        max_chars=55,
        overlap_chars=20,
    )

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 55 for chunk in chunks)
    assert chunks[0].text.splitlines()[-1] in chunks[1].text.splitlines()
    assert chunks[0].metadata == {
        "document_id": "sample-document",
        "source": "Sample institution",
        "category": "helpdesk",
        "source_status": "Layak",
        "authority_status": "referensi eksternal; bukan SOP resmi IT Del",
        "source_file": "sample.pdf",
        "document_title": "Sample SOP",
        "page_number": 2,
        "chunk_index": 1,
        "chunk_id": "sample-document-p002-c0001",
    }
    assert chunks[1].metadata["chunk_index"] == 2
    assert chunks[1].metadata["chunk_id"] == "sample-document-p002-c0002"


def test_chunk_page_validates_size_and_overlap():
    document = load_manifest(MANIFEST_PATH)[0]
    page = ExtractedPage(page_number=1, text="Heading\nA procedure.")

    with pytest.raises(ValueError, match="max_chars"):
        chunk_page(page, document, max_chars=0)
    with pytest.raises(ValueError, match="overlap_chars"):
        chunk_page(page, document, max_chars=10, overlap_chars=10)


def test_build_chunks_uses_only_manifest_files():
    documents = load_manifest(MANIFEST_PATH)[:1]

    chunks = build_chunks(DATA_DIR, documents)

    assert chunks
    assert {chunk.metadata["source_file"] for chunk in chunks} == {
        "1.-Layanan-Helpdesk-Teknologi-Informasi-ok.pdf"
    }
    assert {chunk.metadata["page_number"] for chunk in chunks} == {1, 2, 3}
