# Audit Corpus PDF — Milestone 3 (Audit Ulang)

**Tanggal audit:** 6 November 2026  
**Cakupan snapshot:** 10 file `data/*.pdf` yang tersedia saat audit ulang.

## Ringkasan eksekutif

Audit ulang menemukan **10 PDF dengan total 43 halaman**. Seluruh PDF berhasil dibuka, memiliki penanda akhir `%%EOF`, dan menghasilkan teks pada semua halaman (43/43). Tidak ditemukan file duplikat identik atau dokumen yang tidak relevan terhadap dukungan TI. Dengan kriteria *layak sebagai referensi eksternal*, tersedia **10 dokumen Layak**.

Status Layak **tidak** berarti dokumen merupakan SOP resmi IT Del, mutakhir untuk lingkungan Del, atau sudah disetujui untuk penerapan operasional. Identitas sumber pada dokumen mengarah ke institusi lain, termasuk UGM, BPBD DIY, UNM, Pemerintah Kota Surakarta, ITB Ahmad Dahlan, Universitas Lampung, IAIN Metro, dan BSIP. Tidak ditemukan bukti pengesahan/adopsi oleh IT Del.

Perbandingan dengan audit sebelumnya: corpus sekarang berisi 10 PDF yang berbeda dari snapshot 15 PDF sebelumnya. Audit ini hanya menilai file yang hadir sekarang; file yang tidak lagi berada di `data/` tidak dihitung atau dipulihkan.

## Metode dan arti status

- Menginventarisasi nama file, ukuran, versi PDF, jumlah halaman, metadata, sumber yang tertulis pada dokumen, serta jumlah karakter teks hasil ekstraksi.
- Mengekstrak teks dari setiap halaman dan menilai judul, organisasi, prosedur, peran, keluaran, dan keterbatasan yang terbaca.
- Memeriksa hash berkas untuk duplikat identik dan membandingkan teks untuk indikasi kemiripan.
- **Layak** pada audit ini berarti relevan dengan domain dukungan TI dan memiliki teks yang dapat diperiksa sehingga dapat dipakai sebagai **referensi eksternal dengan label sumber dan batas penggunaan**. Status ini bukan pengesahan maupun jaminan bahwa seluruh prosedur lengkap atau cocok untuk IT Del.
- Hasil pemeriksaan PDF tidak menggantikan pemeriksaan visual tanda tangan, diagram, tabel, hak penggunaan, atau konfirmasi versi yang sedang berlaku.
- Tidak dilakukan OCR, embedding, chunking, maupun perubahan ChromaDB.

## Inventaris seluruh dokumen

