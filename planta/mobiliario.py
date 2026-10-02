"""Mobiliario y equipamiento menor de los locales (vista superior a escala real).

Cada mueble se apoya en un rectángulo del modelo y se dibuja en el marco local de `simbolos.M`: u a lo largo
del frente, v hacia el fondo; el frente (lado por el que se usa o se accede) es v = 0. Así ningún local queda
vacío: oficinas, vestuarios, sanitarios, comedor, laboratorio, taller, pañoles, depósitos y salas técnicas
se dibujan con su equipamiento real.

Capa: A-MOBILIARIO (contornos) y A-EQUIPO-RELLENO (rellenos).
"""

import math

from . import simbolos as S
from .simbolos import M, GRIS, GRIS2, OSCURO, MADERA, AGUA, BLANCO, ACERO

MOB = "A-MOBILIARIO"
FINO = "A-EQUIPO-FINO"
OC = "A-EQUIPO-OCULTO"
SEG = "A-SEGURIDAD"
LOZA = (248, 248, 252)
TELA = (214, 226, 240)
VERDE = (214, 236, 214)


# ---------------------------------------------------------------- piezas
def _silla(m, u, v, ang=90.0):
    """Silla de 0,45 m: asiento y respaldo; `ang` es hacia dónde mira la persona sentada."""
    a = math.radians(ang)
    du, dv = math.cos(a), math.sin(a)
    pu, pv = -dv, du
    pts = [(u + pu * s * 0.21 + du * t * 0.2, v + pv * s * 0.21 + dv * t * 0.2) for s, t in
           ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    m.fl(pts, TELA)
    m.pl(pts, MOB, True)
    m.ln((u - du * 0.24 + pu * 0.22, v - dv * 0.24 + pv * 0.22), (u - du * 0.24 - pu * 0.22, v - dv * 0.24 - pv * 0.22),
         MOB)


def _tablero(m, u0, v0, u1, v1, rgb=MADERA):
    m.fr(u0, v0, u1, v1, rgb)
    m.rc(u0, v0, u1, v1, MOB)


# ---------------------------------------------------------------- oficinas
def escritorio(m, n=1):
    """Puesto de oficina: escritorio de 0,70 m al fondo, monitor, teclado, cajonera y silla al frente."""
    U, V = m.Lu, m.Lv
    d = min(0.7, V * 0.55)
    _tablero(m, 0.0, V - d, U, V)
    m.rc(U * 0.3, V - 0.12, U * 0.7, V - 0.06, MOB)          # monitor
    m.ln((U * 0.5, V - 0.12), (U * 0.5, V - 0.2), MOB)
    m.rc(U * 0.32, V - d + 0.1, U * 0.62, V - d + 0.24, FINO)  # teclado
    m.rc(U - 0.45, V - d + 0.02, U - 0.03, V - 0.03, FINO)     # cajonera
    m.ln((U - 0.45, V - d / 2), (U - 0.03, V - d / 2), FINO)
    _silla(m, U * 0.47, V - d - 0.28, 90.0)


def mesa(m, n=6):
    """Mesa rectangular con n sillas repartidas en los dos lados largos."""
    U, V = m.Lu, m.Lv
    _tablero(m, 0.0, 0.45, U, V - 0.45)
    k = max(1, n // 2)
    for i in range(k):
        u = U * (i + 0.5) / k
        _silla(m, u, 0.25, 90.0)
        _silla(m, u, V - 0.25, 270.0)
    if n % 2:
        _silla(m, -0.05, V / 2, 0.0)


def mostrador(m, n=1):
    """Mostrador de atención: tablero alto al frente, tablero bajo, silla y PC."""
    U, V = m.Lu, m.Lv
    _tablero(m, 0.0, 0.0, U, 0.3, GRIS)
    _tablero(m, 0.0, 0.3, U, min(V, 0.75))
    m.rc(U * 0.35, 0.55, U * 0.65, 0.62, MOB)
    if V > 1.0:
        _silla(m, U * 0.5, min(V, 0.75) + 0.25, 270.0)


def archivo(m, n=2):
    """Archivo de cajones (0,45 × 0,60 m por módulo)."""
    U, V = m.Lu, m.Lv
    k = max(1, n)
    for i in range(k):
        u0, u1 = U * i / k, U * (i + 1) / k
        m.fr(u0, 0, u1, V, GRIS)
        m.rc(u0, 0, u1, V, MOB)
        m.rc(u0 + (u1 - u0) * 0.35, 0.02, u0 + (u1 - u0) * 0.65, 0.07, FINO)


def pizarra(m, n=1):
    """Pizarra o tablero visual (gestión a la vista)."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, BLANCO)
    m.rc(0, 0, U, V, MOB)
    m.ln((0.05, V * 0.5), (U - 0.05, V * 0.5), FINO)


def sillas(m, n=3):
    """Fila de sillas de espera."""
    U = m.Lu
    for i in range(n):
        _silla(m, U * (i + 0.5) / n, 0.25, 90.0)


def reloj(m, n=1):
    """Reloj de fichado biométrico y tablero de novedades."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, GRIS2)
    m.rc(0, 0, U, V, MOB)
    m.ci(U / 2, V / 2, min(U, V) * 0.3, FINO)


# ---------------------------------------------------------------- vestuarios y sanitarios
def armarios(m, n=6):
    """Armarios individuales dobles (ropa de calle / ropa de trabajo), dos alturas, 0,60 × 0,50 m."""
    U, V = m.Lu, m.Lv
    for i in range(n):
        u0, u1 = U * i / n, U * (i + 1) / n
        m.fr(u0, 0, u1, V, GRIS)
        m.rc(u0, 0, u1, V, MOB)
        m.ln(((u0 + u1) / 2, 0), ((u0 + u1) / 2, V), FINO)
        for uu in (u0 + (u1 - u0) * 0.38, u0 + (u1 - u0) * 0.88):
            m.ln((uu, 0.03), (uu, 0.1), FINO)


def banco_vest(m, n=1):
    """Banco de vestuario con listones."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, MADERA)
    m.rc(0, 0, U, V, MOB)
    for k in (0.33, 0.66):
        m.ln((0.02, V * k), (U - 0.02, V * k), FINO)


def inodoro(m, n=1):
    """Box de inodoro: mochila al fondo, taza, tabiques laterales y puerta al frente."""
    U, V = m.Lu, m.Lv
    for i in range(n):
        u0, u1 = U * i / n, U * (i + 1) / n
        w = u1 - u0
        c = (u0 + u1) / 2
        m.ln((u0, 0), (u0, V), MOB)
        m.ln((u1, 0), (u1, V), MOB)
        m.fr(c - 0.22, V - 0.2, c + 0.22, V - 0.02, LOZA)
        m.rc(c - 0.22, V - 0.2, c + 0.22, V - 0.02, MOB)
        pts = [(c + 0.18 * math.cos(t) , V - 0.45 + 0.26 * math.sin(t)) for t in
               [math.radians(a) for a in range(0, 361, 20)]]
        m.fl(pts, LOZA)
        m.pl(pts, MOB, True)
        m.ci(c, V - 0.47, 0.1, FINO)
        dw = min(0.7, w - 0.1)
        m.ln((u0 + 0.05, 0), (u0 + 0.05, dw), FINO)
        m.ar(u0 + 0.05, 0, dw, 0, 90, FINO)


def inodoro_acc(m, n=1):
    """Sanitario accesible: inodoro con 0,80 m libre lateral, barras rebatibles, círculo de giro Ø 1,50 m."""
    U, V = m.Lu, m.Lv
    c = 0.45
    m.fr(c - 0.22, V - 0.2, c + 0.22, V - 0.02, LOZA)
    m.rc(c - 0.22, V - 0.2, c + 0.22, V - 0.02, MOB)
    pts = [(c + 0.19 * math.cos(t), V - 0.5 + 0.3 * math.sin(t)) for t in [math.radians(a) for a in range(0, 361, 20)]]
    m.fl(pts, LOZA)
    m.pl(pts, MOB, True)
    m.ln((0.02, V - 0.9), (0.02, V - 0.2), SEG)
    m.ln((c + 0.4, V - 0.95), (c + 0.4, V - 0.25), SEG)
    m.ci(U / 2, max(0.8, V - 1.85), 0.75, OC)


def mingitorios(m, n=4):
    """Mingitorios murales con separadores."""
    U, V = m.Lu, m.Lv
    for i in range(n):
        c = U * (i + 0.5) / n
        pts = [(c + 0.18 * math.cos(t), V - 0.02 - 0.3 * abs(math.sin(t))) for t in
               [math.radians(a) for a in range(0, 181, 15)]]
        m.fl(pts, LOZA)
        m.pl(pts, MOB, True)
        m.ci(c, V - 0.15, 0.03, FINO)
        if i:
            m.ln((U * i / n, V), (U * i / n, V - 0.45), MOB)


def lavabos(m, n=3):
    """Mesada con n bachas ovales, griferías y espejo."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, LOZA)
    m.rc(0, 0, U, V, MOB)
    m.ln((0, V - 0.03), (U, V - 0.03), FINO)
    for i in range(n):
        c = U * (i + 0.5) / n
        pts = [(c + 0.2 * math.cos(t), V * 0.45 + 0.14 * math.sin(t)) for t in
               [math.radians(a) for a in range(0, 361, 20)]]
        m.pl(pts, MOB, True)
        m.ci(c, V * 0.45, 0.025, FINO)
        m.ln((c, V * 0.68), (c, V - 0.06), FINO)


def duchas(m, n=2):
    """Duchas de 0,90 × 0,90 m: plato, rejilla, cortina y tabiques."""
    U, V = m.Lu, m.Lv
    for i in range(n):
        u0, u1 = U * i / n, U * (i + 1) / n
        m.fr(u0, 0, u1, V, AGUA)
        m.rc(u0, 0, u1, V, MOB)
        m.ln((u0, 0), (u1, V), FINO)
        m.ln((u0, V), (u1, 0), FINO)
        m.ci((u0 + u1) / 2, V / 2, 0.05, FINO)
        m.ln((u0 + 0.05, 0.05), (u1 - 0.05, 0.05), OC)


# ---------------------------------------------------------------- comedor, limpieza y primeros auxilios
def mesada(m, n=2):
    """Mesada de office: bachas, anafe eléctrico y 2 microondas en alacena."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, GRIS)
    m.rc(0, 0, U, V, MOB)
    for i in range(n):
        c = 0.5 + i * 0.6
        m.rc(c - 0.25, V * 0.2, c + 0.25, V * 0.8, MOB)
        m.ci(c, V * 0.5, 0.03, FINO)
    u = 0.5 + n * 0.6 + 0.1
    if U > u + 0.6:
        m.rc(u, V * 0.15, u + 0.6, V * 0.85, MOB)
        for du in (0.15, 0.45):
            for dv in (0.3, 0.7):
                m.ci(u + du, V * dv, 0.08, FINO)
    u += 0.8
    k = 0
    while U > u + 0.5 and k < 2:
        m.rc(u, V * 0.2, u + 0.5, V * 0.9, MOB)
        m.rc(u + 0.05, V * 0.3, u + 0.35, V * 0.8, FINO)
        u += 0.6
        k += 1


def heladera(m, n=1):
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, BLANCO)
    m.rc(0, 0, U, V, MOB)
    m.ln((U * 0.55, 0), (U * 0.55, V), FINO)
    m.ln((0.05, 0.05), (0.05, V * 0.4), FINO)


def dispenser(m, n=1):
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, AGUA)
    m.rc(0, 0, U, V, MOB)
    m.ci(U / 2, V / 2, min(U, V) * 0.3, FINO)


def camilla(m, n=1):
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, BLANCO)
    m.rc(0, 0, U, V, MOB)
    m.rc(U * 0.05, V * 0.75, U * 0.95, V * 0.95, FINO)


def botiquin(m, n=1):
    """Armario de primeros auxilios (cruz verde)."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, VERDE)
    m.rc(0, 0, U, V, MOB)
    c, d = (U / 2, V / 2), min(U, V) * 0.3
    m.ln((c[0] - d, c[1]), (c[0] + d, c[1]), MOB)
    m.ln((c[0], c[1] - d), (c[0], c[1] + d), MOB)


def lavaojos(m, n=1):
    """Ducha de emergencia y lavaojos (IRAM / ANSI Z358.1)."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, VERDE)
    m.rc(0, 0, U, V, SEG)
    m.ci(U / 2, V / 2, min(U, V) * 0.35, SEG)
    m.ci(U / 2, V / 2, min(U, V) * 0.12, SEG)


def lavadero(m, n=1):
    """Pileta de lavadero, lavarropas industrial y secarropas."""
    U, V = m.Lu, m.Lv
    w = U / 3
    m.fr(0, 0, w - 0.05, V, LOZA)
    m.rc(0, 0, w - 0.05, V, MOB)
    m.rc(0.08, 0.08, w - 0.13, V - 0.15, FINO)
    for i in (1, 2):
        m.fr(w * i, 0, w * (i + 1) - 0.05, V, BLANCO)
        m.rc(w * i, 0, w * (i + 1) - 0.05, V, MOB)
        m.ci(w * i + (w - 0.05) / 2, V / 2, min(w, V) * 0.32, FINO)


def carro_limpieza(m, n=1):
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, (255, 240, 200))
    m.rc(0, 0, U, V, MOB)
    m.ci(U * 0.3, V * 0.5, min(U, V) * 0.3, FINO)
    m.rc(U * 0.62, V * 0.15, U * 0.95, V * 0.85, FINO)


# ---------------------------------------------------------------- calidad, taller y pañoles
def mesa_lab(m, n=1):
    """Mesada de laboratorio con bacha, enchufes y banqueta."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, (236, 240, 236))
    m.rc(0, 0, U, V, MOB)
    m.rc(U - 0.6, V * 0.2, U - 0.15, V * 0.8, MOB)
    m.ci(U - 0.37, V * 0.5, 0.03, FINO)
    for k in range(1, int(U / 0.6)):
        m.rc(k * 0.6 - 0.04, V - 0.08, k * 0.6 + 0.04, V - 0.02, FINO)
    m.ci(U * 0.3, -0.25, 0.17, MOB)


def marmol(m, n=1):
    """Mármol de metrología con calibre de altura, micrómetros y medidor de espesor por ultrasonido."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, (215, 215, 220))
    m.rc(0, 0, U, V, MOB)
    m.rc(0.06, 0.06, U - 0.06, V - 0.06, FINO)
    m.rc(U * 0.7, V * 0.55, U * 0.85, V * 0.85, FINO)
    m.ci(U * 0.25, V * 0.5, 0.08, FINO)
    m.ci(U * 0.45, V * 0.6, 0.06, FINO)


def camara(m, n=1):
    """Cámara de niebla salina (ensayo de pintura) o estufa: gabinete con tapa, tablero y venteo."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, GRIS)
    m.rc(0, 0, U, V, MOB)
    m.rc(0.06, 0.06, U * 0.72, V - 0.06, FINO)
    m.ln((0.06, V * 0.5), (U * 0.72, V * 0.5), OC)
    m.rc(U * 0.78, V * 0.15, U - 0.05, V * 0.6, FINO)
    m.ci(U * 0.88, V * 0.8, 0.05, FINO)


def balanza_lab(m, n=1):
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, GRIS2)
    m.rc(0, 0, U, V, MOB)
    m.ci(U / 2, V * 0.6, min(U, V) * 0.28, FINO)
    m.rc(U * 0.2, 0.03, U * 0.8, V * 0.18, FINO)


def banco_trabajo(m, n=1):
    S.banco(m)


def torno(m, n=1):
    """Torno paralelo de taller: bancada, cabezal, carro y contrapunta."""
    U, V = m.Lu, m.Lv
    m.fr(0, V * 0.25, U, V * 0.75, GRIS)
    m.rc(0, V * 0.25, U, V * 0.75, MOB)
    m.fr(0, V * 0.1, U * 0.25, V * 0.9, GRIS2)
    m.rc(0, V * 0.1, U * 0.25, V * 0.9, MOB)
    m.ci(U * 0.3, V * 0.5, V * 0.18, MOB)
    m.rc(U * 0.45, V * 0.05, U * 0.6, V * 0.95, FINO)
    m.rc(U * 0.85, V * 0.3, U - 0.03, V * 0.7, FINO)
    m.ln((U * 0.3, V * 0.5), (U * 0.85, V * 0.5), OC)


def agujereadora(m, n=1):
    """Agujereadora de columna y amoladora de banco."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, GRIS)
    m.rc(0, 0, U, V, MOB)
    m.ci(U * 0.5, V * 0.65, min(U, V) * 0.16, MOB)
    m.ci(U * 0.5, V * 0.3, min(U, V) * 0.25, FINO)
    m.ln((U * 0.5 - 0.1, V * 0.65), (U * 0.5 + 0.1, V * 0.65), FINO)


def soldadora(m, n=1):
    """Soldadora MIG móvil con tubo de gas en carro."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U * 0.65, V, GRIS2)
    m.rc(0, 0, U * 0.65, V, MOB)
    m.ci(U * 0.83, V * 0.5, min(U * 0.15, V * 0.3), MOB)
    m.ln((U * 0.33, V), (U * 0.33, V + 0.2), FINO)


def estanteria(m, n=1):
    S.estanteria(m)


def rack(m, n=1):
    S.rack(m)


def tablero_el(m, n=3):
    """Tableros eléctricos en fila: frente de puertas, manijas y espacio de maniobra de 1,0 m."""
    U, V = m.Lu, m.Lv
    for i in range(n):
        u0, u1 = U * i / n, U * (i + 1) / n
        m.fr(u0, 0, u1, V, GRIS2)
        m.rc(u0, 0, u1, V, MOB)
        m.ln(((u0 + u1) / 2, 0), ((u0 + u1) / 2, V * 0.3), FINO)
        m.pl([(u0 + 0.1, V * 0.55), ((u0 + u1) / 2, V * 0.8), ((u0 + u1) / 2, V * 0.45), (u1 - 0.1, V * 0.7)], FINO)
    m.ln((0, -1.0), (U, -1.0), OC)


def compresor(m, n=1):
    """Compresor de tornillo, secador frigorífico, filtros y tanque pulmón."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U * 0.45, V, GRIS2)
    m.rc(0, 0, U * 0.45, V, MOB)
    for k in range(1, 5):
        m.ln((U * 0.45 * k / 5, V * 0.75), (U * 0.45 * k / 5, V - 0.05), FINO)
    m.rc(U * 0.5, 0, U * 0.68, V * 0.6, MOB)
    m.ci(U * 0.84, V * 0.5, min(U * 0.15, V * 0.45), MOB)
    m.ci(U * 0.84, V * 0.5, min(U * 0.15, V * 0.45) * 0.4, FINO)
    m.ln((U * 0.45, V * 0.3), (U * 0.5, V * 0.3), FINO)
    m.ln((U * 0.68, V * 0.3), (U * 0.84 - min(U * 0.15, V * 0.45), V * 0.3), FINO)


def tambores(m, n=6):
    """Tambores de 200 L sobre batea antiderrame (≥110 % del mayor envase)."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, MOB)
    m.rc(0.05, 0.05, U - 0.05, V - 0.05, FINO)
    nu, nv = max(1, int((U - 0.1) / 0.65)), max(1, int((V - 0.1) / 0.65))
    for i in range(nu):
        for j in range(nv):
            u, v = 0.05 + (i + 0.5) * (U - 0.1) / nu, 0.05 + (j + 0.5) * (V - 0.1) / nv
            m.fc(u, v, 0.29, (210, 222, 240))
            m.ci(u, v, 0.29, MOB)
            m.ci(u + 0.12, v, 0.03, FINO)


def bigbags(m, n=1):
    """Big bags de 1 t con asas."""
    U, V = m.Lu, m.Lv
    nu, nv = max(1, int(U / 1.15)), max(1, int(V / 1.15))
    for i in range(nu):
        for j in range(nv):
            u0, v0 = i * U / nu + 0.05, j * V / nv + 0.05
            u1, v1 = (i + 1) * U / nu - 0.05, (j + 1) * V / nv - 0.05
            m.fr(u0, v0, u1, v1, (250, 238, 200))
            m.rc(u0, v0, u1, v1, MOB)
            m.ln((u0, v0), (u1, v1), FINO)
            m.ln((u0, v1), (u1, v0), FINO)
            for uu, vv in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
                m.ci(uu, vv, 0.06, FINO)


def pallets(m, n=0):
    """Pallets de 1,2 × 1,0 m a piso; `n` = tipo de carga (0 cajas, 1 cilindros)."""
    U, V = m.Lu, m.Lv
    nu, nv = max(1, int(U / 1.3)), max(1, int(V / 1.1))
    for i in range(nu):
        for j in range(nv):
            m.pallet(i * U / nu + 0.05, j * V / nv + 0.05, U / nu - 0.1, V / nv - 0.1, "cil" if n else "caja")


def jaula(m, n=1):
    """Jaula de malla con puerta (lotes retenidos, cilindros NO APTO, gases)."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, SEG)
    for k in range(1, int(U / 0.3)):
        m.ln((k * 0.3, 0), (k * 0.3, 0.06), FINO)
        m.ln((k * 0.3, V), (k * 0.3, V - 0.06), FINO)
    m.ln((0.1, 0), (0.1, 0.8), SEG)
    m.ar(0.1, 0, 0.8, 0, 90, SEG)


def cilindros_piso(m, n=0):
    """Cilindros parados a piso (Ø según n: 0 = 5 kg, 1 = 1 kg) dentro de un recinto."""
    U, V = m.Lu, m.Lv
    m.cilindros(0.05, 0.05, U - 0.05, V - 0.05, 0.16 if n == 0 else 0.1)


def contenedor(m, n=1):
    S.contenedores(m)


def carros_vacios(m, n=6):
    """Fila de carros vacíos estacionados (carros porta-cilindros con separadores o zorras de reparto)."""
    U, V = m.Lu, m.Lv
    k = max(1, n)
    for i in range(k):
        u0, u1 = U * i / k + 0.06, U * (i + 1) / k - 0.06
        m.fr(u0, 0.25, u1, V - 0.05, GRIS)
        m.rc(u0, 0.25, u1, V - 0.05, MOB)
        for j in range(1, 4):
            m.ln((u0, 0.25 + (V - 0.3) * j / 4), (u1, 0.25 + (V - 0.3) * j / 4), FINO)
        m.ln((u0 + 0.08, 0.25), (u0 + 0.08, 0.05), MOB)
        m.ln((u1 - 0.08, 0.25), (u1 - 0.08, 0.05), MOB)
        m.ln((u0 + 0.08, 0.05), (u1 - 0.08, 0.05), MOB)
        for uu in (u0 + 0.06, u1 - 0.06):
            for vv in (0.3, V - 0.1):
                m.fc(uu, vv, 0.04, OSCURO)


def cargador(m, n=3):
    """Estación de carga de baterías: cargadores murales, puestos de estacionamiento, lavaojos y extractor."""
    U, V = m.Lu, m.Lv
    k = max(1, n)
    for i in range(k):
        u0, u1 = U * i / k, U * (i + 1) / k
        m.ln((u0, 0), (u0, V - 0.4), OC)
        m.fr((u0 + u1) / 2 - 0.25, V - 0.35, (u0 + u1) / 2 + 0.25, V - 0.05, GRIS2)
        m.rc((u0 + u1) / 2 - 0.25, V - 0.35, (u0 + u1) / 2 + 0.25, V - 0.05, MOB)
        m.ln(((u0 + u1) / 2, V - 0.35), ((u0 + u1) / 2, V * 0.45), FINO)
    m.ln((U, 0), (U, V - 0.4), OC)


def cabina_sold(m, n=3):
    """Cabinas de práctica de soldadura: mamparas ignífugas en 3 lados, mesa, extracción y operario."""
    U, V = m.Lu, m.Lv
    k = max(1, n)
    for i in range(k):
        u0, u1 = U * i / k, U * (i + 1) / k
        m.ln((u0, 0.2), (u0, V), SEG)
        m.ln((u1, 0.2), (u1, V), SEG)
        m.ln((u0, V), (u1, V), SEG)
        c = (u0 + u1) / 2
        m.fr(c - 0.45, V - 0.75, c + 0.45, V - 0.15, GRIS)
        m.rc(c - 0.45, V - 0.75, c + 0.45, V - 0.15, MOB)
        m.extractor(u1 - 0.15, V - 0.1, c + 0.15, V - 0.5)
        S.operario_rev(m, c, V - 1.15, 90.0)


def ventanilla(m, n=1):
    """Ventanilla de entrega del pañol (contra vale)."""
    U, V = m.Lu, m.Lv
    _tablero(m, 0, 0, U, V, GRIS)
    m.ln((0, V * 0.5), (U, V * 0.5), FINO)


def rampa(m, n=1):
    """Rampa niveladora hidráulica de muelle (2,0 × 3,0 m) con labio y topes."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, GRIS)
    m.rc(0, 0, U, V, MOB)
    for k in range(1, 8):
        m.ln((U * k / 8, 0.05), (U * k / 8 - 0.1, V - 0.05), FINO)
    m.rc(0.05, 0, U - 0.05, 0.25, FINO)


TIPOS = {f.__name__: f for f in (
    escritorio, mesa, mostrador, archivo, pizarra, sillas, reloj, armarios, banco_vest, inodoro, inodoro_acc,
    mingitorios, lavabos, duchas, mesada, heladera, dispenser, camilla, botiquin, lavaojos, lavadero,
    carro_limpieza, mesa_lab, marmol, camara, balanza_lab, banco_trabajo, torno, agujereadora, soldadora,
    estanteria, rack, tablero_el, compresor, tambores, bigbags, pallets, jaula, cilindros_piso, contenedor,
    carros_vacios, cargador, cabina_sold, ventanilla, rampa)}

# artefactos sanitarios que se cuentan para el art. 49 del Dec. 351/79
SANITARIOS = {"inodoro": "inodoros", "inodoro_acc": "inodoros", "mingitorios": "orinales", "lavabos": "lavabos",
              "duchas": "duchas", "armarios": "armarios"}


def dibujar(pl, mueble):
    m = M.rect(pl, mueble.rect, mueble.frente)
    TIPOS[mueble.tipo](m, mueble.n)
    m.fin()


def puerta_int(pl, x, y, w, muro, abre):
    """Puerta interior de una hoja: `muro` 'h' (pared horizontal) o 'v'; `abre` +1/-1 hacia +y/+x o -y/-x."""
    if muro == "h":
        pl.linea((x, y), (x, y + abre * w), "A-ABERTURA")
        pl.arco((x, y), w, 0 if abre > 0 else 270, 90 if abre > 0 else 360, "A-ABERTURA")
    else:
        pl.linea((x, y), (x + abre * w, y), "A-ABERTURA")
        pl.arco((x, y), w, 0 if abre > 0 else 90, 90 if abre > 0 else 180, "A-ABERTURA")
