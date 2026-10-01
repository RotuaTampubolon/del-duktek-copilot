"""
Modul Business Constraint Solver — Del-Duktek Copilot
Implementasi CSP dengan AC-3 (constraint propagation) dan
Backtracking Search dengan heuristik MRV
untuk penjadwalan shift teknisi unit Dukungan Teknis (Duktek) IT Del.
"""

from typing import Dict, List, Optional
import copy


class CSPScheduler:
    def __init__(self, variables: List[str], domains: Dict[str, List[str]], constraints: List):
        self.variables = variables
        self.domains = domains          # dict: {variabel: [list domain]}
        self.constraints = constraints  # list of constraint functions


## constraint sebagai fungsi
def constraint_andi_budi_beda_shift(assignment: Dict[str, str]) -> bool:
    """C2: Andi dan Budi tidak boleh dapat shift yang sama."""
    if "Andi" in assignment and "Budi" in assignment:
        return assignment["Andi"] != assignment["Budi"]
    return True  # belum keduanya terisi, jadi belum bisa dicek -> anggap valid dulu


def constraint_citra_tidak_malam(assignment: Dict[str, str]) -> bool:
    """C3: Citra tidak bisa shift malam."""
    if "Citra" in assignment:
        return assignment["Citra"] != "Malam"
    return True


def constraint_semua_shift_terisi(assignment: Dict[str, str], semua_variabel: List[str]) -> bool:
    """C1: Setiap shift harus terisi minimal 1 teknisi (dicek saat assignment lengkap)."""
    if len(assignment) < len(semua_variabel):
        return True  # belum lengkap, belum bisa dicek final
    shift_terisi = set(assignment.values())
    return shift_terisi == {"Pagi", "Siang", "Malam"}


## Implementasi AC-3 (Arc Consistency)
from collections import deque

def ac3(domains: Dict[str, List[str]], arcs: List[tuple], constraint_check) -> Dict[str, List[str]]:
    """
    Algoritma AC-3: mempersempit domain dengan memeriksa konsistensi
    antar pasangan variabel (arc) secara berulang sampai stabil.
    """
    domains = copy.deepcopy(domains)
    queue = deque(arcs)

    while queue:
        (xi, xj) = queue.popleft()
        if revise(domains, xi, xj, constraint_check):
            if len(domains[xi]) == 0:
                return None  # domain kosong -> tidak ada solusi
            # jika domain xi berubah, arc yang mengarah ke xi perlu dicek ulang
            tetangga = [arc for arc in arcs if arc[1] == xi and arc[0] != xj]
            queue.extend(tetangga)

    return domains


def revise(domains, xi, xj, constraint_check) -> bool:
    """Menghapus nilai dari domain xi yang tidak konsisten dengan xj."""
    revised = False
    for nilai_xi in domains[xi][:]:
        # cek apakah ada minimal 1 nilai di domain xj yang membuat pasangan ini valid
        ada_yang_valid = any(
            constraint_check({xi: nilai_xi, xj: nilai_xj})
            for nilai_xj in domains[xj]
        )
        if not ada_yang_valid:
            domains[xi].remove(nilai_xi)
            revised = True
    return revised


## Implementasi Backtracking Search dengan heuristik MRV
def pilih_variabel_mrv(assignment: Dict[str, str], domains: Dict[str, List[str]], variables: List[str]) -> str:
    """Heuristik MRV: pilih variabel belum terisi dengan domain tersisa paling sedikit."""
    belum_terisi = [v for v in variables if v not in assignment]
    return min(belum_terisi, key=lambda var: len(domains[var]))


def is_consistent(var: str, nilai: str, assignment: Dict[str, str], constraints: List) -> bool:
    """Cek apakah menetapkan nilai ke var melanggar batasan yang ada."""
    percobaan = {**assignment, var: nilai}
    return all(c(percobaan) for c in constraints)


def backtracking_search(
    domains: Dict[str, List[str]],
    variables: List[str],
    constraints: List,
    assignment: Optional[Dict[str, str]] = None,
) -> Optional[Dict[str, str]]:
    """
    Backtracking Search dengan heuristik MRV untuk menyelesaikan CSP
    penjadwalan shift teknisi Duktek.
    """
    if assignment is None:
        assignment = {}

    if len(assignment) == len(variables):
        return assignment  # semua variabel sudah terisi dan valid

    var = pilih_variabel_mrv(assignment, domains, variables)

    for nilai in domains[var]:
        if is_consistent(var, nilai, assignment, constraints):
            assignment[var] = nilai
            hasil = backtracking_search(domains, variables, constraints, assignment)
            if hasil is not None:
                return hasil
            del assignment[var]  # backtrack: batalkan pilihan, coba nilai lain

    return None  # tidak ada solusi dari cabang ini


## Rangkai di fungsi utama
def constraint_check_untuk_ac3(assignment: Dict[str, str]) -> bool:
    """Constraint check sederhana khusus untuk AC-3 (pengecekan pasangan)."""
    return constraint_andi_budi_beda_shift(assignment) and constraint_citra_tidak_malam(assignment)


if __name__ == "__main__":
    variables = ["Andi", "Budi", "Citra", "Dewi"]
    domains = {
        "Andi": ["Pagi", "Siang", "Malam"],
        "Budi": ["Pagi", "Siang", "Malam"],
        "Citra": ["Pagi", "Siang", "Malam"],
        "Dewi": ["Pagi", "Siang", "Malam"],
    }

    arcs = [("Andi", "Budi"), ("Budi", "Andi")]  # arc untuk C2

    print("[AC-3] Domain sebelum propagasi:", domains)
    domains_setelah_ac3 = ac3(domains, arcs, constraint_check_untuk_ac3)
    print("[AC-3] Domain setelah propagasi:", domains_setelah_ac3)

    constraints_final = [
        constraint_andi_budi_beda_shift,
        constraint_citra_tidak_malam,
        lambda a: constraint_semua_shift_terisi(a, variables),
    ]

    hasil = backtracking_search(domains_setelah_ac3, variables, constraints_final)

    if hasil:
        print("[HASIL] Jadwal shift ditemukan:")
        for teknisi, shift in hasil.items():
            print(f"  {teknisi}: {shift}")
    else:
        print("[HASIL] Tidak ditemukan jadwal yang memenuhi semua batasan.")