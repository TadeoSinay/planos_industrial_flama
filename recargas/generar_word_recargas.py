"""Genera salida/Justificacion_Recargas.docx: cómo se decidió cada valor de los Aprovechamientos de recargas, de
Recargas.xlsx y de los sustitutos que importan Manuales y Carros, qué implica en cada puesto y de dónde sale.

Los números salen de los Excel ya recalculados (salida/), así que el Word queda igual a lo que muestran. Las
referencias § de los Excel apuntan a las secciones de este documento. Uso: python3 generar_word_recargas.py
(necesita node con el paquete docx; NODE_PATH si no está instalado global).
"""

import json
import os
import subprocess
import sys

from openpyxl import load_workbook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_dim_recargas as g  # noqa: E402
import generar_logistica_recargas as lg  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
PLANTAS = ["Comercial", "Industrial"]
# versión anterior (commit dd24448), para explicar qué cambió
RUB_CORTO = ["Automotor", "Edificios", "Educación", "Hoteles", "Industrias", "Salud", "Súper"]
ANTES = {"Comercial": {"maq": 52, "t2": 14, "pico": "febrero, 10,9 %", "cam": 9, "ocup": 0.956},
         "Industrial": {"maq": 40, "t2": 9, "pico": "febrero, 11,2 %", "cam": 5, "ocup": 0.937}}


def n(x, d=1):
    if x is None:
        return "—"
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if d and s.endswith("," + "0" * d) and abs(x) >= 100:
        s = s[: -(d + 1)]
    return s


def pc(x, d=1):
    return "—" if x is None else n(100 * x, d) + " %"


HAL = [q[0] for q in g.PUESTOS].index("Recuperación y carga de halogenado")


def leer():
    d = {}
    for p in PLANTAS:
        wb = load_workbook(os.path.join(g.SALIDA, f"Aprovechamiento_Recargas_Planta_{p}.xlsx"), data_only=True)
        pr, ss, R, D, px = wb["parametros_recargas"], wb[g.SS], wb["Resumen Capacidad"], wb["Demanda por puesto"], \
            wb["PROY_Indexado"]
        x = {"B": {r: pr.cell(r, 2).value for r in range(2, 11)},
             "crit": {r: [pr.cell(r, 5 + j).value for j in range(8)] for r in range(13, 29)},
             "auto": [pr.cell(r, 2).value for r in range(g.F_ENE, g.F_TRANS + 1)],
             "a": pr.cell(g.F_A, 2).value,
             "rub": [[pr.cell(g.FILA_RUB + c, 5 + m).value for m in range(12)] for c in range(7)],
             "planta": [pr.cell(g.FILA_TIPO + 17, 5 + m).value for m in range(12)],
             "eq": [[pr.cell(g.FILA_EQ + k, c).value for c in range(1, 5)] for k in range(len(g.EQUIV) + 1)],
             "paso1": [[ss.cell(g.S_RUB + j, 2 + c).value for c in range(7)] for j in range(9)],
             "stock": [ss.cell(g.S_STOCK + 17, 2 + i).value for i in range(10)],
             "alta": [ss.cell(g.S_ALTA + 17 + j, 11).value for j in range(4)],
             "rec": [wb["datos_base"].cell(19, 2 + i).value for i in range(10)],
             "lote": [[px.cell(g.P_LOTE + j, 2 + c).value for c in range(7)] for j in range(6)],
             "pct": px["B52"].value,
             "maq_tot": [R.cell(34 + g.N_PUESTOS, 2 + i).value for i in range(10)],
             "util_max": [R.cell(2 + g.N_PUESTOS, 2 + i).value for i in range(10)],
             "puestos": []}
        for k in range(g.N_PUESTOS):
            x["puestos"].append({
                "ruta": [pr.cell(g.FILA_PUESTO + k, 5 + j).value for j in range(8)],
                "t": pr.cell(g.FILA_PUESTO + k, 14).value, "cap": pr.cell(g.FILA_PUESTO + k, 15).value,
                "dem": D.cell(g.fila_dem(9, k), 16).value,
                "util": [R.cell(2 + k, 2 + i).value for i in range(10)],
                "mq": [R.cell(34 + k, 2 + i).value for i in range(10)],
                "tu": [R.cell(66 + k, 2 + i).value for i in range(10)]})
        x["t2"] = sum(1 for pu in x["puestos"] if pu["tu"][9] > 1)
        d[p] = x
    wb = load_workbook(os.path.join(g.SALIDA, "Recargas.xlsx"), data_only=True)
    ws = wb["Resumen"]
    d["log"] = {ws.cell(r, 1).value: [ws.cell(r, 2).value, ws.cell(r, 3).value] for r in range(5, 17)}
    cal = wb["Cálculo"]
    d["rubros_log"] = [[cal.cell(lg.C_R1 + c, col).value for col in range(2, 11)] for c in range(7)]
    d["sup"] = {k: wb["Supuestos"].cell(r, 2).value for k, r in lg.S.items()}
    return d


