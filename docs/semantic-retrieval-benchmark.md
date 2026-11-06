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

## Status hasil aktual

| Pemeriksaan | Hasil |
|---|---:|
| Unit test semantic retrieval dan evaluator | 8 passed |
| Corpus/index ChromaDB pada branch retrieval saat ini | belum tersedia |
| Benchmark model end-to-end | blocked sampai branch embedding/index digabung |
| OOD rejection precision | belum dihitung tanpa skor retrieval aktual |

Angka benchmark model dan threshold OOD tidak diisi sebelum index dan model
benar-benar dijalankan. Setelah tersedia, laporkan recall@5, recall@10, MRR@10,
nDCG@10, per-query ranking, serta threshold OOD hasil
`calibrate_ood_threshold`.
