"""
Deep text extraction for corpus audit - Duktek IT Del
Extracts first 2000 chars from ALL pages per document for manual analysis.
"""
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).parent.parent / "data"


def deep_extract(pdf_path: Path) -> dict:
    import pypdf
    result = {"filename": pdf_path.name, "pages": [], "error": None}
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        meta = reader.metadata or {}
        result["metadata"] = {k: str(v) for k, v in meta.items() if v}
        result["total_pages"] = len(reader.pages)
        for i, page in enumerate(reader.pages):
            try:
                text = (page.extract_text() or "").strip()
            except Exception as e:
                text = f"[ERROR extracting page: {e}]"
            result["pages"].append({
                "page_num": i + 1,
                "chars": len(text),
                "text": text[:2500]  # first 2500 chars
            })
    except Exception as e:
        result["error"] = str(e)
    return result


if __name__ == "__main__":
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))
    print(f"Deep extracting {len(pdf_files)} PDFs...\n")
    
    all_data = []
    for pdf_path in pdf_files:
        print(f"--- {pdf_path.name} ---")
        data = deep_extract(pdf_path)
        all_data.append(data)
        for p in data.get("pages", []):
            if p["chars"] > 10:
                print(f"  [Page {p['page_num']}] ({p['chars']} chars)")
                print(p["text"][:800])
                print()
        if data.get("error"):
            print(f"  ERROR: {data['error']}")
        print()
    
    out = DATA_DIR.parent / "tmp" / "deep_extract.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\nDeep extract saved to: {out}")