# ------------------------------------------------------------------ textos por puesto (§ 5)
# Qué decide la demanda de cada puesto y qué hay que mirar; el paso a paso y el cuándo salen del generador
POR_QUE = {
    "Recepción y registro": "Pasa todo lo que entra a la planta, más los cilindros nuevos de sustituto ABC en la "
    "planta comercial. Lo que se hace en el cliente (retiro y firma del remito) no se cuenta acá: está en el tiempo de "
    "parada de la logística (§ 10.2).",
    "Inspección visual": "La tabla de operaciones del Word dice 70 s, pero el paso a paso del mismo Word suma 90 s. Se "
    "toma el paso a paso porque cada paso se puede cronometrar en la visita y el número de la tabla no trae desglose. "
    "Con 70 s el puesto tendría 22 % más de capacidad y escondería esa diferencia en el aprovechamiento.",
    "Descarga ABC — ruta recuperable": "Toma el ABC con presión que no cambia el polvo: (1 − 5 % usados) × (1 − 10 % "
    "de cambio por dígito del año) = 85,5 % del ABC. El polvo va a la tolva de 240 kg de la Yukon y cada tolva llena "
    "dispara un ensayo de laboratorio (§ 4.9). Los usados llegan sin presión y pasan directo a desarme.",
    "Descarga a descarte (ABC, BC y Clase D)": "ABC con presión al que le toca el cambio por el dígito del año (9,5 % del ABC), BC con presión (el polvo BC se cambia siempre, Word) y Clase D con presión (95 %). El Word de recargas dice que la descarga y la PH de Clase D usan las máquinas comunes; como el polvo descargado no se reutiliza, no hay riesgo de mezclarlo con el ABC recuperable. El BC va a su propio tambor, al lado: la mezcla de ABC con BC puede reaccionar y levantar presión (IRAM 3517-2, 3.5.3.4). Antes el BC tenía un puesto aparte con 0,3 % de aprovechamiento; el tambor es un accesorio del mismo puesto y del mismo operario.",
    "Descarga y carga de agua / AFFF / sales K": "El agente se cambia todos los años (Anexo E): se descarga el 95 % que llega con presión y se cargan todos. La tabla de operaciones decía 180 s de descarga y el paso a paso 105 s; vale el paso a paso. La tabla 3 de IRAM 3517-2 da de 40 a 65 s de descarga en manuales, coherente con los 60 s de vaciado. La carga lleva 100 s y la premezcla de AFFF y sales K se hace en el tanque con bomba de 40 l/min. Antes eran dos puestos (descarga y carga); como el mismo operario de la zona de líquidos hace las dos, ahora es uno.",
    "Recuperación y carga de CO₂": "La trasvasadora 103/D1 recupera y carga: antes eran dos puestos con una máquina cada uno y la máquina se contaba dos veces. La carga toma el CO₂ abierto (PH 25 % o válvula 5 %) o usado (5 %): 35 %. La recuperación, solo el abierto (30 %), con 205 s contra los 240 s de la carga: en la ruta entra como 30 % × 205/240. El resto se pesa y no se abre (Control de peso).",
    "Recuperación y carga de halogenado": "La unidad THB/BP recupera y carga; antes eran dos puestos. Pasa el halogenado que va a PH (25 %), que llega usado (5 %) o que hay que abrir (5 %): 35 %, con 465 s de recuperación y 430 s de carga y presurización. Es el puesto con menos demanda de la planta: queda porque el Word de recargas le da al halogenado su propia unidad de recuperación y carga, que no sirve para el CO₂.",
    "Desarme y limpieza — recinto": "Todos los polvos pasan. La limpieza profunda (120 s) se hace solo en los que "
    "van a PH, por eso el tiempo tipo lleva 120 × 25 %. La tabla de operaciones decía 90 s; el paso a paso da 105 s con "
    "el mismo 25 % de PH.",
    "Desarme e inspección interior — zona general": "CO₂ y halogenados solo cuando se abren; agua, AFFF y sales K "
    "siempre. El enjuague (90 s) lleva el 40 % del original: es un criterio del grupo que queda para la visita (§ 12).",
    "Laboratorio — Puffer y mufla": "Antes se cargaban ensayos por día sin base. Ahora: la norma pide verificar el "
    "polvo en cada mantenimiento (9.9.3.1) y, para el ABC, el ensayo de fusión (9.9.3.3). Como el polvo recuperado de "
    "muchos equipos se junta en la tolva, la muestra representativa es la tolva: un ensayo cada 240 kg de polvo ABC "
    "recuperado. Por eso la demanda sube con las recargas y deja de ser un número fijo.",
    "Prueba hidráulica": "Vence la PH (20 % en polvos y CO₂, 50 % en agua, AFFF y sales K) más el daño menor (5 %, "
    "§ 4.3). Es el puesto más sensible a ese 5 %: con 10 % la planta industrial necesita el 2° turno en PH; con 0 % "
    "la comercial ahorra una máquina. El CO₂ lleva además ultrasonido y acuñado, que no están en el tiempo (§ 12).",
    "Secado": "Secadora Yukon de 6 recipientes: 15 min por ciclo ÷ 6 = 150 s por recipiente, más colocar y retirar. "
    "Pasan los que salen de PH (el mismo día) y, en polvos, los que tienen humedad al desarmar (1 %, § 4.8). Agua, "
    "AFFF y sales K no se secan: se vuelven a llenar.",
    "Inspección interior con videoscopio": "Misma ruta que el secado. En la comercial queda en 88 % con 1 máquina y 1 "
    "turno: si el daño sube a 10 % o la humedad a 5 %, pasa a 2 turnos.",
    "Pintura": "El original tenía 750 s sin pasos. El paso a paso del Word ordena sacar óxido, desengrasar, "
    "enmascarar, fondo, esmalte y secar con lámparas infrarrojas «el tiempo que indique la ficha». La ficha del esmalte "
    "poliuretano de Sherwin (FT 27.00) da 30 min a 60 °C; con las lámparas cubriendo 6 recipientes por tanda quedan "
    "300 s por recipiente. Total 615 s. El 15 % que se pinta no tiene estadística publicada (§ 4.7): con 25 % la "
    "comercial necesita 5 cabinas en vez de 3; con 5 %, 1.",
    "Carga de polvo ABC, BC y Clase D": "ABC: tabla de operaciones 90 s; paso a paso 106 s con 6 s de contraste de balanza por turno. La tabla 9 del Word fija el contraste una vez por mes, así que no va en el tiempo de cada equipo: quedan 100 s. BC y Clase D se cargan en el mismo puesto, con el mismo operario, pero cada uno con su equipo exclusivo para no mezclar polvos (IRAM 3517-2, 3.5.3.4): la cargadora portátil BC (75 s para 5 kg, 140 s con tara, pesada, rosca y registro) y el embudo y la balanza de Clase D (9 kg × 15 s/kg, el ritmo de la cargadora BC: 205 s). Como tardan más que el ABC, entran en la ruta con su tiempo relativo: 140/100 y 205/100. Antes eran dos puestos propios con menos de 1 % de aprovechamiento cada uno.",
    "Ensamblaje y marbete — recinto": "Todos los polvos y los cilindros nuevos de sustituto (planta comercial). Es "
    "manual: se dimensiona con operarios y mesas, no con máquinas.",
    "Presurización — recinto": "Mismos equipos que el ensamblaje. El contraste del manómetro patrón por turno (3 s por "
    "equipo) queda en el tiempo porque el Word lo pide al empezar cada turno.",
    "Ensamblaje y presurización — zona general": "CO₂ y halogenados que se abrieron; agua, AFFF y sales K siempre. El "
    "CO₂ no se presuriza y el halogenado se presuriza en su propia carga.",
    "Control de peso (CO₂ y halogenados sin recarga)": "Los que no se abren (65 %) se pesan y se comparan con la masa "
    "de la placa (Anexo E: control anual de la masa).",
    "Ensayo de pérdidas": "Siempre (operación 12). Tanque de inmersión en tandas de 6; los rodantes, con spray.",
    "Precinto, etiqueta y despacho": "Tabla de operaciones 80 s; paso a paso 86 s. Vale el paso a paso.",
    "Inutilización y disposición final": "Fin de vida útil (5 %; CO₂ 3,3 %), no pasa la PH (2 %) y rotos (1 %). "
    "Acta y foto por equipo (9.12 y Anexo G).",
    "PH de mangueras (CO₂ y rodantes)": "9.7.1.4 pide PH de las mangueras con cierre en el extremo (rodantes) y de "
    "las de CO₂ con manga. La versión anterior copiaba el tiempo de la PH del recipiente; ahora sigue los pasos a) a "
    "h) de 9.7.5.3: retirar sin quitar acoples, marcar acoples, sacar el polvo, poner en la jaula de protección, "
    "llenar y purgar, subir a presión y sostener 1 min, liberar y revisar desplazamientos, escurrir y secar a no más "
    "de 65 °C, y el rótulo de 20 × 30 mm. La demanda es la fila Mangueras del Plan mensual.",
}


