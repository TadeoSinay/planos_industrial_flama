"""Medidas del plano, discos por igualdad de superficie, puentes, demanda y patrones de la bobina madre (opción C).
Los mismos cálculos van como fórmulas en el Excel; acá se usan para el LP de patrones y para los Word."""
import itertools
import math
import os
import sys

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recargas"))
import actualizar_manuales_carros as _A  # noqa: E402

_PED = _A.pedidos()
# Proyecciones (terminados y cilindros, 1 a 100 kg) y sustitutos ABC de las plantas de recargas (alta, paso 4)
D = {"TERM": _A.TERM_MAN + _A.TERM_CAR, "CIL": _A.CIL_MAN + _A.CIL_CAR, "IND": _PED["Industrial"],
     "COM": _PED["Comercial"], "S_ALTA": _A.g.S_ALTA, "URL": _A.g.URL_PROY, "PEGAR": _A.g.PEGAR}
FORM = ["1 kg", "2,5 kg", "5 kg", "10 kg", "25 kg", "50 kg", "70 kg", "100 kg"]
ANIOS = list(range(2026, 2036))
# unidades a fabricar = terminados + cilindros vacíos + sustitutos (industrial terminados + comercial cilindros)
UNID = {f: [D["TERM"][i][y] + D["CIL"][i][y] + D["IND"][i][y] + D["COM"][i][y] for y in range(10)]
        for i, f in enumerate(FORM)}

# cuerpos: alto (modelo 3D del plano) y desarrollo π·(Ø − e); 1 kg en chapa 0,9 (decisión del grupo)
DENS = 7.87
CUERPO = {  # formato: (alto, desarrollo, espesor, hoja ancho, hoja largo, acero)
    "1 kg": (263.5, 236.5, 0.9, 1220, 2440, "LAF"),
    "2,5 kg": (267.5, 385.5, 1.25, 1220, 2440, "LAF"),
    "5 kg": (327.5, 475.5, 1.6, 1000, 2000, "LAF"),
    "10 kg": (493.0, 564.0, 2.0, 1500, 3000, "LAF"),
    "25 kg": (493.0, 858.5, 3.2, 1500, 3000, "LAC"),
    "50 kg": (640.0, 995.5, 3.2, 1500, 3000, "LAC"),
    "70 kg": (680.0, 1210.5, 4.75, 1500, 3000, "LAC"),
    "100 kg": (900.0, 1210.5, 4.75, 1500, 3000, "LAC"),
}
CUERPO_EXACTO = {"1 kg": (263.39, math.pi * (76.2 - 0.9)), "2,5 kg": (267.36, math.pi * (124 - 1.25)),
                 "5 kg": (327.29, math.pi * (153 - 1.6)), "10 kg": (493.06, math.pi * (181.5 - 2.0)),
                 "25 kg": (493.0, math.pi * (276.5 - 3.2)), "50 kg": (640.0, math.pi * (320 - 3.2)),
                 "70 kg": (680.0, math.pi * (390 - 4.75)), "100 kg": (900.0, math.pi * (390 - 4.75))}
PLANO = {"1 kg": 'Plano recipiente 1 kg 3" R1', "2,5 kg": "Plano recipiente 2,5 kg R2",
         "5 kg": "Plano recipiente 5 kg R2", "10 kg": "Plano recipiente 10 kg R2",
         "25 kg": "Plano recipiente 25 kg R3", "50 kg": "Plano recipiente 50 kg R2",
         "70 kg": "Plano extintor rodante 70 kg (Ø390)", "100 kg": "Plano extintor rodante 100 kg R1 (Ø390)"}

# discos: (formato, pieza, perfil, e, Ø ext, h, pollera/pestaña)
#   casquete: semielipsoide de semiejes a = Ø/2 − e/2, b = h − p − e/2 + pollera recta p
#   cóncavo: paraboloide de radio ρ = Ø/2 − e/2 y profundidad h + pestaña recta p (Ø = 2·(R − e del cuerpo))
DISCOS = [
    ("1 kg", "Cúpula", "casquete", 0.9, 76.2, 12.5, 6.0),
    ("1 kg", "Fondo", "casquete", 1.25, 76.2, 22.0, 6.0),
    ("2,5 kg", "Cúpula", "casquete", 1.25, 124.0, 39.5, 6.0),
    ("2,5 kg", "Fondo", "concavo", 1.25, 121.5, 10.5, 10.0),
    ("5 kg", "Cúpula", "casquete", 1.6, 153.0, 54.5, 6.0),
    ("5 kg", "Fondo", "concavo", 1.6, 149.8, 16.0, 10.0),
    ("10 kg", "Cúpula", "casquete", 1.6, 181.5, 62.5, 6.0),
    ("10 kg", "Fondo", "concavo", 2.0, 177.5, 11.7, 10.0),
]
M1 = [(0.08, 0.15, 0.63), (0.15, 0.3, 0.60), (0.3, 0.6, 0.58), (0.6, 1.0, 0.55), (1.0, 1.5, 0.53), (1.5, 2.0, 0.50)]
PUENTE_F, PUENTE_MIN, BORDE_F = 1.5, 0.7, 1.5


def area(perfil, e, d_ext, h, p):
    a = d_ext / 2 - e / 2
    if perfil == "casquete":
        b = h - p - e / 2
        ecc = math.sqrt(1 - (b / a) ** 2)
        return a, b, math.pi * a * a + math.pi * b * b / (2 * ecc) * math.log((1 + ecc) / (1 - ecc)) + 2 * math.pi * a * p
    k = h / a ** 2
    return a, h, math.pi / (6 * k * k) * ((1 + 4 * k * k * a * a) ** 1.5 - 1) + 2 * math.pi * a * p


