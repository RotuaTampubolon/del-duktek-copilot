# Del-Duktek Copilot

Asisten cerdas berbasis AI untuk klasifikasi, prioritas, dan penyelesaian
laporan Dukungan Teknologi Informasi (Duktek) di Institut Teknologi Del.

## Latar Belakang
Ringkas 2-3 kalimat dari Bab 1 laporan kalian (pain points Duktek).

## Anggota Tim & Peran
| Nama | NIM | Peran |
|------|-----|-------|
| ... | ... | AI Architect & Model Lead |
| ... | ... | Data & Knowledge Engineer |
| ... | ... | Integration & Interface Engineer |
| ... | ... | QA, Evaluation & Ethics Lead |

## Struktur Proyek
src/search/ -> modul baseline search (UCS/A*)
tests/ -> unit test
docs/ -> dokumen laporan


## Instalasi & Menjalankan Proyek
Proyek ini menggunakan [Astral uv](https://docs.astral.sh/uv/) sebagai
manajer paket dan environment.

```bash
git clone https://github.com/username-tim/del-duktek-copilot.git
cd del-duktek-copilot
uv sync
uv run python src/search/baseline_search.py
```

## Milestone Progress
- [x] Milestone 1: Problem Framing, PEAS, Baseline Search
- [ ] Milestone 2: Business Constraint Solver (CSP/GA)
- [ ] Milestone 3: Knowledge Base & Vector Search
- [ ] Milestone 4: AI Agent Pipeline (LLM + RAG + MCP)
- [ ] Milestone 5: Web Interface (Gradio)

## Dokumen Laporan
Laporan lengkap tersedia di `docs/laporan-tugas1.pdf`.

## Lisensi
Proyek ini menggunakan lisensi MIT — lihat berkas `LICENSE`.