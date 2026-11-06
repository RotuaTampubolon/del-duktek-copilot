# Del-Duktek Copilot

Asisten cerdas berbasis AI untuk membantu klasifikasi, penentuan prioritas,
eskalasi, dan rekomendasi penyelesaian laporan Dukungan Teknis (Duktek) IT
Institut Teknologi Del.

Proyek ini dikembangkan sebagai bagian dari mata kuliah **10S3001 -
Artificial Intelligence**, Program Studi Sarjana Sistem Informasi, Institut
Teknologi Del, Semester Gasal 2026/2027.

> **Status saat ini:** Milestone 3 sudah memiliki dataset chunk, runner
> embedding, rancangan evaluasi, persistent vector store, dan interface
> retrieval. Eksperimen model dan indexing belum dapat diklaim selesai sebelum
> dependency berhasil disinkronkan dan label relevansi ditinjau manusia
> tersedia.

## Daftar Isi

- [Latar Belakang](#latar-belakang)
- [Tujuan](#tujuan)
- [Struktur Proyek](#struktur-proyek)
- [Persyaratan](#persyaratan)
- [Instalasi](#instalasi)
- [Menjalankan M1 dan M2](#menjalankan-m1-dan-m2)
- [Knowledge Base dan Dataset](#knowledge-base-dan-dataset)
- [Embedding](#embedding)
- [Indexing Persistent](#indexing-persistent)
- [Retrieval](#retrieval)
- [Evaluasi Model](#evaluasi-model)
- [Pengujian](#pengujian)
- [Status Milestone](#status-milestone)
- [Batasan yang Diketahui](#batasan-yang-diketahui)
- [Lisensi](#lisensi)

## Latar Belakang

Unit Duktek IT Del menangani laporan gangguan teknologi informasi, seperti
gangguan jaringan, kerusakan perangkat, masalah helpdesk, dan kebutuhan
eskalasi ke unit atau vendor terkait. Proses manual dapat menyebabkan
ketidakkonsistenan klasifikasi, keterlambatan penanganan, serta distribusi
beban kerja teknisi yang kurang merata.

Del-Duktek Copilot dirancang sebagai purwarupa agen cerdas yang membantu
petugas melakukan triase laporan secara lebih konsisten dan memanfaatkan
referensi prosedur teknis yang telah dikumpulkan.

## Tujuan

Proyek ini mencakup:

1. Pemodelan alur eskalasi tiket menggunakan UCS dan A*.
2. Penyelesaian constraint penjadwalan teknisi menggunakan CSP.
3. Pembangunan knowledge base berbasis chunk dokumen.
4. Evaluasi model embedding multibahasa untuk semantic retrieval.
5. Penyimpanan vector secara persisten dan retrieval berdasarkan kemiripan
   semantik.

## Struktur Proyek

```text
del-duktek-copilot/
├── data/
│   ├── *.pdf                         # Referensi eksternal
│   └── processed/
│       └── corpus_chunks.jsonl       # 114 chunk hasil preprocessing
├── docs/
│   ├── corpus-inventory/             # Manifest dan dokumentasi preprocessing
│   ├── embedding/
│   │   ├── model-evaluation.md       # Evaluasi dan pemilihan model
│   │   └── embedding-experiment-results.md
│   └── modul/                        # Materi milestone
├── src/
│   ├── del_duktek_copilot/
│   │   └── embedding/
│   │       ├── evaluate.py           # Runner benchmark embedding
│   │       ├── index_corpus.py       # Indexing ke ChromaDB
│   │       ├── retrieve.py           # Query retrieval
│   │       └── vector_store.py       # Persistent vector store
│   ├── search/
│   │   └── baseline_search.py        # UCS dan A* untuk eskalasi
│   └── solver/
│       └── solver.py                 # CSP scheduler
├── tests/
│   ├── test_solver.py
│   └── unit/
├── pyproject.toml
├── uv.lock
└── README.md
```

## Persyaratan

- Python 3.11 atau lebih baru.
- [uv](https://docs.astral.sh/uv/).
- CPU dapat digunakan untuk inference, tetapi model embedding memerlukan
  resource lebih besar daripada modul M1/M2.
- Koneksi internet diperlukan saat pertama kali mengunduh dependency dan model
  dari Hugging Face.

## Instalasi

### 1. Clone repository

```bash
git clone https://github.com/RotuaTampubolon/del-duktek-copilot.git
cd del-duktek-copilot
```

### 2. Sinkronkan environment

```bash
uv sync
```

Dependency utama:

```text
numpy>=1.26,<3
chromadb>=1.0,<2
sentence-transformers>=3.0,<6
torch>=2.2,<3
```

Jika `uv sync` gagal dengan `Access is denied`, periksa permission executable
`uv`, interpreter Python yang dipilih, dan izin folder cache. Jangan
menganggap eksperimen berhasil sebelum perintah validasi dapat dijalankan.

## Menjalankan M1 dan M2

### M1: Baseline Search

```bash
uv run python src/search/baseline_search.py
```

Modul ini menampilkan jalur eskalasi dengan:

- Uniform Cost Search (UCS).
- A* Search.

### M2: Business Constraint Solver

```bash
uv run python src/solver/solver.py
```

Modul ini memuat:

- Propagasi constraint AC-3.
- Backtracking search.
- Heuristik Minimum Remaining Values (MRV).

## Knowledge Base dan Dataset

Dataset hasil preprocessing Anggota 1 berada di:

```text
data/processed/corpus_chunks.jsonl
```

Dataset berisi **114 chunk** dari 10 PDF dan 43 halaman. Parameter preprocessing
yang terdokumentasi:

- `max_chars=1200`
- `overlap_chars=150`
- Chunk tidak melintasi halaman.
- Setiap chunk memiliki `chunk_id` stabil dan unik.

Format setiap baris JSONL:

```json
{
  "text": "Isi chunk prosedur ...",
  "metadata": {
    "document_id": "helpdesk-ugm-pos-2024",
    "source": "Universitas Gadjah Mada",
    "category": "helpdesk",
    "source_status": "Layak",
    "authority_status": "referensi eksternal; bukan SOP resmi IT Del",
    "source_file": "source.pdf",
    "document_title": "POS Layanan Helpdesk Teknologi Informasi",
    "page_number": 1,
    "chunk_index": 1,
    "chunk_id": "helpdesk-ugm-pos-2024-p001-c0001"
  }
}
```

`text` digunakan sebagai input embedding. `chunk_id` dan metadata disimpan
sebagai identitas serta provenance; metadata tidak digabungkan ke teks embedding.
Sumber pada corpus adalah referensi eksternal dan bukan otomatis SOP resmi IT
Del.

## Embedding

Dua model yang disiapkan untuk dibandingkan:

| Model | Dimensi | Peran |
|---|---:|---|
| `intfloat/multilingual-e5-base` | 768 | Kandidat utama sementara |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 384 | Baseline ringan |

### Konfigurasi E5

E5 menggunakan prefix berbeda untuk query dan passage:

```text
query: <teks laporan Duktek>
passage: <teks chunk dokumen>
```

Konfigurasi yang digunakan runner:

- Similarity: cosine.
- Embedding dinormalisasi.
- Batch size default: 16.
- E5: maksimum model 512 token.
- MiniLM: maksimum model 128 token.

Pemilihan E5 sebagai kandidat utama masih bersifat sementara dan didasarkan
pada kesesuaiannya dengan passage retrieval, dukungan bahasa Indonesia, dan
konteks teknis corpus. Model final harus ditentukan berdasarkan benchmark
lokal, bukan asumsi atau popularitas.

Penjelasan lengkap tersedia di
[docs/embedding/model-evaluation.md](docs/embedding/model-evaluation.md).

## Indexing Persistent

Indexing dilakukan oleh `index_corpus.py` dan menggunakan ChromaDB
`PersistentClient`.

```bash
uv run python -m del_duktek_copilot.embedding.index_corpus `
  --chunks data/processed/corpus_chunks.jsonl `
  --storage data/vector_store
```

Untuk Linux/macOS, gunakan `\` sebagai pemisah baris atau jalankan sebagai satu
baris:

```bash
uv run python -m del_duktek_copilot.embedding.index_corpus --chunks data/processed/corpus_chunks.jsonl --storage data/vector_store
```

Perilaku indexing:

- `chunk_id` digunakan sebagai ID vector.
- Metadata scalar disimpan bersama dokumen.
- `upsert` membuat proses re-index tidak menggandakan record.
- Database dibuka kembali dari folder storage yang sama setelah aplikasi
  dihentikan.

MiniLM dapat digunakan untuk index pembanding:

```bash
uv run python -m del_duktek_copilot.embedding.index_corpus --chunks data/processed/corpus_chunks.jsonl --storage data/vector_store_minilm --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## Retrieval

Setelah index berhasil dibuat:

```python
from pathlib import Path

from del_duktek_copilot.embedding.retrieve import retrieve

hasil = retrieve(
    "Bagaimana menangani gangguan koneksi jaringan lokal?",
    storage_path=Path("data/vector_store"),
    n_results=5,
)

print(hasil)
```

Retrieval mengembalikan dokumen, metadata, dan distance dari ChromaDB. Query
E5 otomatis diberi prefix `query: `. Model yang digunakan untuk query harus
sama dengan model yang digunakan saat indexing.

## Evaluasi Model

Runner benchmark:

```bash
uv run python -m del_duktek_copilot.embedding.evaluate `
  --chunks data/processed/corpus_chunks.jsonl `
  --relevance data/benchmarks/embedding_relevance.jsonl `
  --output results/embedding-model-comparison.json
```

Runner membandingkan:

- Recall@5.
- Recall@10.
- MRR@10.
- nDCG@10.
- Waktu encoding passage dan query.
- Dimensi embedding.
- Device, batch size, dan RSS memory.

File relevance wajib berisi label yang diperiksa manusia:

```json
{
  "query_id": "q-network-01",
  "query": "Bagaimana menangani gangguan koneksi jaringan lokal?",
  "relevant_chunk_ids": ["network-document-p001-c0001"]
}
```

Runner akan menolak:

- `chunk_id` yang tidak dikenal.
- Query tanpa relevance ID.
- Query ID duplikat.
- Record chunk dengan metadata wajib yang hilang.

Dataset query–relevance belum tersedia pada repository. Karena itu belum ada
angka benchmark yang boleh diklaim sebagai hasil aktual. Detail status dan
rancangan benchmark tersedia di
[docs/embedding/embedding-experiment-results.md](docs/embedding/embedding-experiment-results.md).

## Pengujian

Jalankan seluruh test setelah environment berhasil disinkronkan:

```bash
uv run pytest
```

Test unit embedding mencakup:

- Validasi schema chunk JSONL.
- Validasi relevance ID.
- Perhitungan metrik retrieval.
- Penolakan vector dengan dimensi tidak konsisten.
- Penolakan upsert dengan data yang tidak sejajar.

Validasi dokumentasi:

```bash
git diff --check
```

## Status Milestone

- [x] **Milestone 1** — Problem Framing, PEAS, baseline search UCS/A*.
- [x] **Milestone 2** — Business Constraint Solver dengan AC-3 dan
  backtracking.
- [~] **Milestone 3** — Dataset chunk, desain embedding, runner evaluasi,
  persistent vector store, dan retrieval sudah disiapkan; benchmark aktual
  masih menunggu environment dan relevance labels manusia.
- [ ] **Milestone 4** — Enterprise AI Agent Pipeline (LLM + RAG + MCP).
- [ ] **Milestone 5** — Purwarupa web interaktif.

## Batasan yang Diketahui

1. Corpus berisi referensi eksternal. Status “Layak” tidak berarti dokumen
   tersebut merupakan SOP resmi IT Del.
2. Chunking berbasis karakter; token length tetap perlu dipantau oleh runner
   embedding.
3. Model belum boleh dinyatakan terbaik sebelum benchmark dengan label
   relevansi manusia dijalankan.
4. Model Sentence-Transformers dan ChromaDB perlu diunduh pada instalasi
   pertama.
5. `uv.lock` harus berhasil diperbarui pada environment yang memiliki izin
   eksekusi dan akses package index.

## Dokumentasi

- [Evaluasi model embedding](docs/embedding/model-evaluation.md)
- [Hasil dan kesiapan eksperimen](docs/embedding/embedding-experiment-results.md)
- [Dokumentasi preprocessing](docs/corpus-inventory/preprocessing.md)
- [Manifest corpus](docs/corpus-inventory/corpus-manifest.json)

## Lisensi

Proyek ini menggunakan lisensi MIT. Lihat [LICENSE](LICENSE) untuk detail
selengkapnya.
