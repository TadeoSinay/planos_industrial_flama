"""Biblioteca de símbolos de equipos en planta (vista superior a escala real).

Cada equipo se dibuja en su marco local: u a lo largo del frente, v hacia el fondo; el frente (lado del
operario) es v = 0. El marco se apoya en el rectángulo del equipo y se gira según el frente
('S', 'E', 'N', 'O'); `espejo` invierte el sentido de u (sentido del flujo).

Capas:
    A-EQUIPO          contorno de máquina (línea gruesa)
    A-EQUIPO-FINO     detalle: rodillos, mordazas, pisadores, motores, tableros, cañerías
    A-EQUIPO-OCULTO   partes elevadas o por debajo: vigas, cabezales, transportador aéreo, tanques
    A-EQUIPO-RELLENO  rellenos de cuerpo (acero, motores, agua)
    A-SEGURIDAD       resguardos, cortinas de luz y zonas de barrido (rojo, trazos)
    A-OPERARIO        operarios en su puesto
    A-VEHICULO        autoelevadores, tren logístico y transpaletas
"""

import math

CONT, FINO, OC, SEG, OP, VEH = "A-EQUIPO", "A-EQUIPO-FINO", "A-EQUIPO-OCULTO", "A-SEGURIDAD", "A-OPERARIO", \
    "A-VEHICULO"
REL = "A-EQUIPO-RELLENO"
AREA = "A-AREA-TRABAJO"

ACERO = (226, 231, 238)
GRIS = (238, 238, 238)
GRIS2 = (205, 208, 212)
OSCURO = (150, 155, 160)
AGUA = (200, 225, 250)
MADERA = (238, 222, 192)
POLVO = (250, 238, 200)
CALOR = (250, 215, 200)
BLANCO = (255, 255, 255)

ROT = {"S": 0.0, "E": 90.0, "N": 180.0, "O": 270.0}


def _circ(u, v, r, n=28, a0=0.0, a1=360.0):
    return [(u + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             v + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + (0 if a1 - a0 >= 360 else 1))]


class M:
    """Marco local (u, v) -> mundo (m). Los rellenos se emiten antes que las líneas."""

    def __init__(self, pl, ox, oy, ang, Lu, Lv, espejo=False):
        self.p = pl
        self.ox, self.oy, self.a = ox, oy, ang
        self.ca, self.sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        self.Lu, self.Lv = Lu, Lv
        self.esp = espejo
        self._ops = []

    @classmethod
    def rect(cls, pl, r, frente="S", espejo=False):
        Lu, Lv = (r.w, r.h) if frente in "SN" else (r.h, r.w)
        o = {"S": (r.x0, r.y0), "E": (r.x1, r.y0), "N": (r.x1, r.y1), "O": (r.x0, r.y1)}[frente]
        return cls(pl, o[0], o[1], ROT[frente], Lu, Lv, espejo)

    @classmethod
    def centro(cls, pl, x, y, ang, Lu, Lv):
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        return cls(pl, x - (Lu / 2 * ca - Lv / 2 * sa), y - (Lu / 2 * sa + Lv / 2 * ca), ang, Lu, Lv)

    # ------------------------------------------------------------ transformación
    def W(self, u, v):
        if self.esp:
            u = self.Lu - u
        return (self.ox + u * self.ca - v * self.sa, self.oy + u * self.sa + v * self.ca)

    def Ws(self, pts):
        return [self.W(u, v) for u, v in pts]

    def _ang(self, a):
        return ((180.0 - a) if self.esp else a) + self.a

    # ------------------------------------------------------------ primitivas (diferidas)
    def pl(self, pts, capa=FINO, c=False):
        w = self.Ws(pts)
        self._ops.append((2, lambda: self.p.pl(w, capa, c)))

    def rc(self, u0, v0, u1, v1, capa=FINO):
        self.pl([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], capa, True)

    def ln(self, a, b, capa=FINO):
        wa, wb = self.W(*a), self.W(*b)
        self._ops.append((2, lambda: self.p.linea(wa, wb, capa)))

    def ci(self, u, v, r, capa=FINO):
        w = self.W(u, v)
        self._ops.append((2, lambda: self.p.circulo(w, r, capa)))

    def ar(self, u, v, r, a0, a1, capa=FINO):
        if self.esp:
            a0, a1 = 180.0 - a1, 180.0 - a0
        w = self.W(u, v)
        b0, b1 = a0 + self.a, a1 + self.a
        self._ops.append((2, lambda: self.p.arco(w, r, b0, b1, capa)))

    def fl(self, pts, rgb=ACERO):
        w = self.Ws(pts)
        self._ops.append((0, lambda: self.p.relleno(w, rgb, REL)))

    def fr(self, u0, v0, u1, v1, rgb=ACERO):
        self.fl([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], rgb)

    def fc(self, u, v, r, rgb=ACERO):
        self.fl(_circ(u, v, r, 24), rgb)

    def ray(self, pts, esp=0.08, ang=45.0, capa=FINO):
        w = self.Ws(pts)
        a = self._ang(ang)
        self._ops.append((1, lambda: self.p.rayado(w, capa, max(esp * self.p.s, 0.25), a)))

    def fin(self):
        for _, f in sorted(self._ops, key=lambda t: t[0]):
            f()
        self._ops = []

    # ------------------------------------------------------------ componentes
    def caja(self, u0, v0, u1, v1, rgb=ACERO, capa=CONT):
        self.fr(u0, v0, u1, v1, rgb)
        self.rc(u0, v0, u1, v1, capa)

    def motor(self, u, v, l, d, eje="u"):
        """Motor eléctrico con aletas, tapa de ventilador, eje y caja de bornes."""
        if eje == "u":
            self.caja(u, v - d / 2, u + l, v + d / 2, GRIS2, FINO)
            for k in (-0.3, 0.0, 0.3):
                self.ln((u + l * 0.22, v + k * d), (u + l * 0.92, v + k * d))
            self.rc(u - l * 0.18, v - d * 0.4, u, v + d * 0.4)
            self.ln((u + l, v), (u + l * 1.18, v))
            self.rc(u + l * 0.45, v - d * 0.2, u + l * 0.7, v + d * 0.2)
        else:
            self.caja(u - d / 2, v, u + d / 2, v + l, GRIS2, FINO)
            for k in (-0.3, 0.0, 0.3):
                self.ln((u + k * d, v + l * 0.22), (u + k * d, v + l * 0.92))
            self.rc(u - d * 0.4, v - l * 0.18, u + d * 0.4, v)
            self.ln((u, v + l), (u, v + l * 1.18))
            self.rc(u - d * 0.2, v + l * 0.45, u + d * 0.2, v + l * 0.7)

    def tablero(self, u0, v0, u1, v1):
        """Tablero eléctrico (IEC: rectángulo con diagonal) con puerta y bisagras."""
        self.caja(u0, v0, u1, v1, GRIS2)
        self.ln((u0, v0), (u1, v1))
        self.ci(u0 + (u1 - u0) * 0.85, v0 + (v1 - v0) * 0.5, min(u1 - u0, v1 - v0) * 0.08)

    def botonera(self, u0, v0, u1, v1, n=3):
        self.caja(u0, v0, u1, v1, GRIS2, FINO)
        r = min(u1 - u0, v1 - v0) * 0.18
        for i in range(n):
            self.ci(u0 + (u1 - u0) * (i + 0.5) / n, (v0 + v1) / 2, r)
        self.fc(u0 + (u1 - u0) * 0.5 / n, (v0 + v1) / 2, r, (220, 40, 40))   # parada de emergencia

    def poste(self, u, v, s=0.1, rgb=OSCURO):
        self.caja(u - s / 2, v - s / 2, u + s / 2, v + s / 2, rgb, FINO)

    def operario(self, u, v, mira=90.0):
        """Operario en planta: hombros, cabeza y manos, mirando hacia `mira` (grados locales)."""
        a = math.radians(mira)
        f = (math.cos(a), math.sin(a))
        t = (-f[1], f[0])
        hombros = [(u + t[0] * 0.25 * math.cos(s) + f[0] * 0.13 * math.sin(s),
                    v + t[1] * 0.25 * math.cos(s) + f[1] * 0.13 * math.sin(s))
                   for s in [2 * math.pi * i / 24 for i in range(24)]]
        for sg_ in (-1, 1):   # brazos hacia adelante
            b0 = (u + t[0] * 0.2 * sg_, v + t[1] * 0.2 * sg_)
            b1 = (u + t[0] * 0.17 * sg_ + f[0] * 0.3, v + t[1] * 0.17 * sg_ + f[1] * 0.3)
            n_ = (f[0] * 0.0 + t[0] * 0.045, f[1] * 0.0 + t[1] * 0.045)
            brazo = [(b0[0] - n_[0], b0[1] - n_[1]), (b1[0] - n_[0], b1[1] - n_[1]),
                     (b1[0] + n_[0], b1[1] + n_[1]), (b0[0] + n_[0], b0[1] + n_[1])]
            self.fl(brazo, (235, 180, 225))
            self.pl(brazo, OP, True)
            self.fc(b1[0] + f[0] * 0.03, b1[1] + f[1] * 0.03, 0.045, (250, 225, 200))
            self.ci(b1[0] + f[0] * 0.03, b1[1] + f[1] * 0.03, 0.045, OP)
        self.fl(hombros, (235, 180, 225))
        self.pl(hombros, OP, True)
        self.fc(u + f[0] * 0.01, v + f[1] * 0.01, 0.105, (95, 70, 60))
        self.ci(u + f[0] * 0.01, v + f[1] * 0.01, 0.105, OP)
        self.ln((u + f[0] * 0.1, v + f[1] * 0.1), (u + f[0] * 0.14, v + f[1] * 0.14), OP)   # nariz

    def zona(self, u0, v0, u1, v1):
        self.rc(u0, v0, u1, v1, SEG)

    def extractor(self, u, v, u2, v2):
        """Brazo articulado de extracción de humos: base, dos tramos y campana."""
        um, vm = (u + u2) / 2 + (v2 - v) * 0.25, (v + v2) / 2 - (u2 - u) * 0.25
        self.ci(u, v, 0.09, FINO)
        self.ci(u, v, 0.04, FINO)
        for a, b in (((u, v), (um, vm)), ((um, vm), (u2, v2))):
            L_ = math.dist(a, b) or 1.0
            n = (-(b[1] - a[1]) / L_ * 0.045, (b[0] - a[0]) / L_ * 0.045)
            self.ln((a[0] + n[0], a[1] + n[1]), (b[0] + n[0], b[1] + n[1]), OC)
            self.ln((a[0] - n[0], a[1] - n[1]), (b[0] - n[0], b[1] - n[1]), OC)
        self.ci(um, vm, 0.05, OC)
        self.ci(u2, v2, 0.16, FINO)
        self.ci(u2, v2, 0.1, FINO)

    def rodillos(self, u0, v0, u1, v1, paso=0.15, sentido="u"):
        """Camino de rodillos: largueros en el sentido de avance y rodillos transversales."""
        self.fr(u0, v0, u1, v1, GRIS)
        if sentido == "u":
            self.ln((u0, v0), (u1, v0), CONT)
            self.ln((u0, v1), (u1, v1), CONT)
            n = max(1, int((u1 - u0) / paso))
            for i in range(n + 1):
                uu = u0 + (u1 - u0) * i / n
                self.ln((uu, v0 + 0.03), (uu, v1 - 0.03))
        else:
            self.ln((u0, v0), (u0, v1), CONT)
            self.ln((u1, v0), (u1, v1), CONT)
            n = max(1, int((v1 - v0) / paso))
            for i in range(n + 1):
                vv = v0 + (v1 - v0) * i / n
                self.ln((u0 + 0.03, vv), (u1 - 0.03, vv))

    def pallet(self, u0, v0, a=1.2, b=1.0, carga=None):
        """Pallet de madera con tablas superiores; carga: None, 'caja' o 'cil' (cilindros)."""
        self.fr(u0, v0, u0 + a, v0 + b, MADERA)
        self.rc(u0, v0, u0 + a, v0 + b, FINO)
        for i in range(1, 7):
            uu = u0 + a * i / 7
            self.ln((uu, v0), (uu, v0 + b))
        if carga == "caja":
            self.rc(u0 + 0.04, v0 + 0.04, u0 + a - 0.04, v0 + b - 0.04, CONT)
            self.ln((u0 + 0.04, v0 + 0.04), (u0 + a - 0.04, v0 + b - 0.04))
            self.ln((u0 + 0.04, v0 + b - 0.04), (u0 + a - 0.04, v0 + 0.04))
        elif carga == "cil":
            self.cilindros(u0 + 0.03, v0 + 0.03, u0 + a - 0.03, v0 + b - 0.03, 0.16)

    def cilindros(self, u0, v0, u1, v1, d=0.16):
        """Cilindros parados vistos desde arriba: cuerpo, cuello y válvula."""
        nu, nv = max(1, int((u1 - u0) / d)), max(1, int((v1 - v0) / d))
        du, dv = (u1 - u0) / nu, (v1 - v0) / nv
        for i in range(nu):
            for j in range(nv):
                c = (u0 + du * (i + 0.5), v0 + dv * (j + 0.5))
                self.ci(c[0], c[1], d * 0.45)
                self.ci(c[0], c[1], d * 0.14)

    def malla(self, u0, v0, u1, v1, paso=1.0, e=0.05):
        """Jaula de malla: doble línea de paneles con postes cada `paso`."""
        self.rc(u0, v0, u1, v1, CONT)
        self.rc(u0 + e, v0 + e, u1 - e, v1 - e, FINO)
        for (a, b) in (((u0, v0), (u1, v0)), ((u1, v0), (u1, v1)), ((u1, v1), (u0, v1)), ((u0, v1), (u0, v0))):
            L_ = math.dist(a, b)
            n = max(1, round(L_ / paso))
            for i in range(n + 1):
                p = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
                pu = min(max(p[0], u0 + e / 2), u1 - e / 2)
                pv = min(max(p[1], v0 + e / 2), v1 - e / 2)
                self.poste(pu, pv, e * 1.4)
            # zig-zag de malla
            m = max(2, int(L_ / 0.12))
            pts = []
            for i in range(m + 1):
                s = i / m
                q = (a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s)
                n_ = (-(b[1] - a[1]) / L_, (b[0] - a[0]) / L_)
                k = e * (0.25 if i % 2 else 0.75)
                pts.append((q[0] + n_[0] * k, q[1] + n_[1] * k))
            self.pl(pts, FINO)

    def puerta_batiente(self, u, v, ancho, a0=0.0, hacia=1):
        """Hoja de puerta con arco de giro (u, v = bisagra; hoja sobre +u; abre hacia +v si hacia=1)."""
        self.ln((u, v), (u, v + ancho * hacia), FINO)
        if hacia > 0:
            self.ar(u, v, ancho, 0, 90, OC)
        else:
            self.ar(u, v, ancho, 270, 360, OC)

    def manometro(self, u, v, r=0.06):
        self.fc(u, v, r, BLANCO)
        self.ci(u, v, r, FINO)
        self.ln((u, v), (u + r * 0.7, v + r * 0.5))
        for k in range(7):
            a = math.radians(-45 + 270 * k / 6)
            self.ln((u + r * 0.78 * math.cos(a), v + r * 0.78 * math.sin(a)),
                    (u + r * math.cos(a), v + r * math.sin(a)))

    def ventilador(self, u, v, r):
        self.ci(u, v, r, FINO)
        self.ci(u, v, r * 0.2, FINO)
        for k in range(6):
            a = math.radians(60 * k)
            b = math.radians(60 * k + 35)
            self.pl([(u + r * 0.2 * math.cos(a), v + r * 0.2 * math.sin(a)),
                     (u + r * 0.85 * math.cos(b), v + r * 0.85 * math.sin(b))])

    def eje(self, a, b):
        self.ln(a, b, "A-EJE")


