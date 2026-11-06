# Evaluasi Model Embedding

## Status dan ruang lingkup

Dokumen ini adalah keputusan desain Milestone 3 untuk embedding berbasis
Sentence-Transformers. ChromaDB, perubahan preprocessing, perubahan M1/M2,
dan perubahan dependency belum dilakukan.

Evaluasi ini menggunakan kebutuhan corpus knowledge base Duktek IT Del:
referensi eksternal berbahasa Indonesia dengan istilah teknis berbahasa
Inggris, terutama SOP jaringan, helpdesk, endpoint, backup, SLA, dan prosedur
operasional.

## Audit repository dan dataset Anggota 1

Branch kerja yang dipertahankan: `feature/m3-embedding-chromadb`.

Repository aktif belum memuat modul embedding atau dependency model. Pekerjaan
preprocessing dan chunking Anggota 1 ditemukan pada commit
`42c3a02` di branch `feature/m3-corpus-preprocessing`. Dataset JSONL final yang
dihasilkan pekerjaan tersebut adalah:

```text
data/processed/corpus_chunks.jsonl
```

Dokumentasi preprocessing Anggota 1 menyatakan bahwa dataset tersebut berisi
114 chunk dari 10 PDF, 43 halaman, dengan `max_chars=1200` dan
`overlap_chars=150`. File JSONL sekarang sudah diintegrasikan ke branch kerja.
Benchmark tetap belum dijalankan karena dataset relevance berlabel manusia
belum tersedia.

### Kontrak input JSONL

Contoh record yang diverifikasi dari commit Anggota 1:

```json
{
  "text": "Isi chunk prosedur ...",
  "metadata": {
    "document_id": "helpdesk-ugm-pos-2024",
    "source": "Universitas Gadjah Mada",
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

Struktur ini kompatibel dengan adapter embedding:

| Field JSONL | Penggunaan |
|---|---|
| `text` | Teks yang diberi prefix `passage: ` untuk E5 |
| `metadata.chunk_id` | ID stabil untuk vector store |
| `metadata` lainnya | Metadata filter dan provenance |
| `document_id`/`page_number` | Pelacakan sumber hasil retrieval |
| `source_status`/`authority_status` | Peringatan bahwa sumber adalah referensi eksternal |

Semua field metadata yang diverifikasi berupa string atau integer, sehingga
sesuai kebutuhan umum metadata vector store. Adapter tetap harus memvalidasi
field wajib (`text`, `metadata.chunk_id`) dan menolak record yang rusak secara
eksplisit. Tidak boleh mengubah teks atau metadata hasil preprocessing di tahap
embedding.

## Kandidat model

### 1. `intfloat/multilingual-e5-base`

Spesifikasi berikut berasal dari [model card resmi
multilingual-e5-base](https://huggingface.co/intfloat/multilingual-e5-base):

- 768 dimensi output.
- Berbasis XLM-RoBERTa-base dengan sekitar 278 juta parameter.
- Maksimum 512 token; input yang lebih panjang akan terpotong oleh model.
- Mendukung 94 bahasa, termasuk Bahasa Indonesia.
- Untuk retrieval asimetris, model card mensyaratkan prefix `query: ` pada
  query dan `passage: ` pada dokumen.
- Untuk semantic similarity simetris, gunakan prefix `query: ` pada kedua
  input.

**Kelebihan**

- Tujuan pelatihan dan format inputnya sesuai dengan passage retrieval.
- Kapasitas representasi 768 dimensi lebih memadai untuk membedakan langkah
  prosedur, kondisi gangguan, perangkat, dan jalur eskalasi.
- Mendukung campuran Bahasa Indonesia dan terminologi teknis berbahasa Inggris.
- Batas konteks lebih longgar daripada kandidat MiniLM dan lebih cocok dengan
  chunk 1200 karakter, walaupun tokenisasi tetap harus dipantau.

**Keterbatasan**

- Lebih besar dan lebih lambat, terutama pada CPU.
- Membutuhkan prefix yang konsisten; prefix yang salah dapat menurunkan
  kualitas retrieval.
- Embedding 768 dimensi memerlukan sekitar dua kali ruang penyimpanan float32
  dibanding embedding 384 dimensi.

### 2. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Spesifikasi berikut berasal dari [model card resmi
paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2):

- 384 dimensi output.
- Sekitar 117 juta parameter berdasarkan arsitektur MiniLM-L12.
- Maksimum 128 token.
- Mendukung 50 bahasa, termasuk Bahasa Indonesia.
- API Sentence-Transformers sederhana dan tidak membutuhkan prefix E5.

**Kelebihan**

- Lebih ringan untuk CPU, prototyping, dan deployment dengan resource terbatas.
- Vector berukuran 384 dimensi mengurangi penggunaan RAM dan storage.
- Cocok sebagai baseline semantic similarity dan pembanding yang mudah
  direproduksi.

**Keterbatasan**

- Fokus model adalah paraphrase/semantic similarity umum, bukan retrieval
  prosedur teknis secara khusus.
- Batas 128 token berisiko memotong konteks chunk SOP yang lebih panjang.
- Kapasitas representasi lebih kecil dapat menyulitkan pembedaan prosedur yang
  memiliki istilah umum serupa tetapi langkah atau kondisi berbeda.

## Perbandingan karakteristik

| Karakteristik | `multilingual-e5-base` | `paraphrase-multilingual-MiniLM-L12-v2` |
|---|---:|---:|
| Peran | Kandidat utama retrieval | Baseline ringan |
| Dimensi | 768 | 384 |
| Parameter (perkiraan) | 278M | 117M |
| Maksimum token | 512 | 128 |
| Bahasa | 94, termasuk Indonesia | 50, termasuk Indonesia |
| Prefix retrieval | `query:` / `passage:` | Tidak diperlukan |
| Resource relatif | Lebih tinggi | Lebih rendah |
| Kesesuaian corpus | Tinggi untuk retrieval SOP | Baik sebagai baseline |
| Risiko utama | Latensi dan ukuran | Truncation dan detail teknis |

Angka di atas adalah spesifikasi model, bukan hasil benchmark pada corpus Del
DuKtek. Ukuran file model, latensi, RAM, dan kualitas ranking harus diukur pada
environment yang sama sebelum keputusan produksi.

## Keputusan sementara

`intfloat/multilingual-e5-base` ditetapkan sebagai **kandidat utama sementara**.
`paraphrase-multilingual-MiniLM-L12-v2` ditetapkan sebagai **baseline**.

Dasarnya adalah bentuk tugas, bukan popularitas: query tiket Duktek adalah
input pendek yang mencari chunk prosedur yang relevan. E5 secara eksplisit
mendukung pasangan query-passage dan menyediakan konteks token yang lebih
panjang. Dimensi 768 masih proporsional untuk corpus kecil berisi 114 chunk,
sementara provenance dan kategori metadata tetap disimpan terpisah dari vector.

Keputusan final tetap bergantung pada benchmark lokal. Jika E5 tidak
memberikan peningkatan retrieval yang berarti tetapi membutuhkan resource jauh
lebih besar, MiniLM dapat dipilih sebagai kompromi operasional. Sebaliknya,
MiniLM tidak boleh dipilih hanya karena lebih kecil apabila Recall@K atau MRR
untuk kategori prosedur teknis turun secara material.

## Rancangan konfigurasi embedding

Konfigurasi awal yang akan digunakan setelah desain disetujui:

```text
model_name = "intfloat/multilingual-e5-base"
similarity = "cosine"
normalize_embeddings = true
query_prefix = "query: "
passage_prefix = "passage: "
batch_size = environment-dependent
max_seq_length = model default (maksimum 512 token)
```

Aturan input:

```text
query_embedding   = encode("query: " + query_text)
passage_embedding = encode("passage: " + chunk_text)
```

Untuk MiniLM, teks digunakan tanpa prefix E5. Kedua model harus dibandingkan
dengan chunk dan query yang sama, normalisasi yang sama, dan similarity cosine.
`chunk_id` tidak dimasukkan ke teks embedding; ID dan seluruh metadata disimpan
sebagai provenance.

Chunk Anggota 1 dibatasi karakter, bukan token. Karena itu adapter harus
mengukur token length, mencatat jumlah input yang terpotong, dan tidak diam-diam
mengubah chunk. Jika truncation substansial ditemukan, isu tersebut dikembalikan
ke tahap desain chunking, bukan diperbaiki secara diam-diam pada adapter.

## Rancangan benchmark

### Dataset evaluasi

Benchmark memerlukan query dan relevansi yang ditinjau manusia. Dataset JSONL
chunk saja belum cukup untuk menghitung ranking metric. Set evaluasi minimal
harus berisi:

```json
{
  "query_id": "q-001",
  "query": "Bagaimana menangani gangguan koneksi jaringan lokal?",
  "relevant_chunk_ids": ["network-...-c0001"]
}
```

Query harus mencakup kategori yang ada pada manifest, setidaknya jaringan,
helpdesk, endpoint, backup, account management, dan SLA/vendor. Query
ambiguous atau tidak memiliki relevansi yang disepakati dicatat terpisah dan
tidak dipakai untuk klaim model terbaik.

### Prosedur

1. Muat `corpus_chunks.jsonl` tanpa mengubah `text` atau metadata.
2. Encode seluruh chunk dengan masing-masing model.
3. Encode query dengan prefix yang sesuai.
4. Hitung cosine similarity dan urutkan chunk secara descending.
5. Gunakan query dan relevansi yang sama untuk kedua model.
6. Ulangi encoding dengan batch size yang sama dan catat environment.
7. Ukur truncation, waktu encoding, peak RAM, dan ukuran embedding float32.

### Metrik

- Recall@5 dan Recall@10: apakah chunk relevan muncul dalam top-k.
- MRR@10: seberapa cepat chunk relevan pertama muncul.
- nDCG@10: kualitas ranking jika satu query memiliki beberapa chunk relevan.
- Latensi encoding corpus dan query.
- Peak RAM serta ukuran vector hasil.
- Persentase input yang terpotong pada batas token model.

Pelaporan harus memuat hasil per kategori dan agregat. Tidak boleh menyatakan
model “terbaik” hanya dari satu query atau dari angka semantic similarity
buatan. Pada tahap ini belum ada hasil eksperimen lokal, sehingga semua metrik
di atas berstatus **belum dijalankan**.

## Dependency yang diperlukan

Implementasi embedding nantinya membutuhkan:

- `sentence-transformers` untuk API `SentenceTransformer` dan encoding.
- Backend PyTorch yang sesuai dengan platform untuk inferensi model.
- `numpy` untuk manipulasi vector jika belum dibawa oleh dependency utama.
- `chromadb` untuk persistent vector storage pada tahap berikutnya.
- `pytest` hanya untuk pengujian adapter, bukan runtime embedding.

Dependency runtime sudah dideklarasikan di `pyproject.toml`, tetapi `uv.lock`
belum dapat direfresh karena executable `uv` diblokir `Access is denied`.
Environment harus disinkronkan sebelum eksperimen dijalankan. Versi backend
CPU/GPU dan strategi cache model tetap perlu diverifikasi pada environment
yang digunakan untuk benchmark.

## Sumber verifikasi

- [multilingual-e5-base model card](https://huggingface.co/intfloat/multilingual-e5-base)
- [paraphrase-multilingual-MiniLM-L12-v2 model card](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- [Sentence-Transformers semantic textual similarity documentation](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)
- `docs/corpus-inventory/preprocessing.md` pada commit Anggota 1 `42c3a02`
- `data/processed/corpus_chunks.jsonl` pada commit Anggota 1 `42c3a02`
