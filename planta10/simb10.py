"""Símbolos de planta que faltaban para el layout v10 (vista superior a escala real).

Se registran en planta/simbolos.py (SIMBOLOS y SIN_PUESTO) al importar este módulo, así `S.dibujar` los usa igual
que a los demás. Cada símbolo se dibuja en el marco local (u a lo largo del frente, v hacia el fondo).
"""

import math

from planta import simbolos as S
from planta import dibujo as D

CONT, FINO, OC, SEG = S.CONT, S.FINO, S.OC, S.SEG
GRIS, GRIS2, OSCURO, MADERA, AGUA, BLANCO = S.GRIS, S.GRIS2, S.OSCURO, S.MADERA, S.AGUA, S.BLANCO
ROJO = (225, 60, 50)

# demarcación de piso IRAM 10005: amarillo (circulación y pulmones), verde (liberado), rojo (no conforme)
D.CAPAS_PLANTA.setdefault("A-DEM-AM", (2, 35, "CONTINUOUS", (215, 165, 0), "Demarcación amarilla de piso"))
D.CAPAS_PLANTA.setdefault("A-DEM-VE", (3, 35, "CONTINUOUS", (0, 150, 60), "Demarcación verde de piso (liberado)"))
D.CAPAS_PLANTA.setdefault("A-DEM-RO", (1, 35, "CONTINUOUS", (210, 30, 30), "Demarcación roja de piso (no conforme)"))
DEM = {"AM": "A-DEM-AM", "VE": "A-DEM-VE", "RO": "A-DEM-RO"}


def rodante(m, u, v, s=1.0):
    """Extintor rodante visto desde arriba: cuerpo, dos ruedas a los costados, pata y manija (hacia +v)."""
    r = 0.17 * s
    m.fc(u, v, r, (240, 120, 110))
    m.ci(u, v, r, CONT)
    m.ci(u, v, 0.05 * s)
    for k in (-1, 1):
        m.caja(u + k * (r + 0.05 * s) - 0.03 * s, v - 0.15 * s, u + k * (r + 0.05 * s) + 0.03 * s, v + 0.13 * s,
               OSCURO, FINO)
    m.pl([(u - 0.13 * s, v + r), (u - 0.13 * s, v + r + 0.12 * s), (u + 0.13 * s, v + r + 0.12 * s),
          (u + 0.13 * s, v + r)], CONT)
    m.ln((u - 0.06 * s, v - r), (u + 0.06 * s, v - r - 0.06 * s), FINO)


def rodantes(m, nu, nv, capa="A-DEM-AM", n=None):
    """Lugares demarcados para nu × nv carros (filas a lo largo de u, enfrentadas de a dos con la manija afuera)."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, capa)
    du, dv = U / nu, V / nv
    k = 0
    for j in range(nv):
        for i in range(nu):
            if n is not None and k >= n:
                break
            u, v = (i + 0.5) * du, (j + 0.5) * dv
            m.rc(i * du + 0.03, j * dv + 0.03, (i + 1) * du - 0.03, (j + 1) * dv - 0.03, FINO)
            # en un par de filas la de abajo mira hacia abajo y la de arriba hacia arriba
            if j % 2 == 0 and nv > 1:
                rodante_inv(m, u, v)
            else:
                rodante(m, u, v)
            k += 1
        if j % 2 == 0 and j + 1 < nv:
            m.ln((0, (j + 1) * dv), (U, (j + 1) * dv), capa)


def rodante_u(m, u, v, s=1.0):
    """Carro visto desde arriba con la manija hacia -u (para filas de carros uno detrás del otro)."""
    r = 0.16 * s
    m.fc(u, v, r, (240, 120, 110))
    m.ci(u, v, r, CONT)
    m.ci(u, v, 0.045 * s)
    for k in (-1, 1):
        m.caja(u - 0.12 * s, v + k * (r + 0.04 * s) - 0.025 * s, u + 0.12 * s, v + k * (r + 0.04 * s) + 0.025 * s,
               OSCURO, FINO)
    m.pl([(u - r, v - 0.11 * s), (u - r - 0.1 * s, v - 0.11 * s), (u - r - 0.1 * s, v + 0.11 * s),
          (u - r, v + 0.11 * s)], CONT)


def filas(m, por_fila, n_filas, capa="A-DEM-AM", n=None):
    """Filas demarcadas de carros uno detrás del otro (a lo largo de u), apiladas en v; la manija hacia u = 0."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, capa)
    du, dv = U / por_fila, V / n_filas
    s = min(1.0, dv / 0.62, du / 0.6)
    k = 0
    for j in range(n_filas):
        if j:
            m.ln((0, j * dv), (U, j * dv), capa)
        for i in range(por_fila):
            if n is not None and k >= n:
                break
            rodante_u(m, (i + 0.55) * du, (j + 0.5) * dv, s)
            k += 1