# =================================================================== equipos de corte y conformado
def guillotina(m):
    U, V = m.Lu, m.Lv
    hs = min(0.45, U * 0.11)
    yb = min(0.62, V * 0.27)
    vb = yb + min(0.42, V * 0.18)
    for u0 in (0, U - hs):
        m.caja(u0, yb - 0.05, u0 + hs, V - 0.08, GRIS2)
        m.ci(u0 + hs / 2, vb + 0.05, hs * 0.36, CONT)
        m.ci(u0 + hs / 2, vb + 0.05, hs * 0.2)
        m.rc(u0 + 0.06, V - 0.58, u0 + hs - 0.06, V - 0.16)
        for uu in (u0 + 0.1, u0 + hs - 0.1):
            for vv in (V - 0.53, V - 0.21):
                m.ci(uu, vv, 0.015)
    m.caja(hs, yb, U - hs, V - 0.25)
    # mesa con ranuras y bolas de apoyo
    for k in range(int((U - 2 * hs) / 0.25)):
        m.ci(hs + 0.15 + k * 0.25, yb + 0.1, 0.022)
    # viga portacuchilla, cuchilla y pisadores
    m.caja(hs, vb - 0.18, U - hs, vb + 0.28, GRIS)
    m.fr(hs, vb - 0.02, U - hs, vb + 0.02, OSCURO)
    m.ln((hs, vb), (U - hs, vb), CONT)
    n = max(3, int((U - 2 * hs - 0.2) / 0.2))
    for i in range(n):
        u = hs + 0.1 + (i + 0.5) * (U - 2 * hs - 0.2) / n
        m.ci(u, vb - 0.1, 0.035)
        m.ci(u, vb - 0.1, 0.017)
    # central hidráulica sobre la viga
    tu = U / 2
    m.caja(tu - 0.55, vb - 0.12, tu + 0.55, vb + 0.25, GRIS2, FINO)
    m.motor(tu - 0.4, vb + 0.06, 0.32, 0.17)
    m.ci(tu + 0.3, vb + 0.06, 0.05)
    m.ci(tu + 0.45, vb + 0.06, 0.025)
    # protección de dedos
    m.ln((hs, vb - 0.24), (U - hs, vb - 0.24), SEG)
    for k in range(int((U - 2 * hs) / 0.1)):
        u = hs + 0.05 + k * 0.1
        m.ln((u, vb - 0.24), (u, vb - 0.19))
    # brazos delanteros con bolas y escuadra graduada
    for u in (hs + 0.4, U / 2, U - hs - 0.4):
        m.caja(u - 0.05, 0.0, u + 0.05, yb, GRIS2, FINO)
        for k in range(int(yb / 0.15)):
            m.ci(u, 0.08 + k * 0.15, 0.025)
    m.caja(hs + 0.02, 0.0, hs + 0.1, yb, ACERO, FINO)
    for k in range(int(yb / 0.05) + 1):
        m.ln((hs + 0.02, k * 0.05), (hs + (0.07 if k % 2 else 0.1), k * 0.05))
    # tope trasero con husillos y motor
    vt = vb + 0.28 + (V - 0.25 - vb - 0.28) * 0.45
    for u in (hs + 0.25, U - hs - 0.25):
        m.ln((u, vb + 0.28), (u, V - 0.3), OC)
        m.ci(u, V - 0.32, 0.04)
    m.caja(hs + 0.1, vt - 0.04, U - hs - 0.1, vt + 0.04, GRIS2, FINO)
    for k in range(4):
        uu = hs + 0.4 + k * (U - 2 * hs - 0.8) / 3
        m.rc(uu - 0.04, vt - 0.1, uu + 0.04, vt - 0.04)
    m.motor(U / 2 - 0.2, V - 0.38, 0.32, 0.14)
    m.ln((hs + 0.25, V - 0.32), (U - hs - 0.25, V - 0.32), OC)
    m.tablero(U - hs - 0.62, V - 0.62, U - hs - 0.08, V - 0.27)
    # consola colgante, pedal y barrera trasera
    m.botonera(U - hs - 0.4, 0.12, U - hs - 0.08, 0.36)
    m.ln((U - hs - 0.08, 0.24), (U - hs, yb), OC)
    m.caja(U / 2 + 0.55, 0.04, U / 2 + 0.85, 0.3, GRIS2, FINO)
    for k in range(4):
        m.ln((U / 2 + 0.6, 0.08 + k * 0.06), (U / 2 + 0.8, 0.08 + k * 0.06))
    m.ln((U / 2 + 0.7, 0.3), (U / 2 + 0.7, yb), OC)
    for u in (0.05, U - 0.05):
        m.poste(u, V - 0.03, 0.06, (220, 40, 40))
    m.ln((0.05, V - 0.03), (U - 0.05, V - 0.03), SEG)


def prensa(m):
    U, V = m.Lu, m.Lv
    m.caja(0.3, 0.3, U - 0.3, V - 0.35)
    # columnas con tuercas hexagonales
    for (u, v) in ((0.6, 0.6), (U - 0.6, 0.6), (0.6, V - 0.65), (U - 0.6, V - 0.65)):
        m.fl([(u + 0.2 * math.cos(math.radians(30 + 60 * k)), v + 0.2 * math.sin(math.radians(30 + 60 * k)))
              for k in range(6)], GRIS2)
        m.pl([(u + 0.2 * math.cos(math.radians(30 + 60 * k)), v + 0.2 * math.sin(math.radians(30 + 60 * k)))
              for k in range(6)], CONT, True)
        m.ci(u, v, 0.14, CONT)
        m.ci(u, v, 0.06)
    # cilindro principal y corredera (por encima)
    cu, cv = U / 2, (V - 0.05) / 2
    m.ci(cu, cv, 0.5, OC)
    m.ci(cu, cv, 0.36, OC)
    m.rc(0.85, 0.85, U - 0.85, V - 0.9, OC)
    # mesa con ranuras en T
    for k in (-2, -1, 0, 1, 2):
        m.ln((0.85, cv + k * 0.22), (U - 0.85, cv + k * 0.22))
    # matriz con columnas guía
    m.caja(cu - 0.55, cv - 0.42, cu + 0.55, cv + 0.42, GRIS, FINO)
    for su in (-1, 1):
        for sv in (-1, 1):
            m.ci(cu + su * 0.45, cv + sv * 0.32, 0.05)
    m.ci(cu, cv, 0.2)
    m.ci(cu, cv, 0.12)
    # fleje de alimentación
    m.ln((0, cv - 0.17), (U, cv - 0.17), OC)
    m.ln((0, cv + 0.17), (U, cv + 0.17), OC)
    # central hidráulica posterior
    m.caja(0.7, V - 0.35, U - 0.7, V - 0.02, GRIS2, FINO)
    m.motor(0.9, V - 0.18, 0.45, 0.22)
    m.ci(U - 1.0, V - 0.18, 0.08)
    m.ci(U - 0.8, V - 0.18, 0.05)
    m.manometro(U - 1.25, V - 0.18, 0.05)
    # cortinas de luz y mando bimanual
    for u in (0.32, U - 0.32):
        m.caja(u - 0.05, 0.02, u + 0.05, 0.3, (240, 200, 60), FINO)
    m.ln((0.37, 0.16), (U - 0.37, 0.16), SEG)
    m.botonera(cu - 0.35, 0.02, cu + 0.35, 0.24, 3)
    # tobogán de recortes
    m.pl([(U - 0.3, cv - 0.35), (U, cv - 0.25), (U, cv + 0.25), (U - 0.3, cv + 0.35)], FINO)
    m.tablero(0.0, V - 0.9, 0.28, V - 0.35)


