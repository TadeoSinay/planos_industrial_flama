"""Genera salida/Recargas.xlsx: logística de recargas de las dos plantas (camión, viajes, sustitutos y pulmón).

Rearma el Recargas.xlsx del grupo: todo lo que viene de la demanda sale por IMPORTRANGE de los Dimensionamientos de
recargas (recargas por tipo, mix por rubro, lote, días en planta, ciclo y stock de sustitutos), el perfil es plano
(IRAM 3517-2 9.4.14 a), los sustitutos son los del dimensionamiento (un solo número) y el vehículo es el camión con
baranda rebatible y jaulas palletizables del Word de recargas. Hojas: Links -> Importados -> Supuestos -> Demanda y mix
-> Camión y viajes -> Sustitutos y pulmón -> Resumen.
"""

import os
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter as L

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_dim_recargas as g  # noqa: E402
from generar_dim_recargas import cab, celda, hoja, nota, tit  # noqa: E402

PLANTAS = ["Comercial", "Industrial"]
LINKS = [("Dimensionamiento Recargas Planta Comercial", g.PEGAR, "datos_base, PROY_Indexado, sobrestock_sustitutos y "
          "parametros_recargas de la planta comercial"),
         ("Dimensionamiento Recargas Planta Industrial", g.PEGAR, "lo mismo de la planta industrial")]
LK = {"Comercial": "Links!$B$4", "Industrial": "Links!$B$5"}
TIPOS = [n for n, v in g.REC]
# Importados: primera fila de cada bloque y desplazamientos
IMP0 = {"Comercial": 4, "Industrial": 104}
O_REC, O_MIX, O_LOT, O_STK, O_LLE, O_PAR = 1, 20, 39, 50, 69, 88
LOTE_FILAS = ["% de las recargas", "Lote por cliente", "Superficie mínima del lote (m²)", "Minutos por equipo",
              "Minutos del lote", "Días en planta con 1 turno", "Días en planta con 2 turnos", "Ciclo con 1 turno",
              "Ciclo con 2 turnos"]
PAR_FILAS = [t for r, t, v, f, d, fu in g.P_GEN]
# Supuestos: filas
S = {"anio": 5, "turnos": 6, "dias": 7, "horas": 8, "modelo": 11, "carga": 12, "pos": 13, "pers": 14, "kgp": 15,
     "tara": 16, "neta": 17, "precio": 18, "iv": 21, "parada": 22, "manejo": 23, "d_rec": 26, "d_desp": 27,
     "medio": 28, "vacias": 29, "niveles": 30, "apil": 31, "m2pos": 32, "tipo1": 35, "rub1": 55}
# peso lleno: BOM FLAMA (Resumen, peso de catálogo) y, para los carros, Word de carros (Tabla 0, carro terminado)
PESO = [1.9, 4.6, 8.5, 16.5, 12.55, 12.6, 100, 8.5, 8.25, 9, 20, 8.5, 16.5, 53, 90, 136, 179]
F_PESO = ["BOM FLAMA, peso de catálogo"] * 13 + ["Word de carros, Tabla 0 (carro terminado)"] * 4
# u. por jaula de 1,2 × 1,0 m: Word de recargas (A: 72 de 1 kg; B: 30 de 2,5, 24 de 5 o 16 de 10 kg); el resto por
# tamaño parecido y los rodantes por posición (Recargas.xlsx del grupo)
U_JAULA = [72, 30, 24, 16, 16, 16, 2, 24, 20, 30, 20, 24, 16, 3, 2, 2, 1]
JAULA = ["A"] + ["B"] * 5 + ["Rodantes"] + ["B"] * 6 + ["Rodantes"] * 4
MIN_U = [0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.0]   # min por u. en el cliente (Recargas.xlsx, Supuestos E84:E90)


def datos_dim(planta):
    """Valores actuales del Dimensionamiento de la planta (lo que trae cada IMPORTRANGE)."""
    wb = load_workbook(os.path.join(g.SALIDA, f"Dimensionamiento_Recargas_Planta_{planta}.xlsx"), data_only=True)
    db, px, ss, pr = wb["datos_base"], wb["PROY_Indexado"], wb[g.SS], wb["parametros_recargas"]
    return {"rec": [[db.cell(2 + k, 2 + i).value for i in range(10)] for k in range(17)],
            "mix": [[px.cell(g.P_MIX + k, 2 + c).value for c in range(7)] for k in range(17)],
            "lot": [[ss.cell(g.S_RUB + j, 2 + c).value for c in range(7)] for j in range(9)],
            "stk": [[ss.cell(g.S_STOCK + k, 2 + i).value for i in range(10)] for k in range(17)],
            "lle": [[ss.cell(g.S_TIPO + k, 2).value] for k in range(17)],
            "par": [[pr.cell(2 + j, 2).value] for j in range(9)]}