def bloques(d):
    C, I = d["Comercial"], d["Industrial"]
    L = d["log"]
    out = []

    def h1(x): out.append({"t": "h1", "x": x})
    def h2(x): out.append({"t": "h2", "x": x})
    def h3(x): out.append({"t": "h3", "x": x})
    def p(x): out.append({"t": "p", "x": x})
    def b(x): out.append({"t": "b", "x": x})
    def nota(x): out.append({"t": "nota", "x": x})

    def tabla(cols, cab, filas, num=(), negrita=()):
        out.append({"t": "tabla", "cols": cols, "cab": cab, "filas": filas, "num": list(num), "negrita": list(negrita)})

    out.append({"t": "titulo", "x": "Recargas — justificación del dimensionamiento"})
    out.append({"t": "sub", "x": "Plantas comercial e industrial · cómo se decidió cada valor, de dónde sale y qué "
                                 "implica en cada puesto"})
    out.append({"t": "sub", "x": "FLAMA · octubre de 2026"})
    p("Los Excel llevan solo números, fórmulas y una referencia corta (§) a la sección de este documento donde está el "
      "porqué. Los archivos son: Aprovechamiento_Recargas_Planta_Comercial.xlsx, Aprovechamiento_Recargas_Planta_"
      "Industrial.xlsx, Recargas.xlsx (logística) y Aprovechamiento_Manuales.xlsx / Aprovechamiento_Carros.xlsx "
      "(alta de sustitutos ABC).")

    # 1
    h1("1. Alcance y cadena de cálculo")
    p("Cada planta toma las recargas por tipo de Proyecciones y su porcentaje de zonas. La cadena es la misma en las "
      "dos: recargas del año por tipo → reparto mensual con la estacionalidad de los rubros que atiende (§ 3) → "
      "fracción de cada agente que pasa por cada puesto según los criterios de la norma (§ 4) → demanda del mes pico "
      "en unidades por hora de un turno → aprovechamiento = demanda ÷ (capacidad × máquinas × turnos). Ningún puesto "
      "puede pasar el 90 % (§ 8).")
    p("Los valores se clasifican en cuatro estados, que el Excel muestra en la columna Estado de los criterios:")
    b("**Norma:** lo fija IRAM 3517-2:2020 u otra norma citada por cláusula.")
    b("**Dato:** viene de Proyecciones, del Word de recargas o de una fuente publicada.")
    b("**Criterio:** no hay estadística publicada; el valor se adoptó con el razonamiento que se explica y queda para "
      "confirmar en la visita al recargador (§ 12). En el Excel tiene fondo gris.")
    b("**Cálculo:** sale de otras filas.")
    p("Control: el modelo está replicado en Python (generar_dim_recargas.py, función modelo_demanda) y la diferencia "
      "máxima con el Excel recalculado es menor que 1 × 10⁻¹² u/h en las dos plantas. Los cinco Excel se recalculan sin "
      "errores de fórmula.")

    # 2
    h1("2. Demanda")
    p(f"Las recargas por tipo de 2026 a 2035 vienen de Proyecciones (Indexado Dim Técnico B27:K43, por IMPORTRANGE). "
      f"Cada planta toma la suma de sus zonas: comercial {pc(C['pct'])} (CABA Norte, Este y Oeste, y PBA Norte y Oeste) "
      f"e industrial {pc(I['pct'])} (CABA Sur y PBA Sur). PBA Interior (15,7 %) queda afuera porque la atienden "
      f"distribuidores ajenos. En 2035 son {n(C['rec'][9], 0)} recargas en la comercial y {n(I['rec'][9], 0)} en la "
      f"industrial.")
    p("El mix por rubro (qué tipos recarga cada rubro) sale de las hojas PROYECCION <rubro> de Proyecciones, sumando "
      "solo las zonas de cada planta. Ese mix define el perfil mensual de cada tipo y el ciclo de los sustitutos.")
    p("Los carros se reparten 25/55/12/8 % entre 25, 50, 70 y 100 kg, como en PxQ (Corregido), filas 66 a 69. Es el "
      "mismo reparto con que el grupo proyectó ventas y precios; no hay estadística pública de rodantes por capacidad. "
      "Se mantiene para que recargas, Manuales y Carros usen el mismo mercado: si cambia, cambia en los tres.")
    p("Tasas de Proyecciones que se usan (iguales en todos los tipos): equipos que llegan descargados por uso 5 %, que "
      "no pasan la PH 2 % y rotos 1 %. La tasa de fin de vida útil de Proyecciones (3,3 %) no se usa porque aplica la "
      "misma vida a todos los tipos; acá va la del Anexo E (§ 4.2).")

    # 3
    h1("3. Estacionalidad")
    p("IRAM 3517-2:2020 pide mantenimiento al menos una vez al año (9.2.1) y que la tarjeta indique mes y año del "
      "próximo (9.4.14). El mes de la próxima recarga lo fija la última, así que un rubro puede elegir en qué mes "
      "recargar: adelanta una vez el turno y desde ahí vuelve cada año en ese mes. Mientras el equipo está en la planta "
      "el cliente queda con un sustituto (9.4.5), y descolgar, retirar y reponer equipos es un trabajo que cada rubro "
      "evita en su temporada alta y concentra en sus meses tranquilos. Por eso cada rubro lleva los meses que marcan "
      "sus pliegos, cámaras y manuales; el que no tiene una ventana así queda parejo (1/12 por mes).")
    tabla([22] + [7] * 12, ["Comercial"] + g.MESES,
          [[RUB_CORTO[c]] + [pc(v) for v in C["rub"][c]] for c in range(7)]
          + [["Toda la planta"] + [pc(v) for v in C["planta"]], ["Industrial: planta"] + [pc(v) for v in I["planta"]]],
          num=range(1, 13), negrita=(7, 8))
    h2("3.1 Automotor")
    p("La versión anterior repartía las recargas por el cronograma de VTV de PBA (terminación de patente de febrero a "
      "noviembre) y ponía en enero y diciembre solo a los autos exentos de VTV, con los patentamientos de ACARA. Daba "
      "0,7 % en enero y 0,3 % en diciembre. El error estaba en suponer que el matafuego se recarga en el mes de la VTV: "
      "la VTV controla que la carga esté vigente (iProfesional), y una carga hecha en diciembre sigue vigente en la VTV "
      "de cualquier mes de los 12 siguientes. El mes de la VTV no fija el mes de la recarga.")
    p("Lo que sí concentra la recarga es la salida a la ruta: el matafuego es obligatorio para circular (Ley 24.449, "
      "art. 40) y para salir a la ruta en vacaciones se pide la VTV al día (iProfesional). El único dato mensual "
      "publicado es el de la ITV de "
      "Córdoba: el 12 % de las inspecciones del año se hace en enero, con recargadores que informan el mismo pico "
      "(Hoy Día Córdoba). En Mendoza, diciembre y enero siguen siendo los meses de más demanda de la RTO, que exige el "
      "matafuego cargado, por los viajes del verano (Sitio Andino, jul. 2026); recargadores de Paraná y Rafaela "
      "informan la suba antes de las vacaciones (Elonce; Rafaela Noticias).")
    A = C["auto"]
    p("Se adopta **enero 12 %** (ITV Córdoba) y **diciembre igual a enero**, porque las fuentes ubican la temporada en "
      "esos dos meses: diciembre carga los viajes de enero y enero los de febrero. Para que el perfil no salte de un mes "
      "al otro, **noviembre y febrero llevan la mitad del exceso** de la temporada (criterio de transición: la demanda "
      "sube y baja de a poco, no de un día para el otro). Marzo a octubre quedan parejos.")
    p(f"Cuenta (parametros_recargas, filas {g.F_ENE} a {g.F_TRANS}): con enero = diciembre = J, noviembre = febrero = base + "
      f"½ × exceso y el resto = base, los 12 meses suman 100 % si exceso = (12 × J − 1) ÷ (10 − 2 × ½) = {pc(A[3])}. "
      f"Mes común = {pc(A[0])} − {pc(A[3])} = {pc(A[4])}; noviembre y febrero = {pc(A[5])}; diciembre y enero = "
      f"{pc(A[0])}. La subida es en dos escalones de unos 2,5 puntos, en vez de un salto de 4,4.")
    p("La regla de exención de VTV se investigó para separar zonas: en PBA la VTV es obligatoria desde los 2 años de "
      "patentado (Ámbito, oct. 2025) y en CABA desde los 4 años o 64.000 km, lo que ocurra primero (La Nación, feb. "
      "2026). Con el perfil adoptado la exención no cambia el resultado, porque el perfil ya no depende del mes de VTV; "
      "por eso las dos plantas usan el mismo perfil de automotor.")
    p(f"Efecto: el ABC 1 kg (97 % del automotor) sigue este perfil. El mes pico de las dos plantas pasa de febrero a "
      f"enero: comercial {pc(max(C['planta']))} (antes {ANTES['Comercial']['pico']}) e industrial "
      f"{pc(max(I['planta']))} (antes {ANTES['Industrial']['pico']}).")
    a_inst = C["a"]
    h2("3.2 Edificios (consorcios)")
    p("Las asambleas ordinarias anuales de los consorcios, donde el administrador rinde cuentas y se aprueban las "
      "expensas extraordinarias y los fondos para las actualizaciones de seguridad y el abono de matafuegos, se "
      "concentran entre abril y junio (CAPHAI, Circular N.° 14, 2025; Arya Seguridad, matafuegos en consorcios). Enero y "
      "febrero son temporada baja administrativa: receso de las administraciones y licencias anuales de los encargados "
      "de edificio (convenio colectivo de SUTERH), que dejan sin acceso a cocheras, bauleras y salas cerradas.")
    b("**Abril, mayo y junio: preferidos (+). Enero y febrero: vedados (−).**")
    h2("3.3 Educación")
    p("Las escuelas hacen el mantenimiento en los recesos, cuando no hay alumnos. El Ministerio de Educación de Río "
      "Negro emitió órdenes de servicio para la recarga de matafuegos de las escuelas de General Roca durante el receso "
      "de verano, intensifica el mantenimiento en el receso de invierno y hace recambio y recarga de matafuegos en el "
      "plan preventivo de Cipolletti. En General Pueyrredón, el Consejo Escolar aprovecha las vacaciones de invierno para "
      "el mantenimiento de las escuelas (La Capital). En PBA, la DGCyE transfiere a los Consejos Escolares los fondos de "
      "inicio del ciclo antes de las clases (Ámbito, 2022), que se usan para poner las escuelas en condiciones.")
    b("**Enero, febrero y marzo: preferidos (+), igual los tres** (receso de verano y puesta en condiciones del inicio "
      "de clases). **Julio: medio preferido (+½)**, porque el receso de invierno dura dos semanas. La versión anterior "
      "ponía todas las estatales en febrero (67,5 % del rubro en un mes); ninguna fuente respalda esa concentración.")
    h2("3.4 Hoteles")
    p("Los planes de mantenimiento preventivo de hotelería programan todo trabajo con proveedores externos en "
      "habitaciones, pasillos y áreas comunes en los meses de baja ocupación, para no afectar a los huéspedes. En "
      "temporada alta (enero, febrero y julio) el hotel está lleno de personas que no conocen las salidas y los comités "
      "de higiene y seguridad restringen el movimiento de equipos: descolgar, subir por los ascensores de huéspedes y "
      "acopiar sustitutos genera cuellos de botella en las vías de evacuación (MaxiSeguridad, seguridad contra incendios "
      "en hoteles).")
    b("**Mayo, junio, agosto, septiembre y octubre: preferidos (+). Enero, febrero y julio: vedados (−).**")
    h2("3.5 Industrias y almacenes")
    p("Sin estacionalidad. Las normas que los alcanzan (Res. SRT 463/09 y 529/09, relevamiento general de riesgos "
      "laborales) no fijan un mes, y el mantenimiento del matafuego no necesita parar la planta, así que las paradas de "
      "enero que muestra el INDEC no ubican la recarga en enero: el vencimiento sigue la tarjeta.")
    h2("3.6 Salud")
    p("Los pliegos de especificaciones técnicas del Ministerio de Salud de CABA para el mantenimiento hospitalario "
      "refuerzan las tareas de servicios generales en los meses de verano, cuando baja la ocupación de camas por "
      "enfermedades respiratorias, y prohíben en guardias e internación las tareas invasivas (obstruir el tránsito, "
      "ruidos, retiros masivos de equipamiento de seguridad) durante la Campaña de Invierno (Boletín Oficial CABA, "
      "anexos de la DGACSA y de la SSASS, 2026).")
    b("**Diciembre, enero y febrero: preferidos (+). Junio, julio y agosto: vedados (−).**")
    h2("3.7 Supermercados")
    p("El recambio de los matafuegos de salón con sus sustitutos es un trabajo invasivo en pasillos, y las prestadoras lo "
      "coordinan en los meses de menor facturación y tránsito, de mayo a agosto (MaxiSeguridad, carga de matafuegos en "
      "comercios). Hacia fin de año los depósitos y las góndolas trabajan con su máximo stock y su máxima carga de fuego, "
      "y el servicio de higiene y seguridad no deja descolgar la dotación fija del salón (LEA Global, incendios en "
      "supermercados y depósitos). Los controles trimestrales de las áreas críticas (panadería, rotisería, salas de "
      "frío; Extintec, CAGESRA) se hacen en el local y no pasan por la planta.")
    b("**Mayo a agosto: preferidos (+). Noviembre a febrero: vedados (−).**")
    h2("3.8 Cuánto pesa un mes preferido")
    p(f"Las fuentes dicen en qué meses se concentra o se evita la recarga, pero no cuánto. Se toma un mes preferido "
      f"con 1 + a y uno vedado con 1 − a de un mes común, con a = {pc(a_inst)} (criterio; parametros_recargas, B{g.F_A}); cada "
      "rubro se divide por su suma para que el año dé 100 %. Así, en cada rubro el mes más cargado queda como mucho en el "
      "doble del menos cargado y ningún mes pasa de 11 % del año. "
      f"Ejemplo, edificios: abril a junio {pc(C['rub'][1][3])}, enero y febrero {pc(C['rub'][1][0])} y el resto "
      f"{pc(C['rub'][1][2])}.")
    p(f"Con todo junto, la planta comercial va de {pc(min(C['planta']))} a {pc(max(C['planta']))} por mes y la "
      f"industrial de {pc(min(I['planta']))} a {pc(max(I['planta']))}: el automotor sigue marcando el pico del verano y "
      "los rubros institucionales llenan el otoño y el invierno.")

    # 4
    h1("4. Criterios de recarga por agente")
    p("Cada fila de la tabla de criterios dice qué le pasa al equipo en el año, por agente. Los puestos toman esas "
      "filas en la columna de su agente, así que cambiar un valor cambia la ruta de todos los puestos que lo usan.")
    cr = C["crit"]
    nom = ["ABC", "BC", "Clase D", "Agua", "AFFF", "Sales K", "CO₂", "Halog."]

    def fila(r, t, est, fu, fmt=pc):
        return [t] + [fmt(v) if isinstance(v, (int, float)) else "—" for v in cr[r]] + [est, fu]
    filas = [fila(13, "Intervalo de PH (años)", "Norma", "Anexo E", lambda v: n(v, 0)),
             fila(15, "Daño menor → PH", "Criterio", "9.7.1.2"),
             fila(16, "Pasa por PH", "Cálculo", "—"),
             fila(17, "Vida útil (años)", "Norma", "Anexo E", lambda v: n(v, 0)),
             fila(21, "Se inutiliza", "Cálculo", "9.12"),
             fila(22, "Llega descargado", "Dato", "Proyecciones"),
             fila(23, "Cambio obligatorio del agente", "Norma", "9.9.4 a), Anexo E"),
             fila(24, "Abrir la válvula", "Criterio", "Anexo F"),
             fila(25, "Se pinta", "Criterio", "9.10"),
             fila(26, "Humedad al desarmar", "Criterio", "9.8"),
             fila(28, "Ensayos de laboratorio por u.", "Cálculo", "9.9.3", lambda v: n(v, 4))]
    tabla([30] + [10] * 8 + [11, 16], ["Criterio"] + nom + ["Estado", "Cláusula"], filas, num=range(1, 9))
    h2("4.1 Prueba hidráulica")
    p("El Anexo E fija el intervalo: 5 años para polvos, CO₂ y halogenados; 2 años para agua, AFFF y sales K. En "
      "régimen vence la PH de 1 de cada 5 (o de cada 2) equipos por año (9.7.2): 20 % o 50 %.")
    h2("4.2 Vida útil e inutilización")
    p("Anexo E: 20 años (CO₂ 30, IRAM 3509). Se inutiliza en la recepción el 5 % (CO₂ 3,3 %) por fin de vida, más el "
      "2 % que no pasa la PH y el 1 % de rotos, ambos de Proyecciones. El 2 % equivale a 1 de cada 12,5 equipos que "
      "se prueban.")
    h2("4.3 Daño menor que manda a PH")
    p("9.7.1.2 manda a PH el recipiente con daños menores por corrosión o acción mecánica; 9.7.1.3 b) y el Anexo F "
      "mandan a inutilizar la corrosión que compromete el recipiente y la abolladura. La norma dice qué hacer, no con "
      "qué frecuencia pasa. Se buscó la frecuencia en literatura de servicio (NFPA 10, manuales de fabricantes, "
      "servicios de PH) y no hay estadística publicada. Se toma 5 % del Dimensionamiento Técnico V2 del grupo, que "
      "usaba 25 % de PH en polvos = 20 % por vencimiento + 5 % por daño.")
    p("Efecto medido con el modelo: con 10 % la PH industrial pasa a 2 turnos y el videoscopio comercial también; con "
      "0 % la comercial ahorra una máquina de PH y el secado de las dos plantas baja a 1 turno.")
    h2("4.4 Datos de Proyecciones")
    p("Usados 5 %, no pasa la PH 2 % y rotos 1 %: cocientes sobre RECARGAS An de las hojas PROYECCION, iguales en todos "
      "los tipos y rubros.")
    h2("4.5 Cambio obligatorio del agente")
    p("ABC: se cambia por el dígito del año de fabricación (9.9.4 a), 1 de cada 10 equipos por año. BC: siempre polvo "
      "nuevo (Word de recargas). Clase D: siempre, se descarga y se carga a mano. Agua, AFFF y sales K: el agente se "
      "cambia cada año (Anexo E). CO₂ y halogenados se reutilizan.")
    h2("4.6 Abrir la válvula de CO₂ y halogenados")
    p("El Anexo F manda a recargar el equipo con masa inadecuada; como referencia, la norma de EE. UU. para equipos "
      "marinos (46 CFR 132.350) manda recargar el CO₂ que perdió más del 10 % de la carga. No hay frecuencia publicada: "
      "se toma 5 %. Efecto: con 15 % no cambia ninguna máquina en ninguna planta, porque los puestos de CO₂ y "
      "halogenados tienen demanda baja.")
    h2("4.7 Pintura")
    p("9.10 y el Anexo F mandan a pintar con óxido, metal a la vista, pérdida de brillo o color, o repintado parcial "
      "con diferencia de color. Sin frecuencia publicada: 15 % del Dimensionamiento Técnico V2. Es el criterio que más "
      "mueve máquinas: con 25 % la comercial necesita 5 cabinas (hoy 3) y la industrial 3 (hoy 2); con 5 %, 1 en cada "
      "planta. Es la primera pregunta para la visita.")
    h2("4.8 Humedad al desarmar")
    p("9.8 y el Word (operación 7): si al desarmar aparece humedad, el recipiente se seca aunque no vaya a PH. 1 % en "
      "polvos, criterio. Con 5 % el videoscopio comercial pasa a 2 turnos; el resto no cambia.")
    h2("4.9 Laboratorio")
    p(f"9.9.3.1 pide verificar el polvo en cada mantenimiento y 9.9.3.3 agrega, para el ABC, el ensayo de fusión "
      f"(IRAM 3569) y los de IRAM 3672 si hay dudas. El polvo recuperado de muchos equipos se mezcla en la tolva de "
      f"240 kg de la Yukon, así que se ensaya cada tolva antes de usarla. Ensayos por equipo = fracción recuperable "
      f"(85,5 %) × kg de polvo ABC por u. equivalente (pesado con las recargas 2035) ÷ 240 kg = {n(cr[28][0], 4)}: "
      f"un ensayo cada {n(1 / cr[28][0], 0)} equipos ABC. BC y Clase D no se recuperan: se cargan con polvo nuevo con "
      f"Sello IRAM.")

    # 5
    h1("5. Tiempos y efecto en cada puesto")
    p("Los tiempos salen del Word de recargas (tabla de operaciones y paso a paso de cada operación) y del Excel "
      "original del grupo. Cuando la tabla de operaciones y el paso a paso no coinciden, vale el paso a paso: cada paso "
      "se puede cronometrar en la visita y el número de la tabla no trae desglose. En el Excel el tiempo queda como "
      "fórmula con los pasos sumados (por ejemplo =15+45+15+15+10), así se ve de dónde sale.")
    tabla([34, 14, 14, 38], ["Puesto", "Antes (s)", "Ahora (s)", "Por qué"], [
        ["Inspección visual", "70", "90", "Paso a paso del Word"],
        ["Descarga de agua / AFFF / sales K", "180", "105", "Paso a paso del Word"],
        ["Desarme y limpieza — recinto", "90", "105", "Paso a paso con 25 % de PH"],
        ["Carga de polvo ABC", "90 / 106", "100", "Contraste de balanza mensual (tabla 9)"],
        ["Precinto, etiqueta y despacho", "80", "86", "Paso a paso del Word"],
        ["Pintura", "750", "615", "Pasos del Word + ficha del esmalte"],
        ["Clase D", "490", "205", "Descarga al tambor común; carga a 15 s/kg"],
        ["PH de mangueras", "302", "300", "Pasos de 9.7.5.3"]], num=(1, 2))
    p("En cada puesto: cuándo pasa el equipo, el paso a paso del tiempo, qué fracción de cada agente entra y cómo "
      "queda en 2035 (máquinas u operarios × turnos y aprovechamiento del año). La demanda se mide en el mes pico, en "
      "unidades por hora de un turno; los rodantes cuentan como 6,36 u. equivalentes (§ 6).")
    for k, (pu, maq, rec, ruta, t, des, no) in enumerate(g.PUESTOS):
        h3(f"5.{k + 1} {pu}")
        pc_, pi_ = C["puestos"][k], I["puestos"][k]
        fr = ", ".join(f"{nom[j]} {pc(v)}" for j, v in enumerate(pc_["ruta"]) if isinstance(v, (int, float)) and v > 0)
        if ruta is None:
            fr = "mangueras con PH anual (rodantes y CO₂ con manga)"
        elif pu in g.CILINDRO_NUEVO:
            fr += " y los cilindros nuevos de sustituto ABC (comercial)"
        p(f"**Equipo:** {maq} ({rec.lower()}). **Cuándo pasa:** {g.CUANDO[pu]}. **Entra:** {fr}.")
        p(f"**Paso a paso (s):** {des} = **{n(pc_['t'], 0)} s** → {n(pc_['cap'], 1)} u/h por máquina u operario.")
        p(POR_QUE[pu])
        p(f"**2035:** comercial {pc_['mq'][9]} × {pc_['tu'][9]} turno{'s' if pc_['tu'][9] > 1 else ''}, "
          f"{pc(pc_['util'][9], 0)} (demanda {n(pc_['dem'], 2)} u/h); industrial {pi_['mq'][9]} × {pi_['tu'][9]} "
          f"turno{'s' if pi_['tu'][9] > 1 else ''}, {pc(pi_['util'][9], 0)} (demanda {n(pi_['dem'], 2)} u/h).")

    # 6
    h1("6. Equivalencia de un rodante")
    p("Un carro no ocupa un puesto lo mismo que un manual. Se mide con los tiempos de fábrica de FLAMA en las "
      "operaciones que comparten la fábrica y la recarga: tiempo del carro (Aprovechamiento Carros, ponderado con el "
      "mix 2035) ÷ tiempo del manual (Aprovechamiento Manuales). Los dos se importan por IMPORTRANGE.")
    tabla([40, 18, 18, 18], ["Operación", "Manual (s)", "Carro (min)", "Carro ÷ manual"],
          [[r[0], n(r[1], 0), n(r[2], 2), n(r[3], 2)] for r in C["eq"][:-1]]
          + [["Promedio (va a parametros_recargas B9)", "", "", n(C["eq"][-1][3], 2)]], num=(1, 2, 3), negrita=(4,))
    p(f"El Dimensionamiento Técnico V2 usaba 3 sin fuente. Con {n(C['B'][9], 2)}, un ABC de 25 a 100 kg o un AFFF de "
      f"50 l cargan los puestos como {n(C['B'][9], 2)} manuales en todas las operaciones.")

    # 7
    h1("7. Sustitutos")
    p("IRAM 3517-2 9.4.5: mientras el equipo está en planta, el cliente queda con uno del mismo tipo. El sustituto sale "
      "con el camión que retira el lote y vuelve con el que lo devuelve. El ABC 1 kg de automotor no lleva sustituto "
      "(sin canje).")
    h2("7.1 Lote por cliente")
    p("Antes era un dato del grupo sin fuente (25, 14, 18, 20, 45, 35 y 16). Ahora sale de Proyecciones: parque de "
      "matafuegos de cada rubro (hojas PROYECCION, zonas CABA y PBA sin Interior) ÷ establecimientos del rubro (% "
      "PENETRACION, AÑO 8). Se usa 2033 porque es el primer año con todas las zonas de las dos plantas (CABA y PBA sin "
      "Interior). 2035 no sirve: edificios cae de 139.625 a 90.843 establecimientos con el parque en aumento, una "
      "inconsistencia de la fuente.")
    lt = C["lote"]
    tabla([28] + [10] * 7, ["Concepto"] + RUB_CORTO,
          [["Parque 2033"] + [n(v, 0) for v in lt[0]],
           ["Establecimientos 2033"] + [n(v, 0) for v in lt[1]],
           ["Matafuegos por establecimiento"] + [n(v, 1) for v in lt[2]],
           ["Superficie media (m²)"] + [n(v, 0) if v else "—" for v in lt[3]],
           ["Piso Dec. 351/79"] + [n(v, 0) if v else "—" for v in lt[4]],
           ["Lote adoptado"] + [n(v, 0) for v in lt[5]],
           ["Antes (grupo)"] + ["25", "14", "18", "20", "45", "35", "16"]], num=range(1, 8), negrita=(5,))
    p("La dotación mínima por superficie es la del Dec. 351/79 (art. 176 y anexo VII): un matafuego cada 200 m² y "
      "recorrido máximo de 20 m hasta uno (fuego clase A) o 15 m (clase B). La Ley 6116 de CABA regula el servicio y "
      "la vigencia anual de la carga, pero no fija cantidad por superficie. Solo hay superficie media publicada para "
      "supermercados: la Encuesta de Supermercados del INDEC da 3.382.730 m² de ventas en 3.147 bocas, 1.075 m² por "
      "boca → mínimo 6 matafuegos. Proyecciones daba 3,0, por debajo del mínimo legal, así que se toma 6.")
    p("Automotor: la dotación es un matafuego por vehículo (Ley 24.449, art. 40), así que el lote es la cantidad de "
      "vehículos por punto de retiro (flota, concesionaria o lubricentro, como lo definía el grupo). Proyecciones da 9,3 "
      "contra los 25 que usaba el grupo. Es el valor que más mueve la logística (§ 10.5) y queda para confirmar qué "
      "cuenta la columna CANTIDAD de AUTOMOTRIZ (§ 12).")
    h2("7.2 Días en planta y ciclo")
    p("El lote viaja junto en su jaula: días en planta = minutos de operación del lote ÷ minutos productivos por día, "
      "redondeado hacia arriba (mínimo 1). Ciclo = 1 día de retiro + días en planta + 1 día de devolución.")
    s1 = C["paso1"]
    tabla([30] + [10] * 7, ["Comercial"] + RUB_CORTO,
          [["Min de operación por equipo"] + [n(v, 1) for v in s1[3]],
           ["Min del lote"] + [n(v, 0) for v in s1[4]],
           ["Días en planta (1 turno)"] + [n(v, 0) for v in s1[5]],
           ["Ciclo con 1 turno (días)"] + [n(v, 0) for v in s1[7]],
           ["Ciclo con 2 turnos (días)"] + [n(v, 0) for v in s1[8]]], num=range(1, 8))
    p("Salud es el único rubro que no entra en un día: un lote de 61 equipos con 23,8 min cada uno ocupa 4 días con "
      "un turno y 2 con dos.")
    h2("7.3 Stock")
    p(f"Stock por tipo = recargas del año × % del mes pico del tipo ÷ días hábiles del mes × ciclo (con 2 turnos desde "
      f"2032), redondeado hacia arriba. El stock del año anterior se mantiene en la planta (9.4.5 y 9.2.1) y entra al "
      f"Plan mensual por la ruta de su tipo, 1/12 por mes. 2035: comercial {n(C['stock'][9], 0)} u. e industrial "
      f"{n(I['stock'][9], 0)} u.")
    h2("7.4 Alta y origen")
    p(f"Alta del año = lo que crece el stock + stock del año anterior × % que se inutiliza. Los ABC llegan a la planta "
      f"comercial como cilindro vacío desde la industrial y se cargan en la ruta del cilindro nuevo (recepción, carga "
      f"ABC, ensamblaje, presurización, ensayo de pérdidas y despacho), con el perfil de producción del MRP (E01, E02 "
      f"y E03). En la industrial salen terminados de la línea. El resto de los tipos se compra. Alta 2035: comercial "
      f"{n(C['alta'][0], 0)} cilindros vacíos y {n(C['alta'][2], 0)} de compra; industrial {n(I['alta'][1], 0)} "
      f"terminados y {n(I['alta'][2], 0)} de compra.")

    # 8
    h1("8. Capacidad, máquinas y turnos")
    p("Reglas, iguales en recargas, Manuales y Carros:")
    b("Umbral de aprovechamiento 90 %, límite duro: por encima, cualquier desvío de la demanda o una parada deja el "
      "puesto sin margen, y eso es lo primero que marca el análisis de riesgos.")
    b("Antes de 2032 se agrega máquina (u operario en los puestos manuales). 2032 es el año del 2° turno del "
      "Dimensionamiento Técnico V2 y de Manuales.")
    b("En 2032 se dimensiona hasta 2035: los puestos que lo necesitan pasan a 2 turnos ese año, todos juntos, y se "
      "agregan las máquinas que hagan falta para que ningún año hasta 2035 pase el 90 %. Después de 2032 no se agrega "
      "nada: no se compra una máquina para el último año.")
    b("Máximo 2 turnos: la Ley 11.544 fija 8 h por jornada y 7 h la nocturna (21 a 6 h); un tercer turno sería "
      "nocturno.")
    filas = []
    for p_ in PLANTAS:
        x = d[p_]
        filas.append([p_, str(x["maq_tot"][4]), str(x["maq_tot"][5]), str(x["maq_tot"][9]), str(x["t2"]),
                      pc(max(x["util_max"]), 0), str(ANTES[p_]["maq"]), str(ANTES[p_]["t2"])])
    tabla([16, 12, 12, 12, 14, 14, 12, 12], ["Planta", "Máq. 2030", "Máq. 2031", "Máq. 2035", "Puestos con 2 turnos",
                                             "Aprov. máximo", "Máq. antes", "2 turnos antes"], filas,
          num=range(1, 8))
    p("Qué cambió en los puestos respecto de la versión anterior: el laboratorio pasó de una carga fija a un ensayo por "
      "tolva y sube de 16 % a más de 60 % (la comercial le suma el 2° turno); la pintura comercial baja de 4 a 3 "
      "cabinas por los 615 s; el videoscopio comercial vuelve a 1 turno y la PH y el ensayo de pérdidas industriales "
      "quedan en 1 turno porque el mes pico pasó de febrero (11,2 %) a enero (10,2 %). En la industrial, la descarga "
      "ABC recuperable y la presurización pasan de 2 máquinas con 1 turno a 1 máquina con 2: el total baja de 40 a 38 "
      "y en la comercial de 52 a 51.")
    p(f"Puestos unidos en esta versión: los que comparten equipo u operario dejan de figurar como puestos "
      "separados, porque un puesto con 1 % de aprovechamiento no es un puesto sino un accesorio de otro. La "
      "trasvasadora de CO₂ y la unidad de halogenados recuperan y cargan (antes se contaban dos veces); la descarga y "
      "la carga de agua, AFFF y sales K las hace el mismo operario de la zona de líquidos; el BC y el Clase D se "
      "descargan y se cargan en los puestos de polvo con su tambor, su cargadora y su embudo exclusivos, sin tocar el "
      f"equipo de ABC (IRAM 3517-2, 3.5.3.4). Quedan {g.N_PUESTOS} puestos. En 2035 el total baja a "
      f"{C['maq_tot'][-1]} en la comercial (antes 51) y {I['maq_tot'][-1]} en la industrial (antes 38). El halogenado "
      f"sigue con el aprovechamiento más bajo ({pc(C['puestos'][HAL]['util'][-1])} en la comercial): su unidad no sirve para "
      "otro agente y la demanda es mínima.")

    # 9
    h1("9. Manuales y Carros")
    p("Los Aprovechamientos de Manuales y Carros del grupo importan del paso 4 (alta) de cada Aprovechamiento de "
      "recargas los sustitutos ABC: Manuales los de 1 a 10 kg y Carros los de 25 a 100 kg. La industrial los pide "
      "terminados (proceso completo); la comercial, como cilindro vacío. La estacionalidad de producción viene del MRP "
      "(hoja ESTACIONALIDAD, perfiles E01 a E03), que es el que define los picos. Se aplican las mismas reglas del § 8; "
      "los textos y tiempos originales del grupo en esos archivos no se tocaron.")

    # 10
    h1("10. Logística (Recargas.xlsx)")
    sp = d["sup"]
    h2("10.1 Camión")
    p("El Word de recargas define un camión de cabina simple con caja de baranda rebatible, de unas 2 t de carga útil, "
      "que lleva jaulas palletizables de 1,2 × 1,0 m cargadas con autoelevador por el costado. Se toma el Iveco Daily "
      "55C17 chasis cabina (Autocosmos): 3.450 mm entre ejes y 5.803 mm de largo, que admite una caja de unos 3,7 × "
      "2,1 m: 2 jaulas a lo ancho × 3 a lo largo = 6 posiciones. La carga útil del chasis (3.190 kg) deja margen para "
      "el peso de la caja por encima de las 2 t del Word.")
    p(f"Carga neta por viaje = 2.000 kg − 2 personas × 75 kg − 6 jaulas × 75 kg = {n(sp['neta'], 0)} kg. Antes: "
      f"personas de 80 kg y una tara de 10 % sin fuente. Ahora: 75 kg por ocupante, la masa normalizada de la Directiva "
      f"2007/46/CE, y 75 kg por jaula (Palletower Hypacage de 1.000 × 1.200 × 890 mm). Dos personas es criterio del "
      f"grupo: el ayudante retira y coloca sustitutos mientras el chofer controla y firma el remito.")
    h2("10.2 Recorrido")
    p("Ida y vuelta 1,5 h: 25 km por tramo entre la planta y la zona de clientes (dato del grupo); si 15 km son de "
      "autopista a 61 km/h y "
      "10 km de ciudad a 20 km/h (TomTom Traffic Index 2024 para Buenos Aires: 30 min 09 s cada 10 km en ciudad) son "
      "45 min por tramo. Manejo entre paradas 15 min: 5 km a 20 km/h. Dos turnos de logística, los mismos de la planta. "
      "Tiempo fijo por parada 20 min (estacionar, presentarse, controlar el remito y firmar): no hay estudio publicado "
      "para el AMBA, queda como criterio (§ 12).")
    h2("10.3 Pulmón y jaulas")
    p("Recepción y despacho guardan medio día (lo que trae un turno entra al proceso en el siguiente; lo recargado sale "
      "en el turno siguiente). Factor 1,15 de jaulas a medio llenar, porque el Word separa las jaulas por cliente y por "
      "familia de agente. 15 % de jaulas vacías de reserva. Sustitutos en estantería de 3 niveles y rodantes en el "
      "piso. Las jaulas vacías se apilan de a 4, lo que admite la Hypacage. Superficie por posición 2,4 m² (1,2 m² de "
      "jaula más el pasillo de transpaleta compartido por dos filas). Los valores de días, factor, reserva y niveles "
      "son criterio.")
    p("Unidades por jaula: el Word da la jaula A (72 de 1 kg) y la B (30 de 2,5 kg, 24 de 5 kg o 16 de 10 kg). El resto "
      "se ubica en la clase del Word cuya huella (ancho × profundidad del catálogo FLAMA) lo contiene: sales K 6 l "
      "(270 × 190 mm) y CO₂ 5 kg (310 × 140 mm) no entran en la celda de 5 kg y van con 16, como el 10 kg (antes 20); "
      "el ABC 25 kg (480 × 630 mm) entra de a 2 en la base de 1.000 × 1.200 (antes 3).")
    h2("10.4 Minutos por equipo en el cliente")
    p("0,5 min en automotor (1 kg en mano, sin colgar), 1,5 min en edificios, educación, hoteles, industrias y salud, y "
      "1,0 min en supermercados. Son del grupo y no hay medición publicada. Sirven de control los recorridos del Dec. "
      "351/79: con un recorrido máximo de 20 m hasta un matafuego, entre dos hay como mucho unos 40 m, medio minuto a "
      "paso normal; el resto es descolgar, colgar el sustituto y controlar la tarjeta. Quedan para medir en la visita.")
    h2("10.5 Resultados")
    rl = d["rubros_log"]
    tabla([30, 14, 14, 14, 14],
          ["Rubro (mes pico)", "u/día com.", "Paradas com.", "u/día ind.", "Paradas ind."],
          [[g.RUBROS[c], n(rl[c][1], 0), n(rl[c][3], 0), n(rl[c][5], 0), n(rl[c][7], 0)] for c in range(7)],
          num=range(1, 5))
    filas = []
    for k_ in ["Mes pico", "Llegan por día en el mes pico (u)", "Sustitutos que salen por día (u)", "Paradas por día",
               "Viajes por día", "Camiones", "Ocupación de la flota", "Posiciones del pulmón",
               "Superficie del pulmón (m²)"]:
        v = L[k_]
        f = (lambda x: pc(x, 0)) if "Ocupación" in k_ else ((lambda x: x) if k_ == "Mes pico" else (lambda x: n(x, 0)))
        filas.append([k_, f(v[0]), f(v[1])])
    tabla([50, 25, 25], ["2035", "Comercial", "Industrial"], filas, num=(1, 2))
    p(f"Los camiones pasan de {ANTES['Comercial']['cam']} a {L['Camiones'][0]} en la comercial y de "
      f"{ANTES['Industrial']['cam']} a {L['Camiones'][1]} en la industrial. Tres causas, en este orden de peso:")
    b("Lote de automotor 9 en vez de 25: el automotor pasa de unas 54 a 150 paradas por día en la comercial, y el "
      "tiempo de parada es lo que limita la flota (los viajes por tiempo superan a los viajes por carga).")
    b(f"La flota tiene el mismo límite del 90 % que los puestos. La versión anterior quedaba en "
      f"{pc(ANTES['Comercial']['ocup'], 0)} y {pc(ANTES['Industrial']['ocup'], 0)}; ahora "
      f"{pc(L['Ocupación de la flota'][0], 0)} y {pc(L['Ocupación de la flota'][1], 0)}.")
    b("El mes pico es enero, con el automotor al 12 %: más paradas chicas que en febrero.")
    p("Si en la visita se confirma que un cliente automotor es un punto de acopio de 25 equipos, la comercial vuelve a "
      "9 camiones y la industrial a 5, ya con el límite del 90 %.")

    # 11
    h1("11. Parámetros de planta")
    b("**Días hábiles por mes: 20.** 2035 tiene 261 días de lunes a viernes; menos 13 feriados nacionales que caen en "
      "día hábil (Ley 27.399) quedan 248, 20,7 por mes. Se usa 20, que deja 3 % de margen.")
    b("**8 h por turno:** Ley 11.544.")
    b("**30 min de refrigerio:** valor del Excel del grupo; la ley no fija la duración de la pausa y depende del "
      "convenio. Quedan 7,5 h productivas por turno y 150 h por mes.")
    b("**Máximo 2 turnos y 2° turno en 2032:** § 8.")

    # 12
    h1("12. Para confirmar en la visita al recargador")
    for x in ["Porcentaje de equipos que se pintan (hoy 15 %): es el criterio que más mueve máquinas (§ 4.7).",
              "Porcentaje que va a PH por daño menor (hoy 5 %) y por humedad (1 %) (§ 4.3 y 4.8).",
              "Porcentaje de CO₂ y halogenados que se abren por pérdida de masa (hoy 5 %) (§ 4.6).",
              "Tiempo del ultrasonido y acuñado del CO₂ en la PH, que no está en el tiempo del puesto (§ 5.12).",
              "Porcentaje de enjuague en el desarme de la zona general (hoy 40 %) (§ 5.10).",
              "Cronometrar los pasos de inspección visual, descarga de agua, desarme, carga ABC, pintura y precinto: son "
              "los que tenían dos tiempos en el Word (§ 5).",
              "Qué es un cliente automotor y cuántos equipos retira el camión en cada uno (hoy 9) (§ 7.1).",
              "Tiempo fijo por parada y minutos por equipo en el cliente (§ 10.2 y 10.4).",
              "Meses preferidos y vedados de cada rubro con los clientes de la zona (§ 3.2 a 3.8) y si la temporada de diciembre y enero del automotor "
              "se ve en el AMBA como en Córdoba y Mendoza (§ 3.1)."]:
            b(x)

    # 13
    h1("13. Fuentes")
    for x in [
        "IRAM 3517-2:2020 (cláusulas 9.2.1, 9.4.5, 9.4.14, 9.7.1.2, 9.7.1.3, 9.7.1.4, 9.7.2, 9.7.5.3, 9.8, 9.9.3, 9.9.4, "
        "9.10, 9.12; tabla 3; anexos E, F y G). IRAM 3509, IRAM 3569, IRAM 3672 y IRAM 3550 citadas por cláusula.",
        "Word de recargas del grupo (tabla de operaciones, paso a paso, tablas 0 y 9); Dimensionamiento Técnico V2; "
        "Proyecciones (Indexado Dim Técnico, PROYECCION <rubro>, % PENETRACION, PxQ Corregido).",
        "[Dec. 351/79, anexo VII (InfoLEG)](https://servicios.infoleg.gob.ar/infolegInternet/anexos/30000-34999/32030/"
        "dto351-1979-anexo7.htm)",
        "[Ley 6116 CABA (Boletín Oficial)](https://boletinoficial.buenosaires.gob.ar/normativaba/norma/448273)",
        "[Dec. 4992/90 PBA](https://normas.gba.gob.ar/ar-b/decreto/1990/4992/101600)",
        "[VTV CABA](https://buenosaires.gob.ar/tramites/verificacion-tecnica-vehicular-obligatoria) · "
        "[VTV PBA, plazos](https://vtv.gba.gob.ar/plazos) · [Ámbito, VTV PBA oct. 2025](https://www.ambito.com/"
        "informacion-general/vtv-provincia-buenos-aires-precios-requisitos-y-beneficios-octubre-2025-n6202713)",
        "[Hoy Día Córdoba: demanda de ITV y recarga de matafuegos](https://hoydia.com.ar/sociedad/"
        "alta-demanda-de-itv-y-recarga-de-matafuegos-en-cordoba/)",
        "[Ámbito: fondos a los Consejos Escolares](https://www.ambito.com/pba-env237an-3000-m-consejos-escolares-n5367560)",
        "[CAPHAI, Circular N.° 14 (2025)](https://caphai.com.ar/site/wp-content/uploads/2025/04/CircularN14.pdf) · "
        "[Arya Seguridad: matafuegos en consorcios](https://www.aryaseguridad.com/cuantos-matafuegos-necesita-un-consorcio-"
        "y-cada-cuanto-deben-revisarse) · convenio colectivo de SUTERH (licencias de encargados)",
        "Río Negro, Ministerio de Educación: [recarga de matafuegos en el receso de verano, General Roca]"
        "(https://rionegro.gov.ar/articulo/6211/tareas-de-mantenimiento-en-escuelas-de-general-roca) · [mantenimiento en "
        "el receso de invierno](https://rionegro.gov.ar/articulo/60168/receso-escolar-se-intensifican-las-tareas-de-"
        "mantenimiento-en-las-escuelas) · [recambio y recarga de matafuegos, Cipolletti](https://rionegro.gov.ar/articulo/"
        "58563/obras-y-mantenimiento-preventivo-en-escuelas-de-cipolletti)",
        "[La Capital (Mar del Plata): mantenimiento de escuelas en las vacaciones de invierno](https://www.lacapitalmdp.com/"
        "aprovechan-las-vacaciones-de-invierno-para-realizar-mantenimiento-en-escuelas/)",
        "[MaxiSeguridad: seguridad contra incendios en hoteles](https://www.maxiseguridad.com.ar/detalle-noticias-"
        "maxiseguridad/34/Seguridad-contra-incendios-en-Hoteles) · [MaxiSeguridad: carga de matafuegos en comercios]"
        "(https://www.maxiseguridad.com.ar/detalle-noticias-maxiseguridad/80/Carga-de-Matafuegos-en-comercios-Normativas)",
        "Boletín Oficial CABA, Ministerio de Salud: [anexo DGACSA 434/26](https://documentosboletinoficial.buenosaires.gob."
        "ar/publico/PE-DIS-MSGC-DGACSA-434-26-ANX-18.pdf) · [anexo SSASS 607/26](https://documentosboletinoficial."
        "buenosaires.gob.ar/publico/PE-RES-MSGC-SSASS-607-26-ANX.pdf)",
        "[LEA Global: incendios en supermercados y depósitos](https://www.lea-global.com/uploads/circulares/2018/02/"
        "05-04-incendios-en-supermercados-y-depositos-de-mercaderias.pdf) · [Extintec: IRAM 3517 e inspecciones]"
        "(https://extintec.com.ar/web/2026/03/11/norma-iram-3517/) · [CAGESRA, circular N.° 168]"
        "(https://cagesra.org.ar/circular-n-168/)",
        "[Sitio Andino: movimiento de la RTO en Mendoza y pico de demanda (jul. 2026)](https://www.sitioandino.com.ar/"
        "sociedad/como-es-el-movimiento-la-rto-mendoza-el-pico-demanda-n5715925) · [Elonce: alta demanda de recargas por "
        "las vacaciones](https://www.elonce.com/parana/matafuegos-para-vehnculos-alta-demanda-de-recargas-por-las-"
        "vacaciones.htm) · [Rafaela Noticias: recarga de matafuegos antes de las vacaciones](https://rafaelanoticias.com/"
        "locales/alta-demanda-de-servicios-esenciales-antes-de-las-vacaciones-recarga-de-matafuegos-y-mantenimiento-"
        "vehicular.htm)",
        "[46 CFR 132.350](https://www.ecfr.gov/current/title-46/chapter-I/subchapter-L/part-132/subpart-C/"
        "section-132.350)",
        "[Iveco Daily 55C17 chasis cabina (Autocosmos)](https://www.autocosmos.com.ar/catalogo/2020/iveco/daily-chasis/"
        "chasis-cabina-simple-55c17/164089) · [Palletower Hypacage](https://palletower.com/uncategorized/"
        "heavy-duty-hypacage-large/)",
        "[TomTom Traffic Index, Buenos Aires](https://www.tomtom.com/traffic-index/buenos-aires-traffic/)",
        "INDEC, Encuesta de Supermercados (bocas y superficie de ventas). Directiva 2007/46/CE (masa por ocupante). "
        "Ley 24.449, art. 40. Ley 11.544. Ley 27.399. Ficha técnica Sherwin FT 27.00 (esmalte poliuretano).",
    ]:
        b(x)
    return out


def generar():
    d = leer()
    js = os.path.join(g.SALIDA, "_bloques_recargas.json")
    with open(js, "w", encoding="utf-8") as f:
        json.dump(bloques(d), f, ensure_ascii=False)
    ruta = os.path.join(g.SALIDA, "Justificacion_Recargas.docx")
    subprocess.run(["node", os.path.join(AQUI, "word_recargas.js"), js, ruta], check=True)
    os.remove(js)
    return ruta


if __name__ == "__main__":
    print(generar())