def rodante_inv(m, u, v, s=1.0):
    r = 0.17 * s
    m.fc(u, v, r, (240, 120, 110))
    m.ci(u, v, r, CONT)
    m.ci(u, v, 0.05 * s)
    for k in (-1, 1):
        m.caja(u + k * (r + 0.05 * s) - 0.03 * s, v - 0.13 * s, u + k * (r + 0.05 * s) + 0.03 * s, v + 0.15 * s,
               OSCURO, FINO)
    m.pl([(u - 0.13 * s, v - r), (u - 0.13 * s, v - r - 0.12 * s), (u + 0.13 * s, v - r - 0.12 * s),
          (u + 0.13 * s, v - r)], CONT)


def ruedas(m, u0, v0, u1, v1, d=0.05):
    for uu, vv in ((u0 + 0.07, v0 + 0.07), (u1 - 0.07, v0 + 0.07), (u0 + 0.07, v1 - 0.07), (u1 - 0.07, v1 - 0.07)):
        m.ci(uu, vv, d)


def manija(m, u0, u1, v):
    m.pl([(u0 + 0.1, v), (u0 + 0.1, v + 0.12), (u1 - 0.1, v + 0.12), (u1 - 0.1, v)], CONT)


def efe(m):
    """Carro portaplacas EFE 600: bastidor con separadores verticales y las chapas paradas."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS)
    for k in range(1, 6):
        m.ln((U * k / 6, 0.06), (U * k / 6, V - 0.06), CONT)
    m.rc(0.05, V * 0.35, U - 0.05, V * 0.65, OC)
    ruedas(m, 0, 0, U, V)


def mesa_movil(m):
    """Mesa móvil con ruedas (cuerpos de 70 y 100 kg): tablero, ruedas y manija."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, MADERA)
    m.rc(0.08, 0.08, U - 0.08, V - 0.08)
    ruedas(m, 0, 0, U, V)
    manija(m, 0, U, V)


def carro_plat(m):
    """Carro de plataforma (salida, kits, cajas o fondos): bandeja con borde, ruedas y manija."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS)
    m.rc(0.05, 0.05, U - 0.05, V - 0.05)
    for k in (0.33, 0.66):
        m.ln((U * k, 0.05), (U * k, V - 0.05))
    ruedas(m, 0, 0, U, V)
    manija(m, 0, U, V)


def fchp(m):
    """Carro FCHP20505 de 3 planos (manuales): bandeja con cuerpos parados vistos desde arriba."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS, FINO)
    m.cilindros(0.06, 0.06, U - 0.06, V - 0.06, 0.2)
    ruedas(m, 0, 0, U, V, 0.04)