def desbobinador(m):
    U, V = m.Lu, m.Lv
    cv = V / 2
    # base del desbobinador
    m.caja(0.05, 0.15, U * 0.55, V - 0.15, GRIS)
    # rollo (eje horizontal: se ve como un cilindro con generatrices)
    R = min(0.6, U * 0.25)
    cu = 0.1 + R
    w = min(0.45, V * 0.3)
    m.fr(cu - R, cv - w / 2, cu + R, cv + w / 2, ACERO)
    m.rc(cu - R, cv - w / 2, cu + R, cv + w / 2, CONT)
    for k in range(1, 12):
        uu = cu + R * math.cos(math.pi * k / 12)
        m.ln((uu, cv - w / 2), (uu, cv + w / 2))
    # mandril expansible, freno y motorreductor
    m.caja(cu - 0.08, cv + w / 2, cu + 0.08, V - 0.3, GRIS2, FINO)
    m.caja(cu - 0.22, V - 0.42, cu + 0.22, V - 0.18, GRIS2, FINO)
    m.motor(cu + 0.24, V - 0.3, 0.3, 0.16)
    m.ci(cu - 0.32, V - 0.3, 0.08)
    # brazo pisador
    m.rc(cu + R - 0.05, cv - w / 2 - 0.05, cu + R + 0.25, cv + w / 2 + 0.05, OC)
    m.ci(cu + R + 0.12, cv, 0.06, OC)
    # enderezadora de 7 rodillos con volantes de ajuste
    u0 = U * 0.62
    m.caja(u0, cv - w / 2 - 0.25, U - 0.05, cv + w / 2 + 0.25)
    for k in range(7):
        uu = u0 + 0.08 + k * (U - 0.18 - u0) / 6
        m.ln((uu, cv - w / 2 - 0.05), (uu, cv + w / 2 + 0.05), CONT if k % 2 else FINO)
        if k % 2:
            m.ci(uu, cv + w / 2 + 0.17, 0.06)
    m.motor(U * 0.82, cv - w / 2 - 0.12, 0.25, 0.14)
    # fleje entre rollo y enderezadora (lazo) y foso de lazo
    m.ln((cu + R, cv - w / 2 + 0.02), (u0, cv - w / 2 + 0.02))
    m.ln((cu + R, cv + w / 2 - 0.02), (u0, cv + w / 2 - 0.02))
    m.zona(cu + R + 0.3, 0.1, u0 - 0.05, V - 0.1)
    m.tablero(0.05, 0.0, 0.5, 0.12)


def alimentador(m):
    U, V = m.Lu, m.Lv
    cv = V / 2
    m.caja(0.05, 0.1, U - 0.05, V - 0.1)
    for uu in (U * 0.35, U * 0.45):
        m.caja(uu - 0.04, 0.2, uu + 0.04, V - 0.2, GRIS2, FINO)
    for uu in (0.15, 0.25):
        m.ci(uu, cv - 0.22, 0.03)
        m.ci(uu, cv + 0.22, 0.03)
    m.ln((0, cv - 0.17), (U, cv - 0.17), OC)
    m.ln((0, cv + 0.17), (U, cv + 0.17), OC)
    m.motor(U * 0.4, V - 0.22, 0.35, 0.16)
    m.tablero(U - 0.4, 0.12, U - 0.08, 0.35)
    m.rc(U * 0.6, cv - 0.3, U * 0.9, cv + 0.3)
    m.ln((U * 0.6, cv), (U * 0.9, cv))


def laser_tubo(m):
    U, V = m.Lu, m.Lv
    bv = min(V, 1.3)               # ancho de la bancada
    cv = bv / 2
    # bancada y rieles
    m.caja(0.0, cv - 0.38, U, cv + 0.38, GRIS)
    for k in (-0.3, 0.3):
        m.ln((0.05, cv + k), (U - 0.05, cv + k), CONT)
        m.ln((0.05, cv + k + (0.03 if k > 0 else -0.03)), (U - 0.05, cv + k + (0.03 if k > 0 else -0.03)))
    # cremallera
    for i in range(int((U - 0.1) / 0.08)):
        u = 0.05 + i * 0.08
        m.ln((u, cv + 0.33), (u + 0.04, cv + 0.36))
    # soportes en V del tubo
    uc = U - 1.6
    for i in range(int((uc - 1.4) / 0.9)):
        u = 1.4 + i * 0.9
        m.caja(u - 0.08, cv - 0.18, u + 0.08, cv + 0.18, GRIS2, FINO)
        m.ln((u - 0.08, cv), (u + 0.08, cv))
    # tubo (pieza) Ø 76,2
    m.ln((0.6, cv - 0.04), (U - 0.3, cv - 0.04), OC)
    m.ln((0.6, cv + 0.04), (U - 0.3, cv + 0.04), OC)
    # mandril trasero móvil
    m.caja(0.4, cv - 0.42, 1.1, cv + 0.42, GRIS2)
    m.ci(1.0, cv, 0.24, CONT)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        m.ln((1.0 + 0.1 * math.cos(a), cv + 0.1 * math.sin(a)), (1.0 + 0.22 * math.cos(a), cv + 0.22 * math.sin(a)),
             CONT)
    m.motor(0.5, cv, 0.25, 0.16)
    # mandril delantero fijo y cabezal de corte
    m.caja(uc - 0.25, cv - 0.42, uc + 0.15, cv + 0.42, GRIS2)
    m.ci(uc - 0.05, cv, 0.2, CONT)
    m.ci(uc - 0.05, cv, 0.06)
    m.caja(uc + 0.15, cv - 0.5, uc + 0.55, cv + 0.5, ACERO, OC)      # pórtico Y-Z
    m.ci(uc + 0.35, cv, 0.07, CONT)
    m.ci(uc + 0.35, cv, 0.02)
    m.ln((uc + 0.25, cv), (uc + 0.45, cv))
    m.ln((uc + 0.35, cv - 0.1), (uc + 0.35, cv + 0.1))
    # recinto de corte con cerramiento y descarga basculante
    m.zona(uc - 0.35, cv - 0.6, U, cv + 0.6)
    for k in range(3):
        u = uc + 0.75 + k * (U - uc - 0.9) / 2
        m.caja(u - 0.03, cv - 0.55, u + 0.03, cv + 0.15, GRIS2, FINO)
    m.rc(uc + 0.7, cv - 0.58, U - 0.05, cv - 0.38, OC)
    # extracción de humos bajo el corte
    m.ln((uc + 0.35, cv - 0.38), (uc + 0.35, 0.0), OC)
    # cargador de atados (si hay fondo) y fuente láser, enfriador y tablero
    if V > 1.6:
        m.caja(0.6, bv + 0.05, uc - 0.6, V - 0.05, GRIS)
        n = max(2, int((uc - 1.2) / 1.1))
        for i in range(n + 1):
            u = 0.7 + i * (uc - 1.4) / n
            m.caja(u - 0.04, bv + 0.05, u + 0.04, V - 0.05, GRIS2, FINO)
        for j in range(5):
            m.ci(uc / 2, bv + 0.2 + j * 0.09, 0.038)
        m.tablero(uc - 0.4, bv + 0.1, uc + 0.4, V - 0.05)
        m.caja(uc + 0.6, bv + 0.1, U - 0.05, V - 0.05, GRIS2)
        m.ventilador(uc + 0.6 + (U - uc - 0.65) / 2, bv + (V - bv) / 2, min(0.25, (V - bv) / 2 - 0.1))
    else:
        m.tablero(U - 0.55, cv + 0.42, U - 0.05, bv)


def cilindradora(m):
    U, V = m.Lu, m.Lv
    cv = V / 2
    hs = min(0.4, U * 0.13)
    # bastidores (fijo con motorreductor y basculante)
    m.caja(0, 0.1, hs, V - 0.1, GRIS2)
    m.caja(U - hs, 0.15, U, V - 0.15, GRIS2)
    m.ci(U - hs / 2, V - 0.3, 0.07, CONT)
    m.ci(U - hs / 2, 0.3, 0.06)
    # rodillos: superior, inferior y laterales
    d = min(0.24, V * 0.16)
    for (vv, dd, capa, rgb) in ((cv, d, CONT, ACERO), (cv - d * 1.1, d * 0.8, OC, None),
                                 (cv + d * 1.7, d * 0.7, CONT, GRIS), (cv - d * 1.9, d * 0.7, CONT, GRIS)):
        if rgb:
            m.fr(hs, vv - dd / 2, U - hs, vv + dd / 2, rgb)
        m.rc(hs, vv - dd / 2, U - hs, vv + dd / 2, capa)
        m.eje((hs - 0.05, vv), (U - hs + 0.05, vv))
    # motorreductor y freno
    m.motor(hs * 0.15, V - 0.28, hs * 0.7, 0.18)
    m.caja(hs * 0.1, 0.18, hs * 0.9, 0.5, GRIS, FINO)
    # chapa en proceso
    m.rc(hs + 0.1, cv - d * 2.6, U - hs - 0.1, cv - d * 1.35, OC)
    # mesa de apoyo frontal y botonera colgante
    for u in (U * 0.3, U * 0.7):
        m.caja(u - 0.04, 0.0, u + 0.04, cv - d * 2.3, GRIS2, FINO)
    m.botonera(U - hs - 0.4, 0.02, U - hs - 0.08, 0.22)


