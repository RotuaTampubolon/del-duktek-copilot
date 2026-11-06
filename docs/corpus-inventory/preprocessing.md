# Corpus preprocessing dan chunking

## Cakupan dan batas penggunaan

`corpus-manifest.json` adalah allowlist berdasarkan [audit corpus](./corpus-audit.md):
10 PDF yang berstatus **Layak**, dengan total 43 halaman. PDF di luar manifest
tidak diproses. Status `Layak` hanya berarti referensi eksternal yang relevan,
bukan persetujuan atau SOP resmi IT Del. Teks dan metadata selalu membawa status
sumber tersebut.

PDF asli tidak ditulis ulang. Modul membaca halaman memakai pypdf dalam mode
`layout`, sehingga pemisah baris dan jarak kolom pada tabel/form tetap tersedia.
Cleaning memakai Unicode NFC, merapikan line ending, menghapus karakter kontrol
non-teks, dan membatasi baris kosong berulang; tidak meratakan baris, kolom, atau
langkah prosedur.

`SOP-IT.pdf` berisi empat prosedur. Manifest memisahkannya berdasarkan
halaman 1–4 (jaringan lokal), 5–7 (pembuatan e-mail), 8–11 (perbaikan PC), dan
12–14 (monitoring bandwidth). Nomor halaman metadata tetap nomor halaman PDF
asal. Kelompok halaman terakhir menggunakan judul isi bandwidth meskipun header
PDF hasil ekstraksi mengulang judul jaringan.

## Parameter chunk

| Parameter | Nilai bawaan | Alasan |
|---|---:|---|
| `max_chars` | 1200 | Batas karakter deterministik tanpa menambah tokenizer bahasa tertentu; cukup kecil untuk embedding dan menjaga satu atau beberapa langkah dalam konteks. |
| `overlap_chars` | 150 | Mengulang sekitar 12,5% batas chunk untuk mempertahankan konteks antar potongan. Pemotongan dilakukan pada batas baris agar judul, baris prosedur, dan baris tabel tidak terbelah jika dapat dihindari. |

Chunk tidak pernah melintasi halaman; teks yang terlalu panjang untuk satu baris
dipecah pada batas spasi jika tersedia. `chunk_index` dimulai dari 1 dan
berurutan di dalam setiap `document_id`. `chunk_id` stabil dengan pola
`<document_id>-p<nomor-halaman>-c<indeks>`.

## Format output untuk pipeline embedding

`data/processed/corpus_chunks.jsonl` berisi satu objek JSON per baris:

```json
{
  "text": "Isi chunk ...",
  "metadata": {
    "document_id": "helpdesk-ugm-pos-2024",
    "source": "Universitas Gadjah Mada, ...",
    "category": "helpdesk",
    "source_status": "Layak",
    "authority_status": "referensi eksternal; bukan SOP resmi IT Del",
    "source_file": "1.-Layanan-Helpdesk-Teknologi-Informasi-ok.pdf",
    "document_title": "POS Layanan Helpdesk Teknologi Informasi",
    "page_number": 1,
    "chunk_index": 1,
    "chunk_id": "helpdesk-ugm-pos-2024-p001-c0001"
  }
}
```

`text` dapat dipetakan ke `documents`, `metadata` ke metadata dokumen, dan
`chunk_id` ke ID oleh adapter pipeline embedding. Metadata berisi nilai skalar
agar mudah dipakai oleh vector store, tanpa mengimplementasikan embedding atau
ChromaDB pada milestone ini.

## Hasil aktual

Dengan versi manifest dan parameter bawaan di atas, preprocessing menghasilkan
**114 chunk** dari 10 PDF (43 halaman) yang dipetakan menjadi 13 identitas
prosedur/dokumen. Ukuran chunk terbesar tepat 1200 karakter dan seluruh
`chunk_id` unik. Dataset JSONL yang dihasilkan berukuran 162.772 byte.

## Menjalankan

Dari root repository:

```bash
uv sync
uv run python -m del_duktek_copilot.corpus
```

Perintah tersebut membangun ulang dataset menggunakan manifest dan parameter
bawaan. Opsi `--data-dir`, `--manifest`, `--output`, `--max-chars`, dan
`--overlap-chars` dapat digunakan untuk lokasi atau parameter berbeda. Untuk
pengujian:

```bash
uv run pytest tests/test_corpus_preprocessing.py
```

Ekstraksi teks bukan pemeriksaan visual dokumen. Relasi sel tabel, diagram,
tanda tangan, hak penggunaan, dan kecocokan prosedur terhadap kebijakan Del
tetap memerlukan verifikasi terpisah sebelum pemakaian operasional.