def h_importados(wb, datos):
    ws = hoja(wb, "Importados", [40] + [11] * 16)
    tit(ws, 1, "Importados de los Dimensionamientos de recargas (IMPORTRANGE; el link va en la hoja Links)")
    nota(ws, 2, "No se escribe nada acá: cada bloque es un IMPORTRANGE y el resto del libro lee de esta hoja.")
    for p in PLANTAS:
        r0, d, lk = IMP0[p], datos[p], LK[p]
        tit(ws, r0, f"Planta {p.lower()}")
        cab(ws, r0 + O_REC, ["Recargas por tipo (datos_base B2:K18)"] + g.ANIOS)
        for k in range(17):
            celda(ws, r0 + O_REC + 1 + k, 1, TIPOS[k])
        g.importrange(ws, r0 + O_REC + 1, 2, lk, "datos_base!B2:K18", d["rec"], "#,##0")
        cab(ws, r0 + O_MIX, ["Mix de mercado (PROY_Indexado B97:H113)"] + g.RUBROS + ["Total"]
            + [f"% {x.split(' ')[0]}" for x in g.RUBROS])
        for k in range(17):
            r = r0 + O_MIX + 1 + k
            celda(ws, r, 1, TIPOS[k])
            celda(ws, r, 9, f"=SUM(B{r}:H{r})", "#,##0", res=True)
            for c in range(7):
                celda(ws, r, 10 + c, f"=IF($I{r}=0,0,{L(2 + c)}{r}/$I{r})", "0.0%")
        g.importrange(ws, r0 + O_MIX + 1, 2, lk, f"PROY_Indexado!B{g.P_MIX}:H{g.P_MIX + 16}", d["mix"], "#,##0")
        cab(ws, r0 + O_LOT, [f"Lote y ciclo por rubro (sobrestock_sustitutos B{g.S_RUB}:H{g.S_RUB + 8})"] + g.RUBROS)
        for j, t in enumerate(LOTE_FILAS):
            celda(ws, r0 + O_LOT + 1 + j, 1, t)
        g.importrange(ws, r0 + O_LOT + 1, 2, lk, f"sobrestock_sustitutos!B{g.S_RUB}:H{g.S_RUB + 8}", d["lot"], "0.0")
        cab(ws, r0 + O_STK, [f"Stock de sustitutos (sobrestock_sustitutos B{g.S_STOCK}:K{g.S_STOCK + 16})"] + g.ANIOS)
        for k in range(17):
            celda(ws, r0 + O_STK + 1 + k, 1, TIPOS[k])
        g.importrange(ws, r0 + O_STK + 1, 2, lk, f"sobrestock_sustitutos!B{g.S_STOCK}:K{g.S_STOCK + 16}", d["stk"],
                      "#,##0")
        cab(ws, r0 + O_LLE, [f"Lleva sustituto (sobrestock_sustitutos B{g.S_TIPO}:B{g.S_TIPO + 16})", "1 = sí"])
        for k in range(17):
            celda(ws, r0 + O_LLE + 1 + k, 1, TIPOS[k])
        g.importrange(ws, r0 + O_LLE + 1, 2, lk, f"sobrestock_sustitutos!B{g.S_TIPO}:B{g.S_TIPO + 16}", d["lle"], "0")
        cab(ws, r0 + O_PAR, ["Parámetros de planta (parametros_recargas B2:B10)", "Valor"])
        for j, t in enumerate(PAR_FILAS):
            celda(ws, r0 + O_PAR + 1 + j, 1, t)
        g.importrange(ws, r0 + O_PAR + 1, 2, lk, "parametros_recargas!B2:B10", d["par"], "0.00")
    ws.freeze_panes = "B4"


def imp(p, o, k=0, col="B"):
    return f"Importados!${col}${IMP0[p] + o + 1 + k}"