def sold_long(m):
    U, V = m.Lu, m.Lv
    cv = V * 0.48
    # columna posterior y bastidor
    m.caja(0.0, V - 0.45, U, V - 0.05, GRIS2)
    m.caja(0.1, cv - 0.45, U - 0.4, cv + 0.45, GRIS)
    # mandril con barra de respaldo de cobre
    m.caja(0.15, cv - 0.11, U - 0.35, cv + 0.11, ACERO)
    m.fr(0.15, cv - 0.025, U - 0.35, cv + 0.025, (230, 160, 110))
    m.ln((0.15, cv), (U - 0.35, cv), CONT)
    # dedos neumáticos de sujeción (teclas de piano)
    p = 0.075
    n = int((U - 0.6) / p)
    for i in range(n):
        u = 0.2 + i * p
        m.rc(u, cv + 0.13, u + 0.05, cv + 0.32)
        m.rc(u, cv - 0.32, u + 0.05, cv - 0.13)
    m.rc(0.15, cv + 0.12, U - 0.35, cv + 0.38, OC)
    m.rc(0.15, cv - 0.38, U - 0.35, cv - 0.12, OC)
    # viga del carro de antorcha y carro
    m.ln((0.05, cv + 0.05), (U - 0.05, cv + 0.05), OC)
    m.ln((0.05, cv - 0.05), (U - 0.05, cv - 0.05), OC)
    m.caja(U * 0.38, cv - 0.16, U * 0.38 + 0.3, cv + 0.16, GRIS2, CONT)
    m.ci(U * 0.38 + 0.15, cv, 0.035, CONT)
    m.ln((U * 0.38 + 0.08, cv), (U * 0.38 + 0.22, cv))
    # alimentador de alambre y fuente
    m.caja(0.2, V - 0.42, 0.65, V - 0.08, GRIS, FINO)
    m.ci(0.42, V - 0.25, 0.14)
    m.ci(0.42, V - 0.25, 0.04)
    m.caja(U - 0.6, V - 0.44, U - 0.05, V - 0.06, GRIS2, FINO)
    m.ventilador(U - 0.33, V - 0.25, 0.13)
    m.ln((0.65, V - 0.25), (U * 0.38 + 0.15, cv + 0.16), OC)
    # brazo de extracción, botonera y pedal
    m.extractor(U * 0.75, V - 0.25, U * 0.5, cv + 0.5)
    m.botonera(U - 0.4, 0.02, U - 0.06, 0.24)
    m.caja(U * 0.2, 0.02, U * 0.2 + 0.28, 0.24, GRIS2, FINO)


def sold_circ(m):
    U, V = m.Lu, m.Lv
    cv = V * 0.45
    # bancada con guías
    m.caja(0.0, cv - 0.4, U, cv + 0.4, GRIS)
    for k in (-0.32, 0.32):
        m.ln((0.55, cv + k), (U - 0.05, cv + k), CONT)
    # cabezal giratorio con plato de 3 mordazas
    m.caja(0.0, cv - 0.45, 0.55, cv + 0.5, GRIS2)
    m.motor(0.05, cv + 0.32, 0.3, 0.14)
    m.caja(0.55, cv - 0.25, 0.68, cv + 0.25, ACERO, CONT)
    for k in (-0.17, 0.0, 0.17):
        m.caja(0.68, cv + k - 0.035, 0.76, cv + k + 0.035, OSCURO, FINO)
    # pieza: cuerpo con cúpula y fondo (por encima de la bancada)
    r = min(0.16, V * 0.1)
    u1, u2 = 0.78, U - 0.75
    m.ln((u1 + r, cv - r), (u2 - r, cv - r), OC)
    m.ln((u1 + r, cv + r), (u2 - r, cv + r), OC)
    m.ar(u1 + r, cv, r, 90, 270, OC)
    m.ar(u2 - r, cv, r, 270, 90, OC)
    m.eje((u1 - 0.1, cv), (u2 + 0.1, cv))
    for uu in (u1 + r + 0.05, u2 - r - 0.05):
        m.ln((uu, cv - r), (uu, cv + r), FINO)
    # contrapunto neumático
    m.caja(U - 0.72, cv - 0.24, U - 0.28, cv + 0.24, GRIS2)
    m.pl([(U - 0.72, cv - 0.08), (u2 + 0.02, cv), (U - 0.72, cv + 0.08)], CONT)
    m.caja(U - 0.28, cv - 0.1, U - 0.02, cv + 0.1, ACERO, FINO)
    # columna y brazo porta-antorcha
    uc = (u1 + u2) / 2
    m.fc(uc, V - 0.22, 0.13, GRIS2)
    m.ci(uc, V - 0.22, 0.13, CONT)
    m.ci(uc, V - 0.22, 0.06)
    m.rc(uc - 0.07, cv + 0.05, uc + 0.07, V - 0.22, OC)
    m.caja(uc - 0.12, cv + r + 0.02, uc + 0.12, cv + r + 0.22, GRIS, FINO)
    m.ci(uc, cv + r - 0.02, 0.03, CONT)
    # alimentador, fuente y extracción
    m.caja(uc + 0.2, V - 0.4, uc + 0.55, V - 0.05, GRIS, FINO)
    m.ci(uc + 0.375, V - 0.225, 0.12)
    m.caja(0.05, V - 0.4, 0.5, V - 0.02, GRIS2, FINO)
    m.ventilador(0.27, V - 0.21, 0.12)
    m.extractor(U - 0.3, V - 0.2, uc + 0.35, cv + 0.05)
    m.botonera(U - 0.42, 0.02, U - 0.08, 0.22)


def torno(m):
    """Preparación de cuello: torno de roscado y refrentado de cuello."""
    U, V = m.Lu, m.Lv
    cv = V * 0.5
    m.caja(0.0, 0.15, U, V - 0.1, GRIS)
    m.caja(0.0, 0.15, U * 0.35, V - 0.1, GRIS2)
    m.ci(U * 0.38, cv, min(0.16, V * 0.18), CONT)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        m.ln((U * 0.38 + 0.05 * math.cos(a), cv + 0.05 * math.sin(a)),
             (U * 0.38 + 0.15 * math.cos(a), cv + 0.15 * math.sin(a)))
    m.caja(U * 0.6, cv - 0.15, U * 0.8, cv + 0.15, GRIS2, FINO)
    m.ln((U * 0.6, cv), (U * 0.48, cv), CONT)
    m.ln((U * 0.45, 0.2), (U - 0.05, 0.2), OC)
    m.ci(U - 0.15, V - 0.25, 0.07)
    m.motor(0.05, V - 0.3, U * 0.2, 0.14)
    m.zona(U * 0.33, 0.12, U * 0.85, V - 0.12)


def encastre(m):
    """Prensa neumática de encastre de fondo y cúpula con utillaje y mando bimanual."""
    U, V = m.Lu, m.Lv
    cu, cv = U / 2, V * 0.55
    m.caja(0.05, 0.25, U - 0.05, V - 0.05, GRIS)
    m.caja(0.2, V - 0.3, U - 0.2, V - 0.05, GRIS2)            # columna
    m.ci(cu, cv, min(0.22, U * 0.2), OC)                         # cilindro (arriba)
    m.ci(cu, cv, min(0.12, U * 0.11), OC)
    m.ci(cu, cv, min(0.16, U * 0.14), CONT)                      # utillaje inferior
    m.ci(cu, cv, min(0.08, U * 0.07))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        m.ci(cu + 0.2 * math.cos(a), cv + 0.2 * math.sin(a), 0.02)
    m.ci(U - 0.15, V - 0.17, 0.05)
    m.manometro(0.17, V - 0.17, 0.05)
    m.botonera(cu - 0.3, 0.02, cu + 0.3, 0.2, 2)
    m.zona(0.1, 0.25, U - 0.1, V - 0.3)


def marcadora(m):
    """Numeradora de cuerpo: cabezal de micropercusión sobre prisma en V."""
    U, V = m.Lu, m.Lv
    cv = V * 0.5
    m.caja(0.05, 0.15, U - 0.05, V - 0.05, GRIS)
    m.pl([(0.15, cv - 0.15), (U / 2, cv - 0.02), (U - 0.15, cv - 0.15)], CONT)
    m.pl([(0.15, cv + 0.15), (U / 2, cv + 0.02), (U - 0.15, cv + 0.15)], CONT)
    m.caja(U / 2 - 0.12, V - 0.3, U / 2 + 0.12, V - 0.05, GRIS2)
    m.rc(U / 2 - 0.08, cv - 0.08, U / 2 + 0.08, V - 0.3, OC)
    m.ci(U / 2, cv, 0.03, CONT)
    m.tablero(U - 0.35, V - 0.3, U - 0.08, V - 0.06)


def bordoneadora(m):
    U, V = m.Lu, m.Lv
    cv = V * 0.5
    m.caja(0.05, 0.15, U - 0.05, V - 0.05, GRIS)
    m.caja(U * 0.3, cv - 0.06, U * 0.7, cv - 0.01, ACERO, CONT)
    m.caja(U * 0.3, cv + 0.01, U * 0.7, cv + 0.06, ACERO, CONT)
    m.ci(U * 0.25, cv + 0.25, 0.09)
    for k in range(5):
        a = math.radians(72 * k)
        m.ln((U * 0.25, cv + 0.25), (U * 0.25 + 0.09 * math.cos(a), cv + 0.25 + 0.09 * math.sin(a)))
    m.motor(U * 0.55, V - 0.2, 0.3, 0.15)
    m.caja(U * 0.15, 0.0, U * 0.35, 0.15, GRIS2, FINO)


def inspeccion(m):
    """Mesa de inspección con virador de rodillos, lámpara lupa y negatoscopio."""
    U, V = m.Lu, m.Lv
    m.caja(0.05, 0.1, U - 0.05, V - 0.05, GRIS)
    m.rodillos(0.2, 0.25, U * 0.65, V * 0.6, 0.12)
    m.ci(U * 0.78, V * 0.4, 0.15)
    m.ln((U * 0.78 - 0.1, V * 0.4), (U * 0.78 + 0.1, V * 0.4))
    m.ln((U * 0.78, V * 0.4 - 0.1), (U * 0.78, V * 0.4 + 0.1))
    m.ln((U * 0.78, V * 0.4), (U - 0.15, V - 0.15), FINO)
    m.ci(U - 0.15, V - 0.15, 0.05)
    m.rc(0.2, V * 0.7, U * 0.6, V - 0.1)


def banco(m):
    """Banco de trabajo con morsa, cajonera y tablero de herramientas."""
    U, V = m.Lu, m.Lv
    m.caja(0.0, 0.1, U, V - 0.05, MADERA)
    m.rc(U * 0.62, 0.1, U - 0.05, V * 0.55)
    for k in range(1, 4):
        m.ln((U * 0.62, 0.1 + k * (V * 0.45 - 0.1) / 4), (U - 0.05, 0.1 + k * (V * 0.45 - 0.1) / 4))
    m.caja(0.1, 0.0, 0.32, 0.18, GRIS2, FINO)
    m.ln((0.21, 0.0), (0.21, -0.08))
    m.ln((0.05, V - 0.15), (U - 0.05, V - 0.15), OC)


def banco_sold(m):
    """Puesto de corrección: banco de soldadura, posicionador, amoladora y extracción."""
    U, V = m.Lu, m.Lv
    m.caja(0.0, 0.1, U * 0.62, V - 0.05, GRIS)
    for k in range(1, 6):
        m.ln((U * 0.62 * k / 6, 0.1), (U * 0.62 * k / 6, V - 0.05))
    m.ci(U * 0.31, V * 0.5, 0.2, CONT)
    m.ci(U * 0.31, V * 0.5, 0.08)
    m.caja(U * 0.66, V - 0.5, U - 0.05, V - 0.05, GRIS2, FINO)
    m.ventilador(U * 0.83, V - 0.27, 0.15)
    m.extractor(U * 0.66, 0.25, U * 0.4, V * 0.55)


