"""
Audit Script – Corpus PDF Duktek IT Del
Milestone 3: Corpus Audit & Validation
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).parent.parent / "data"

# ── PDF extraction ──────────────────────────────────────────────────────────
def extract_with_pypdf(pdf_path: Path) -> dict:
    """Extract metadata and text using pypdf."""
    result = {
        "pages": 0,
        "pages_with_text": 0,
        "total_chars": 0,
        "pdf_version": "",
        "metadata": {},
        "sample_texts": [],   # first 500 chars per page (max 3 pages)
        "error": None,
        "issues": [],
    }
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        result["pages"] = len(reader.pages)
        meta = reader.metadata or {}
        result["metadata"] = {k: str(v) for k, v in meta.items() if v}

        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
                chars = len(text.strip())
                result["total_chars"] += chars
                if chars > 5:
                    result["pages_with_text"] += 1
                if i < 3 and chars > 0:
                    result["sample_texts"].append(text[:500].strip())
            except Exception as pe:
                result["issues"].append(f"page {i+1}: {pe}")

        # Check for garbled characters (common with bad font encoding)
        all_text = " ".join(result["sample_texts"])
        garbled = sum(1 for c in all_text if ord(c) > 0xFFFD or (0 < ord(c) < 32 and c not in "\n\r\t"))
        if garbled > 10:
            result["issues"].append(f"Possible garbled characters: {garbled} suspicious chars in first 3 pages")

    except Exception as e:
        result["error"] = str(e)
    return result


def get_file_hash(path: Path) -> str:
    """Compute MD5 hash of file."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_relevance(filename: str, sample_texts: list) -> dict:
    """
    Heuristically tag domain relevance based on filename and sample text.
    Returns dict of domain: bool.
    """
    combined = (filename + " " + " ".join(sample_texts)).lower()
    domains = {
        "helpdesk_tiket":      any(kw in combined for kw in ["helpdesk", "tiket", "ticket", "laporan", "pengaduan", "customer service"]),
        "troubleshooting_pc":  any(kw in combined for kw in ["troubleshoot", "komputer", "pc", "laptop", "hardware", "software", "os", "windows", "sistem operasi"]),
        "jaringan":            any(kw in combined for kw in ["jaringan", "network", "internet", "intranet", "koneksi", "bandwidth", "router", "switch", "wifi", "access point", "lan", "ping"]),
        "infrastruktur_it":    any(kw in combined for kw in ["infrastruktur", "server", "data center", "backup", "storage", "firewall", "pemeliharaan", "maintenance", "monitoring"]),
        "sop_layanan_it":      any(kw in combined for kw in ["sop", "standar operasional", "prosedur", "layanan", "service", "dukungan teknis", "it support"]),
    }
    return domains


# ── Main audit ──────────────────────────────────────────────────────────────
def run_audit():
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        print("ERROR: No PDF files found in", DATA_DIR)
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF file(s) in {DATA_DIR}\n")

    results = []
    hashes = {}

    for pdf_path in pdf_files:
        size_kb = pdf_path.stat().st_size / 1024
        file_hash = get_file_hash(pdf_path)
        is_duplicate = file_hash in hashes

        info = extract_with_pypdf(pdf_path)
        relevance = classify_relevance(pdf_path.name, info["sample_texts"])

        record = {
            "filename": pdf_path.name,
            "size_kb": round(size_kb, 1),
            "md5": file_hash,
            "is_duplicate": is_duplicate,
            "duplicate_of": hashes.get(file_hash, None),
            **info,
            "relevance": relevance,
        }

        if not is_duplicate:
            hashes[file_hash] = pdf_path.name

        results.append(record)
        status_icon = "OK" if not info["error"] else "ERR"
        print(f"{status_icon} {pdf_path.name}")
        print(f"   Size: {size_kb:.1f} KB | Pages: {info['pages']} | Pages w/ text: {info['pages_with_text']} | Chars: {info['total_chars']}")
        if info["error"]:
            print(f"   ERROR: {info['error']}")
        if info["issues"]:
            for iss in info["issues"]:
                print(f"   ISSUE: {iss}")
        if info["sample_texts"]:
            preview = info["sample_texts"][0][:200].replace("\n", " ")
            print(f"   Preview: {preview}")
        rel_tags = [k for k, v in relevance.items() if v]
        print(f"   Relevance tags: {rel_tags or ['(none)']}")
        if is_duplicate:
            print(f"   DUPLICATE of: {record['duplicate_of']}")
        print()

    # Save JSON for reference
    out_json = DATA_DIR.parent / "tmp" / "audit_results.json"
    out_json.parent.mkdir(exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        # Remove sample_texts from dump to keep it clean; save separately
        dump = []
        for r in results:
            d = dict(r)
            dump.append(d)
        json.dump(dump, f, ensure_ascii=False, indent=2)
    print(f"\nJSON results saved to: {out_json}")

    # Print summary table
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)
    print(f"{'#':<3} {'Filename':<65} {'Pages':>5} {'WithTxt':>7} {'Chars':>7} {'Dupe':>4}")
    print("-"*80)
    for i, r in enumerate(results, 1):
        dupe = "YES" if r["is_duplicate"] else ""
        name = r["filename"][:64]
        print(f"{i:<3} {name:<65} {r['pages']:>5} {r['pages_with_text']:>7} {r['total_chars']:>7} {dupe:>4}")

    total_pages = sum(r["pages"] for r in results)
    total_chars = sum(r["total_chars"] for r in results)
    readable = sum(1 for r in results if r["pages_with_text"] > 0)
    scan_only = sum(1 for r in results if r["pages"] > 0 and r["pages_with_text"] == 0)

    print("-"*80)
    print(f"{'TOTAL':<68} {total_pages:>5} {readable:>7} {total_chars:>7}")
    print(f"\nFiles with NO extractable text (scan/image PDFs): {scan_only}")
    print(f"Files with extractable text: {readable}")

    return results


if __name__ == "__main__":
    run_audit()
