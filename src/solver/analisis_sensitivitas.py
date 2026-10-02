"""
Analisis Sensitivitas — Modul CSP Solver Del-Duktek Copilot
Mengukur performa solver (waktu konvergensi) terhadap variasi
ukuran masalah (jumlah teknisi), sesuai kebutuhan Luaran #3 Milestone 2.
"""

import time
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(__file__))

from solver import backtracking_search, constraint_semua_shift_terisi
from solver import backtracking_search, constraint_semua_shift_terisi


def uji_sensitivitas(jumlah_teknisi_list):
    """Menjalankan solver pada berbagai ukuran masalah dan mencatat waktunya."""
    hasil_waktu = []

    for n in jumlah_teknisi_list:
        variables = [f"Teknisi_{i}" for i in range(n)]
        domains = {v: ["Pagi", "Siang", "Malam"] for v in variables}
        constraints = [lambda a: constraint_semua_shift_terisi(a, variables)]

        t0 = time.perf_counter()
        backtracking_search(domains, variables, constraints)
        durasi = (time.perf_counter() - t0) * 1000

        hasil_waktu.append((n, durasi))
        print(f"Jumlah teknisi: {n:>3} -> waktu: {durasi:.2f} ms")

    return hasil_waktu


def plot_hasil(hasil_waktu):
    """Membuat grafik waktu eksekusi solver terhadap jumlah teknisi."""
    jumlah, waktu = zip(*hasil_waktu)
    plt.plot(jumlah, waktu, marker="o")
    plt.xlabel("Jumlah Teknisi")
    plt.ylabel("Waktu Eksekusi (ms)")
    plt.title("Analisis Sensitivitas: Waktu Konvergensi CSP Solver")
    plt.grid(True)
    plt.savefig("docs/analisis-sensitivitas.png")
    plt.show()


if __name__ == "__main__":
    print("=== Analisis Sensitivitas: Waktu Konvergensi vs Ukuran Masalah ===\n")
    hasil = uji_sensitivitas([4, 8, 16, 32, 64])

    print("\n=== Ringkasan ===")
    for n, waktu in hasil:
        print(f"{n} teknisi: {waktu:.2f} ms")

    plot_hasil(hasil)