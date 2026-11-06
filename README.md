# Del-Duktek Copilot

Asisten cerdas berbasis AI untuk klasifikasi, prioritas, dan penyelesaian
laporan Dukungan Teknologi Informasi (Duktek) di Institut Teknologi Del.

Proyek ini dikembangkan sebagai bagian dari mata kuliah **10S3001 - Artificial
Intelligence / Kecerdasan Buatan**, Program Studi Sarjana Sistem Informasi,
Institut Teknologi Del, Semester Gasal 2026/2027.

## Latar Belakang

Unit Dukungan Teknis (Duktek) IT Del menangani berbagai laporan gangguan
teknologi informasi, mulai dari kerusakan perangkat keras, gangguan jaringan,
hingga masalah pada perangkat pribadi mahasiswa. Proses triase laporan saat
ini masih dilakukan manual oleh petugas, sehingga rentan terhadap
inkonsistensi klasifikasi, keterlambatan eskalasi laporan prioritas tinggi,
dan distribusi beban kerja teknisi yang tidak merata.

Del-Duktek Copilot dirancang sebagai purwarupa agen cerdas yang membantu
proses klasifikasi, penentuan prioritas, dan rekomendasi penyelesaian
laporan gangguan secara otomatis dan terstandardisasi.

## Anggota Tim & Peran
| Nama | NIM | Peran |
|------|-----|-------|
| ... | ... | AI Architect & Model Lead |
| ... | ... | Data & Knowledge Engineer |
| ... | ... | Integration & Interface Engineer |
| ... | ... | QA, Evaluation & Ethics Lead |

## Struktur Proyek
del-duktek-copilot/
├── src/
│   └── del_duktek_copilot/
│   └── search/
│   └── baseline_search.py # Modul UCS/A* untuk eskalasi tiket
├── docs/ # Dokumen laporan & diagram arsitektur
├── tests/ # Unit test (pytest)
├── .gitignore
├── LICENSE
├── pyproject.toml
├── uv.lock
└── README.md


## Instalasi & Menjalankan Proyek

Proyek ini menggunakan [Astral uv](https://docs.astral.sh/uv/) sebagai
manajer paket dan environment Python.

**1. Clone repositori**
```bash
git clone https://github.com/username-tim/del-duktek-copilot.git
cd del-duktek-copilot
```

**2. Sinkronkan dependensi**
```bash
uv sync
```

**3. Jalankan modul baseline search**
```bash
uv run python src/search/baseline_search.py
```

Program akan menampilkan hasil pencarian jalur eskalasi tiket menggunakan
algoritma Uniform Cost Search (UCS) dan A* Search beserta estimasi total
waktu penanganannya.

## Progress Milestone

- [x] **Milestone 1** — Problem Framing, Spesifikasi PEAS, Baseline Search (UCS/A*)
- [ ] Milestone 2 — Business Constraint Solver (CSP/GA)
- [ ] Milestone 3 — Enterprise Knowledge Base & Vector Search (ChromaDB)
- [ ] Milestone 4 — Enterprise AI Agent Pipeline (LLM + RAG + MCP)
- [ ] Milestone 5 — Purwarupa Web Interaktif (Gradio)

## Semantic Retrieval (Milestone 3)

Modul retrieval berada di
[`src/del_duktek_copilot/knowledge_base/semantic_search.py`](src/del_duktek_copilot/knowledge_base/semantic_search.py).
Modul ini menerima vector store ChromaDB dan fungsi encoder dari pipeline
embedding yang telah disediakan, sehingga tidak membuat model atau collection
baru. `SemanticRetriever.search(query, top_k=5)` mengembalikan teks chunk,
seluruh metadata, sumber dokumen, nomor halaman, cosine distance, dan cosine
similarity.

ChromaDB dikonfigurasi dengan cosine space. Karena ChromaDB mengembalikan
`distance`, nilai similarity dihitung konsisten sebagai
`cosine_similarity = 1 - cosine_distance`; keduanya ditampilkan agar tidak
tertukar.

Ground truth query yang ditetapkan sebelum benchmark tersedia di
[`data/evaluation/retrieval_queries.jsonl`](data/evaluation/retrieval_queries.jsonl).
Dataset tersebut mencakup query domain, sinonim, ambigu, dan out-of-domain.
Metrik recall@k, MRR, nDCG, serta kalibrasi threshold OOD tersedia di
[`src/del_duktek_copilot/knowledge_base/evaluation.py`](src/del_duktek_copilot/knowledge_base/evaluation.py).

Jalankan validasi modul:

```bash
uv sync
uv run pytest tests/unit/test_semantic_search.py tests/unit/test_evaluation.py
```

Benchmark end-to-end hanya boleh dijalankan setelah corpus JSONL dan index
ChromaDB persisten hasil pipeline embedding tersedia. Jangan mengisi hasil
benchmark secara manual; simpan output aktual dan threshold hasil kalibrasi
bersama laporan eksperimen.

## Dokumen Laporan

Laporan lengkap tersedia di `docs/laporan-tugas1.pdf`.

## Lisensi

Proyek ini menggunakan lisensi MIT — lihat berkas [LICENSE](LICENSE) untuk
detail lebih lanjut.
>>>>>>> df41cfc1b15b652421efa091e72af62a0960be0b
