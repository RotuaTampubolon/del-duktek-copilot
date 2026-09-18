"""
Modul Baseline Search — Del-Duktek Copilot
Implementasi Uniform Cost Search (UCS) dan A* Search
untuk menentukan jalur eskalasi tiket dengan biaya penanganan minimum
pada graf alur kerja unit Dukungan Teknis (Duktek) IT Del.

Struktur data priority queue menggunakan heapq (min-heap).
"""

import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(order=True)
class PrioritizedNode:
    priority: float
    node: str = field(compare=False)
    path: List[str] = field(compare=False)


class DuktekEscalationGraph:
    """
    Merepresentasikan graf ruang keadaan (X, A, T, G, C) alur eskalasi
    laporan gangguan pada unit Duktek IT Del.
    Bobot edge merepresentasikan estimasi waktu penanganan riil (menit).
    """

    def __init__(self):
        # Representasi graf berarah berbobot: adjacency list
        self.graph: Dict[str, List[Tuple[str, float]]] = {}

    def add_edge(self, asal: str, tujuan: str, biaya: float):
        self.graph.setdefault(asal, []).append((tujuan, biaya))
        self.graph.setdefault(tujuan, [])

    def get_neighbors(self, node: str) -> List[Tuple[str, float]]:
        return self.graph.get(node, [])


def uniform_cost_search(
    graph: DuktekEscalationGraph, start: str, goal: str
) -> Optional[Tuple[List[str], float]]:
    """
    Uniform Cost Search: menemukan jalur eskalasi dengan akumulasi
    biaya (waktu penanganan) minimum dari simpul awal ke simpul tujuan.
    Kompleksitas ruang/waktu: O(b^(1 + C*/eps)) — konsisten dengan
    kerangka teori UCS pada Russell & Norvig.
    """
    frontier: List[PrioritizedNode] = []
    heapq.heappush(frontier, PrioritizedNode(0.0, start, [start]))
    visited_cost: Dict[str, float] = {start: 0.0}

    while frontier:
        current = heapq.heappop(frontier)

        if current.node == goal:
            return current.path, current.priority

        # Lewati simpul yang sudah ditemukan jalur lebih murah sebelumnya
        if current.priority > visited_cost.get(current.node, float("inf")):
            continue

        for neighbor, biaya_edge in graph.get_neighbors(current.node):
            biaya_baru = current.priority + biaya_edge
            if biaya_baru < visited_cost.get(neighbor, float("inf")):
                visited_cost[neighbor] = biaya_baru
                heapq.heappush(
                    frontier,
                    PrioritizedNode(biaya_baru, neighbor, current.path + [neighbor]),
                )

    return None  # Tujuan tidak dapat dijangkau


def a_star_search(
    graph: DuktekEscalationGraph,
    start: str,
    goal: str,
    heuristic: Dict[str, float],
) -> Optional[Tuple[List[str], float]]:
    """
    A* Search: memperluas UCS dengan fungsi evaluasi f(n) = g(n) + h(n),
    di mana h(n) adalah estimasi biaya tersisa (heuristik) menuju goal.
    Heuristik harus bersifat admissible agar solusi tetap optimal.
    """
    frontier: List[PrioritizedNode] = []
    g_score: Dict[str, float] = {start: 0.0}
    f_start = heuristic.get(start, 0.0)
    heapq.heappush(frontier, PrioritizedNode(f_start, start, [start]))

    while frontier:
        current = heapq.heappop(frontier)
        current_g = g_score[current.node]

        if current.node == goal:
            return current.path, current_g

        for neighbor, biaya_edge in graph.get_neighbors(current.node):
            tentative_g = current_g + biaya_edge
            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic.get(neighbor, 0.0)
                heapq.heappush(
                    frontier,
                    PrioritizedNode(f_score, neighbor, current.path + [neighbor]),
                )

    return None


def bangun_graf_studi_kasus() -> DuktekEscalationGraph:
    """
    Membangun graf studi kasus alur eskalasi tiket Duktek berdasarkan
    estimasi rata-rata waktu penanganan (menit) antarunit.
    """
    g = DuktekEscalationGraph()
    g.add_edge("Loket_Penerimaan", "Triase_Otomatis", 2)
    g.add_edge("Triase_Otomatis", "Tim_Jaringan", 15)
    g.add_edge("Triase_Otomatis", "Tim_Hardware_Lab", 20)
    g.add_edge("Triase_Otomatis", "Tim_Perangkat_Mahasiswa", 10)
    g.add_edge("Tim_Jaringan", "Selesai_Jaringan", 30)
    g.add_edge("Tim_Hardware_Lab", "Vendor_Eksternal", 45)
    g.add_edge("Tim_Hardware_Lab", "Selesai_Hardware", 25)
    g.add_edge("Vendor_Eksternal", "Selesai_Hardware", 60)
    g.add_edge("Tim_Perangkat_Mahasiswa", "Selesai_Mahasiswa", 18)
    return g


if __name__ == "__main__":
    graf_duktek = bangun_graf_studi_kasus()

    # --- Studi Kasus: Eskalasi laporan kerusakan hardware laboratorium ---
    hasil_ucs = uniform_cost_search(
        graf_duktek, start="Loket_Penerimaan", goal="Selesai_Hardware"
    )
    if hasil_ucs:
        jalur, total_biaya = hasil_ucs
        print("[UCS] Jalur eskalasi optimal:", " -> ".join(jalur))
        print(f"[UCS] Estimasi total waktu penanganan: {total_biaya} menit")

    # --- Heuristik admissible: estimasi kasar sisa waktu menuju goal ---
    heuristik_estimasi = {
        "Loket_Penerimaan": 40,
        "Triase_Otomatis": 35,
        "Tim_Jaringan": 100,
        "Tim_Hardware_Lab": 20,
        "Tim_Perangkat_Mahasiswa": 100,
        "Vendor_Eksternal": 55,
        "Selesai_Hardware": 0,
        "Selesai_Jaringan": 0,
        "Selesai_Mahasiswa": 0,
    }

    hasil_astar = a_star_search(
        graf_duktek,
        start="Loket_Penerimaan",
        goal="Selesai_Hardware",
        heuristic=heuristik_estimasi,
    )
    if hasil_astar:
        jalur, total_biaya = hasil_astar
        print("[A*] Jalur eskalasi optimal:", " -> ".join(jalur))
        print(f"[A*] Estimasi total waktu penanganan: {total_biaya} menit")[[8]]