def posicionador(m):
    """Puesto de punteo y armado de estructura con posicionador de rodillos."""
    U, V = m.Lu, m.Lv
    cv = V * 0.5
    for u in (0.15, U - 0.55):
        m.caja(u, cv - 0.4, u + 0.4, cv + 0.4, GRIS2)
        for s in (-1, 1):
            m.ci(u + 0.2, cv + s * 0.25, 0.1, CONT)
    m.rc(0.3, cv - 0.25, U - 0.3, cv + 0.25, OC)
    m.eje((0.1, cv), (U - 0.1, cv))
    m.caja(U * 0.4, V - 0.35, U * 0.6, V - 0.05, GRIS, FINO)
    m.ci(U * 0.5, V - 0.2, 0.1)
    m.extractor(U * 0.75, V - 0.15, U * 0.55, cv + 0.3)


def ph(m):
    """Prueba hidráulica: jaula de malla con cabezales, bomba, tanque, manómetros y desagüe."""
    U, V = m.Lu, m.Lv
    uj = U * 0.68
    m.fr(0, 0, uj, V, (245, 248, 252))
    m.malla(0, 0, uj, V, 1.0, 0.05)
    # puerta corrediza de la jaula
    m.ln((uj * 0.15, -0.04), (uj * 0.6, -0.04), CONT)
    m.ln((uj * 0.15, -0.09), (uj * 0.6, -0.09), OC)
    # rieles de cabezales con cilindros en prueba
    n = max(2, int((uj - 0.4) / 0.38))
    for fila, vv in enumerate((V * 0.35, V * 0.68)):
        m.ln((0.15, vv + 0.2), (uj - 0.15, vv + 0.2), CONT)
        for i in range(n):
            u = 0.3 + i * (uj - 0.6) / max(1, n - 1)
            m.fc(u, vv, 0.12, ACERO)
            m.ci(u, vv, 0.12, CONT)
            m.ci(u, vv, 0.04)
            m.ln((u, vv + 0.04), (u, vv + 0.2))
            m.ci(u, vv + 0.2, 0.025)
    # rejilla de desagüe
    m.rc(0.1, V * 0.08, uj - 0.1, V * 0.16)
    for k in range(int((uj - 0.2) / 0.06)):
        m.ln((0.12 + k * 0.06, V * 0.08), (0.12 + k * 0.06, V * 0.16))
    # bomba de prueba, tanque de agua, manómetro patrón y tablero
    m.caja(uj + 0.1, V * 0.55, U - 0.05, V - 0.05, AGUA)
    m.rc(uj + 0.15, V * 0.6, U - 0.1, V - 0.1, OC)
    m.ci(uj + (U - uj) * 0.7, V * 0.62 + 0.12, 0.07)
    m.caja(uj + 0.1, V * 0.25, U - 0.05, V * 0.5, GRIS2, FINO)
    m.motor(uj + 0.15, V * 0.375, (U - uj) * 0.45, 0.16)
    m.ci(U - 0.25, V * 0.375, 0.08)
    m.manometro(uj + (U - uj) * 0.4, V * 0.15, 0.09)
    m.manometro(uj + (U - uj) * 0.75, V * 0.15, 0.07)
    m.ln((uj, V * 0.375), (uj - 0.15, V * 0.375), CONT)


def secadora(m):
    """Secadora de cilindros post-PH: gabinete con quemador, recirculación y transportador."""
    horno(m, recirc=True)


def granalladora(m):
    """Granalladora de túnel de rodillos: vestíbulos con cortinas, 4 turbinas, elevador y separador."""
    U, V = m.Lu, m.Lv
    vs = min(0.6, U * 0.15)
    m.caja(vs, 0.1, U - vs, V - 0.1, GRIS)
    for u0 in (0, U - vs):
        m.caja(u0, 0.25, u0 + vs, V - 0.25, ACERO, FINO)
        for k in range(4):
            uu = u0 + vs * (k + 1) / 5
            pts = [(uu + (0.03 if j % 2 else -0.03), 0.3 + j * (V - 0.6) / 10) for j in range(11)]
            m.pl(pts)
    m.rodillos(0.0, V * 0.35, U, V * 0.65, 0.18)
    # turbinas con rodete y motor
    for k in range(4):
        u = vs + (k + 0.5) * (U - 2 * vs) / 4
        v = 0.42 if k % 2 == 0 else V - 0.42
        m.caja(u - 0.25, v - 0.25, u + 0.25, v + 0.25, GRIS2, CONT)
        m.ci(u, v, 0.2)
        for j in range(8):
            a = math.radians(45 * j)
            m.ln((u + 0.06 * math.cos(a), v + 0.06 * math.sin(a)), (u + 0.18 * math.cos(a + 0.3),
                                                                      v + 0.18 * math.sin(a + 0.3)))
    # elevador de cangilones, tornillo de retorno y separador
    m.caja(U / 2 - 0.25, V - 0.1 - 0.5, U / 2 + 0.25, V - 0.1, GRIS2, CONT)
    m.rc(U / 2 - 0.18, V - 0.55, U / 2 + 0.18, V - 0.15)
    m.ln((vs, V * 0.5), (U - vs, V * 0.5), OC)
    m.rc(U / 2 - 0.6, V * 0.2, U / 2 + 0.6, V * 0.8, OC)
    m.zona(-0.05, 0.05, U + 0.05, V - 0.05)


def colector(m):
    """Colector de polvo de cartuchos con tolva, ventilador y venteo de explosión."""
    U, V = m.Lu, m.Lv
    m.caja(0.0, 0.0, U * 0.7, V, GRIS)
    nu, nv = max(1, int(U * 0.7 / 0.38)), max(1, int(V / 0.38))
    for i in range(nu):
        for j in range(nv):
            u, v = (i + 0.5) * U * 0.7 / nu, (j + 0.5) * V / nv
            m.ci(u, v, 0.15)
            m.ci(u, v, 0.06)
    m.ln((0, 0), (U * 0.7, V), OC)
    m.ln((0, V), (U * 0.7, 0), OC)
    m.ventilador(U * 0.85, V * 0.35, min(0.2, U * 0.13))
    m.motor(U * 0.75, V * 0.75, U * 0.2, 0.14)
    m.caja(-0.05, V * 0.3, 0.0, V * 0.7, (240, 200, 60), SEG)


# =================================================================== pintura
def tunel(m):
    """Túnel de pretratamiento por aspersión: etapas con picos, escurrido, tanques y bombas."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (238, 246, 252))
    m.rc(0.08, 0.08, U - 0.08, V - 0.08, CONT)
    etapas = 3
    lz = U / (etapas * 1.4 + (etapas - 1) * 0.0)
    u = 0.0
    for k in range(etapas):
        ue = u + lz
        # picos de aspersión en ambos lados
        for j in range(int(lz / 0.3)):
            uu = u + 0.15 + j * 0.3
            for vv in (0.2, V - 0.2):
                m.ci(uu, vv, 0.04)
                m.ln((uu, vv), (uu, vv + (0.08 if vv < V / 2 else -0.08)))
        m.ln((u, 0.12), (ue, 0.12))
        m.ln((u, V - 0.12), (ue, V - 0.12))
        # tanque (abajo) y bomba
        m.rc(u + 0.1, 0.3, ue - 0.1, V - 0.3, OC)
        m.ci(u + lz / 2, V + 0.2 if V < 1.5 else V - 0.45, 0.1)
        u = ue
        if k < etapas - 1:
            m.ln((u, 0.08), (u, V - 0.08), CONT)
            m.ln((u + lz * 0.4, 0.08), (u + lz * 0.4, V - 0.08))
            m.ray([(u, 0.08), (u + lz * 0.4, 0.08), (u + lz * 0.4, V - 0.08), (u, V - 0.08)], 0.15, 45)
            u += lz * 0.4
    # transportador aéreo con ganchos y piezas colgadas
    m.eje((-0.2, V / 2), (U + 0.2, V / 2))
    for j in range(int(U / 0.5)):
        uu = 0.25 + j * 0.5
        m.ci(uu, V / 2, 0.08)
    m.ventilador(U - 0.4, V - 0.4, 0.2) if V > 1.6 else None


def horno(m, recirc=False):
    """Horno de convección: paneles aislados, quemador con chimenea, recirculación y transportador."""
    U, V = m.Lu, m.Lv
    e = 0.12
    m.fr(0, 0, U, V, CALOR)
    m.fr(e, e, U - e, V - e, (255, 245, 238))
    m.rc(0, 0, U, V, CONT)
    m.rc(e, e, U - e, V - e, CONT)
    m.ray([(0, 0), (U, 0), (U, e), (0, e)], 0.06, 45)
    m.ray([(0, V - e), (U, V - e), (U, V), (0, V)], 0.06, 45)
    # juntas de paneles
    for k in range(1, int(U / 1.0)):
        m.ln((k * 1.0, 0), (k * 1.0, e))
        m.ln((k * 1.0, V - e), (k * 1.0, V))
    # recorrido del transportador (2 pasadas en U)
    a, b = V * 0.33, V * 0.67
    m.eje((-0.3, a), (U - 0.6, a))
    m.eje((U - 0.6, a), (U - 0.6, b))
    m.eje((U - 0.6, b), (-0.3, b))
    for j in range(int((U - 0.8) / 0.4)):
        m.ci(0.2 + j * 0.4, a, 0.07)
        m.ci(0.2 + j * 0.4, b, 0.07)
    # cámara de combustión, quemador y chimenea
    m.caja(U * 0.35, V - e - 0.02, U * 0.65, V + 0.02, GRIS2, FINO) if V > 1.8 else None
    m.ci(U * 0.5, V * 0.5, 0.18, CONT)
    m.ci(U * 0.5, V * 0.5, 0.12)
    m.pl([(U * 0.5 - 0.06, V * 0.5 - 0.05), (U * 0.5, V * 0.5 + 0.08), (U * 0.5 + 0.06, V * 0.5 - 0.05)], FINO,
         True)
    m.ventilador(U * 0.2, V * 0.5, 0.14)
    if recirc:
        m.ventilador(U * 0.8, V * 0.5, 0.14)
    # puerta de inspección
    m.puerta_batiente(U * 0.85, V, 0.5, hacia=1)


def cabina(m):
    """Cabina de pintura en polvo con reciprocadores, pistolas, aberturas de silueta y retoque manual."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (245, 245, 252))
    m.rc(0.05, 0.05, U - 0.05, V - 0.05)
    # aberturas de silueta en los extremos
    for u in (0.0, U):
        m.ln((u, V * 0.38), (u, V * 0.62), FINO)
    m.eje((-0.3, V / 2), (U + 0.3, V / 2))
    for j in range(int(U / 0.4)):
        m.ci(0.2 + j * 0.4, V / 2, 0.06)
    # reciprocadores con pistolas
    for v, s in ((0.15, 1), (V - 0.15, -1)):
        m.caja(U * 0.3, v - 0.1, U * 0.7, v + 0.1, GRIS2, CONT)
        for k in range(3):
            uu = U * 0.35 + k * U * 0.15
            m.pl([(uu, v + s * 0.1), (uu - 0.03, v + s * 0.3), (uu + 0.03, v + s * 0.3)], CONT, True)
    # abertura de retoque manual
    m.ln((U * 0.8, 0.0), (U * 0.95, 0.0), SEG)
    # centro de polvo (tolva fluidizada) y ducto a ciclones
    m.ci(U * 0.15, V * 0.25, 0.12)
    m.ci(U * 0.15, V * 0.25, 0.05)
    m.rc(U - 0.3, V * 0.3, U, V * 0.7, OC)


