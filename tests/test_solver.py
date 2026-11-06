"""
Unit Test — Modul CSP Solver Del-Duktek Copilot
Menguji kebenaran algoritma AC-3 dan Backtracking Search (MRV),
termasuk pengujian kasus ekstrem (edge cases) sesuai rubrik Milestone 2.
"""

import os
import sys

# Supaya pytest bisa menemukan modul di src/solver/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

# pylint: disable=wrong-import-position
from solver.solver import (
    ac3,
    backtracking_search,
    constraint_andi_budi_beda_shift,
    constraint_citra_tidak_malam,
    constraint_semua_shift_terisi,
)
# pylint: enable=wrong-import-position

# ---------------------------------------------------------
# SETUP DATA UJI (dipakai berulang di beberapa test)
# ---------------------------------------------------------

def buat_variabel_domain_normal():
    """Siapkan variabel, domain, dan batasan untuk skenario normal."""
    variables = ["Andi", "Budi", "Citra", "Dewi"]
    domains = {
        "Andi": ["Pagi", "Siang", "Malam"],
        "Budi": ["Pagi", "Siang", "Malam"],
        "Citra": ["Pagi", "Siang", "Malam"],
        "Dewi": ["Pagi", "Siang", "Malam"],
    }
    constraints = [
        constraint_andi_budi_beda_shift,
        constraint_citra_tidak_malam,
        lambda a: constraint_semua_shift_terisi(a, variables),
    ]
    return variables, domains, constraints


# ---------------------------------------------------------
# TEST 1 — Kasus Normal: solusi harus ditemukan
# ---------------------------------------------------------

def test_solusi_valid_ditemukan():
    """
    Kasus dasar: dengan domain penuh dan batasan wajar,
    solver harus berhasil menemukan jadwal yang valid.
    """
    variables, domains, constraints = buat_variabel_domain_normal()
    hasil = backtracking_search(domains, variables, constraints)

    assert hasil is not None, "Solver seharusnya menemukan solusi pada kasus normal"
    assert len(hasil) == len(variables), "Semua teknisi harus mendapat shift"


def test_solusi_memenuhi_semua_batasan():
    """
    Memastikan solusi yang dihasilkan benar-benar mematuhi
    semua batasan (C1, C2, C3), bukan cuma lengkap tapi melanggar aturan.
    """
    variables, domains, constraints = buat_variabel_domain_normal()
    hasil = backtracking_search(domains, variables, constraints)

    assert hasil is not None
    # C2: Andi dan Budi tidak boleh shift sama
    assert hasil["Andi"] != hasil["Budi"], "Andi dan Budi tidak boleh dapat shift yang sama"
    # C3: Citra tidak boleh shift malam
    assert hasil["Citra"] != "Malam", "Citra tidak boleh mendapat shift malam"
    # C1: semua shift harus terisi
    assert set(hasil.values()) == {"Pagi", "Siang", "Malam"}, "Semua shift wajib terisi"


# ---------------------------------------------------------
# TEST 2 — Edge Case: domain terlalu sempit (over-constrained)
# ---------------------------------------------------------

def test_edge_case_domain_bentrok_tidak_ada_solusi():
    """
    Edge case: domain sengaja dibuat sangat sempit sehingga
    Andi dan Budi terpaksa harus dapat shift yang sama (melanggar C2).
    Solver harus mengembalikan None, bukan crash atau solusi salah.
    """
    variables = ["Andi", "Budi", "Citra", "Dewi"]
    domains = {
        "Andi": ["Pagi"],
        "Budi": ["Pagi"],  # sengaja hanya ada 1 pilihan yang sama dengan Andi
        "Citra": ["Siang"],
        "Dewi": ["Siang"],
    }
    constraints = [
        constraint_andi_budi_beda_shift,
        constraint_citra_tidak_malam,
        lambda a: constraint_semua_shift_terisi(a, variables),
    ]

    hasil = backtracking_search(domains, variables, constraints)
    assert hasil is None, "Seharusnya tidak ada solusi karena Andi dan Budi pasti bentrok"