def carro_caj(m):
    """Carro de estantes para 12 cajones plásticos de 600 × 400 mm (manuales)."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS, FINO)
    nu, nv = max(1, round(U / 0.6)), max(1, round(V / 0.4))
    for i in range(nu):
        for j in range(nv):
            m.caja(i * U / nu + 0.04, j * V / nv + 0.04, (i + 1) * U / nu - 0.04, (j + 1) * V / nv - 0.04,
                   (250, 236, 200), FINO)
    ruedas(m, 0, 0, U, V, 0.04)


def canasto(m):
    """Canasto de malla (enfriamiento o carro canasto) con cúpulas adentro."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (245, 245, 245))
    m.malla(0.03, 0.03, U - 0.03, V - 0.03, paso=0.3, e=0.03)
    m.cilindros(0.1, 0.1, U - 0.1, V - 0.1, 0.22)


def cuna(m):
    """Cuna volcadora: dos largueros en V con el cilindro acostado y el pivote."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS2, FINO)
    m.ln((0.05, V * 0.15), (U - 0.05, V * 0.15), CONT)
    m.ln((0.05, V * 0.85), (U - 0.05, V * 0.85), CONT)
    m.rc(0.12, V * 0.28, U - 0.12, V * 0.72, OC)
    m.ci(0.08, V / 2, 0.05, CONT)
    m.ci(U - 0.08, V / 2, 0.05, CONT)


def soldadora(m):
    """Soldadora MIG/MAG (Pampa 300 o MIG-350IX) con el tubo de gas encadenado al lado."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U * 0.68, V, (215, 225, 235))
    m.rc(0.05, 0.05, U * 0.3, V - 0.05)
    m.ci(U * 0.48, V * 0.5, min(U, V) * 0.12)
    r = min(U * 0.15, V * 0.32)
    m.fc(U * 0.84, V * 0.5, r, (190, 210, 190))
    m.ci(U * 0.84, V * 0.5, r, CONT)
    m.ci(U * 0.84, V * 0.5, r * 0.35)


def chiller(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (215, 230, 245))
    m.ventilador(U / 2, V / 2, min(U, V) * 0.38)


def tablero_herr(m):
    """Tablero de herramientas o de planillas (pared): panel con siluetas de herramientas."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, MADERA)
    for k in range(1, 5):
        m.ln((U * k / 5, V * 0.2), (U * k / 5, V * 0.8))


def cajonera(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS)
    for k in range(1, 4):
        m.ln((0.03, V * k / 4), (U - 0.03, V * k / 4))
    ruedas(m, 0, 0, U, V, 0.03)


def cajones(m):
    """Cajones de ejes o de piezas sobre el piso."""
    U, V = m.Lu, m.Lv
    n = max(1, round(U / 0.4))
    for i in range(n):
        m.caja(i * U / n + 0.02, 0.02, (i + 1) * U / n - 0.02, V - 0.02, (250, 236, 200))
        m.ln((i * U / n + 0.06, V * 0.5), ((i + 1) * U / n - 0.06, V * 0.5))


def dobladora(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (215, 225, 215))
    m.ci(U * 0.5, V * 0.6, min(U, V) * 0.28, CONT)
    m.ci(U * 0.5, V * 0.6, min(U, V) * 0.1)
    m.ln((0.05, V * 0.2), (U - 0.05, V * 0.2), CONT)


def taladro(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS)
    m.ci(U * 0.5, V * 0.45, min(U, V) * 0.3, CONT)
    m.ci(U * 0.5, V * 0.45, 0.03)
    m.caja(U * 0.35, V * 0.8, U * 0.65, V - 0.02, GRIS2, FINO)


def prensa_h(m):
    """Prensa hidráulica de taller (20 t): bastidor en H, cilindro y mesa."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (225, 230, 236))
    m.caja(0.05, 0.05, 0.2, V - 0.05, OSCURO, FINO)
    m.caja(U - 0.2, 0.05, U - 0.05, V - 0.05, OSCURO, FINO)
    m.ci(U / 2, V / 2, min(U, V) * 0.22, CONT)
    m.rc(0.25, V * 0.25, U - 0.25, V * 0.75)