def anio_col(p, o, k):
    """Valor del año de cálculo en un bloque por año de Importados."""
    r = IMP0[p] + o + 1 + k
    h = IMP0[p] + o
    return f"INDEX(Importados!$B${r}:$K${r},MATCH(Supuestos!$B${S['anio']},Importados!$B${h}:$K${h},0))"


def h_supuestos(wb):
    ws = hoja(wb, "Supuestos", [52, 16, 12, 12, 14, 90])
    tit(ws, 1, "Supuestos y datos de logística (cada uno con su fuente o criterio)")
    nota(ws, 2, "La demanda, el mix, el lote, los días en planta y los sustitutos no se cargan acá: vienen de Importados.")

    def fila(r, t, v, fmt, fu, dato=True):
        celda(ws, r, 1, t)
        celda(ws, r, 2, v, fmt, dato=dato, res=not dato).alignment = g.CEN
        celda(ws, r, 3, fu)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)

    cab(ws, 4, ["1. Generales", "Valor", "Fuente / criterio"])
    ws.merge_cells("C4:F4")
    fila(S["anio"], "Año de cálculo", 2035, "0", "Año que se dimensiona (último del horizonte de Proyecciones)")
    fila(S["turnos"], "Turnos de logística por día", 2, "0",
         "Criterio del grupo (Recargas.xlsx original): el camión sale a la mañana y a la tarde")
    fila(S["dias"], "Días hábiles por año", f"={imp('Comercial', O_PAR, 0)}*12", "0",
         "parametros_recargas B2 × 12 (importado)", dato=False)
    fila(S["horas"], "Horas productivas por turno", f"={imp('Comercial', O_PAR, 3)}", "0.00",
         "parametros_recargas B5 (importado)", dato=False)
    cab(ws, 10, ["2. Camión (Word de recargas)", "Valor", "Fuente / criterio"])
    ws.merge_cells("C10:F10")
    fila(S["modelo"], "Vehículo", "Iveco cabina simple con caja de baranda rebatible", None,
         "Word de recargas: jaulas palletizables 1,2 × 1,0 m que se cargan y descargan con autoelevador por el costado")
    fila(S["carga"], "Carga útil (kg)", 2000, "#,##0", "Word de recargas: capacidad aprox. 2 t (pico de carga 1,2 t)")
    fila(S["pos"], "Posiciones de jaula 1,2 × 1,0 m en la caja", 6, "0",
         "Criterio: 2 a lo ancho × 3 a lo largo en una caja de unos 3,7 × 2,1 m sobre el chasis Daily de 3.450 mm entre "
         "ejes (Autocosmos, Daily 55C17: largo total 5.803 mm). Confirmar con el carrocero")
    fila(S["pers"], "Personas a bordo (chofer + ayudante)", 2, "0", "Criterio del grupo (Recargas.xlsx original)")
    fila(S["kgp"], "Peso por persona (kg)", 80, "0", "Criterio del grupo (Recargas.xlsx original)")
    fila(S["tara"], "Tara de jaulas y cinchas (% de la carga útil)", 0.1, "0%",
         "Criterio del grupo (Recargas.xlsx original)")
    fila(S["neta"], "Carga neta por viaje (kg)", f"=(B{S['carga']}-B{S['pers']}*B{S['kgp']})*(1-B{S['tara']})",
         "#,##0", "Carga útil − personas − tara", dato=False)
    fila(S["precio"], "Precio del camión con caja (ARS)", None, "#,##0", "A cotizar (concesionario Iveco + carrocero)")
    cab(ws, 20, ["3. Recorrido", "Valor", "Fuente / criterio"])
    ws.merge_cells("C20:F20")
    fila(S["iv"], "Ida y vuelta planta ↔ zona de clientes (h por viaje)", 1.5, "0.0",
         "Criterio del grupo (Recargas.xlsx original): clientes en AMBA, ~25 km por tramo")
    fila(S["parada"], "Tiempo fijo por parada (min)", 20, "0",
         "Criterio del grupo: estacionar, presentarse, remito y firma")
    fila(S["manejo"], "Manejo entre paradas (min)", 15, "0", "Criterio del grupo (Recargas.xlsx original)")
    cab(ws, 25, ["4. Pulmón", "Valor", "Fuente / criterio"])
    ws.merge_cells("C25:F25")
    fila(S["d_rec"], "Días de llegada que esperan en recepción", 0.5, "0.0",
         "Criterio del grupo: lo que trae un turno entra al proceso en el turno siguiente")
    fila(S["d_desp"], "Días de recargados que esperan el recorrido", 0.5, "0.0",
         "Criterio del grupo: salen en el turno siguiente")
    fila(S["medio"], "Factor de jaulas a medio llenar", 1.15, "0.00",
         "Criterio del grupo: las jaulas se separan por cliente y familia de agente (Word: agrupados por cliente)")
    fila(S["vacias"], "Jaulas vacías de reserva (% de las ocupadas)", 0.15, "0%", "Criterio del grupo")
    fila(S["niveles"], "Niveles de la estantería de sustitutos", 3, "0",
         "Criterio del grupo: los sustitutos van en estantería; los rodantes, en el piso")
    fila(S["apil"], "Jaulas vacías apiladas por posición", 2, "0", "Criterio del grupo: de a 2 con transpaleta")
    fila(S["m2pos"], "Superficie por posición con pasillo (m²)", "=1.2*1*2", "0.0",
         "Posición de 1,2 × 1,0 m × 2 (pasillo de transpaleta compartido por dos filas)")
    cab(ws, S["tipo1"] - 1, ["5. Tipos", "Peso lleno (kg)", "u. por jaula", "Jaula", "Rodante (1 = sí)",
                             "Fuente del peso"])
    for k in range(17):
        r = S["tipo1"] + k
        celda(ws, r, 1, TIPOS[k])
        celda(ws, r, 2, PESO[k], "0.0", dato=True)
        celda(ws, r, 3, U_JAULA[k], "0", dato=True)
        celda(ws, r, 4, JAULA[k]).alignment = g.CEN
        celda(ws, r, 5, 1 if JAULA[k] == "Rodantes" else 0, "0")
        celda(ws, r, 6, F_PESO[k])
    nota(ws, S["tipo1"] + 17, "u. por jaula: Word de recargas (A: 72 de 1 kg; B: 30 de 2,5 kg, 24 de 5 kg o 16 de 10 "
                              "kg); el resto por tamaño parecido y los rodantes por posición (Recargas.xlsx del grupo).")
    cab(ws, S["rub1"] - 1, ["6. Rubros", "min por u. en el cliente", "", "", "", "Fuente / criterio"])
    for c, rb in enumerate(g.RUBROS):
        r = S["rub1"] + c
        celda(ws, r, 1, rb)
        celda(ws, r, 2, MIN_U[c], "0.0", dato=True)
        celda(ws, r, 6, "Recargas.xlsx original (Supuestos E84:E90), criterio del grupo")
    nota(ws, S["rub1"] + 8, "Ya no se usan: estacionalidad por rubro y factor de día pico (el perfil es plano, IRAM "
                            "3517-2 9.4.14 a), % con transitorio por rubro (lo define el dimensionamiento por tipo) y "
                            "vehículos Kangoo / Master (el Word usa el camión con jaulas).")


