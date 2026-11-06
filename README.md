# Del-Duktek Copilot

Del-Duktek Copilot adalah purwarupa asisten cerdas untuk membantu unit
Dukungan Teknis (Duktek) IT Institut Teknologi Del dalam melakukan triase
laporan, menentukan prioritas, memilih jalur eskalasi, dan memberikan
rekomendasi penyelesaian gangguan teknologi informasi.

Proyek ini dikembangkan untuk mata kuliah **10S3001 - Artificial Intelligence**
di Program Studi Sarjana Sistem Informasi, Institut Teknologi Del, Semester
Gasal 2026/2027.

> **Status branch `main`:** Milestone 1 dan Milestone 2 tersedia. Fitur
> knowledge base dan vector search Milestone 3 dikembangkan pada branch fitur
> terpisah dan belum menjadi bagian dari isi branch `main` ini.

## Daftar Isi

- [Latar Belakang](#latar-belakang)
- [Tujuan Sistem](#tujuan-sistem)
- [Fitur yang Tersedia](#fitur-yang-tersedia)
- [Struktur Repository](#struktur-repository)
- [Teknologi](#teknologi)
- [Persyaratan](#persyaratan)
- [Instalasi](#instalasi)
- [Menjalankan Program](#menjalankan-program)
- [Pengujian](#pengujian)
- [Penjelasan Modul](#penjelasan-modul)
- [Status Milestone](#status-milestone)
- [Rencana Pengembangan](#rencana-pengembangan)
- [Dokumentasi](#dokumentasi)
- [Lisensi](#lisensi)

## Latar Belakang

Unit Duktek menangani berbagai laporan, antara lain:

- Gangguan jaringan.
- Kerusakan komputer atau perangkat keras.
- Masalah perangkat mahasiswa.
- Permintaan bantuan helpdesk.
- Eskalasi kepada unit internal atau vendor.

Jika proses triase dan eskalasi dilakukan sepenuhnya secara manual, beberapa
masalah dapat muncul:

1. Klasifikasi laporan tidak konsisten.
2. Tiket prioritas tinggi terlambat ditangani.
3. Jalur eskalasi tidak selalu menggunakan biaya waktu minimum.
4. Distribusi pekerjaan teknisi kurang seimbang.

Del-Duktek Copilot menjadi purwarupa untuk mengeksplorasi penerapan algoritma
Artificial Intelligence pada permasalahan tersebut.

## Tujuan Sistem

Sistem dirancang untuk:

1. Merepresentasikan alur eskalasi tiket sebagai graf berbobot.
2. Menentukan jalur eskalasi dengan biaya penanganan minimum.
3. Menyusun jadwal shift teknisi berdasarkan constraint operasional.
4. Menjadi dasar pengembangan knowledge base dan retrieval berbasis dokumen.
5. Menyediakan struktur yang dapat dikembangkan menjadi pipeline RAG pada
   milestone berikutnya.

## Fitur yang Tersedia

### Milestone 1: Baseline Search

Modul baseline search menyediakan:

- Uniform Cost Search (UCS).
- A* Search.
- Graf eskalasi berarah dengan bobot estimasi waktu penanganan.
- Perhitungan jalur dan total biaya eskalasi.

### Milestone 2: Business Constraint Solver

Modul solver menyediakan:

- Constraint Satisfaction Problem (CSP).
- Propagasi constraint dengan AC-3.
- Backtracking search.
- Heuristik Minimum Remaining Values (MRV).
- Constraint teknisi dan pembagian shift.
- Analisis sensitivitas performa solver beserta visualisasi.

### Milestone 3: Knowledge Base

Milestone 3 sedang dikembangkan pada branch fitur. Rancangan tahap ini
mencakup:

- Preprocessing dan chunking dokumen referensi.
- Evaluasi model embedding multibahasa.
- Semantic retrieval.
- Persistent vector storage.
- Integrasi ChromaDB.

Komponen Milestone 3 tidak boleh dianggap tersedia pada `main` kecuali file
dan dependency terkait sudah digabungkan ke branch ini.

## Struktur Repository

Struktur branch `main` saat ini:

```text
del-duktek-copilot/
├── .gitignore
├── .python-version
├── LICENSE
├── README.md
├── pyproject.toml
├── uv.lock
├── docs/
│   └── analisis-sensitivitas.png
├── src/
│   ├── __init__.py
│   ├── del_duktek_copilot/
│   │   └── __init__.py
│   ├── search/
│   │   ├── __init__.py
│   │   └── baseline_search.py
│   └── solver/
│       ├── solver.py
│       └── analisis_sensitivitas.py
└── tests/
    └── test_solver.py
```

## Teknologi

- Python 3.11 atau lebih baru.
- `uv` sebagai package manager dan environment manager.
- Standard library Python untuk implementasi graf dan algoritma pencarian.
- `matplotlib` untuk visualisasi analisis sensitivitas.
- `pytest` untuk pengujian.

Dependency runtime dan development didefinisikan di
[pyproject.toml](pyproject.toml). `uv.lock` digunakan untuk menjaga resolusi
dependency tetap reproducible.

## Persyaratan

Sebelum instalasi, pastikan tersedia:

- Python sesuai versi pada [.python-version](.python-version).
- `uv` versi terbaru yang didukung oleh sistem.
- Git.
- Terminal yang memiliki izin menjalankan Python dan `uv`.

Verifikasi instalasi:

```bash
python --version
uv --version
git --version
```

## Instalasi

### 1. Clone repository

```bash
git clone https://github.com/RotuaTampubolon/del-duktek-copilot.git
cd del-duktek-copilot
```

### 2. Pastikan berada di branch `main`

```bash
git switch main
```

### 3. Sinkronkan dependency

```bash
uv sync
```

Perintah tersebut membuat atau memperbarui environment yang dikelola `uv`
berdasarkan `pyproject.toml` dan `uv.lock`.

Jika muncul error `Access is denied` pada Windows:

1. Pastikan `uv.exe` dapat dijalankan dari terminal.
2. Pastikan folder repository dan cache `uv` dapat ditulis oleh pengguna.
3. Pastikan tidak ada proses Python atau `uv` lain yang mengunci file.
4. Jalankan kembali dari terminal yang memiliki izin workspace.
5. Jangan menganggap instalasi berhasil sebelum `uv sync` selesai tanpa error.

## Menjalankan Program

### Menjalankan baseline search

```bash
uv run python src/search/baseline_search.py
```

Contoh ini membangun graf studi kasus eskalasi dan menampilkan:

- Jalur hasil UCS.
- Estimasi waktu penanganan UCS.
- Jalur hasil A*.
- Estimasi waktu penanganan A*.

### Menjalankan business constraint solver

```bash
uv run python src/solver/solver.py
```

Program tersebut menjalankan contoh penjadwalan teknisi dengan constraint:

- Andi dan Budi tidak boleh mendapat shift yang sama.
- Citra tidak dapat mengambil shift malam.
- Setiap shift harus terisi.

### Menjalankan analisis sensitivitas

```bash
uv run python src/solver/analisis_sensitivitas.py
```

Output analisis dapat berupa data atau visualisasi performa solver sesuai
konfigurasi pada modul tersebut.

## Pengujian

Jalankan seluruh test:

```bash
uv run pytest
```

Jalankan test solver secara terfokus:

```bash
uv run pytest tests/test_solver.py -v
```

Sebelum membuat commit, periksa whitespace pada perubahan:

```bash
git diff --check
```

Jika test atau `uv` gagal karena permission Windows, catat error yang muncul
dan perbaiki environment terlebih dahulu. Jangan mengganti hasil test dengan
klaim berhasil.

## Penjelasan Modul

### `src/search/baseline_search.py`

Berisi:

- `DuktekEscalationGraph` untuk merepresentasikan graf.
- `uniform_cost_search()` untuk mencari jalur dengan biaya minimum.
- `a_star_search()` untuk pencarian berbasis biaya aktual dan heuristik.
- `bangun_graf_studi_kasus()` untuk membuat graf contoh.

Bobot edge pada graf merepresentasikan estimasi waktu penanganan dalam menit.

### `src/solver/solver.py`

Berisi:

- Representasi variabel dan domain teknisi.
- Constraint validasi assignment.
- Fungsi `ac3()` dan `revise()`.
- Fungsi `backtracking_search()`.
- Heuristik `pilih_variabel_mrv()`.

### `src/solver/analisis_sensitivitas.py`

Berisi analisis perubahan performa solver berdasarkan ukuran atau konfigurasi
masalah dan menghasilkan visualisasi yang disimpan di folder `docs/`.

## Status Milestone

| Milestone | Status | Keterangan |
|---|---|---|
| Milestone 1 | Selesai | Problem framing, PEAS, UCS, dan A* |
| Milestone 2 | Selesai | CSP, AC-3, backtracking, dan analisis sensitivitas |
| Milestone 3 | Pengembangan terpisah | Knowledge base, embedding, dan vector search |
| Milestone 4 | Belum dimulai | Pipeline LLM, RAG, dan MCP |
| Milestone 5 | Belum dimulai | Prototype web interaktif |

## Rencana Pengembangan

Tahap berikutnya direncanakan sebagai berikut:

1. Menggabungkan preprocessing corpus ke branch integrasi.
2. Menambahkan dependency embedding setelah desain disetujui.
3. Menjalankan evaluasi `multilingual-e5-base` dan MiniLM dengan query dan
   relevance labels yang ditinjau manusia.
4. Memilih model berdasarkan Recall@K, MRR, nDCG, latency, dan kebutuhan
   resource.
5. Menambahkan persistent vector storage.
6. Mengembangkan retrieval sebagai bagian dari pipeline RAG.
7. Menyediakan antarmuka penggunaan untuk petugas Duktek.

Model embedding tidak boleh dinyatakan terbaik hanya berdasarkan popularitas
atau ukuran model. Keputusan harus didukung hasil benchmark yang dapat
direproduksi.

## Dokumentasi

Dokumen yang tersedia pada branch `main`:

- [Analisis sensitivitas solver](docs/analisis-sensitivitas.png)
- [LICENSE](LICENSE)
- [pyproject.toml](pyproject.toml)

Dokumentasi Milestone 3 berada pada branch fitur terkait dan baru dapat
dirujuk dari `main` setelah branch tersebut digabungkan.

## Kontribusi

Alur kontribusi yang disarankan:

1. Buat branch fitur dari `main`.
2. Buat perubahan yang terfokus pada satu milestone.
3. Jalankan test yang relevan.
4. Jalankan `git diff --check`.
5. Dokumentasikan perubahan dan kendala.
6. Buat pull request dengan deskripsi yang jelas.

Perubahan pada M1 dan M2 harus mempertahankan perilaku yang sudah diuji,
kecuali perubahan tersebut memang menjadi bagian dari requirement baru.

## Lisensi

Proyek ini menggunakan lisensi MIT. Lihat [LICENSE](LICENSE) untuk informasi
selengkapnya.
