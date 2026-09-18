<<<<<<< HEAD
# del-duktek-copilot

"AdryanPanjaitann"
"andryanpanjaitan30@gmail.com"
=======
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
│ └── del_duktek_copilot/
│ └── search/
│ └── baseline_search.py # Modul UCS/A* untuk eskalasi tiket
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

## Lisensi

Proyek ini menggunakan lisensi MIT — lihat berkas [LICENSE](LICENSE) untuk
detail lebih lanjut.
>>>>>>> e19b5cea05c195465573d9bd7e9203e1604eb54b