def bloque_dem(p):
    return 4 + 34 * PLANTAS.index(p)


def h_demanda(wb):
    ws = hoja(wb, "Demanda y mix", [36] + [13] * 11)
    tit(ws, 1, "Demanda del año de cálculo y mix (perfil plano: cada día llega lo mismo)")
    for p in PLANTAS:
        r0 = bloque_dem(p)
        tit(ws, r0, f"Planta {p.lower()}")
        cab(ws, r0 + 1, ["Tipo", "Recargas del año (u)", "u/día", "Lleva sustituto", "Sustitutos que salen por día",
                         "Peso lleno (kg)", "u. por jaula", "Jaulas por día", "Rodante"])
        t1, t17 = r0 + 2, r0 + 18
        for k in range(17):
            r = r0 + 2 + k
            st = S["tipo1"] + k
            celda(ws, r, 1, TIPOS[k])
            celda(ws, r, 2, f"={anio_col(p, O_REC, k)}", "#,##0")
            celda(ws, r, 3, f"=B{r}/Supuestos!$B${S['dias']}", "#,##0.0")
            celda(ws, r, 4, f"={imp(p, O_LLE, k)}", "0")
            celda(ws, r, 5, f"=C{r}*D{r}", "#,##0.0")
            celda(ws, r, 6, f"=Supuestos!$B${st}", "0.0")
            celda(ws, r, 7, f"=Supuestos!$C${st}", "0")
            celda(ws, r, 8, f"=C{r}/G{r}", "0.00")
            celda(ws, r, 9, f"=Supuestos!$E${st}", "0")
        rt = r0 + 19
        celda(ws, rt, 1, "Total", neg=True)
        for c in (2, 3, 5, 8):
            col = L(c)
            celda(ws, rt, c, f"=SUM({col}{t1}:{col}{t17})", "#,##0.0", res=True)
        celda(ws, rt, 6, f"=SUMPRODUCT(C{t1}:C{t17},F{t1}:F{t17})/C{rt}", "0.0", res=True)
        cab(ws, r0 + 21, ["Rubro", "u/día", "% del total", "Sustitutos por día", "Lote (u/cliente)",
                          "Clientes por día", "Paradas por día", "min por u. en el cliente", "Horas de parada por día",
                          "Días en planta", "Ciclo del sustituto (días)"])
        for c, rb in enumerate(g.RUBROS):
            r = r0 + 22 + c
            sh = f"Importados!${L(10 + c)}${IMP0[p] + O_MIX + 1}:${L(10 + c)}${IMP0[p] + O_MIX + 17}"
            col = L(2 + c)
            dos = f"Supuestos!$B${S['anio']}>={imp(p, O_PAR, 8)}"
            celda(ws, r, 1, rb)
            celda(ws, r, 2, f"=SUMPRODUCT($C${t1}:$C${t17},{sh})", "#,##0.0")
            celda(ws, r, 3, f"=B{r}/$C${rt}", "0.0%")
            celda(ws, r, 4, f"=SUMPRODUCT($E${t1}:$E${t17},{sh})", "#,##0.0")
            celda(ws, r, 5, f"={imp(p, O_LOT, 1, col)}", "0")
            celda(ws, r, 6, f"=B{r}/E{r}", "0.0")
            celda(ws, r, 7, f"=2*F{r}", "0.0")
            celda(ws, r, 8, f"=Supuestos!$B${S['rub1'] + c}", "0.0")
            celda(ws, r, 9, f"=G{r}*(Supuestos!$B${S['parada']}+Supuestos!$B${S['manejo']})/60+2*B{r}*H{r}/60",
                  "0.0")
            celda(ws, r, 10, f"=IF({dos},{imp(p, O_LOT, 6, col)},{imp(p, O_LOT, 5, col)})", "0")
            celda(ws, r, 11, f"=IF({dos},{imp(p, O_LOT, 8, col)},{imp(p, O_LOT, 7, col)})", "0")
        rr = r0 + 29
        celda(ws, rr, 1, "Total", neg=True)
        for c in (2, 3, 4, 6, 7, 9):
            col = L(c)
            celda(ws, rr, c, f"=SUM({col}{r0 + 22}:{col}{r0 + 28})", "0.0%" if c == 3 else "#,##0.0", res=True)
        nota(ws, rr + 1, "Paradas = 2 por cliente (retiro con sustituto y devolución). Horas de parada = paradas × "
                         "(parada + manejo) + 2 manipulaciones por u. en el cliente. Días en planta y ciclo: del "
                         "dimensionamiento, con 2 turnos desde el año del 2° turno.")
    ws.freeze_panes = "B4"