def ciclones(m):
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, GRIS)
    n = max(1, int(U / 1.2))
    for i in range(n):
        u = (i + 0.5) * U / n
        r = min(V * 0.42, U / n * 0.4)
        m.fc(u, V / 2, r, ACERO)
        m.ci(u, V / 2, r, CONT)
        m.ci(u, V / 2, r * 0.45)
        m.ci(u, V / 2, r * 0.15)
        m.rc(u - r, V / 2 + r * 0.55, u, V / 2 + r * 0.95)
    m.rc(0, 0, U, V, OC)


def enfriamiento(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (235, 245, 252))
    if U > V:
        m.eje((0, V / 2), (U, V / 2))
    else:
        m.eje((U / 2, 0), (U / 2, V))
    if U > V:
        for j in range(int(U / 0.4)):
            m.ci(0.2 + j * 0.4, V / 2, 0.07)
        for j in range(int(U / 1.6)):
            m.ventilador(0.8 + j * 1.6, 0.35, 0.22)
            m.ventilador(0.8 + j * 1.6, V - 0.35, 0.22)
    else:
        for j in range(int(V / 0.4)):
            m.ci(U / 2, 0.2 + j * 0.4, 0.07)
        for j in range(int(V / 1.6)):
            m.ventilador(0.35, 0.8 + j * 1.6, 0.22)
            m.ventilador(U - 0.35, 0.8 + j * 1.6, 0.22)


def estacion_pintura(m):
    """Estación de carga o descarga del transportador aéreo: lazo con ganchos, carros y puestos."""
    U, V = m.Lu, m.Lv
    m.fr(0, 0, U, V, (248, 248, 248))
    r = min(U, V) * 0.22
    a, b = (U * 0.25, V * 0.5), (U * 0.75, V * 0.5)
    m.eje((a[0], a[1] - r), (b[0], b[1] - r))
    m.eje((a[0], a[1] + r), (b[0], b[1] + r))
    m.ar(a[0], a[1], r, 90, 270, "A-EJE")
    m.ar(b[0], b[1], r, 270, 90, "A-EJE")
    n = int((b[0] - a[0]) / 0.4)
    for j in range(n + 1):
        u = a[0] + j * (b[0] - a[0]) / n
        for vv in (a[1] - r, a[1] + r):
            m.ci(u, vv, 0.06)
            m.ln((u, vv - 0.06), (u, vv - 0.18))
    # carros de piezas
    for u0 in (0.2, U - 1.4):
        m.caja(u0, 0.15, u0 + 1.2, 0.95, GRIS, FINO)
        m.cilindros(u0 + 0.05, 0.2, u0 + 1.15, 0.9, 0.18)
        for (uu, vv) in ((u0 + 0.1, 0.15), (u0 + 1.1, 0.15), (u0 + 0.1, 0.95), (u0 + 1.1, 0.95)):
            m.ci(uu, vv, 0.05)
    m.rc(0.05, 0.05, U - 0.05, V - 0.05, OC)


def retoque(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0.1, U, V, GRIS)
    m.rc(0.1, 0.2, U * 0.55, V - 0.1)
    m.ci(U * 0.3, V * 0.55, 0.15)
    m.caja(U * 0.62, V * 0.3, U - 0.1, V - 0.1, GRIS2, FINO)
    m.ci(U * 0.8, V * 0.65, 0.06)
    m.ln((U * 0.62, V * 0.2), (U - 0.1, V * 0.2), OC)


# =================================================================== terminación
def carga_polvo(m):
    """Estación de big bag con puente de izaje, tolva, dosificador, balanza y extracción."""
    U, V = m.Lu, m.Lv
    s = min(1.5, V - 0.2, U * 0.5)
    u0, v0 = 0.1, V - s - 0.05
    # bastidor y big bag
    m.fr(u0, v0, u0 + s, v0 + s, POLVO)
    for (u, v) in ((u0, v0), (u0 + s, v0), (u0, v0 + s), (u0 + s, v0 + s)):
        m.poste(u, v, 0.12)
    m.rc(u0, v0, u0 + s, v0 + s, CONT)
    m.pl(_circ(u0 + s / 2, v0 + s / 2, s * 0.42, 32), OC, True)
    for (u, v) in ((u0 + 0.2, v0 + 0.2), (u0 + s - 0.2, v0 + 0.2), (u0 + 0.2, v0 + s - 0.2),
                   (u0 + s - 0.2, v0 + s - 0.2)):
        m.ci(u, v, 0.04)
    m.rc(u0 - 0.06, v0 + s / 2 - 0.06, u0 + s + 0.06, v0 + s / 2 + 0.06, OC)      # viga de izaje
    # tolva y válvula
    c = (u0 + s / 2, v0 + s / 2)
    m.ci(c[0], c[1], s * 0.28)
    m.ci(c[0], c[1], s * 0.08, CONT)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        m.ln((c[0] + s * 0.08 * math.cos(a), c[1] + s * 0.08 * math.sin(a)),
             (c[0] + s * 0.28 * math.cos(a), c[1] + s * 0.28 * math.sin(a)))
    # dosificador y llenadora sobre balanza
    uf = u0 + s + 0.25
    m.caja(uf, 0.25, U - 0.1, v0 + s * 0.6, GRIS, FINO)
    m.ln((uf, 0.25), (U - 0.1, v0 + s * 0.6))
    m.ln((uf, v0 + s * 0.6), (U - 0.1, 0.25))
    m.ci((uf + U - 0.1) / 2, (0.25 + v0 + s * 0.6) / 2, 0.12, CONT)
    m.ci((uf + U - 0.1) / 2, (0.25 + v0 + s * 0.6) / 2, 0.05)
    m.ln(c, ((uf + U - 0.1) / 2, (0.25 + v0 + s * 0.6) / 2), OC)
    m.caja(U - 0.45, V - 0.4, U - 0.08, V - 0.08, GRIS2, FINO)
    m.rc(U - 0.4, V - 0.3, U - 0.13, V - 0.18)
    # campana de extracción
    m.extractor(U - 0.25, V - 0.6, (uf + U - 0.1) / 2 + 0.25, (0.25 + v0 + s * 0.6) / 2 + 0.25)
    m.rodillos(uf, 0.0, U - 0.1, 0.22, 0.1)


def deshumidificador(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS)
    m.ventilador(U * 0.25, V / 2, min(V, U / 2) * 0.38)
    m.rc(U * 0.5, 0.1, U - 0.1, V - 0.1)
    for k in range(int((U * 0.5 - 0.2) / 0.08)):
        m.ln((U * 0.5 + 0.05 + k * 0.08, 0.1), (U * 0.5 + 0.05 + k * 0.08, V - 0.1))
    m.rc(U * 0.2, V, U * 0.4, V + 0.2, OC)


def ensamble(m):
    """Puesto de ensamblaje de válvula: banco con atornilladora de torque, alimentación de piezas."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0.1, U, V - 0.05, MADERA)
    m.ci(U * 0.4, V * 0.45, 0.12, CONT)
    m.ci(U * 0.4, V * 0.45, 0.05)
    m.ln((U * 0.4, V * 0.45), (U * 0.4, V - 0.1), OC)
    for k in range(4):
        m.rc(U * 0.6 + k * U * 0.09, V * 0.6, U * 0.6 + k * U * 0.09 + U * 0.08, V - 0.1)
    m.rodillos(0.05, 0.12, U * 0.25, V - 0.1, 0.1, "v")
    m.ln((0.05, V - 0.08), (U - 0.05, V - 0.08), OC)


def presurizacion(m):
    """Presurización con N2: manifold con mangueras, manómetros y jaula de protección."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0.1, U, V - 0.05, GRIS)
    m.caja(0.1, V - 0.25, U - 0.1, V - 0.12, ACERO, FINO)
    n = max(2, int((U - 0.2) / 0.3))
    for i in range(n):
        u = 0.25 + i * (U - 0.5) / max(1, n - 1)
        m.manometro(u, V - 0.185, 0.045)
        m.pl([(u, V - 0.25), (u + 0.05, V * 0.6), (u, V * 0.4)], OC)
        m.ci(u, V * 0.35, 0.07)
    m.rc(0.05, 0.15, U - 0.05, V * 0.6, SEG)