def caballetes(m):
    """Caballetes con rodillo, sensitiva y tope: la barra entra sin levantarla."""
    U, V = m.Lu, m.Lv
    m.ln((0.0, V * 0.5), (U, V * 0.5), OC)
    for uu in (0.4, U * 0.35):
        m.caja(uu - 0.2, 0.05, uu + 0.2, V - 0.05, GRIS2, FINO)
        m.ln((uu - 0.15, V * 0.5), (uu + 0.15, V * 0.5), CONT)
    m.caja(U * 0.6, 0.0, U * 0.6 + 0.55, V, (215, 225, 235))      # sensitiva
    m.ci(U * 0.6 + 0.27, V * 0.5, min(0.18, V * 0.4), CONT)
    m.caja(U - 0.15, 0.1, U - 0.05, V - 0.1, ROJO, FINO)            # tope


def pantalla(m):
    """Pantalla rebatible de policarbonato (protección de la prueba hidráulica)."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, (200, 225, 245))
    m.rc(0, 0, U, V, CONT)
    for k in range(int(U / 0.6) + 1):
        m.poste(min(k * 0.6 + 0.03, U - 0.03), V / 2, 0.06)


def bandeja(m):
    """Puesto de prueba: bandeja con rejilla y rampa."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, AGUA)
    for k in range(1, int(U / 0.1)):
        m.ln((k * 0.1, 0.08), (k * 0.1, V - 0.08))
    m.rc(U * 0.25, -0.0, U * 0.75, 0.2, CONT)


def canaleta(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, AGUA)
    for k in range(1, int(U / 0.1)):
        m.ln((k * 0.1, 0.0), (k * 0.1, V))


def pozo(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, AGUA)
    m.ln((U / 2, 0), (U / 2, V), CONT)
    m.ln((0, 0), (U, V))


def bomba(m):
    U, V = m.Lu, m.Lv
    m.motor(0.05, V / 2, U * 0.55, V * 0.6)
    m.ci(U * 0.78, V / 2, min(U, V) * 0.32, CONT)
    m.ci(U * 0.78, V / 2, min(U, V) * 0.1)


def planilla(m):
    """Mesa o atril con planillas, manómetros patrón y cabezales."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, MADERA)
    m.rc(0.06, 0.06, U * 0.45, V - 0.06)
    for k in (0.6, 0.8):
        m.manometro(U * k, V * 0.5, min(U, V) * 0.15)


def tarima(m):
    """Tarima de carga con topes, bolsillos para las uñas y rampa enganchable (W-CAR 11)."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS)
    m.rc(0.05, 0.05, U - 0.05, V - 0.05, CONT)
    for uu in (U * 0.3, U * 0.7):
        m.rc(uu - 0.1, 0.05, uu + 0.1, V - 0.05, OC)
    for p in ((0.1, 0.1), (U - 0.1, 0.1), (0.1, V - 0.1), (U - 0.1, V - 0.1)):
        m.ci(p[0], p[1], 0.04)
    m.pl([(U * 0.25, V), (U * 0.25, V + 0.35), (U * 0.75, V + 0.35), (U * 0.75, V)], OC)


def cambio_juego(m):
    """Lugar de cambio de juego: carro sobre el crique, zorra de retorno y cajones de ejes y ruedas."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, "A-DEM-AM")
    rodante(m, U * 0.3, V * 0.5)
    m.caja(U * 0.3 - 0.12, V * 0.5 - 0.42, U * 0.3 + 0.12, V * 0.5 - 0.22, (220, 60, 60), FINO)   # crique
    m.caja(U * 0.58, 0.15, U - 0.08, V * 0.55, GRIS, FINO)                                       # zorra
    m.cilindros(U * 0.6, 0.2, U - 0.1, V * 0.5, 0.18)
    m.caja(U * 0.58, V * 0.65, U * 0.78, V - 0.1, (250, 236, 200), FINO)                          # cajones
    m.caja(U * 0.8, V * 0.65, U - 0.08, V - 0.1, (250, 236, 200), FINO)


def lugar(m):
    """Lugar demarcado de un carro (estación de trabajo sin máquina fija)."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, "A-DEM-AM")
    n = max(1, round(U / 1.0))
    for i in range(n):
        rodante(m, (i + 0.5) * U / n, V * 0.5)