def h_camion(wb):
    ws = hoja(wb, "Camión y viajes", [58, 16, 16, 90])
    tit(ws, 1, "Camión y viajes por día (cada viaje lleva recargados + sustitutos y trae lo retirado + sustitutos)")
    cab(ws, 3, ["Concepto", "Comercial", "Industrial", "Cómo se calcula"])
    filas = []

    def f(t, fx, fmt, como):
        filas.append((t, fx, fmt, como))

    sp = "Supuestos!$B$"
    f("Equipos que se retiran por día (u)", lambda p, r0: f"='Demanda y mix'!C{r0 + 19}", "#,##0.0",
      "Demanda y mix, total u/día")
    f("Sustitutos que salen por día (u)", lambda p, r0: f"='Demanda y mix'!E{r0 + 19}", "#,##0.0",
      "Demanda y mix, total de sustitutos")
    f("Carga por sentido por día (u)", lambda p, r0: "={c}4+{c}5", "#,##0.0",
      "Sale con recargados + sustitutos y vuelve con lo retirado + sustitutos devueltos")
    f("Peso medio por u. (kg)", lambda p, r0: f"='Demanda y mix'!F{r0 + 19}", "0.0", "Promedio pesado por u/día")
    f("Jaulas por u.", lambda p, r0: f"='Demanda y mix'!H{r0 + 19}/'Demanda y mix'!C{r0 + 19}", "0.000",
      "Jaulas por día ÷ u/día (cada tipo en su jaula)")
    f("Capacidad por viaje por espacio (u)", lambda p, r0: f"={sp}{S['pos']}/({{c}}8*{sp}{S['medio']})", "#,##0",
      "Posiciones de la caja ÷ (jaulas por u. × factor de jaulas a medio llenar)")
    f("Capacidad por viaje por peso (u)", lambda p, r0: f"={sp}{S['neta']}/{{c}}7", "#,##0",
      "Carga neta ÷ peso medio")
    f("Capacidad por viaje (u)", lambda p, r0: "=MIN({c}9,{c}10)", "#,##0", "La menor de las dos")
    f("Viajes por día por carga", lambda p, r0: "={c}6/{c}11", "0.00", "Carga por sentido ÷ capacidad por viaje")
    f("Paradas por día", lambda p, r0: f"='Demanda y mix'!G{r0 + 29}", "0.0", "Demanda y mix, total de paradas")
    f("Horas de parada y manipuleo por día", lambda p, r0: f"='Demanda y mix'!I{r0 + 29}", "0.0",
      "Demanda y mix, total")
    f("Viajes por día por tiempo", lambda p, r0: f"={{c}}14/({sp}{S['horas']}-{sp}{S['iv']})", "0.00",
      "Horas de parada ÷ (horas del turno − ida y vuelta): cada viaje entra en un turno")
    f("Viajes por día", lambda p, r0: "=ROUNDUP(MAX({c}12,{c}15),0)", "0", "El mayor de los dos, redondeado")
    f("Horas de camión por día", lambda p, r0: f"={{c}}16*{sp}{S['iv']}+{{c}}14", "0.0",
      "Viajes × ida y vuelta + horas de parada y manipuleo")
    f("Camiones necesarios", lambda p, r0: f"=ROUNDUP({{c}}17/({sp}{S['horas']}*{sp}{S['turnos']}),0)", "0",
      "Horas de camión ÷ (horas por turno × turnos de logística)")
    f("Ocupación de la flota", lambda p, r0: f"={{c}}17/({{c}}18*{sp}{S['horas']}*{sp}{S['turnos']})", "0%",
      "Horas de camión ÷ horas disponibles")
    f("Peso por viaje (kg)", lambda p, r0: "={c}6*{c}7/{c}16", "#,##0",
      "Control: tiene que quedar por debajo de la carga neta")
    f("Inversión en camiones (ARS)", lambda p, r0: f'=IF({sp}{S["precio"]}="","a cotizar",{{c}}18*{sp}{S["precio"]})',
      "#,##0", "Camiones × precio (Supuestos)")
    for j, (t, fx, fmt, como) in enumerate(filas):
        r = 4 + j
        celda(ws, r, 1, t, neg=(t in ("Viajes por día", "Camiones necesarios")))
        for i, p in enumerate(PLANTAS):
            c = L(2 + i)
            celda(ws, r, 2 + i, fx(p, bloque_dem(p)).replace("{c}", c), fmt,
                  res=(t in ("Viajes por día", "Camiones necesarios"))).alignment = g.DER
        celda(ws, r, 4, como)
    nota(ws, 4 + len(filas) + 1, "El camión carga y descarga las jaulas con el autoelevador por el costado (Word de "
                                 "recargas); las jaulas van agrupadas por cliente en el orden del recorrido.")