def hermeticidad(m):
    """Cuba de inmersión con agua para control de pérdidas."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0.1, U, V - 0.05, GRIS2)
    m.fr(0.08, 0.18, U - 0.08, V - 0.13, AGUA)
    m.rc(0.08, 0.18, U - 0.08, V - 0.13)
    for k in range(3):
        v = 0.3 + k * (V - 0.55) / 2
        pts = [(0.15 + j * (U - 0.3) / 12, v + (0.02 if j % 2 else -0.02)) for j in range(13)]
        m.pl(pts, OC)
    m.cilindros(U * 0.3, V * 0.3, U * 0.7, V * 0.75, 0.16)


def etiquetadora(m):
    U, V = m.Lu, m.Lv
    m.rodillos(0, 0.15, U, V * 0.55, 0.08)
    m.caja(U * 0.35, V * 0.58, U * 0.75, V - 0.05, GRIS2)
    m.ci(U * 0.45, V * 0.78, 0.1)
    m.ci(U * 0.65, V * 0.78, 0.1)
    m.ci(U * 0.45, V * 0.78, 0.03)
    m.ci(U * 0.65, V * 0.78, 0.03)
    m.tablero(U * 0.8, V * 0.6, U - 0.05, V - 0.05)


def palletizado(m):
    """Puesto de embalaje y palletizado: pallet en mesa giratoria, cajas y fleje."""
    U, V = m.Lu, m.Lv
    a, b = min(1.2, U - 0.2), min(1.0, V - 0.3)
    m.ci(0.1 + a / 2, 0.25 + b / 2, max(a, b) * 0.62, OC)
    m.pallet(0.1, 0.25, a, b, "cil")
    if U > a + 0.5:
        m.caja(a + 0.25, 0.25, U - 0.05, V - 0.05, MADERA)
        for k in range(3):
            m.rc(a + 0.3, 0.3 + k * (V - 0.4) / 3, U - 0.1, 0.3 + (k + 1) * (V - 0.4) / 3 - 0.05)


def envolvedora(m):
    """Envolvedora de pallets: plato giratorio, mástil con carro de film, rampa."""
    U, V = m.Lu, m.Lv
    s = min(U, V)
    c = (s / 2, s / 2) if V >= U else (s / 2, V / 2)
    m.fc(c[0], c[1], s * 0.46, GRIS)
    m.ci(c[0], c[1], s * 0.46, CONT)
    m.ci(c[0], c[1], s * 0.08)
    m.pallet(c[0] - 0.6 * min(1, s / 1.4), c[1] - 0.5 * min(1, s / 1.4), 1.2 * min(1, s / 1.4),
             1.0 * min(1, s / 1.4), "caja")
    if V >= U:
        m.caja(0.05, s + 0.02, s - 0.05, s + 0.35, GRIS2)
        m.ci(s * 0.5, s + 0.18, 0.08)
        m.rc(0.1, s + 0.4, s - 0.1, V - 0.05, OC)
        m.ar(c[0], c[1], s * 0.55, 200, 340, SEG)
    else:
        m.caja(s + 0.02, 0.05, s + 0.35, V - 0.05, GRIS2)


def balanza(m):
    U, V = m.Lu, m.Lv
    m.caja(0.05, 0.05, U - 0.05, V - 0.05, GRIS)
    m.ln((0.05, 0.05), (U - 0.05, V - 0.05))
    m.ln((0.05, V - 0.05), (U - 0.05, 0.05))
    for (u, v) in ((0.15, 0.15), (U - 0.15, 0.15), (0.15, V - 0.15), (U - 0.15, V - 0.15)):
        m.ci(u, v, 0.05)
    m.caja(U - 0.05, V * 0.4, U + 0.15, V * 0.6, GRIS2, FINO)


def mesa_tijera(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS)
    m.ln((0.1, 0.1), (U - 0.1, V - 0.1), OC)
    m.ln((0.1, V - 0.1), (U - 0.1, 0.1), OC)
    m.rc(0.15, 0.15, U - 0.15, V - 0.15, CONT)
    for k in range(1, 8):
        m.ln((0.15, 0.15 + k * (V - 0.3) / 8), (U - 0.15, 0.15 + k * (V - 0.3) / 8))
    m.ci(0.15, V / 2, 0.04)


def mesa_bolas(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, GRIS)
    for i in range(int((U - 0.1) / 0.18)):
        for j in range(int((V - 0.1) / 0.18)):
            m.ci(0.12 + i * 0.18, 0.12 + j * 0.18, 0.025)


def mesa_rodillos(m):
    m.rodillos(0, 0, m.Lu, m.Lv, 0.12, "u" if m.Lu >= m.Lv else "v")


def mesa_control(m):
    """Mesa de control de recepción: mesa, micrómetro, PC y armario de certificados."""
    U, V = m.Lu, m.Lv
    m.caja(0, 0.1, U, V - 0.05, MADERA)
    m.rc(U * 0.1, V * 0.4, U * 0.35, V - 0.15)
    m.ln((U * 0.1, V * 0.4), (U * 0.35, V - 0.15))
    m.rc(U * 0.45, V * 0.55, U * 0.65, V - 0.12, CONT)
    m.rc(U * 0.7, V * 0.3, U - 0.1, V - 0.12)
    m.ci(U * 0.55, V * 0.35, 0.06)


def pluma(m):
    """Pluma giratoria: columna, pluma con polipasto y radio de barrido."""
    U, V = m.Lu, m.Lv
    c = (U / 2, V / 2)
    m.fc(c[0], c[1], U / 2, GRIS2)
    m.ci(c[0], c[1], U / 2, CONT)
    m.ci(c[0], c[1], U / 4)
    R = 4.0
    m.ci(c[0], c[1], R, SEG)
    m.rc(c[0], c[1] - 0.1, c[0] + R, c[1] + 0.1, OC)
    m.caja(c[0] + R * 0.6, c[1] - 0.18, c[0] + R * 0.6 + 0.35, c[1] + 0.18, GRIS, FINO)
    m.ci(c[0] + R * 0.6 + 0.175, c[1], 0.07)


def cabina_muestras(m):
    U, V = m.Lu, m.Lv
    m.caja(0, 0, U, V, (245, 245, 252))
    m.rc(0.1, V - 0.6, U - 0.1, V - 0.1, CONT)
    for k in range(int((U - 0.3) / 0.25)):
        m.ci(0.25 + k * 0.25, V - 0.35, 0.09)
    m.caja(0.3, 0.6, U - 0.3, 1.2, MADERA, FINO)
    m.ci(U / 2, 0.9, 0.2, CONT)
    m.ci(U / 2, 0.9, 0.06)
    m.ln((0.0, 0.0), (U * 0.4, 0.0), SEG)


def rack(m):
    """Rack selectivo de pallets: bastidores con diagonales, largueros, pallets y protecciones."""
    U, V = m.Lu, m.Lv
    vano = 2.7 if V >= 0.9 else 1.4
    n = max(1, round(U / vano))
    vano = U / n
    m.rc(0, 0, U, V, OC)
    m.ln((0, 0.06), (U, 0.06), CONT)
    m.ln((0, V - 0.06), (U, V - 0.06), CONT)
    for i in range(n + 1):
        u = min(max(i * vano, 0.05), U - 0.05)
        m.poste(u, 0.06, 0.1, OSCURO)
        m.poste(u, V - 0.06, 0.1, OSCURO)
        pts = [(u + (0.02 if j % 2 else -0.02), 0.06 + j * (V - 0.12) / 4) for j in range(5)]
        m.pl(pts)
        m.pl([(u - 0.07, 0.0), (u, -0.08), (u + 0.07, 0.0)], SEG)
    for i in range(n):
        u0 = i * vano
        k = max(1, int((vano - 0.1) / 1.25))
        a = min(1.2, (vano - 0.15) / k - 0.08)
        for j in range(k):
            pu = u0 + 0.1 + j * (vano - 0.1) / k
            m.pallet(pu, 0.08, a, min(1.0, V - 0.16), "caja")


def kanban(m):
    """Estantería dinámica (FIFO): carriles de rodillos inclinados con cajas KLT."""
    U, V = m.Lu, m.Lv
    largo = max(U, V)
    m.caja(0, 0, U, V, GRIS)
    if U >= V:
        n = max(1, int((U - 0.1) / 0.62))
        for i in range(n):
            u0 = 0.05 + i * (U - 0.1) / n
            u1 = u0 + (U - 0.1) / n - 0.06
            m.rodillos(u0, 0.05, u1, V - 0.05, 0.09, "v")
            for j in range(int((V - 0.1) / 0.42)):
                m.rc(u0 + 0.03, 0.08 + j * 0.42, u1 - 0.03, 0.08 + j * 0.42 + 0.38, CONT)
    else:
        n = max(1, int((V - 0.1) / 0.62))
        for i in range(n):
            v0 = 0.05 + i * (V - 0.1) / n
            v1 = v0 + (V - 0.1) / n - 0.06
            m.rodillos(0.05, v0, U - 0.05, v1, 0.09, "u")
            for j in range(int((U - 0.1) / 0.42)):
                m.rc(0.08 + j * 0.42, v0 + 0.03, 0.08 + j * 0.42 + 0.38, v1 - 0.03, CONT)
    _ = largo


def pulmon(m):
    """Pulmón de cilindros: carros con cilindros parados y ruedas."""
    U, V = m.Lu, m.Lv
    largo, prof = (U, V) if U >= V else (V, U)
    n = max(1, int(largo / 1.3))
    for i in range(n):
        a0 = i * largo / n + 0.05
        a1 = (i + 1) * largo / n - 0.05
        if U >= V:
            m.caja(a0, 0.05, a1, V - 0.05, GRIS, FINO)
            m.cilindros(a0 + 0.04, 0.09, a1 - 0.04, V - 0.09, 0.18)
            for (uu, vv) in ((a0 + 0.08, 0.05), (a1 - 0.08, 0.05), (a0 + 0.08, V - 0.05), (a1 - 0.08, V - 0.05)):
                m.ci(uu, vv, 0.05)
            m.ln((a1, V / 2), (a1 + 0.04, V / 2), CONT)
        else:
            m.caja(0.05, a0, U - 0.05, a1, GRIS, FINO)
            m.cilindros(0.09, a0 + 0.04, U - 0.09, a1 - 0.04, 0.18)
            for (uu, vv) in ((0.05, a0 + 0.08), (0.05, a1 - 0.08), (U - 0.05, a0 + 0.08), (U - 0.05, a1 - 0.08)):
                m.ci(uu, vv, 0.05)
    _ = prof


def carros(m):
    """Estacionamiento de extintores rodantes (carros) a pintura tercerizada."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, OC)
    nu, nv = max(1, int(U / 0.9)), max(1, int(V / 1.0))
    for i in range(nu):
        for j in range(nv):
            u, v = (i + 0.5) * U / nu, (j + 0.5) * V / nv
            m.caja(u - 0.3, v - 0.3, u + 0.3, v + 0.3, GRIS, FINO)
            m.ci(u, v + 0.05, 0.22, CONT)
            m.ci(u, v + 0.05, 0.06)
            for s in (-1, 1):
                m.caja(u + s * 0.36 - 0.05, v - 0.28, u + s * 0.36 + 0.05, v - 0.02, OSCURO, FINO)
            m.ln((u - 0.25, v + 0.3), (u + 0.25, v + 0.3), CONT)


def paquetes(m):
    """Paquetes de chapa a piso (2 alturas): bloques de 1,6 × 3,1 m con la pila de hojas y separadores."""
    U, V = m.Lu, m.Lv
    nu = max(1, int(U / 1.75))
    nv = max(1, int(V / 2.6))
    du, dv = U / nu, V / nv
    for i in range(nu):
        for j in range(nv):
            u0, v0 = i * du + 0.08, j * dv + 0.08
            u1, v1 = (i + 1) * du - 0.08, (j + 1) * dv - 0.08
            m.caja(u0, v0, u1, v1, (232, 236, 242), CONT)
            m.rc(u0 + 0.08, v0 + 0.08, u1 - 0.08, v1 - 0.08)
            m.ln((u0 + 0.08, v0 + 0.08), (u1 - 0.08, v1 - 0.08))
            for k in (0.25, 0.75):
                m.rc(u0 + 0.1, v0 + (v1 - v0) * k - 0.05, u1 - 0.1, v0 + (v1 - v0) * k + 0.05, OC)


def cantilever(m):
    """Cantiléver: columna central, brazos cada 1 m y atados de caño apoyados a lo largo."""
    U, V = m.Lu, m.Lv
    vc = V / 2
    m.caja(0, vc - 0.1, U, vc + 0.1, OSCURO, CONT)
    for i in range(int(U / 1.0) + 1):
        u = min(i * 1.0 + 0.1, U - 0.1)
        m.caja(u - 0.05, 0.05, u + 0.05, V - 0.05, GRIS2, FINO)
    for vv in (0.25, 0.45, V - 0.45, V - 0.25):
        m.ln((0.0, vv), (U, vv), CONT)
        m.ln((0.0, vv + 0.06), (U, vv + 0.06))


def portaflejes(m):
    """Porta-flejes: bastidor con rollos de fleje (Ø 1,0 m) apoyados de canto."""
    U, V = m.Lu, m.Lv
    m.rc(0, 0, U, V, CONT)
    n = max(1, int(U / 1.1))
    r = min(0.5, V / 2 - 0.05)
    for i in range(n):
        u = (i + 0.5) * U / n
        m.fc(u, V / 2, r, (225, 230, 236))
        m.ci(u, V / 2, r, CONT)
        m.ci(u, V / 2, r * 0.5)
        m.ci(u, V / 2, r * 0.75, OC)


def estanteria(m):
    """Estantería de pañol: módulos con cruz (como el rev4), parantes y estantes."""
    U, V = m.Lu, m.Lv
    n = max(1, int(U / 1.0))
    for i in range(n):
        u0, u1 = i * U / n, (i + 1) * U / n
        m.caja(u0, 0, u1, V, GRIS, FINO)
        m.ln((u0, 0), (u1, V))
        m.ln((u0, V), (u1, 0))
        m.poste(u0 + 0.04, 0.04, 0.06)
        m.poste(u1 - 0.04, V - 0.04, 0.06)


