"""Word «Sistema de trazabilidad FLAMA» (salida/Sistema_de_trazabilidad_FLAMA.docx): marcado por modelo (lugar,
contenido, profundidad, faja), trazabilidad intraplanta puesto por puesto, extraplanta, retorno y re-especificación,
seguros, devolución e inutilización, y revendidos. La geometría sale de cuerpos.json (modelo 3D de los planos)."""
import json
import os
import subprocess
import tempfile

from PIL import Image

import figuras_trazabilidad as FT

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DOCX = os.path.join(RAIZ, "salida", "Sistema_de_trazabilidad_FLAMA.docx")
JS = os.path.join(RAIZ, "corte", "word_corte.js")
NODE_PATH = os.environ.get("NODE_PATH", "/tmp/claude-0/-home-user-TP-optimizacion/"
                                        "15292aaf-e550-5dee-a83e-77fd9177a6ef/scratchpad/jw/node/node_modules")

U_PANNIER = "https://www.directindustry.com/prod/pannier/product-24420-679289.html"
U_FAB = ("https://www.thefabricator.com/thefabricator/product/shopmanagement/"
         "dot-peen-system-makes-marks-that-are-readable-after-coating")
U_PROTO = "https://www.protocase.com/products/graphics-markings/dot-peening/"
U_KEY = ("https://www.keyence.com/products/marker/laser-marker/resources/laser-marking-resources/"
         "shot-blast-resistant-laser-marking.jsp")
U_EPCIS = "https://www.gs1.org/epcis"
U_EPCIS2 = "https://GS1.org/docs/epcis/epcis_2-0_launch.pdf"
U_ZX = "https://github.com/zxing-cpp/zxing-cpp/"
U_DMTX = "https://desk.ximea.com/kb/articles/pdf/libdmtx"
U_YOLO1 = "https://engrxiv.org/preprint/view/6685"
U_YOLO2 = "https://hal.archives-ouvertes.fr/hal-03837669"
U_CCYCN = "https://www.conceptosjuridicos.com/ar/articulos/codigo-civil-y-comercial-articulo-1298/"
U_COT = ("https://web.arba.gov.ar/sites/default/files/2024-02/"
         "COT%20C%C3%B3digo%20de%20Operaci%C3%B3n%20Traslado%20o%20Transporteggti.pdf")
U_SEG = "https://economis.com.ar/?p=438705"
U_RFID = "https://www.rfidtagworld.com/products/On-Metal-Tag/On-Metal-Tag_1548.html"
U_UMP = ("https://news.ump.edu.my/research/"
         "ts-dr-wan-isni-sofiah-develops-mobile-application-streamline-fire-extinguisher-maintenance")

ORDEN = ["1kg", "2.5kg", "5kg", "10kg", "25kg", "50kg", "70kg", "100kg"]
# catálogo de los planos (flama/catalogo.py): masa total cargada y presión de ensayo; IRAM 3517-2 tabla 3: tolerancia
MASA = {"1kg": "1,90", "2.5kg": "4,60", "5kg": "8,50", "10kg": "16,50", "25kg": "55", "50kg": "93", "70kg": "125",
        "100kg": "180"}
TOL = {"1kg": "0 / +100 g", "2.5kg": "0 / +100 g", "5kg": "0 / +300 g", "10kg": "0 / +300 g", "25kg": "± 3 %",
       "50kg": "± 3 %", "70kg": "± 3 %", "100kg": "± 3 %"}
DESC = {"25kg": "≥ 10 s", "50kg": "≥ 15 s", "70kg": "≥ 15 s", "100kg": "≥ 30 s"}


def render(bl, salida, pie):
    tmpj = salida + ".json"
    with open(tmpj, "w", encoding="utf-8") as fh:
        json.dump(bl, fh, ensure_ascii=False)
    subprocess.run(["node", JS, tmpj, salida, pie], check=True, env=dict(os.environ, NODE_PATH=NODE_PATH))
    os.remove(tmpj)


def g(x):
    return f"{x:g}".replace(".", ",")