def bloque_pul(p):
    return 4 + 32 * PLANTAS.index(p)


def h_pulmon(wb):
    ws = hoja(wb, "Sustitutos y pulmón", [36] + [13] * 7 + [70])
    tit(ws, 1, "Sustitutos y pulmón de recargas (año de cálculo)")
    for p in PLANTAS:
        r0, rd = bloque_pul(p), bloque_dem(p)
        tit(ws, r0, f"Planta {p.lower()}")
        cab(ws, r0 + 1, ["Tipo", "Stock de sustitutos (u)", "Salen por día", "En planta por día (u)",
                         "Jaulas en planta", "Rodante"])
        t1, t17 = r0 + 2, r0 + 18
        for k in range(17):
            r = r0 + 2 + k
            d = rd + 2 + k
            celda(ws, r, 1, TIPOS[k])
            celda(ws, r, 2, f"={anio_col(p, O_STK, k)}", "#,##0")
            celda(ws, r, 3, f"='Demanda y mix'!E{d}", "#,##0.0")
            celda(ws, r, 4, f"=C{r}", "#,##0.0")
            celda(ws, r, 5, f"=D{r}/'Demanda y mix'!G{d}", "0.00")
            celda(ws, r, 6, f"='Demanda y mix'!I{d}", "0")
        rt = r0 + 19
        celda(ws, rt, 1, "Total", neg=True)
        for c in (2, 3, 4, 5):
            col = L(c)
            celda(ws, rt, c, f"=SUM({col}{t1}:{col}{t17})", "#,##0.0", res=True)
        nota(ws, rt + 1, "Stock: del dimensionamiento (Little: sustitutos por día × ciclo). En planta: los que vuelven "
                         "con la devolución esperan hasta el retiro del día siguiente.")
        cab(ws, r0 + 21, ["Zona del pulmón", "Matafuegos (u)", "Jaulas de manuales", "Jaulas de rodantes",
                          "Posiciones 1,2 × 1,0 m", "", "", "", "Dónde y cómo van"])
        sp = "Supuestos!$B$"
        dm = "'Demanda y mix'!"
        man = f"SUMPRODUCT(({dm}$I${rd + 2}:$I${rd + 18}=0)*{dm}$H${rd + 2}:$H${rd + 18})"
        rod = f"SUMPRODUCT(({dm}$I${rd + 2}:$I${rd + 18}=1)*{dm}$H${rd + 2}:$H${rd + 18})"
        zonas = [("Recepción", f"={dm}C{rd + 19}*{sp}{S['d_rec']}", f"={man}*{sp}{S['d_rec']}*{sp}{S['medio']}",
                  f"={rod}*{sp}{S['d_rec']}", "=ROUNDUP(C{r},0)+ROUNDUP(D{r},0)",
                  "Jaulas A (1 kg) y B por cliente, en orden de llegada; rodantes en su jaula"),
                 ("Despacho", f"={dm}C{rd + 19}*{sp}{S['d_desp']}", f"={man}*{sp}{S['d_desp']}*{sp}{S['medio']}",
                  f"={rod}*{sp}{S['d_desp']}", "=ROUNDUP(C{r},0)+ROUNDUP(D{r},0)",
                  "Jaulas armadas por recorrido y en el orden de entrega"),
                 ("Sustitutos en planta", f"=D{rt}", f"=SUMPRODUCT((F{t1}:F{t17}=0)*E{t1}:E{t17})",
                  f"=SUMPRODUCT((F{t1}:F{t17}=1)*E{t1}:E{t17})", f"=ROUNDUP(C{{r}}/{sp}{S['niveles']},0)+ROUNDUP(D{{r}},0)",
                  "Estantería con faja amarilla, por tipo; rodantes en el piso"),
                 ("Jaulas vacías", "—", "—", "—",
                  f"=ROUNDUP(SUM(E{r0 + 22}:E{r0 + 24})*{sp}{S['vacias']}/{sp}{S['apil']},0)",
                  "Apiladas de a 2, junto a despacho")]
        for j, (z, u, cm, cr, pos, donde) in enumerate(zonas):
            r = r0 + 22 + j
            celda(ws, r, 1, z)
            celda(ws, r, 2, u, "#,##0")
            celda(ws, r, 3, cm, "0.0")
            celda(ws, r, 4, cr, "0.0")
            celda(ws, r, 5, pos.replace("{r}", str(r)), "0")
            celda(ws, r, 9, donde)
        r = r0 + 26
        celda(ws, r, 1, "Total de posiciones", neg=True)
        celda(ws, r, 5, f"=SUM(E{r0 + 22}:E{r0 + 25})", "0", res=True)
        celda(ws, r + 1, 1, "Superficie del pulmón con pasillo (m²)", neg=True)
        celda(ws, r + 1, 5, f"=E{r}*{sp}{S['m2pos']}", "0.0", res=True)
        ci = L(2 + PLANTAS.index(p))
        celda(ws, r + 2, 1, "Jaulas A y B a tener (planta + camiones + vacías)", neg=True)
        celda(ws, r + 2, 5, f"=ROUNDUP(SUM(C{r0 + 22}:C{r0 + 23})+C{r0 + 24},0)+'Camión y viajes'!{ci}18*{sp}{S['pos']}"
                            f"+E{r0 + 25}*{sp}{S['apil']}", "0", res=True)
    ws.freeze_panes = "B4"