| # | Nama file | Halaman | Sumber yang terbaca di dokumen | Format dan ekstraksi | Status | Alasan dan bukti penilaian |
|---:|---|---:|---|---|---|---|
| 1 | `1.-Layanan-Helpdesk-Teknologi-Informasi-ok.pdf` | 3 | Universitas Gadjah Mada, Fakultas Kedokteran, Kesehatan Masyarakat, dan Keperawatan; POS efektif 1 Oktober 2024 | PDF 1.7; 442.626 byte; teks 3/3 halaman, 2.764 karakter | **Layak** | POS helpdesk mencatat keluhan, meminta identitas pemohon, melakukan verifikasi/analisis, dan menindaklanjuti atau mengarahkan pemohon bila di luar kewenangan unit. Sumber, nomor POS, tanggal, dan pengesahan tercantum. Referensi eksternal; rentang waktu respons dan unit/kanal kontak khusus UGM tidak boleh dianggap berlaku di Del. |
| 2 | `20260330072215SOP_Penyimpanan_Data_dan_Backup_Data.pdf` | 2 | BPBD Daerah Istimewa Yogyakarta, Pusdalops; SOP No. 35 Tahun 2026, efektif 30 Maret 2026 | PDF 1.7; 523.386 byte; teks 2/2 halaman, 5.177 karakter | **Layak** | Langkah terbaca mencakup penyimpanan di server, pengelompokan lokasi berdasarkan bidang/tahun, pemisahan file dan dokumentasi, serta backup berkala setiap tiga bulan. Relevan untuk tata kelola/backup data; rincian frekuensi dan media bersifat spesifik BPBD, bukan kebijakan Del. Tanda tangan digital tampil sebagai placeholder `${ttd}` pada ekstraksi. |
| 3 | `20260330072739SOP_Penanganan_Jaringan_Internet_dan_Intranet.pdf` | 2 | BPBD Daerah Istimewa Yogyakarta, Pusdalops; SOP No. 36 Tahun 2026, efektif 30 Maret 2026 | PDF 1.7; 518.909 byte; teks 2/2 halaman, 5.290 karakter | **Layak** | Tabel prosedur mencakup pelaporan gangguan, pemeriksaan hardware/software, analisis, penanganan, pelaporan, dan koordinasi dengan Diskominfo untuk masalah jaringan utama. Tahap dan keluaran dicantumkan; detail teknis diagnosis masih umum. Dokumen secara eksplisit terkait dengan SOP backup (#2), bukan salinan identik. |
| 4 | `MIM_8_SOP-Penanganan-Gangguan-Koneksi-Internet-Jaringan-Lokal.pdf` | 3 | Universitas Negeri Makassar (UNM), UPT ICT; isi menyebut SOP 2019 | PDF 1.7; 79.813 byte; teks 3/3 halaman, 3.942 karakter | **Layak** | Alur menyebut deteksi/laporan gangguan, penerusan oleh Front Office/helpdesk ke staf jaringan, pemeriksaan `ping`, konfirmasi lokasi, dan troubleshooting/escalation. Relevan untuk tiket/konektivitas. Formulir tabel memiliki beberapa kolom/perlengkapan yang kosong atau generik; dipakai sebagai contoh alur, bukan prosedur lengkap atau SLA Del. |
| 5 | `SOP SKA_Diskominfo-SP_01_01_CFM_-01_SOP_BID_Tinf_3 20230525081216.pdf` | 5 | Dinas Komunikasi, Informatika, Statistik dan Persandian Kota Surakarta; disahkan 25 Agustus 2022 | PDF 1.4; 567.657 byte; teks 5/5 halaman, 4.415 karakter | **Layak** | SOP pemeliharaan jaringan internal dengan identitas dokumen, persetujuan, kualifikasi pelaksana, dan perlengkapan. Relevan bagi pemeliharaan infrastruktur jaringan; dasar hukum dan tata kerja Pemerintah Kota Surakarta bersifat lokal. |
| 6 | `SOP SKA_Setwan_02_03_CFM_03_SOP_BAG_UMUMKEU_16 20230524155532.pdf` | 5 | Sekretariat DPRD Kota Surakarta; SOP Pemeliharaan Komputer atau Laptop, disahkan 25 Agustus 2022 | PDF 1.4; 569.650 byte; teks 5/5 halaman, 4.865 karakter | **Layak** | Tabel aktivitas memuat identifikasi kelayakan perangkat, usulan pemeliharaan/perbaikan, disposisi/pemeriksaan, dan keluaran administrasi. Relevan untuk alur pemeliharaan endpoint, tetapi persetujuan/pengadaan sesuai proses administrasi instansi asal. |
| 7 | `SOP-IT.pdf` | 14 | Institut Teknologi dan Bisnis Ahmad Dahlan Jakarta (ITB-AD); SOP jaringan lokal, pembuatan email, perbaikan PC, dan bandwidth | PDF 1.7; 382.695 byte; teks 14/14 halaman, 15.418 karakter | **Layak** | Berisi beberapa SOP IT yang dapat dibedakan melalui judul dan halaman, termasuk gangguan koneksi jaringan lokal, perbaikan PC, akun email, dan bandwidth. Cakupan relevan; file menggabungkan beberapa SOP dan header/page numbering berulang, sehingga sumber dan batas SOP perlu dipertahankan saat pemakaian berikutnya. Alur birokrasi surat/disposisi bukan alur tiket Del. |
| 8 | `SOP-TIK-PDI-04 Pengelolaan Sistem Helpdesk.pdf` | 4 | UPT TIK Universitas Lampung; dibuat 2015, revisi 10 Agustus 2017, efektif 31 Agustus 2017 | PDF 1.7; 100.240 byte; teks 4/4 halaman, 3.618 karakter | **Layak** | SOP memiliki nomor, tanggal, pengesahan, peran, penerimaan surat/tiket, disposisi, penyelesaian, dan pelaporan. Relevan bagi pengelolaan helpdesk; versi cukup lama dan model kerja berbasis surat/tiket instansi asal perlu diperlakukan sebagai referensi historis. |
| 9 | `SOP-TIPD-2024-PENANGANAN-GANGGUAN-JARINGAN-KOMPUTER.pdf` | 2 | UPT Teknologi Informasi dan Pangkalan Data IAIN Metro; SOP No. 0008/TIPD/10/2023, efektif 11 Oktober 2023 | PDF 1.7; 256.010 byte; teks 2/2 halaman, 2.424 karakter | **Layak** | SOP mencakup penanganan gangguan jaringan, pemeriksaan perangkat, pemeliharaan/monitoring access point, peran, dan perlengkapan. Relevan untuk jaringan; ringkas dan memiliki salah ketik, sehingga langkah teknis hanya digunakan sejauh dapat diverifikasi dari dokumen. |
| 10 | `SOP_Helpdesk_Penanganan_Permasalahan_Teknis_TI_Sekretariat_BSIP.pdf` | 3 | Kementerian Pertanian, Badan Standardisasi Instrumen Pertanian (BSIP), Sekretariat Badan; revisi 29 Agustus 2024, efektif 6 September 2024 | PDF 1.4; 158.454 byte; teks 3/3 halaman, 3.278 karakter | **Layak** | Alur mencakup persetujuan permintaan bantuan, identifikasi kerusakan, penanganan aplikasi/website atau server down, perbaikan, pengecekan, dan pelaporan ke satuan kerja. Relevan untuk intake dan eskalasi helpdesk; alur disposisi administratif serta tool yang disebut khusus untuk BSIP, tidak otomatis sesuai untuk Del. |

## Pemeriksaan relevansi dan kualitas

| Area | Bukti dokumen | Penilaian |
|---|---|---|
| Helpdesk dan tiket | #1 UGM, #8 Unila, #10 BSIP, #4 UNM | Tersedia intake keluhan/permintaan, pencatatan, peran, penyelesaian atau eskalasi, dan/atau pelaporan. Model kanal kerja beragam dan sebagian berbasis surat, bukan platform tiket IT Del. |
| Troubleshooting perangkat komputer | #6 pemeliharaan komputer/laptop; #7 perbaikan PC; #10 identifikasi kerusakan TI | Ada alur pemeriksaan dan perbaikan/pengusulan perbaikan. Referensi eksternal tidak menetapkan konfigurasi atau prosedur khusus perangkat Del. |
| Jaringan dan konektivitas | #3 BPBD DIY; #4 UNM; #5 Diskominfo Surakarta; #7 ITB-AD; #9 IAIN Metro | Cakupan paling banyak. Ada laporan gangguan, pemeriksaan, monitoring, koordinasi, dan pemeliharaan; kedalaman teknis bervariasi. |
| Pemeliharaan infrastruktur TI | #2 backup/storage; #3 jaringan; #5 jaringan internal; #6 endpoint | Ada contoh pemeliharaan jaringan, pengelolaan lokasi penyimpanan, backup, dan pemeriksaan perangkat. Tidak ada bukti bahwa jadwal, vendor, atau topologi tersebut berlaku di IT Del. |
| SOP layanan dukungan TI | #1, #8, #10 helpdesk; #7 SOP layanan email; beberapa SOP jaringan memuat alur dukungan | Dapat menjadi referensi proses; sebelum dijadikan aturan, cocokkan pemilik proses, jalur eskalasi, otorisasi, target layanan, dan kebijakan keamanan IT Del. |

## Duplikasi, relevansi, dan integritas file

- Tidak ditemukan hash berkas identik di antara 10 PDF.
- Kemiripan teks tinggi antara dua SOP BPBD DIY (#2 dan #3) berasal dari kop, dasar hukum, dan format template yang sama. Nomor SOP, judul, dan langkah kegiatan berbeda; keduanya merupakan dokumen terkait, bukan duplikat.
- SOP jaringan Diskominfo Surakarta (#5) dan pemeliharaan komputer Setwan Surakarta (#6) menggunakan gaya/formulir pemerintah daerah yang serupa, tetapi prosedur dan objek pemeliharaannya berbeda.
- Tidak ada PDF kosong atau tidak relevan pada snapshot ini.
- Semua file memiliki `%%EOF` dan dapat dibuka parser. Pemeriksaan ini tidak membuktikan validitas tanda tangan digital atau tidak adanya masalah tampilan visual.

## Rekomendasi corpus final

**Rekomendasi: 10 PDF layak dimasukkan sebagai referensi eksternal pendukung**, dengan identitas sumber dan status non-otoritatif yang terlihat. Dengan definisi Layak pada audit ini, persyaratan minimal 10 dokumen terpenuhi tepat pada batas minimum; tidak ada dasar untuk menyebutnya sebagai corpus SOP resmi IT Del.

Ketentuan sebelum penggunaan dalam KB:

1. Beri metadata untuk setiap PDF: institusi asal, judul/nomor SOP, tanggal/revisi yang tercantum, status `referensi eksternal`, area topik, serta catatan “bukan SOP resmi IT Del”.
2. Jawaban tentang kebijakan, SLA, kanal kontak, konfigurasi, target waktu, jadwal backup, atau mekanisme eskalasi IT Del harus bersumber dari dokumen resmi IT Del; dokumen eksternal tidak cukup untuk mengklaim aturan Del.
3. Pertahankan keterlacakan halaman. Khusus `SOP-IT.pdf`, pisahkan identitas empat SOP berdasarkan judul/halaman saat tahap penyiapan korpus nanti; jangan menyatukan prosedurnya menjadi satu aturan.
4. Tinjau visual tabel, alur/diagram, tanggal berlaku, dan pengesahan sebelum penggunaan operasional. Hal ini terutama penting untuk ekstraksi SOP berbentuk tabel/form.
5. Prioritaskan pengadaan sumber internal IT Del yang belum terwakili jelas: prosedur ticketing/SLA resmi, langkah troubleshooting perangkat yang disetujui, arsitektur/eskalasi jaringan kampus, serta standar pemeliharaan dan backup Del. Materi tersebut akan melengkapi referensi, bukan mengganti SOP internal.

## Kendala ekstraksi PDF

- Tidak ada file yang gagal dibuka atau halaman tanpa teks hasil ekstraksi; 43 dari 43 halaman menghasilkan teks yang dapat dicari. Tidak terindikasi kebutuhan OCR wajib dari hasil ekstraksi.
- Beberapa dokumen berformat tabel/form. Ekstraksi teks linear dapat mengubah urutan kolom atau hubungan antara kegiatan, pelaksana, waktu, dan output; validasi visual tetap diperlukan.
- `SOP-IT.pdf` menggabungkan beberapa SOP dalam satu PDF dengan header serta nomor halaman berulang. Jangan kehilangan batas dokumen/halaman jika nanti diproses.
- Pada dua SOP BPBD DIY, placeholder tanda tangan `${ttd}` muncul di lapisan teks walaupun penutup PDF menyatakan dokumen ditandatangani elektronik; validasi tanda tangan perlu dilakukan terpisah.
- Parser memberi peringatan struktur whitespace pada object header saat membaca `SOP-TIK-PDI-04 Pengelolaan Sistem Helpdesk.pdf`; file tetap terbaca, semua 4 halaman menghasilkan teks, dan tidak ada kegagalan ekstraksi.
- Tidak ada pengujian autentikasi sumber, hak penggunaan, tanda tangan digital, maupun keberlakuan dokumen terhadap kebijakan IT Del.