def bloques(fig):
    b = []

    def add(t, x, **k):
        b.append(dict(t=t, x=x, **k))

    def p(x):
        add("p", x)

    def bul(*xs):
        for x in xs:
            add("b", x)

    def tabla(cab, filas, cols, **k):
        b.append(dict(t="tabla", cab=cab, filas=filas, cols=cols, **k))

    def img(clave, pie, ancho=16.5):
        w, h = Image.open(fig[clave]).size
        b.append(dict(t="img", ruta=fig[clave], pie=pie, ancho=ancho, anchoPx=w, alto=h))

    C, M = FT.CUERPOS, {k: FT.marcado(k) for k in ORDEN}

    add("titulo", "Sistema de trazabilidad FLAMA")
    add("sub", "Marcado del recipiente, trazabilidad en planta y fuera de ella, recarga, retorno, inutilización y "
               "revendidos · versión 2")
    p("Un número por recipiente, grabado en el cuerpo cuando se corta la chapa, que no se pierde nunca. Todo lo demás "
      "(etiqueta, QR, app, legajo) cuelga de ese número. Las normas se citan por cláusula, sin transcribirlas; donde "
      "un valor es una decisión de diseño y no un requisito se marca **criterio**. Las medidas de los cuerpos, la "
      "etiqueta, la oblea, los sellos, los triángulos del eje y la faja salen del modelo 3D de los planos "
      "(trazabilidad/cuerpos.json).")

    # ================================================================== 0
    add("h1", "0. Respuestas directas")
    add("h2", "0.1 ¿La faja del sustituto tapa el grabado?")
    p("**Sí, con el plano actual la tapaba.** El plano FL_SUS pone una faja amarilla de hasta 40 mm desde el borde "
      "inferior que rodea todo el perímetro (con 20 mm de solape), y la franja grabada de los manuales va justamente "
      "en la pollera. Lo mismo pasaría con la faja verde de los equipos de reserva.")
    p("Qué dice la norma: la faja de sustituto va «en su borde inferior o pollera», con una altura máxima de 40 mm y "
      "tres leyendas (IRAM 3517-2 9.4.5 b); la de reserva, en el mismo lugar y «evitando tapar los datos grabados» "
      "(5.3). Ninguna de las dos exige que la faja dé la vuelta completa. Entonces:")
    bul("**Manuales:** la franja se graba del lado opuesto a la costura (ver 1.3) y la faja pasa a ser **abierta** "
        "(en C): arranca y termina 5 mm antes de cada punta de la franja (**criterio**). Las leyendas quedan del lado "
        "de la etiqueta, que es el que se ve.",
        "**Carros:** la franja sube por encima de los triángulos del eje; la faja queda abajo, abierta entre los dos "
        "triángulos (hoy los cruza: están soldados de 20 mm hacia arriba). No se tocan.",
        "**Hallazgo de paso:** en el 2,5 kg la faja actual (30,4 mm) pisa 6 mm la tarjeta AGC, que arranca a 24,4 mm "
        "del borde. Con la faja abierta se baja a 21 mm (≤ 40, cumple).")
    img("faja", "5 kg desarrollado: a la izquierda el plano actual (la faja tapa la franja), a la derecha la faja "
                "abierta.")
    tabla(["Modelo", "Faja hoy (alto × largo)", "Faja propuesta (alto × largo)", "Dónde queda abierta"],
          [[FT.NOMBRE[k], f"{g(C[k]['faja_actual']['alto'])} × {g(round(C[k]['faja_actual']['largo']))}",
            f"{g(M[k]['faja_alto'])} × {g(round(M[k]['faja_largo']))}",
            ("entre los triángulos del eje (lado costura)" if M[k]["carro"] else
             f"sobre la franja: {g(round(M[k]['L'] + 10))} mm del lado opuesto a la costura")] for k in ORDEN],
          [2.5, 4, 4, 6.5])
    p("Cambia el largo de la faja en el BOM (ítem FAJA-SUS) y en los planos FL_SUS; la faja verde de reserva lleva las "
      "mismas medidas.")

    add("h2", "0.2 ¿Cómo se hace con los revendidos que no vienen grabados?")
    p("Primero, lo que dice la norma: el revendido **tiene que venir grabado por su fabricante**. Las normas de "
      "producto que pude leer lo exigen igual que para los propios: fabricante, número de recipiente y año, en el "
      "recipiente o en un accesorio fijo (IRAM 3523 5.1 para BC y Clase D; IRAM 3525 5.1 para agua). Los cilindros de "
      "CO₂ llevan el estampado de su fabricante (IRAM 2533). Las IRAM 3527, 3541, 3694 y 3504 están escaneadas sin "
      "texto: hay que confirmar la cláusula de marcado, pero la estructura de estas normas es la misma.")
    p("Segundo, por qué no se puede aceptar uno sin grabado: un extintor sin fecha de fabricación o sin número de "
      "serie **no se puede instalar, mantener ni recargar** y se considera obsoleto (IRAM 3517-2 9.11; anexo F, "
      "recipiente: «fecha de fabricación o n° de serie faltante o adulterado → inutilizar»). Además, la etiqueta de "
      "cada servicio tiene que llevar el número de serie del recipiente (9.4.14 b). Un revendido sin grabado se "
      "vendería con un año de vida, hasta su primera recarga.")
    p("Tercero, por qué FLAMA no lo graba: grabaría «FLAMA S.A.» como fabricante en un recipiente que no fabricó, "
      "estamparía una pared a presión que ya pasó la prueba hidráulica de otro fabricante sin volver a probarla, y "
      "el sello IRAM es del fabricante, no de FLAMA. Por eso el revendido se identifica con **su** grabado más una "
      "etiqueta FLAMA con QR. El detalle está en la sección 6.")

    add("h2", "0.3 Qué cambió respecto de la versión 1")
    tabla(["Tema", "Versión 1", "Versión 2 (con las medidas del modelo 3D)"], [
        ["Lado de la franja (manuales)", "«adelante, a 180° de la costura, bajo la etiqueta»",
         "En los planos la etiqueta envuelve la costura (están del mismo lado). La franja va del lado opuesto, bajo el "
         "QR de serie: queda contra la pared, protegida, y se lee al descolgarlo"],
        ["Altura de la franja (carros)", "35 a 49 mm", "Encima de los triángulos del eje: de 95 a 138 mm según el modelo "
                                                       "(a 35 mm quedaba detrás de los triángulos)"],
        ["Faja de sustituto y reserva", "no se trataba", "Abierta, con medidas por modelo (0.1)"],
        ["Revendidos", "«etiqueta en la recepción»", "Procedimiento completo y regla de rechazo (sección 6)"],
        ["Detalle por puesto", "una línea por puesto", "Ficha completa por puesto con valor, regla y fuente (sección 2)"],
    ], [3.5, 4.5, 9])

    # ================================================================== 1
    add("h1", "1. Marcado: forma, lugar y profundidad por modelo")
    add("h2", "1.1 Qué pide la norma y cómo se cumple")
    tabla(["Requisito", "Fuente", "Cómo se cumple"], [
        ["Grabar fabricante, n° de recipiente y año (2 dígitos), en el recipiente o en un accesorio fijo; ±3 meses en "
         "el cambio de año", "IRAM 3523 5.1 (manuales); IRAM 3550 5.1 (carros)", "Texto de 5 mm en la franja"],
        ["Carros: además la presión de ensayo", "IRAM 3550 5.1", "«PE 4,0 MPa» en la primera línea"],
        ["Cuño DPS 1,5 × 0,7 cm al lado del n° de identificación, en la pollera u ojiva", "Res. 349/07 anexo IV",
         "Cuño en el extremo derecho de la franja"],
        ["No dañar la identificación", "Res. 349/07 art. 25 e)", "Franja fuera de soldaduras; fajas abiertas"],
        ["Faja de reserva / sustituto ≤ 40 mm en el borde inferior, sin tapar lo grabado",
         "IRAM 3517-2 5.3 y 9.4.5 b)", "Faja abierta sobre la franja (0.1)"],
        ["N° de recipiente en la placa, igual al grabado; mes y año de fabricación", "IRAM 3523 / 3550 5.2.4",
         "La etiqueta se imprime leyendo el grabado (compuerta del puesto 24)"],
        ["Sistema informatizado de seguimiento y trazabilidad del recargador; registro de 6 años",
         "IRAM 3517-2 4.x aa) y 9.4.16", "Este sistema; los eventos no se borran"],
    ], [7, 4, 5.5])
    p("Lo que se **suma** sin reemplazar nada es un DataMatrix grabado al lado del texto, con el mismo número, para "
      "leerlo con una cámara. La norma no fija tecnología de marcado.")

    add("h2", "1.2 Contenido exacto de la franja")
    img("contenido", "Las tres franjas a escala.")
    tabla(["Campo", "Contenido", "Regla"], [
        ["N° de serie", "AA-NNNNNN (ej. 26-000123)", "AA = año del corte; NNNNNN correlativo por año, único para "
                                                     "todos los modelos; un número anulado no se reutiliza (**criterio**)"],
        ["Año", "2 dígitos (26)", "IRAM 3523 / 3550 5.1"],
        ["Fabricante", "FLAMA S.A.", "IRAM 3523 / 3550 5.1"],
        ["Presión de ensayo (carros)", "PE 4,0 MPa", "IRAM 3550 5.1; valor del catálogo de los planos"],
        ["DataMatrix ECC 200", "con GTIN: (01) GTIN del modelo + (21) 26000123 (cadena GS1, 26 dígitos); sin GTIN: "
                               "26000123", "18 × 18 celdas de 0,6 mm = 10,8 mm; la cadena entra holgada"],
        ["Cuño DPS", "el que entregue la DPS", "Res. 349/07 anexo IV"],
    ], [3.5, 6.5, 7])
    p("**Por qué 0,6 mm por celda:** cada celda es un punto del punzón, y con 0,6 mm el código mide 10,8 mm: entra en "
      "una franja de 12 mm y en el Ø 76 del 1 kg (la curvatura es chica frente al código). Se confirma en el ensayo "
      "1.6. El texto es el respaldo: si la cámara no lee, el operario tipea el número.")

    add("h2", "1.3 Dónde va en cada modelo")
    p("Tres datos de los planos deciden el lugar: (1) la etiqueta, la oblea, el sello IRAM y la tarjeta AGC están del "
      "mismo lado que la costura longitudinal; (2) del lado opuesto los manuales solo tienen el QR de serie, y los "
      "carros tienen la manga enrollada; (3) los carros tienen los triángulos y el caño del eje soldados abajo, del "
      "lado de la costura.")
    img("vistas", "Cómo queda armado: 5 kg de los dos lados y 25 kg del lado de la etiqueta y del lado de la manga.")
    ley = ("Rojo: franja grabada · amarillo: faja de sustituto o reserva · gris: etiqueta · violeta: oblea PBA y "
           "tarjeta AGC · rosa: sello IRAM · celeste: QR de serie · gris oscuro: triángulos y caño del eje. Los bordes "
           "gruesos son la costura; es la planchuela como la ve la marcadora, cara exterior arriba.")
    img("mapas_1", "1 kg y 2,5 kg desarrollados. " + ley)
    img("mapas_2", "5 kg y 10 kg desarrollados.")
    img("mapas_3", "25 kg y 50 kg desarrollados: la franja arranca a 25 mm del borde de costura, encima de los "
                   "triángulos.")
    img("mapas_4", "70 kg y 100 kg desarrollados.")
    filas = []
    for k in ORDEN:
        c, m = C[k], M[k]
        arco = m["L"] / c["R"] * 180 / 3.14159265
        lado = ("lado de la costura, encima de los triángulos" if m["carro"] else
                "lado opuesto a la costura, bajo el QR de serie")
        zona = ("pared a presión" if (m["carro"] or not c["pollera"]) else f"pollera de {g(c['pollera'])} mm")
        filas.append([FT.NOMBRE[k], lado, f"{g(round(m['u0'], 1))} – {g(round(m['u1'], 1))}",
                      f"{g(m['z0'])} – {g(m['z1'])}", f"{g(round(arco))}°", zona, g(c["e"]), FT.PROF[k]])
    tabla(["Modelo", "Lado", "u desde el borde de costura (mm)", "z desde el borde inferior (mm)", "Arco",
           "Zona", "e (mm)", "Profundidad (criterio, mm)"], filas, [1.6, 4.2, 2.4, 2.2, 1.2, 2.6, 1.1, 2.2])
    bul("**1 kg:** no tiene pollera (el fondo monta por fuera), así que la franja va en la pared a presión, encima "
        "del fondo, en dos líneas para no rodear medio cuerpo.",
        "**2,5 a 10 kg:** en la pollera, que está debajo del fondo y no trabaja a presión. Es el mejor lugar: se "
        "puede grabar más hondo sin tocar la pared resistente.",
        "**Carros:** del lado de la manga no se puede (la manga enrollada la tapa) y abajo del lado de la costura "
        "están los triángulos y el caño del eje. Queda encima de los triángulos, a 25 mm del borde de costura "
        "(fuera de la zona afectada por la soldadura longitudinal, **criterio**) y debajo de la oblea y del sello.",
        "**Cilindros vendidos vacíos y sustitutos:** igual que su modelo.",
        "**DPS:** la Res. 349/07 pide el cuño en la pollera u ojiva. En los 2,5 a 10 kg va en la pollera. Para el "
        "1 kg y los carros falta confirmar con la DPS que vale el cuerpo bajo; si no, el número y el cuño se "
        "repiten en la ojiva.")

    add("h2", "1.4 Profundidad")
    img("profundidad", "Corte de la pared con la huella del punzón y la pintura (esquema).")
    tabla(["Modelo", "e (mm)", "Zona", "Regla (criterio)", "Profundidad"], [
        ["1 kg", "0,9", "pared a presión", "≤ 10 % de e. La prueba hidráulica al 100 % se hace después del grabado y "
                                           "valida la pared ya marcada", "0,08 – 0,10 mm"],
        ["2,5 / 5 / 10 kg", "1,25 / 1,6 / 2,0", "pollera", "≈ 3 veces el espesor de pintura (70 µm, planilla de MP: "
         "poliéster 60 a 80 µm), para seguir legible después de repintados", "0,20 – 0,25 mm"],
        ["25 / 50 kg", "3,2", "pared a presión", "≤ 10 % de e (0,32) y ≥ 3 × pintura (0,21)", "0,30 mm"],
        ["70 / 100 kg", "4,75", "pared a presión", "≤ 10 % de e (0,475) y ≥ 3 × pintura", "0,40 – 0,45 mm"],
    ], [2.5, 2.2, 2.5, 7, 2.5])
    p(f"La Pannier ADP120160D graba texto, logos y códigos 2D en una ventana de 120 × 160 mm y su fabricante la "
      f"ofrece para marcas profundas legibles después de granallado y pintura ([ficha]({U_PANNIER})); "
      f"[The Fabricator]({U_FAB}) y [Protocase]({U_PROTO}) reportan lo mismo para micropercusión bajo "
      f"recubrimiento. La franja de 130 mm entra de un golpe si se orienta a lo largo del lado de 160 mm de la "
      f"ventana. En carros la franja va en dos líneas (115 × 13 mm) para entrar en la ventana de la DTMAQ MPE 150130 "
      f"(el nombre sugiere 150 × 130 mm: confirmar).")

    add("h2", "1.5 Cómo se graba, paso a paso")
    tabla(["Paso", "Manuales (salida de G2, Pannier)", "Carros (puesto 2.1, DTMAQ MPE 150130)"], [
        ["1. Orden", "El programa de corte de G2 le pasa a la app el modelo de la tanda", "Ídem desde el corte"],
        ["2. Número", "La app pide el próximo serie al sistema y se lo envía a la marcadora como texto variable "
                      "(confirmar con Pannier el ingreso desde PC)", "Ídem (confirmar con DTMAQ)"],
        ["3. Posición", "Planchuela con la cara exterior arriba, contra el tope del borde inferior y el tope del "
                        "centro (desarrollo / 2)", "Contra el tope del borde inferior y del borde de costura "
                                                  "derecho: la franja arranca a 25 mm"],
        ["4. Programa", "Uno por espesor (fuerza y paso del punzón); lo fija el ensayo 1.6", "Ídem 3,2 y 4,75"],
        ["5. Grabado", "Un campo: la franja a lo largo del lado de 160 mm de la ventana", "Un campo (115 × 13 mm)"],
        ["6. Verificación", "Cámara fija sobre la mesa: lee el DataMatrix y compara con el número pedido",
         "Ídem o lector de mano"],
        ["7. Resultado", "Lee bien → evento CORTADO y GRABADO, atado a la hoja y al lote de chapa", "Ídem"],
        ["8. Si no lee", "No se graba encima. El número queda ANULADO con motivo; la planchuela se aparta para "
                         "revisión (**criterio**)", "Ídem"],
    ], [2.2, 7.4, 7.4])
    p("**Orientación en la roladora:** el grabado va hacia afuera. El operario de la roladora lo ve antes de cilindrar; "
      "si la planchuela entra al revés el grabado queda adentro y la cámara del puesto siguiente no lo encuentra: "
      "rechazo inmediato.")

    add("h2", "1.6 Ensayo de validación (antes de cambiar los planos)")
    tabla(["Etapa", "Qué se hace", "Qué se mide", "Se aprueba si (criterio)"], [
        ["Muestras", "5 planchuelas por espesor (0,9 · 1,25 · 1,6 · 2,0 · 3,2 · 4,75)", "—", "—"],
        ["Grabado", "3 profundidades por espesor alrededor de la tabla 1.4", "profundidad con comparador o "
                                                                             "perfilómetro", "dentro de la banda"],
        ["Conformado", "cilindrado y soldaduras como en producción", "lectura del DataMatrix", "lee al primer intento"],
        ["Prueba hidráulica", "a la presión de ensayo, 1 min (DOC-02 R3)", "deformación en la franja", "ninguna visible"],
        ["Granallado y pintura", "como en producción (DOC-01)", "lectura y legibilidad del texto", "lee; texto legible "
                                                                                                  "a simple vista"],
        ["Repintado", "una segunda mano encima (simula 9.10)", "lectura", "sigue leyendo"],
        ["Resultado", "se fija la profundidad y el programa por espesor", "—", "pasa a ser valor de ficha"],
    ], [2.6, 5.2, 4.4, 4.8])

    # ================================================================== 2
    add("h1", "2. Trazabilidad intraplanta: del grabado al embalado")
    add("h2", "2.1 La estación barata de cada puesto")
    tabla(["Componente", "Qué es", "Por qué"], [
        ["Celular o tablet Android en soporte", "La pantalla del puesto", "Barato, se cambia en el día"],
        ["Lector", f"Cámara del celular con [zxing-cpp]({U_ZX}) o [libdmtx]({U_DMTX}); lector DPM de mano donde la "
                   "cámara no lea (lo dice el ensayo 1.6)", "El código grabado tiene poco contraste"],
        ["App", "AppSheet sobre Google Sheets (FLAMA ya trabaja en Sheets); funciona sin conexión y sincroniza",
         "Sin programar ni servidores"],
        ["Integración", "Balanza de carga, banco de PH y manómetro patrón por USB o carga manual", "El dato entra sin "
                                                                                                 "tipear donde se puede"],
        ["Ficha del modelo", "Tabla FICHAS: modelo, revisión, puesto, parámetro, mínimo, máximo, unidad, fuente",
         "El operario ve qué tiene que cumplir el equipo que tiene en la mano"],
    ], [3.5, 8, 5.5])
    img("app", "Tres pantallas de ejemplo (datos inventados): puesto 14, puesto 24 y recepción en recargas.")
    p("**Cómo trabaja el operario:** lee el grabado → la app muestra modelo, estado y la ficha del puesto → completa "
      "o toma los valores → la app compara con la regla → si cumple pasa al estado siguiente; si no, pide motivo y "
      "foto y lo manda a RECHAZO. Cada lectura queda como evento en el legajo del equipo.")

    add("h2", "2.2 Estados y compuertas")
    img("intraplanta", "Estados del recipiente. Las compuertas (GATE) bloquean el paso si la ficha no se cumple.")
    tabla(["Estado", "Entra cuando", "Puede salir a"], [
        ["CORTADO y GRABADO", "la cámara lee el DataMatrix recién grabado", "CONFORMADO · ANULADO"],
        ["CONFORMADO", "cilindrado, soldaduras y armado registrados con sus lotes", "PROBADO · RECHAZO"],
        ["PROBADO (GATE)", "espesor ≥ mínimo y PH aprobada", "TERMINADO · ANULADO"],
        ["TERMINADO", "granallado, defectos corregidos y pintura con lote", "CARGADO · CILINDRO VACÍO"],
        ["CARGADO", "masa y presión dentro de la ficha", "APROBADO · RECHAZO"],
        ["APROBADO (GATE)", "sin pérdidas (y a las 24 h, criterio FLAMA de DOC-02 R8)", "IDENTIFICADO"],
        ["IDENTIFICADO (GATE)", "el QR pegado se lee y es igual al grabado", "EMBALADO"],
        ["EMBALADO", "serie dentro de una caja y la caja en un pallet (SSCC)", "DESPACHADO (sección 3)"],
        ["RECHAZO", "un control no cumple", "vuelve al puesto (retrabajo) o ANULADO"],
        ["ANULADO", "no se puede recuperar; el número queda registrado con motivo", "— (chatarra)"],
    ], [3.6, 9, 4.4])

    add("h2", "2.3 Ficha por puesto: manuales")
    p("Las reglas salen de DOC-02 «Ensayos de fabricación ABC» (R1 a R9) y del catálogo de los planos. Lo que no tiene "
      "norma se marca criterio.")
    tabla(["Puesto", "Lee", "Registra", "Regla y fuente", "Si no cumple"], [
        ["1 Recepción de chapa", "remito", "proveedor, colada, espesor, certificado", "espesor ≥ nominal del plano "
         "(DOC-02 R1)", "lote retenido"],
        ["2 Corte G2 + Pannier", "—", "**nace el serie**: modelo, hoja, lote, programa de grabado", "lectura OK (1.5)",
         "ANULADO"],
        ["4 a 7 Disco, cuello y cúpula", "carro de cúpulas", "lote de cúpulas (ya no se numera la cúpula), lote de "
         "cuellos", "embutido y soldadura sin defectos", "lote retenido"],
        ["8 Cilindrado", "grabado", "máquina, operario", "modelo = matriz cargada; grabado hacia afuera", "RECHAZO"],
        ["9 Soldadura longitudinal", "grabado", "soldador, lote de alambre y gas", "visual ISO 5817 nivel C "
         "(DOC-02 R2)", "RECHAZO"],
        ["10 a 12 Encastre, bordón, soldadura circunferencial", "grabado + lote de cúpula y de fondo",
         "**agregación** serie ← cúpula ← fondo; soldador", "ídem R2", "RECHAZO"],
        ["13 Control de espesor", "grabado", "espesores medidos", "≥ espesor del plano", "**GATE**: ANULADO"],
        ["14 Prueba hidráulica", "grabado", "presión, tiempo, resultado, banco y patrón", "3,5 MPa durante 1 min, sin "
         "caída, pérdidas ni deformación (DOC-02 R3; IRAM 3517-2 9.7.5.2)", "**GATE**: ANULADO"],
        ["15 Secado", "grabado", "tiempo, control con cámara", "sin agua ni condensado (R4; 9.8.2)", "repetir"],
        ["16 Granallado · 17 Defectos · 18 Corrección", "grabado + foto", "defectos detectados y corregidos",
         "sin poros ni golpes; decide el operario", "RECHAZO"],
        ["19 Pintura", "grabado al colgar", "lote de pintura, horno", "espesor y adherencia (R5, DOC-01)", "repintar"],
        ["19 Descarga", "grabado", "destino: carga o cilindro vacío", "—", "—"],
        ["20 Carga", "grabado", "lote de polvo, masa (balanza)", "masa nominal con su tolerancia (tabla 2.4; R6)",
         "corregir"],
        ["21 Ensamblaje", "grabado", "n° o lote de válvula y manómetro, tubo de pesca", "componentes del BOM",
         "corregir"],
        ["22 Presurización", "grabado", "presión", "N₂ seco a 1,4 MPa a 20 °C; aguja en verde (R7)", "corregir"],
        ["23 Pérdidas", "grabado", "resultado; control a 24 h", "sin pérdida (R8; 9.4.10)", "**GATE**: RECHAZO"],
        ["24 Etiquetado", "grabado", "etiqueta con QR impresa leyendo el grabado; sello IRAM, oblea PBA, precinto, "
         "masa final", "QR = grabado; masa total en tolerancia (R9)", "**GATE**: reimprimir"],
        ["25 Embalaje", "QR", "caja → pallet (SSCC)", "cantidad del pallet", "corregir"],
    ], [3.2, 2.2, 4.2, 4.6, 2.8])

    add("h2", "2.4 Valores de ficha por modelo")
    tabla(["Modelo", "Carga nominal", "Tolerancia de carga", "Masa total (catálogo)", "Presión de servicio",
           "Presión de ensayo", "Descarga"],
          [[FT.NOMBRE[k], FT.NOMBRE[k], TOL[k], f"{MASA[k]} kg", "1,4 MPa", "4,0 MPa" if M[k]["carro"] else "3,5 MPa",
            DESC.get(k, "≥ 8 s")] for k in ORDEN], [2, 2.2, 2.6, 2.4, 2.3, 2.3, 2.2])
    p("Fuentes: catálogo de los planos (masa total, presiones); IRAM 3517-2 tabla 3 y DOC-02 (tolerancia y descarga, "
      "que se ensaya por lote: DOC-02 L3).")

    add("h2", "2.5 Carros: lo que cambia")
    tabla(["Puesto", "Lee y registra", "Regla", "Estado"], [
        ["2 Corte + 2.1 Marcado", "nace el serie (DTMAQ: confirmar DataMatrix e ingreso de texto)", "lectura OK",
         "CORTADO y GRABADO"],
        ["3 a 8 Cilindrado, punteo, soldaduras, cupla, accesorios", "soldador; lotes de casquetes, triángulos, caño "
         "del eje, ruedas", "ISO 5817 C; todo soldado antes de la PH (IRAM 3550 6.1.1)", "CONFORMADO"],
        ["9 PH · 10 Secado", "presión, tiempo, resultado", "4,0 MPa, 1 min (DOC-02 R3)", "**GATE** PROBADO"],
        ["11 Pulmón a pintura tercerizada", "lectura **sale** de cada carro; la app arma la lista del envío",
         "lista = carros cargados al camión", "EN PINTOR"],
        ["12 Recepción de pintados", "lectura **entra**; la app compara con la lista y marca faltantes; rechazados "
                                     "del pintor con foto", "todos los enviados vuelven o están justificados",
         "TERMINADO"],
        ["13 Carga · 14 Pérdidas", "lote, masa, presión; ensayo de pérdidas", "± 3 %; 1,4 MPa; sin pérdida",
         "**GATE** APROBADO"],
        ["15 Etiquetado e inspección final", "QR = grabado; foto", "ídem manuales", "**GATE** IDENTIFICADO"],
        ["16 Depósito PT · 17 Ensayos de lote", "retenido hasta que aprueba el lote (DOC-02 L1 a L5); la muestra "
                                               "destruida queda ANULADA", "lote aprobado", "liberado"],
    ], [4, 6.2, 4.2, 2.6])

    add("h2", "2.6 El legajo del equipo (ejemplo inventado)")
    p("Es la «ficha de producto» que pediste: se arma sola con las lecturas, y por cada dato dice lo especificado, lo "
      "real y si cumple.")
    tabla(["Fecha", "Puesto", "Dato", "Especificado", "Real", "Cumple", "Quién"], [
        ["02/03/26", "2 G2 + Pannier", "serie · hoja · lote de chapa", "—", "26-000123 · H-0412 · col. 4521", "✓",
         "op. 104"],
        ["03/03/26", "9 Soldadura long.", "lote alambre / gas", "BOM", "AL-2602 / G-77", "✓", "sold. 21"],
        ["03/03/26", "12 Circunferencial", "lote cúpula / fondo", "—", "CU-0303 / FO-0301", "✓", "sold. 18"],
        ["04/03/26", "13 Espesor", "espesor mínimo", "≥ 1,60 mm", "1,62 mm", "✓", "op. 33"],
        ["04/03/26", "14 PH", "presión / tiempo", "3,5 MPa / 60 s", "3,52 MPa / 62 s", "✓", "op. 112"],
        ["06/03/26", "19 Pintura", "lote", "—", "PP-2603-2", "✓", "línea"],
        ["09/03/26", "20 Carga", "polvo", "5,00 kg 0/+0,30", "5,14 kg", "✓", "balanza B2"],
        ["09/03/26", "22 Presurización", "presión", "1,4 MPa a 20 °C", "1,40 MPa", "✓", "op. 51"],
        ["10/03/26", "23 Pérdidas", "24 h", "sin pérdida", "sin pérdida", "✓", "op. 51"],
        ["10/03/26", "24 Etiquetado", "QR = grabado · masa total", "8,50 kg (+ tol.)", "26-000123 · 8,62 kg", "✓",
         "op. 60"],
        ["10/03/26", "25 Embalaje", "caja / pallet", "—", "C-88412 / SSCC …0457", "✓", "op. 60"],
    ], [1.6, 2.8, 3, 2.6, 3.4, 1.2, 1.8])

    add("h2", "2.7 Situaciones especiales")
    tabla(["Situación", "Qué hace el sistema"], [
        ["Se corta la red", "La app sigue sin conexión y sincroniza después; el orden de eventos lo da la hora del "
                            "celular"],
        ["La cámara no lee el grabado", "Se tipea el número; queda marcado «lectura manual» para revisar el puesto"],
        ["Retrabajo (ej. una soldadura)", "Vuelve al puesto con el mismo serie; el legajo muestra el retrabajo"],
        ["Falla la PH", "ANULADO; el serie queda en el registro con el motivo; la chatarra se separa"],
        ["Cilindro vendido vacío", "Desde la descarga de pintura va a embalaje; sin carga ni compuerta de pérdidas"],
        ["Lote de polvo o válvulas con problema", "Consulta lote → series → dónde están: se retienen en planta y se "
                                                  "avisa a los despachados (4.7)"],
        ["Se mezclan cúpulas de dos lotes", "El carro de cúpulas es el lote; si se mezcla, se registran los dos y el "
                                            "llamado a revisión toma ambos"],
        ["Etiqueta mal pegada o dañada", "Se reimprime desde el grabado; la vieja queda anulada"],
    ], [5, 12])

    add("h2", "2.8 Visión con YOLO")
    tabla(["Uso", "Dónde", "Cómo", "Qué decide"], [
        ["Ubicar y leer el grabado", "todos los puestos y recargas", "YOLO encuentra la franja en la foto, la recorta y "
         "se la pasa a zxing-cpp / libdmtx; si falla, OCR del texto", "solo lee"],
        ["Defectos de superficie y soldadura", "puesto 17", f"detector entrenado con fotos propias de poros, golpes "
         f"y cordones ([YOLO en soldadura]({U_YOLO1}); [YOLOv3]({U_YOLO2}))", "marca; decide el operario"],
        ["Control final", "24 manuales · 15 carros", "verifica etiqueta, precinto, manómetro en verde, pasador, "
                                                       "tobera y faja; guarda la foto", "si falta algo, frena"],
        ["Conteo de pallet", "despacho", "cuenta equipos en la foto y compara con el SSCC", "avisa faltantes"],
        ["Estado en recepción", "recargas", "corrosión y golpes como apoyo a IRAM 3517-2 9.7.1.3", "decide el "
                                                                                                     "recargador"],
    ], [3.6, 2.8, 7.2, 3.4])
    p("Corre en una PC chica con cámara fija. El entrenamiento necesita un lote de fotos propias etiquetadas: va en la "
      "fase 3.")

    add("h2", "2.9 Datos e integridad")
    tabla(["Tabla", "Qué guarda"], [
        ["SERIES", "serie, modelo (GTIN), estado, rev. de ficha, lote de chapa, quién lo tiene, fecha de fabricación"],
        ["EVENTOS", "id, serie o SSCC, tipo, puesto, fecha y hora, operario, valores, resultado, foto, hash anterior, "
                    "hash"],
        ["FICHAS", "modelo, revisión, puesto, parámetro, mínimo, máximo, unidad, fuente"],
        ["LOTES", "chapa, polvo, válvulas, manómetros, pintura, precintos, marbetes: proveedor y certificado"],
        ["AGREGACIONES", "padre (lote de cúpula, caja, pallet SSCC) e hijo (serie)"],
        ["CUSTODIA", "serie, quién lo tiene, desde cuándo, documento"],
    ], [3.2, 13.8])
    p(f"Cada evento guarda el hash del anterior: si alguien edita un renglón viejo, la cadena se rompe y se nota. Los "
      f"eventos siguen la estructura de [GS1 EPCIS 2.0]({U_EPCIS}) ([lanzamiento]({U_EPCIS2})): qué, cuándo, dónde, "
      f"por qué y cómo.")

    # ================================================================== 3
    add("h1", "3. Trazabilidad extraplanta: de la carta de porte a la llave en mano")
    img("extraplanta", "Cadena de custodia: cada traspaso es una doble lectura con su documento.")
    tabla(["Traspaso", "Documento", "Quién lee y cómo", "Datos que quedan", "Si falta o llega dañado"], [
        ["FLAMA → transportista", f"remito y factura; carta de porte suscripta por el cargador (CCyCN "
                                  f"[art. 1298]({U_CCYCN}); segundo ejemplar art. 1299; guía art. 1300); COT si el "
                                  f"traslado supera los umbrales vigentes ([ARBA]({U_COT}))",
         "despacho lee cada pallet (sale ✓); el chofer lee el QR del remito con su celular (entra ✓)",
         "fecha, camión, chofer, pallets y series", "no se cierra el despacho"],
        ["Transportista → distribuidor", "remito firmado", "el distribuidor lee el pallet (entra ✓)",
         "custodia: distribuidor", "foto y faltante en el mismo traspaso"],
        ["Distribuidor → instalador o cliente", "factura o remito del distribuidor", "al abrir el pallet lee cada "
         "serie que vende (desagregación)", "a quién se vendió cada serie", "—"],
        ["Instalador → cliente (llave en mano)", "acta de entrega firmada en el celular", "lee el serie ya colgado",
         "dirección, sector, foto en el soporte, altura, dueño", "—"],
    ], [3, 5, 3.6, 3.2, 2.2])
    p("**El punto débil** es el distribuidor, que no está obligado a leer nada. Propuesta (**criterio**): la garantía "
      "del equipo se activa cuando se registra la venta o la instalación. Así el que vende tiene un motivo para leer. "
      "Los instaladores propios de FLAMA leen siempre.")
    p("El QR de la etiqueta (GS1 Digital Link) abre la ficha con dos solapas, **técnica** y **comercial**, las dos con "
      "la historia; los lotes, los operarios y los parámetros de máquina quedan solo para FLAMA.")

    # ================================================================== 4
    add("h1", "4. Retorno, re-especificación por recarga y seguros")
    img("retorno", "Ciclo en servicio.")
    add("h2", "4.1 Aviso")
    p("El sistema conoce el vencimiento de cada equipo: mantenimiento anual (IRAM 3517-2 9.2.1; semestral recomendado "
      "en vehículos) y PH cada 5 años en polvo (anexo E). Avisa al cliente antes de que venza (**criterio**: 30 días).")
    add("h2", "4.2 Retiro y sustituto")
    bul("Se deja un sustituto de igual clasificación y por lo menos igual capacidad (9.4.5), con la faja amarilla "
        "abierta (0.1) y la tarjeta «sustituto habilitado» (Res. 349/07 art. 32).",
        "La app **parea** sustituto ↔ equipo retirado: se sabe dónde está cada sustituto y cuántos días lleva afuera.",
        "El equipo retirado viaja con su serie: lectura sale ✓ del cliente y entra ✓ en recargas.")
    add("h2", "4.3 Recepción en recargas")
    p("Se lee el grabado, se saca foto y la app aplica el anexo F y 9.7.1.3 como bloqueos (tercera pantalla de 2.1):")
    tabla(["Revisión", "Fuente", "Qué hace la app"], [
        ["Fecha de fabricación o n° de serie faltante o adulterado", "anexo F; 9.11", "INUTILIZAR"],
        ["Vida útil cumplida (20 años polvo)", "9.11; anexo E", "INUTILIZAR"],
        ["Reparaciones por soldadura o masilla, corrosión, quemado", "9.7.1.3", "INUTILIZAR sin PH"],
        ["Daño mecánico, abolladura o abrasión", "anexo F", "INUTILIZAR"],
        ["Daños menores por corrosión o golpe", "9.7.1.2", "exige PH"],
        ["PH vencida", "anexo E", "exige PH"],
        ["Pintura deficiente", "9.10; anexo F", "exige pintura y etiqueta nueva"],
        ["Tipo de agente", "9.4.6", "no deja cargar otro agente"],
    ], [7.5, 3, 6.5])
    add("h2", "4.4 Servicio")
    tabla(["Paso", "Registro", "Fuente"], [
        ["Desarmado", "marbete indicador nuevo entre válvula y cuello: color del año y n° de serie o lote del marbete",
         "9.6.1 a 9.6.4"],
        ["PH (si corresponde)", "presión 2,5 × Ps (rodantes 4 MPa), 1 min, resultado", "9.7.3; 9.7.5.2"],
        ["Secado", "control con cámara", "9.8.2"],
        ["Recarga", "lote del agente, masa", "9.9; tabla 3"],
        ["Pintura", "si corresponde; reimprime la etiqueta con QR", "9.10"],
        ["Precinto", "n° o lote del precinto (trazable)", "9.4.13"],
        ["Etiqueta de servicio", "próximo mantenimiento, n° de serie del recipiente, vencimiento de PH, prestador",
         "9.4.14"],
        ["Registro", "insumos con lote, procesos, propiedad; 6 años", "9.4.16"],
    ], [3.5, 9.5, 4])
    add("h2", "4.5 Re-especificación: ficha rev. n+1")
    p("El equipo nace con la ficha rev. 0 (cómo se fabricó). Cada servicio cierra una revisión nueva (cómo quedó); "
      "las anteriores no se borran.")
    tabla(["Campo", "Rev. 0 (fábrica)", "Rev. n+1 (servicio)"], [
        ["Agente", "lote de fábrica, masa", "lote de la recarga, masa nueva (o recuperado + reposición)"],
        ["Presión", "1,4 MPa de fábrica", "presión de servicio medida"],
        ["Componentes", "válvula, manómetro, manguera de fábrica", "los que se cambiaron, con su lote"],
        ["PH", "PH de fábrica", "fecha, presión y resultado si tocó"],
        ["Terminación", "pintura de fábrica", "repintado, etiqueta nueva"],
        ["Marbete y precinto", "—", "color del año y n°; precinto nuevo"],
        ["Vencimientos", "recarga y PH", "recalculados; la vida útil sigue contando desde la fabricación y ningún "
                                         "vencimiento puede pasarla (9.11)"],
        ["Responsable", "FLAMA", "recargador, tarjeta DPS / AGC"],
    ], [3.2, 5.5, 8.3])
    add("h2", "4.6 Recargas de equipos de otras marcas")
    p("Entran igual que un revendido (sección 6): se identifican por el grabado de su fabricante y reciben una etiqueta "
      "FLAMA con QR; desde ahí tienen legajo propio.")
    add("h2", "4.7 Seguros y llamado a revisión")
    p(f"El sistema no cambia lo que cubre una póliza (eso lo dice cada póliza; ver por ejemplo [qué cubre un seguro de "
      f"incendio]({U_SEG})), pero da la prueba: con el QR se muestra, a la fecha del siniestro, el último servicio, "
      f"el marbete vigente, la ubicación y las fotos, con la cadena de hashes como garantía de que no se editó. No "
      f"encontré una fuente que diga que la aseguradora condiciona el pago al mantenimiento.")
    p("Para FLAMA el valor fuerte es el **llamado a revisión**: lote con problema → series → quién lo tiene (custodia) "
      "→ aviso directo y retiro. Sin agregación y custodia no se puede hacer.")

    # ================================================================== 5
    add("h1", "5. Devolución al cliente e inutilización")
    add("h2", "5.1 Devolución")
    bul("Doble lectura en la propiedad: el equipo entra ✓ y el sustituto sale ✓; el pareo se cierra.",
        "Estado EN SERVICIO con la ficha rev. n+1; el QR muestra el servicio nuevo.")
    add("h2", "5.2 Inutilización paso a paso")
    tabla(["Paso", "Qué se hace", "Fuente", "Registro"], [
        ["1. Decisión", "la app lo indica por regla (4.3) o por falla en PH (9.7.6)", "9.7.1.3; 9.7.6; 9.11",
         "motivo"],
        ["2. Agente", "se retira y va a disposición según normas ambientales", "9.12.1 a)", "kg y destino"],
        ["3. Cilindro expulsor (si tiene)", "dos orificios de Ø ≥ 10 mm en lugar visible", "9.12.1 b)", "foto"],
        ["4. Recipiente", "dos orificios de Ø ≥ 10 mm en lugar visible, **lejos de la franja** para que el grabado "
                          "siga legible en la foto del acta (**criterio**)", "9.12.1 c)", "foto con grabado y "
                                                                                       "orificios"],
        ["5. Manguera", "cortada en dos partes como mínimo", "9.12.1 d)", "foto"],
        ["6. Válvula y accesorios", "a disposición final", "9.12.1 e)", "destino"],
        ["7. Acta", "acta del anexo G con equipo, marca, puesto, capacidad, tipo, fecha de fabricación y motivo; "
                    "firmada y notificada al responsable de la propiedad", "9.12.2; anexo G", "PDF en el legajo"],
        ["8. Depósito", "queda 30 días corridos a disposición del propietario", "anexo G", "fecha de salida"],
        ["9. Disposición final", "chatarra y residuos según normas ambientales", "9.12.1", "certificado"],
        ["10. Bloqueo", "el serie queda BAJA para siempre; leerlo muestra «INUTILIZADO — fecha — acta»", "criterio",
         "evento final"],
    ], [3, 7, 3, 4])
    p("La numeración queda auditable: cada serie está fabricado, anulado en planta o dado de baja.")

    # ================================================================== 6
    add("h1", "6. Revendidos y equipos de otras marcas")
    img("revendidos", "Recepción de un revendido.")
    add("h2", "6.1 Qué marcado trae cada uno")
    tabla(["Equipo revendido", "Norma de fabricación", "Marcado del fabricante", "Leído"], [
        ["BC 5 kg · Clase D 9 l", "IRAM 3523", "grabado de fabricante, n° y año (5.1)", "sí"],
        ["Agua 10 l", "IRAM 3525", "grabado de fabricante, n° y año en el recipiente o accesorio fijo (5.1)", "sí"],
        ["CO₂ 2 y 5 kg", "IRAM 3509 / cilindro IRAM 2533", "estampado del fabricante del cilindro", "notas de los "
                                                                                                   "planos"],
        ["AFFF 10 l · AFFF 50 l", "IRAM 3527 · IRAM 3541", "a confirmar (PDF sin texto)", "no"],
        ["Sales K 6 l", "IRAM 3694", "a confirmar", "no"],
        ["HCFC/HFC 5 kg", "IRAM 3504", "a confirmar (PDF sin texto)", "no"],
    ], [3.8, 3.8, 7, 2.4])
    add("h2", "6.2 Recepción paso a paso")
    tabla(["Paso", "Qué se hace", "Por qué"], [
        ["1. Antes de que llegue", "la orden de compra pide al proveedor la lista de series de cada remito "
                                   "(**criterio**)", "se recibe contra una lista, no a ciegas"],
        ["2. Lectura", "foto del grabado; OCR o tipeo de fabricante + n° + año", "es la identidad del equipo"],
        ["3. Control", "el grabado existe, es legible y está en la lista", "sin grabado no se puede recargar "
                                                                          "nunca (9.11; anexo F)"],
        ["4. Alta", "clave = fabricante + n° + año (el n° solo puede repetirse entre marcas); el sistema le da un ID "
                    "FLAMA R-AA-NNNNNN", "una sola clave por equipo"],
        ["5. Etiqueta", "QR del ID FLAMA en vinilo destructible, del lado opuesto a la etiqueta del fabricante, sin "
                        "tapar su grabado ni su placa (9.4.15)", "no se puede pasar a otro equipo"],
        ["6. Stock", "entra al depósito con su lote de compra", "llamado a revisión del proveedor"],
        ["7. Si no tiene grabado", "no conforme: se separa, se reclama al proveedor (devolución o reemplazo) y no se "
                                   "vende", "no cumple su norma ni se puede mantener"],
    ], [3.2, 8.3, 5.5])
    p("Si la etiqueta FLAMA se pierde (repintado), el recargador busca por fabricante + n° + año grabados y "
      "reimprime. **Opción a negociar** (**criterio**): que el fabricante grabe, además de su número, un DataMatrix "
      "con el ID FLAMA en su planta.")

    # ================================================================== 7
    add("h1", "7. Herramientas, fases y pendientes")
    tabla(["Herramienta", "Uso", "Decisión"], [
        ["Micropercusión profunda (Pannier / DTMAQ)", "grabado + DataMatrix", "**Base**: ya están en planta"],
        ["DataMatrix ECC 200 + QR en la etiqueta (GS1 Digital Link)", "lectura automática y acceso del cliente", "Sí"],
        ["GS1 EPCIS 2.0 + SSCC", "eventos y agregación", "Sí (la estructura; no hace falta software GS1)"],
        ["Cadena de hashes", "integridad", "Sí"],
        ["AppSheet sobre Sheets", "estación de puesto", "Sí (fase 1)"],
        ["YOLO + zxing-cpp / libdmtx + OCR", "visión y lectura", "Fase 3"],
        [f"Etiqueta RFID / NFC para metal ([ejemplo]({U_RFID}))", "lectura sin línea de vista",
         "No por ahora: se va con el repintado igual que la etiqueta"],
        ["Tinta invisible UV", "marca oculta", "No: el granallado y el repintado la quitan o la tapan"],
        [f"App de mantenimiento con QR ([caso UMP]({U_UMP}))", "referencia de uso", "Referencia"],
        [f"Marcado láser ([Keyence]({U_KEY}))", "alternativa al punzón", "No: máquina nueva sin necesidad"],
    ], [6.5, 4.5, 6])
    tabla(["Fase", "Qué entra"], [
        ["0", "Ensayo 1.6; confirmación con la DPS (1 kg y carros); confirmación de Pannier y DTMAQ (texto variable, "
              "ventana, DataMatrix)"],
        ["1", "Serie, estados, compuertas, fichas por puesto, etiqueta con QR, faja abierta en BOM y planos"],
        ["2", "Agregación SSCC, doble lectura en despacho y en la pintura tercerizada, portal QR, revendidos"],
        ["3", "Visión YOLO, recargas con ficha rev. n+1, pareo de sustitutos, llamado a revisión"],
    ], [2, 15])
    add("h2", "Pendientes antes de tocar los planos")
    bul("Profundidades y programa por espesor (hoy criterio): ensayo 1.6.",
        "Pannier: ingreso de texto variable desde PC y orientación de la franja en la ventana de 120 × 160 mm.",
        "DTMAQ MPE 150130: DataMatrix, texto variable y tamaño de la ventana.",
        "DPS: cuño en el cuerpo bajo para 1 kg y carros.",
        "GTIN (alta en GS1 Argentina) o solo número de serie.",
        "Cláusulas de marcado de IRAM 3527, 3541, 3694 y 3504 (PDF sin texto).",
        "Umbrales vigentes del COT de ARBA.")
    p("Después: en los planos se pasa el marcado de la cúpula a la franja de cada modelo, la faja de sustituto y "
      "reserva a la versión abierta (con 21 mm en el 2,5 kg), y la Pannier del puesto 6 a la salida de G2.")

    add("h1", "Fuentes")
    for t, u in (("Pannier ADP120160D Deep Marker", U_PANNIER),
                 ("The Fabricator: micropercusión legible tras recubrimiento", U_FAB), ("Protocase: dot peening", U_PROTO),
                 ("Keyence: marcado láser resistente al granallado", U_KEY), ("GS1 EPCIS", U_EPCIS),
                 ("GS1 EPCIS 2.0", U_EPCIS2), ("zxing-cpp", U_ZX), ("libdmtx", U_DMTX),
                 ("Detección de defectos de soldadura con YOLO", U_YOLO1),
                 ("Defectos de soldadura con YOLOv3", U_YOLO2), ("CCyCN art. 1298 a 1300", U_CCYCN), ("ARBA: COT", U_COT),
                 ("Seguro de incendio", U_SEG), ("Etiqueta RFID para metal", U_RFID),
                 ("UMP: app de mantenimiento de matafuegos", U_UMP)):
        add("b", f"[{t}]({u})")
    add("b", "IRAM 3523 5.1 y 5.2.4 · IRAM 3525 5.1 · IRAM 3550 5.1, 5.2.4 y 6.1.1 · IRAM 2533 · IRAM 3517-2:2020 "
             "(5.3, 9.2, 9.4.5, 9.4.6, 9.4.10, 9.4.13 a 9.4.16, 9.6, 9.7, 9.8.2, 9.9, 9.10, 9.11, 9.12, tabla 3, "
             "anexos E, F y G) · Res. 349/07 PBA (art. 25, 28, 29, 32 y anexo IV). Se citan, no se transcriben.")
    add("b", "Documentos FLAMA: DOC-01 Tratamiento superficial y pintura; DOC-02 Ensayos de fabricación ABC; planos "
             "FL_MAT, FL_SUS y modelo 3D (cuerpos.json); planilla de MP (pintura).")
    return b


def main():
    fig = FT.todas(tempfile.mkdtemp(prefix="figs_traz_"))
    render(bloques(fig), DOCX, "Sistema de trazabilidad FLAMA")
    print("ok", DOCX)


if __name__ == "__main__":
    main()