def disco(fila):
    f, pz, perfil, e, d_ext, h, p = fila
    a, b, A = area(perfil, e, d_ext, h, p)
    d0 = math.sqrt(4 * A / math.pi)
    d0a = math.ceil(d0 * 2) / 2
    d = 2 * a
    m = d / d0a
    td = e / d0a * 100
    m1 = [x[2] for x in M1 if td >= x[0]][-1]
    puente = max(PUENTE_F * e, PUENTE_MIN)
    borde = BORDE_F * puente
    hd = (h if perfil == "casquete" else h + p) / d_ext
    return dict(formato=f, pieza=pz, perfil=perfil, e=e, d_ext=d_ext, h=h, p=p, a=a, b=b, A=A, d0=d0, d0a=d0a,
                d=d, m=m, td=td, m1=m1, ok=m >= m1, hd=hd, puente=puente, borde=borde,
                ancho=d0a + 2 * borde, paso=d0a + puente, masa=math.pi * d0a ** 2 / 4 * e * DENS / 1e6)


DISC = [disco(x) for x in DISCOS]


def _patrones(anchos, util):
    lim = [int(util // w) for w in anchos]
    out = []
    for n in itertools.product(*[range(x + 1) for x in lim]):
        s = sum(a * b for a, b in zip(n, anchos))
        if 0 < s <= util and all(s + w > util for w in anchos):     # solo patrones que no admiten otra tira
            out.append(n)
    return out


def lp_grupo(tiras, madre, margen=10.0, max_pat=3):
    """tiras: lista de (nombre, ancho, avance, formato). Devuelve patrones (≤3) y participaciones."""
    anchos = [t[1] for t in tiras]
    pats = _patrones(anchos, madre - margen)
    need = np.array([sum(UNID[t[3]]) * t[2] / 1000 for t in tiras])       # metros de cada tira en 10 años
    n = len(pats)
    A = np.array(pats, dtype=float).T                                     # tiras × patrones
    big = need.sum() * 10
    c = np.concatenate([np.ones(n), np.zeros(n)])
    cons = [LinearConstraint(np.hstack([A, np.zeros_like(A)]), need, np.inf),
            LinearConstraint(np.hstack([np.eye(n), -big * np.eye(n)]), -np.inf, 0),
            LinearConstraint(np.concatenate([np.zeros(n), np.ones(n)])[None, :], 0, max_pat)]
    integ = np.concatenate([np.zeros(n), np.ones(n)])
    r = milp(c, constraints=cons, integrality=integ, bounds=Bounds(0, np.concatenate([np.full(n, np.inf), np.ones(n)])))
    x = r.x[:n]
    usados = [j for j in range(n) if x[j] > 1e-6]
    usados.sort(key=lambda j: -x[j])
    tot = sum(x[j] for j in usados)
    part = [round(x[j] / tot, 4) for j in usados]
    part[0] = round(1 - sum(part[1:]), 4)
    return [pats[j] for j in usados], part


def metros_anuales(tiras, pats, part):
    H = [sum(p[i] * w for p, w in zip(pats, part)) for i in range(len(tiras))]
    return [max(UNID[t[3]][y] * t[2] / 1000 / H[i] for i, t in enumerate(tiras)) for y in range(10)]


def tiras_grupo(g, orient):
    """Tiras de cada grupo de espesor (opción C) en el orden de las filas de BobinaMadre."""
    def cuerpo(f, o):
        al, de = CUERPO[f][:2]
        return (f"Cuerpo {f}", al, de, f) if o == 1 else (f"Cuerpo {f}", de, al, f)

    def dsc(f, pz):
        d = next(x for x in DISC if x["formato"] == f and x["pieza"] == pz)
        return (f"{pz} {f}", d["ancho"], d["paso"], f)
    return {
        "0,9": [dsc("1 kg", "Cúpula"), cuerpo("1 kg", orient)],
        "1,25": [cuerpo("2,5 kg", orient), dsc("2,5 kg", "Cúpula"), dsc("2,5 kg", "Fondo"), dsc("1 kg", "Fondo")],
        "1,6": [cuerpo("5 kg", orient), dsc("5 kg", "Cúpula"), dsc("5 kg", "Fondo"), dsc("10 kg", "Cúpula")],
        "2,0": [cuerpo("10 kg", orient), dsc("10 kg", "Fondo")],
        "3,2": [cuerpo("25 kg", orient), cuerpo("50 kg", orient)],
    }[g]


MADRE = {"0,9": 1220, "1,25": 1000, "1,6": 1000, "2,0": 1000, "3,2": 1500}


def patrones_c():
    out = {}
    for g, B in MADRE.items():
        best = None
        for o in (1, 2):
            t = tiras_grupo(g, o)
            pats, part = lp_grupo(t, B)
            tot = sum(metros_anuales(t, pats, part))
            if best is None or tot < best[0] - 1e-6:
                best = (tot, o, pats, part, t)
        out[g] = dict(orient=best[1], pats=best[2], part=best[3], tiras=best[4], metros=best[0])
    return out


if __name__ == "__main__":
    for d in DISC:
        print(f"{d['pieza']:6} {d['formato']:6} e={d['e']:4} A={d['A']:8.0f} D0={d['d0']:6.1f} → {d['d0a']:5.1f}  "
              f"m={d['m']:.3f} m1={d['m1']} ok={d['ok']} h/d={d['hd']:.2f} ancho={d['ancho']:.2f} paso={d['paso']:.2f}")
    print({f: round(UNID[f][-1]) for f in FORM})
    for g, r in patrones_c().items():
        print(g, "orient", r["orient"], r["pats"], r["part"], round(r["metros"]))