def contenedores(m):
    """Contenedores basculantes de scrap (1 m³) con bocas de horquilla."""
    U, V = m.Lu, m.Lv
    n = max(1, int(U / 1.5))
    for i in range(n):
        u0, u1 = i * U / n + 0.1, (i + 1) * U / n - 0.1
        m.caja(u0, 0.1, u1, V - 0.1, (230, 230, 230), CONT)
        m.pl([(u0 + 0.1, 0.1), (u0 + 0.25, V - 0.25), (u1 - 0.25, V - 0.25), (u1 - 0.1, 0.1)])
        for k in (0.3, 0.7):
            m.rc(u0 + (u1 - u0) * k - 0.12, 0.1, u0 + (u1 - u0) * k + 0.12, 0.3, OC)


# =================================================================== vehículos
def autoelevador(pl, x, y, ang, carga=True):
    """Autoelevador de 3,0 t (planta): contrapeso, techo de protección, mástil, horquillas y pallet."""
    m = M.centro(pl, x, y, ang, 3.9, 1.25)
    v = 0.625
    m.fl([(0.0, v - 0.55), (2.45, v - 0.6), (2.45, v + 0.6), (0.0, v + 0.55)], (255, 230, 150))
    m.pl([(0.25, v - 0.6), (2.45, v - 0.6), (2.45, v + 0.6), (0.25, v + 0.6)], VEH)
    m.ar(0.25 + 0.0, v, 0.6, 90, 270, VEH)
    m.rc(0.7, v - 0.55, 1.95, v + 0.55, OC)                          # techo
    m.ln((0.7, v - 0.55), (1.95, v + 0.55), OC)
    m.ln((0.7, v + 0.55), (1.95, v - 0.55), OC)
    m.rc(1.1, v - 0.25, 1.5, v + 0.25, VEH)                          # asiento
    m.ci(1.75, v, 0.14, VEH)                                         # volante
    for uu, w in ((0.55, 0.45), (2.05, 0.55)):                       # ruedas
        for s in (-1, 1):
            m.caja(uu - w / 2, v + s * 0.62 - 0.11, uu + w / 2, v + s * 0.62 + 0.11, (60, 60, 60), VEH)
    m.caja(2.45, v - 0.5, 2.62, v + 0.5, OSCURO, VEH)                # mástil
    for s in (-1, 1):
        m.caja(2.62, v + s * 0.33 - 0.06, 3.82, v + s * 0.33 + 0.06, OSCURO, VEH)
    if carga:
        m.pallet(2.66, v - 0.5, 1.2, 1.0, "caja")
    m.fin()


def transpaleta(pl, x, y, ang):
    m = M.centro(pl, x, y, ang, 1.6, 0.56)
    m.caja(0.0, 0.0, 0.4, 0.56, (255, 230, 150), VEH)
    m.ci(0.2, 0.28, 0.08, VEH)
    m.ln((0.2, 0.28), (-0.25, 0.28), VEH)
    for s in (0.08, 0.36):
        m.caja(0.4, s, 1.6, s + 0.12, OSCURO, VEH)
    m.fin()


def tren(pl, x, y, ang, n=3, carga=True):
    """Tren logístico: tractor eléctrico y n carros con barras de tiro (x, y = centro del tractor)."""
    largo = 1.7 + n * 2.3
    m = M.centro(pl, x - math.cos(math.radians(ang)) * (largo / 2 - 0.85),
                 y - math.sin(math.radians(ang)) * (largo / 2 - 0.85), ang, largo, 1.1)
    u = largo
    m.caja(u - 1.6, 0.05, u, 1.05, (255, 230, 150), VEH)
    m.rc(u - 1.2, 0.15, u - 0.6, 0.95, VEH)
    m.ci(u - 0.45, 0.55, 0.12, VEH)
    for uu in (u - 1.35, u - 0.3):
        for vv in (0.0, 1.1):
            m.caja(uu - 0.15, vv - 0.07, uu + 0.15, vv + 0.07, (60, 60, 60), VEH)
    u -= 1.7
    for i in range(n):
        m.ln((u, 0.55), (u + 0.1, 0.55), VEH)
        m.caja(u - 2.1, 0.05, u - 0.1, 1.05, GRIS, VEH)
        if carga:
            m.cilindros(u - 2.0, 0.12, u - 0.2, 0.98, 0.2)
        for uu in (u - 1.8, u - 0.4):
            for vv in (0.0, 1.1):
                m.caja(uu - 0.12, vv - 0.06, uu + 0.12, vv + 0.06, (60, 60, 60), VEH)
        u -= 2.3
    m.fin()


# =================================================================== despacho
SIMBOLOS = {
    "guillotina": guillotina, "prensa": prensa, "desbobinador": desbobinador, "alimentador": alimentador,
    "laser": laser_tubo, "cilindradora": cilindradora, "sold_long": sold_long, "sold_circ": sold_circ,
    "torno": torno, "encastre": encastre, "marcadora": marcadora, "bordoneadora": bordoneadora,
    "inspeccion": inspeccion, "banco": banco, "banco_sold": banco_sold, "posicionador": posicionador,
    "ph": ph, "secadora": secadora, "granalladora": granalladora, "colector": colector, "tunel": tunel,
    "horno": horno, "cabina": cabina, "ciclones": ciclones, "enfriamiento": enfriamiento,
    "estacion_pintura": estacion_pintura, "retoque": retoque, "carga_polvo": carga_polvo,
    "deshumidificador": deshumidificador, "ensamble": ensamble, "presurizacion": presurizacion,
    "hermeticidad": hermeticidad, "etiquetadora": etiquetadora, "palletizado": palletizado,
    "envolvedora": envolvedora, "balanza": balanza, "mesa_tijera": mesa_tijera, "mesa_bolas": mesa_bolas,
    "mesa_rodillos": mesa_rodillos, "mesa_control": mesa_control, "pluma": pluma,
    "cabina_muestras": cabina_muestras, "rack": rack, "kanban": kanban, "pulmon": pulmon, "carros": carros,
    "paquetes": paquetes, "cantilever": cantilever, "portaflejes": portaflejes, "estanteria": estanteria,
    "contenedores": contenedores,
}

CLAVES = [
    ("guillotina", "guillotina"), ("prensa de corte", "prensa"), ("desbobinador", "desbobinador"),
    ("alimentador", "alimentador"), ("láser", "laser"), ("cilindrad", "cilindradora"),
    ("soldadura longitudinal", "sold_long"), ("soldadura circ", "sold_circ"), ("prueba hidráulica", "ph"),
    ("ph 4", "ph"), ("ph ", "ph"), ("secadora", "secadora"), ("granallad", "granalladora"),
    ("colector", "colector"), ("túnel", "tunel"), ("horno", "horno"), ("cabina de pintura", "cabina"),
    ("ciclones", "ciclones"), ("enfriamiento", "enfriamiento"), ("tren de carga", "estacion_pintura"),
    ("tren de descarga", "estacion_pintura"), ("retoque", "retoque"), ("carga de polvo", "carga_polvo"),
    ("deshumidificador", "deshumidificador"), ("descarga de muestras", "cabina_muestras"),
    ("envolvedora", "envolvedora"), ("etiquetadora", "etiquetadora"), ("presurización", "presurizacion"),
    ("hermeticidad", "hermeticidad"), ("palletizado", "palletizado"), ("embalaje", "palletizado"),
    ("ensamblaje", "ensamble"), ("armado de carros", "ensamble"), ("pluma", "pluma"), ("balanza", "balanza"),
    ("mesa elevadora", "mesa_tijera"), ("mesa de bolas", "mesa_bolas"), ("mesa de salida", "mesa_rodillos"),
    ("mesa de control", "mesa_control"), ("preparación de cuello", "torno"), ("numerad", "marcadora"),
    ("marcado", "marcadora"), ("encastre", "encastre"), ("bordonead", "bordoneadora"),
    ("detección", "inspeccion"), ("inspección", "inspeccion"), ("corrección", "banco_sold"),
    ("punteo", "posicionador"), ("probetas", "banco"), ("rack", "rack"), ("estructuras y ruedas", "rack"),
    ("carros a pintura", "carros"), ("pulmón", "pulmon"), ("kanban", "kanban"), ("supermercado", "kanban"),
    ("cúpulas (kanban)", "kanban"),
]


def tipo_de(e):
    t = getattr(e, "tipo", "") or ""
    if t:
        return t
    n = e.nombre.lower()
    for clave, tipo in CLAVES:
        if clave in n:
            return tipo
    return "banco"


def frente_de(e):
    f = getattr(e, "frente", "") or ""
    if f:
        return f
    r = e.rect
    return "S" if r.w >= r.h else "O"


def operario_rev(m, u, v, mira=90.0):
    """Operario estilo de planta (bloque de rev4): semicírculo de hombros y cabeza, mirando a `mira`."""
    a = math.radians(mira)
    f = (math.cos(a), math.sin(a))
    t = (-f[1], f[0])
    r = 0.30
    arco = [(u + t[0] * r * math.cos(s_) - f[0] * r * math.sin(s_), v + t[1] * r * math.cos(s_) - f[1] * r * math.sin(s_))
            for s_ in [math.pi * i / 12 for i in range(13)]]
    m.fl(arco + [arco[0]], (250, 225, 245))
    m.pl(arco, OP, True)
    m.fc(u + f[0] * 0.02, v + f[1] * 0.02, 0.12, BLANCO)
    m.ci(u + f[0] * 0.02, v + f[1] * 0.02, 0.12, OP)


def area_trabajo(m, n_op):
    """Marco del área de trabajo (máquina + puesto), abierto en el frente para el acceso del operario."""
    U, V = m.Lu, m.Lv
    e, fr, g = 0.15, 0.95, 0.45
    u0, u1, v0, v1 = -e, U + e, -fr, V + e
    m.pl([(u0, v0), (u0, v1), (u1, v1), (u1, v0)], AREA)
    huecos = sorted(U * (i + 1) / (n_op + 1) for i in range(max(1, n_op)))
    x = u0
    for h in huecos:
        if h - g > x:
            m.ln((x, v0), (h - g, v0), AREA)
        x = h + g
    if x < u1:
        m.ln((x, v0), (u1, v0), AREA)


SIN_PUESTO = ("rack", "kanban", "pulmon", "carros", "pluma", "paquetes", "cantilever", "portaflejes",
              "estanteria", "contenedores")


def dibujar(pl, e, operarios=True):
    """Dibuja el equipo `e` con su símbolo, su área de trabajo y sus operarios al frente."""
    t = tipo_de(e)
    fn = SIMBOLOS.get(t, banco)
    m = M.rect(pl, e.rect, frente_de(e), getattr(e, "espejo", False))
    fn(m)
    if operarios and e.op > 0 and t not in SIN_PUESTO:
        n = int(e.op)
        area_trabajo(m, n)
        for i in range(n):
            operario_rev(m, m.Lu * (i + 1) / (n + 1), -0.48, 90.0)
    m.fin()
    return t