# ---------------------------------------------------------
# TEST 3 — Edge Case: domain kosong sejak awal
# ---------------------------------------------------------

def test_edge_case_domain_kosong():
    """
    Edge case: salah satu variabel domainnya kosong total.
    Solver harus menangani ini dengan rapi (return None),
    tidak boleh crash/IndexError.
    """
    variables = ["Andi", "Budi", "Citra", "Dewi"]
    domains = {
        "Andi": [],  # domain kosong
        "Budi": ["Pagi"],
        "Citra": ["Siang"],
        "Dewi": ["Malam"],
    }
    constraints = [
        constraint_andi_budi_beda_shift,
        constraint_citra_tidak_malam,
        lambda a: constraint_semua_shift_terisi(a, variables),
    ]

    hasil = backtracking_search(domains, variables, constraints)
    assert hasil is None, "Solver harus mengembalikan None jika ada domain kosong, bukan error"


# ---------------------------------------------------------
# TEST 4 — Edge Case: jumlah teknisi lebih sedikit dari shift wajib
# ---------------------------------------------------------

def test_edge_case_teknisi_kurang_dari_shift():
    """
    Edge case: hanya ada 2 teknisi, padahal wajib ada 3 shift terisi.
    Tidak mungkin 2 orang mengisi 3 shift sekaligus (tiap orang 1 shift),
    jadi solver harus mengembalikan None.
    """
    variables = ["Andi", "Budi"]
    domains = {
        "Andi": ["Pagi", "Siang", "Malam"],
        "Budi": ["Pagi", "Siang", "Malam"],
    }
    constraints = [
        lambda a: constraint_semua_shift_terisi(a, variables),
    ]

    hasil = backtracking_search(domains, variables, constraints)
    assert hasil is None, "Tidak mungkin 2 teknisi mengisi 3 shift wajib sekaligus"


# ---------------------------------------------------------
# TEST 5 — Menguji fungsi AC-3 secara terpisah
# ---------------------------------------------------------

def test_ac3_mempersempit_domain():
    """
    Menguji bahwa AC-3 berhasil mempersempit domain ketika ada
    batasan yang membuat sebagian nilai pasti tidak valid.
    """
    domains = {
        "Andi": ["Pagi"],
        "Budi": ["Pagi", "Siang"],
    }
    arcs = [("Budi", "Andi")]

    def constraint_check(assignment):
        if "Andi" in assignment and "Budi" in assignment:
            return assignment["Andi"] != assignment["Budi"]
        return True

    hasil_domains = ac3(domains, arcs, constraint_check)

    # Karena Andi cuma punya opsi "Pagi", maka "Pagi" harus
    # dihapus dari domain Budi (supaya tidak mungkin sama)
    assert "Pagi" not in hasil_domains["Budi"], \
        "AC-3 seharusnya menghapus nilai 'Pagi' dari domain Budi"
    assert "Siang" in hasil_domains["Budi"], \
        "Nilai yang masih valid tidak boleh ikut terhapus"


def test_ac3_domain_kosong_mengembalikan_none():
    """
    Jika AC-3 membuat suatu domain menjadi kosong total,
    fungsi harus mengembalikan None (menandakan CSP tidak punya solusi).
    """
    domains = {
        "Andi": ["Pagi"],
        "Budi": ["Pagi"],  # cuma ada 1 opsi dan itu sama dengan Andi
    }
    arcs = [("Budi", "Andi")]

    def constraint_check(assignment):
        if "Andi" in assignment and "Budi" in assignment:
            return assignment["Andi"] != assignment["Budi"]
        return True

    hasil_domains = ac3(domains, arcs, constraint_check)
    assert hasil_domains is None, "AC-3 harus mendeteksi domain kosong dan return None"
