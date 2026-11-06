# Semantic Retrieval Benchmark

## Ground truth

Query dan expected document IDs diregistrasikan sebelum pengujian di
[`data/evaluation/retrieval_queries.jsonl`](../data/evaluation/retrieval_queries.jsonl).
Set ini berisi lima query bisnis (termasuk sinonim dan ambigu) serta dua query
out-of-domain. Label OOD tidak memiliki expected document ID.

## Kontrak skor

Collection ChromaDB menggunakan cosine space. ChromaDB mengembalikan cosine
distance, bukan similarity. Retrieval mengubahnya dengan rumus:

```text
cosine_similarity = 1 - cosine_distance
```

Nilai distance dan similarity tetap disimpan bersama provenance agar audit
hasil dapat ditelusuri ke chunk, file sumber, dan halaman.

## Hasil aktual

Benchmark dijalankan pada 7 November 2026 menggunakan 114 chunk, ChromaDB
persisten, model `intfloat/multilingual-e5-large`, dan CPU. Ranking dievaluasi
pada level dokumen dengan deduplikasi stabil dari chunk ke document ID agar satu
dokumen yang memiliki banyak chunk tidak menghitung berulang.

| Pemeriksaan | Hasil |
|---|---:|
| Unit test semantic retrieval, evaluator, dan embedding | 14 passed |
| Corpus chunk | 114 |
| Query in-domain | 5 |
| Query out-of-domain | 2 |
| Recall@5 (in-domain) | 0.80 |
| Recall@10 (in-domain) | 0.80 |
| MRR@10 (in-domain) | 0.667 |
| nDCG@10 (in-domain) | 0.646 |
| OOD threshold hasil kalibrasi | 0.8171 |
| OOD rejection precision | 1.00 (1/1 rejected) |
| OOD rejection coverage | 0.50 (1/2 OOD rejected) |

Per-query ranking dan provenance top-3 tersedia di
[`results/retrieval-benchmark-e5-large.json`](../results/retrieval-benchmark-e5-large.json).

## Analisis

Empat dari lima query in-domain menemukan setidaknya satu dokumen target pada
top-5; query PC tidak menemukan dokumen target sehingga menjadi kasus perbaikan
ground truth/model. Query sinonim jaringan dan query ambigu tetap menghasilkan
dokumen jaringan yang relevan. Dua query OOD memiliki similarity maksimum
0.8234 dan 0.8132: threshold 0.8171 menolak satu query dengan benar, tetapi
query resep masih lolos. Karena itu precision penolakan yang terukur adalah
1.00, sementara cakupan penolakan baru 0.50; precision tidak boleh
diinterpretasikan sebagai seluruh OOD berhasil ditolak.

Artefak benchmark lengkap:
[`results/retrieval-benchmark-e5-large.json`](../results/retrieval-benchmark-e5-large.json).

Benchmark dapat diulang dengan:

```bash
uv run python -m del_duktek_copilot.knowledge_base.benchmark \
  --model intfloat/multilingual-e5-large \
  --storage results/chroma-e5-large \
  --queries data/evaluation/retrieval_queries.jsonl \
  --output results/retrieval-benchmark-e5-large.json \
  --device cpu
```
