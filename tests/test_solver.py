# Uji: domain terlalu sempit sehingga tidak ada solusi
domains_gagal = {
    "Andi": ["Pagi"],
    "Budi": ["Pagi"],  # sengaja bentrok dengan Andi, C2 pasti gagal
    "Citra": ["Siang"],
    "Dewi": ["Malam"],
}
hasil_gagal = backtracking_search(domains_gagal, variables, constraints_final)
assert hasil_gagal is None, "Seharusnya tidak ada solusi untuk kasus ini"
print("[EDGE CASE 1] Berhasil dideteksi: tidak ada solusi (sesuai ekspektasi)")


## Domain kosong sejak awal