def h_resumen(wb):
    ws = hoja(wb, "Resumen", [62, 16, 16, 70])
    tit(ws, 1, "Recargas — logística de las dos plantas")
    nota(ws, 2, "Todo se calcula con Importados (IMPORTRANGE de los dimensionamientos) y Supuestos.")
    celda(ws, 3, 1, "Año de cálculo", neg=True)
    celda(ws, 3, 2, f"=Supuestos!B{S['anio']}", "0", res=True)
    cab(ws, 5, ["Concepto", "Comercial", "Industrial", "De dónde sale"])
    filas = [("Recargas del año (u)", lambda p: f"='Demanda y mix'!B{bloque_dem(p) + 19}", "#,##0", "Importados"),
             ("Llegan por día (u)", lambda p: f"='Demanda y mix'!C{bloque_dem(p) + 19}", "#,##0", "Perfil plano"),
             ("Sustitutos que salen por día (u)", lambda p: f"='Demanda y mix'!E{bloque_dem(p) + 19}", "#,##0",
              "Tipos que llevan sustituto"),
             ("Stock de sustitutos (u)", lambda p: f"='Sustitutos y pulmón'!B{bloque_pul(p) + 19}", "#,##0",
              "Dimensionamiento, paso 3"),
             ("Paradas por día", lambda p: f"='Demanda y mix'!G{bloque_dem(p) + 29}", "#,##0", "2 por cliente"),
             ("Viajes por día", lambda p: f"='Camión y viajes'!{L(2 + PLANTAS.index(p))}16", "0", "Camión y viajes"),
             ("Camiones", lambda p: f"='Camión y viajes'!{L(2 + PLANTAS.index(p))}18", "0", "Camión y viajes"),
             ("Ocupación de la flota", lambda p: f"='Camión y viajes'!{L(2 + PLANTAS.index(p))}19", "0%",
              "Camión y viajes"),
             ("Posiciones del pulmón", lambda p: f"='Sustitutos y pulmón'!E{bloque_pul(p) + 26}", "0",
              "Sustitutos y pulmón"),
             ("Superficie del pulmón (m²)", lambda p: f"='Sustitutos y pulmón'!E{bloque_pul(p) + 27}", "0.0",
              "Sustitutos y pulmón"),
             ("Jaulas A y B a tener", lambda p: f"='Sustitutos y pulmón'!E{bloque_pul(p) + 28}", "0",
              "Sustitutos y pulmón")]
    for j, (t, fx, fmt, de) in enumerate(filas):
        r = 6 + j
        celda(ws, r, 1, t, neg=True)
        for i, p in enumerate(PLANTAS):
            celda(ws, r, 2 + i, fx(p), fmt, res=True).alignment = g.DER
        celda(ws, r, 4, de)
    r = 6 + len(filas) + 1
    tit(ws, r, "Qué cambió respecto del Recargas.xlsx anterior")
    cambios = ["Demanda por IMPORTRANGE de cada planta (antes: 127.340 fijos de una sola planta); PBA Interior afuera.",
               "Mix por rubro de las zonas de cada planta (Proyecciones) en vez del mercado nacional de CONSOLIDADO_24; "
               "carros 25/55/12/8 % en vez de todos como 50 kg.",
               "Perfil plano (IRAM 3517-2 9.4.14 a): sin estacionalidad inventada por rubro ni factor de día pico.",
               "Sustitutos del dimensionamiento (lote, días en planta y ciclo por rubro): un solo número en los dos "
               "archivos.",
               "Camión con baranda rebatible y jaulas del Word de recargas en vez de Kangoo / Master.",
               "Pesos del BOM y del Word de carros; pulmón calculado sin comparar con el plano viejo."]
    for j, t in enumerate(cambios):
        nota(ws, r + 1 + j, "• " + t)


def generar():
    datos = {p: datos_dim(p) for p in PLANTAS}
    wb = Workbook()
    wb.remove(wb.active)
    g.h_links(wb, LINKS)
    h_importados(wb, datos)
    h_supuestos(wb)
    h_demanda(wb)
    h_camion(wb)
    h_pulmon(wb)
    h_resumen(wb)
    wb.move_sheet("Resumen", offset=-(len(wb.sheetnames) - 2))
    wb.active = wb.sheetnames.index("Resumen")
    ruta = os.path.join(g.SALIDA, "Recargas.xlsx")
    wb.save(ruta)
    return ruta


if __name__ == "__main__":
    print(generar())