def nc(m):
    """Zona de no conforme demarcada en rojo, con cruz."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, "A-DEM-RO")
    m.rc(0.06, 0.06, U - 0.06, V - 0.06, "A-DEM-RO")
    m.ln((0.06, 0.06), (U - 0.06, V - 0.06), "A-DEM-RO")
    m.ln((0.06, V - 0.06), (U - 0.06, 0.06), "A-DEM-RO")


def zona_carga(m):
    """Zona libre demarcada (carga axial, maniobra): borde amarillo con cebra en las esquinas."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, "A-DEM-AM")
    for k in range(int(min(U, V) / 0.2)):
        m.ln((0, k * 0.2), (k * 0.2, 0), "A-DEM-AM")


def bastidor(m):
    """Bastidor de descarga de big bag con tolva de 100 L y polipasto."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (250, 245, 225))
    for p in ((0.06, 0.06), (U - 0.06, 0.06), (0.06, V - 0.06), (U - 0.06, V - 0.06)):
        m.poste(p[0], p[1], 0.1)
    m.ci(U / 2, V / 2, min(U, V) * 0.38, CONT)
    m.rc(U / 2 - 0.2, V / 2 - 0.2, U / 2 + 0.2, V / 2 + 0.2, OC)
    m.ln((U / 2 - 0.2, V / 2 - 0.2), (U / 2 + 0.2, V / 2 + 0.2))


def split(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, BLANCO)
    for k in range(1, 6):
        m.ln((U * k / 6, 0.03), (U * k / 6, V - 0.03))


def colector10(m):
    """Colector de polvo con filtro de mangas y tolva."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (230, 230, 220))
    m.cilindros(0.08, 0.08, U - 0.08, V - 0.08, min(U, V) * 0.3)
    m.ventilador(U * 0.5, V * 0.5, min(U, V) * 0.15)


def recinto(m):
    """Recinto de descarga cerrado (alto 3 m): paneles, piso marcado cada 0,5 m y ventana."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (246, 246, 252))
    m.rc(0.1, 0.1, U - 0.1, V - 0.1, CONT)
    for k in range(1, int(U / 0.5)):
        m.ln((k * 0.5, 0.15), (k * 0.5, 0.35))
    m.ln((U * 0.4, V), (U * 0.7, V), "A-VENTANA")
    m.ci(0.6, V / 2, 0.17, CONT)


def estante(m):
    S.estanteria(m)


NUEVOS = {"efe": efe, "mesa_movil": mesa_movil, "carro_plat": carro_plat, "fchp": fchp, "carro_caj": carro_caj,
          "canasto": canasto, "cuna": cuna, "soldadora": soldadora, "chiller": chiller, "tablero_herr": tablero_herr,
          "cajonera": cajonera, "cajones": cajones, "dobladora": dobladora, "taladro": taladro, "prensa_h": prensa_h,
          "caballetes": caballetes, "pantalla": pantalla, "bandeja": bandeja, "canaleta": canaleta, "pozo": pozo,
          "bomba": bomba, "planilla": planilla, "tarima": tarima, "cambio_juego": cambio_juego, "lugar": lugar,
          "nc": nc, "zona_carga": zona_carga, "bastidor": bastidor, "split": split, "colector10": colector10,
          "recinto": recinto}
S.SIMBOLOS.update(NUEVOS)
S.SIN_PUESTO = tuple(S.SIN_PUESTO) + ("efe", "mesa_movil", "carro_plat", "fchp", "carro_caj", "canasto", "cuna",
                                      "soldadora", "chiller", "tablero_herr", "cajonera", "cajones", "pantalla",
                                      "canaleta", "pozo", "bomba", "tarima", "nc", "zona_carga", "bastidor", "split",
                                      "colector10", "recinto", "bandeja")
_ = math
