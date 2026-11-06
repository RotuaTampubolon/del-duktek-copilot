# Laporan Persiapan Eksperimen Embedding

## Status eksperimen

**Status: runner siap; benchmark blocked oleh relevance labels.**

Runner eksperimen yang dapat dijalankan ulang sudah tersedia di
`src/del_duktek_copilot/embedding/evaluate.py`. Runner tersebut menolak
menjalankan evaluasi tanpa file relevance JSONL berlabel manusia dan melakukan
validasi `text`, metadata, serta keunikan `chunk_id` sebelum encoding.

Komponen persistent storage juga sudah disiapkan:

- `src/del_duktek_copilot/embedding/index_corpus.py` melakukan encoding dan
  `upsert` idempotent berdasarkan `chunk_id`.
- `src/del_duktek_copilot/embedding/vector_store.py` memakai
  `chromadb.PersistentClient`, menyimpan metadata scalar, dan menggunakan
  cosine distance.
- `src/del_duktek_copilot/embedding/retrieve.py` menyediakan retrieval query
  dengan model yang sama dan prefix yang sesuai.

Index belum dibuat karena dependency runtime belum tersinkron dan environment
masih terblokir. Persistent storage siap digunakan; jumlah 114 chunk akan
diverifikasi saat proses indexing dapat dijalankan.

Eksperimen tidak boleh dijalankan pada dataset pengganti. Pada pemeriksaan
branch repository:

- Branch aktif tetap `feature/m3-embedding-chromadb`.
- Dataset Anggota 1 sudah diintegrasikan ke branch kerja dari commit
  `42c3a02` pada branch `feature/m3-corpus-preprocessing`, dengan lokasi:

  ```text
  data/processed/corpus_chunks.jsonl
  ```

- Tidak ditemukan dataset query?relevance berlabel pada repository.
- `pyproject.toml` sekarang mendeklarasikan `numpy`, `sentence-transformers`,
  dan `torch`; `uv.lock` belum dapat direfresh karena executable `uv` gagal
  dengan `Access is denied`.

Dataset chunk sekarang tersedia untuk indexing. Namun, karena relevansi ground
truth belum tersedia, Recall@5, Recall@10, MRR@10, dan nDCG@10 belum dapat
dihitung. Tidak ada hasil model, latency, atau penggunaan resource yang
diklaim sebagai hasil eksperimen.

## Pemeriksaan artefak JSONL Anggota 1

Artefak pada commit Anggota 1 diperiksa read-only. Record yang terlihat
memiliki bentuk:

```json
{
  "text": "Isi chunk ...",
  "metadata": {
    "chunk_id": "document-p001-c0001",
    "document_id": "document",
    "page_number": 1,
    "chunk_index": 1,
    "category": "network_connectivity",
    "source_file": "source.pdf"
  }
}
```

Kontrak yang dibutuhkan adapter embedding:

| Pemeriksaan | Hasil |
|---|---|
| Record JSONL | Terintegrasi pada branch kerja |
| `text` | String non-kosong pada record yang diperiksa |
| `metadata` | Object dengan metadata provenance |
| `metadata.chunk_id` | String ID stabil pada record yang diperiksa |
| Metadata tambahan | Mencakup dokumen, sumber, kategori, halaman, dan indeks chunk |
| Jumlah record | 114, menurut dokumentasi preprocessing dan artefak Anggota 1 |
| Panjang teks | 36?1200 karakter pada pemeriksaan artefak |
| Teks di atas 1200 karakter | 0 pada pemeriksaan artefak |
| Data relevansi | Tidak ditemukan |

Dokumentasi dan test preprocessing Anggota 1 juga mendefinisikan `chunk_id`
unik dan stabil. Validasi final setelah integrasi harus tetap memeriksa
keunikan `chunk_id`, tipe `text`, keberadaan `metadata`, dan field provenance
sebelum encoding.

## Kandidat yang akan dibandingkan

1. `intfloat/multilingual-e5-base`
2. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

E5 akan menggunakan prefix retrieval:

```text
query: <teks query>
passage: <teks chunk>
```

MiniLM akan menggunakan teks tanpa prefix E5. Kedua model harus menggunakan
corpus, query, metrik cosine, dan perangkat yang sama.

Perintah setelah dataset dan label tersedia:

```text
uv run python -m del_duktek_copilot.embedding.evaluate \
  --chunks data/processed/corpus_chunks.jsonl \
  --relevance data/benchmarks/embedding_relevance.jsonl \
  --output results/embedding-model-comparison.json
```

`embedding_relevance.jsonl` tidak dibuat pada milestone ini karena label
relevansi harus disusun dan diperiksa manusia.

## Query benchmark yang disiapkan

Query berikut adalah rancangan benchmark domain Duktek, bukan query yang sudah
dinilai relevansinya dan bukan hasil eksperimen:

| ID | Query | Kategori |
|---|---|---|
| q-network-01 | Bagaimana menangani gangguan koneksi jaringan lokal? | network_connectivity |
| q-network-02 | Apa langkah pemeriksaan ketika internet dan intranet tidak dapat diakses? | network_connectivity |
| q-network-03 | Bagaimana prosedur pemeliharaan jaringan internal? | network_maintenance |
| q-helpdesk-01 | Bagaimana alur penerimaan dan penanganan laporan helpdesk TI? | helpdesk |
| q-helpdesk-02 | Apa informasi yang perlu dicatat saat menerima tiket gangguan? | helpdesk |
| q-endpoint-01 | Bagaimana prosedur penanganan komputer atau laptop bermasalah? | endpoint_maintenance |
| q-backup-01 | Bagaimana prosedur penyimpanan dan backup data? | data_storage_backup |
| q-account-01 | Bagaimana prosedur pembuatan akun atau e-mail? | account_management |
| q-sla-01 | Apa target waktu layanan dan eskalasi gangguan berdasarkan SLA? | sla/vendor |

Query ini baru dapat digunakan untuk metrik ranking setelah setiap query
memiliki satu atau lebih `relevant_chunk_ids` yang disepakati melalui review
manusia. Query dengan relevansi ambigu harus ditandai dan dikeluarkan dari
klaim agregat.

## Prosedur eksperimen setelah integrasi

1. Validasi seluruh record dan keunikan `chunk_id`.
2. Siapkan file relevansi yang memetakan `query_id` ke
   `relevant_chunk_ids`.
3. Muat model E5 dan MiniLM melalui Sentence-Transformers.
4. Encode setiap chunk dengan batch size dan perangkat yang sama.
5. Encode query dengan prefix yang sesuai.
6. Hitung cosine similarity dan urutkan seluruh chunk.
7. Hitung Recall@5, Recall@10, MRR@10, dan nDCG@10.
8. Catat waktu encoding corpus/query, peak RAM, device, batch size, dimensi,
   dan jumlah input yang terpotong.
9. Laporkan hasil agregat dan hasil per kategori.

### Definisi metrik

- **Recall@5/Recall@10**: query dihitung berhasil jika setidaknya satu chunk
  relevan berada di top-k.
- **MRR@10**: reciprocal rank dari chunk relevan pertama sampai posisi 10.
- **nDCG@10**: kualitas ranking sampai posisi 10; gunakan graded relevance
  hanya jika anotasi relevansi menyediakan tingkat relevansi.

## Kesiapan resource dan dependency

Eksperimen membutuhkan:

- `sentence-transformers`
- backend PyTorch yang sesuai dengan platform
- `numpy` bila diperlukan oleh runner/metrik
- tooling pengukuran waktu dan memory yang tersedia di Python

Dependency runtime sudah dideklarasikan pada `pyproject.toml`:

- `numpy>=1.26,<3`
- `chromadb>=1.0,<2`
- `sentence-transformers>=3.0,<6`
- `torch>=2.2,<3`

`uv.lock` belum berubah karena `uv lock` gagal dengan `Access is denied`.
Environment Pylance yang terdeteksi adalah
`C:\Users\User\Documents\certan-ai\.venv\Scripts\python.exe`, bukan virtual
environment repository. Environment tersebut memiliki PyTorch 2.14.1 tetapi
tidak memiliki `sentence-transformers`. Model belum diunduh, sehingga ukuran
cache, latency, RAM, dan device tidak dapat dilaporkan.

## Keputusan saat ini

Belum ada dasar eksperimen untuk menetapkan model final. Keputusan desain
sebelumnya tetap berlaku hanya sebagai rekomendasi sementara:

- `intfloat/multilingual-e5-base`: kandidat utama sementara.
- `paraphrase-multilingual-MiniLM-L12-v2`: baseline.

Keputusan final ditunda sampai tersedia anotasi relevansi dan
dan kedua model dapat dijalankan pada environment yang sama.

## Status checklist Anggota 2

| Kriteria | Status | Bukti/kendala |
|---|---|---|
| Model dipilih dengan justifikasi | Selesai sementara | `model-evaluation.md` |
| Embedding seluruh chunk dibuat | Siap dijalankan | JSONL sudah tersedia; environment/dependency masih perlu disinkronkan |
| Dimensi vector konsisten | Implementasi siap | Divalidasi oleh model/Chroma saat index |
| ChromaDB persistent storage | Implementasi siap | `PersistentClient`, belum dieksekusi |
| Metadata setiap chunk tersimpan | Implementasi siap | `upsert` menyimpan metadata scalar |
| Re-index tidak menggandakan data | Selesai secara desain | `upsert` memakai `chunk_id` |
| Database dimuat kembali setelah restart | Implementasi siap | `PersistentClient` membuka path yang sama |
| Unit/integration tests dijalankan | Terblokir environment | interpreter dan `uv` terkena `Access is denied` |
| Interface retrieval didokumentasikan | Selesai | `retrieve.py` dan prosedur di bawah |

Setelah dataset tersedia dan dependency berhasil disinkronkan, perintah yang
akan digunakan adalah:

```text
uv run python -m del_duktek_copilot.embedding.index_corpus \
  --chunks data/processed/corpus_chunks.jsonl \
  --storage data/vector_store
```

Retrieval menggunakan:

```python
from del_duktek_copilot.embedding.retrieve import retrieve

result = retrieve(
    "Bagaimana menangani gangguan koneksi jaringan lokal?",
    storage_path=Path("data/vector_store"),
    n_results=5,
)
```
