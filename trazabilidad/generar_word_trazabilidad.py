"""Word «Sistema de trazabilidad FLAMA» v3 (salida/Sistema_de_trazabilidad_FLAMA.docx): dónde va el marcado y cuánto
perfora (renders del modelo 3D), sistema por lote con hoja de ruta y lecturas en dos puntos, intraplanta y extraplanta
paso a paso con restricciones, etiquetas, tecnología, interfaces y transparencia. Geometría: cuerpos.json; renders:
render_3d.py (render/*.png)."""
import json
import os
import subprocess
import tempfile

from PIL import Image

import figuras_trazabilidad as FT
import figuras_v3 as F3

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DOCX = os.path.join(RAIZ, "salida", "Sistema_de_trazabilidad_FLAMA.docx")
JS = os.path.join(RAIZ, "corte", "word_corte.js")
NODE_PATH = os.environ.get("NODE_PATH", "/tmp/claude-0/-home-user-TP-optimizacion/"
                                        "15292aaf-e550-5dee-a83e-77fd9177a6ef/scratchpad/jw/node/node_modules")

U_PANNIER = "https://www.directindustry.com/prod/pannier/product-24420-679289.html"
U_FAB = ("https://www.thefabricator.com/thefabricator/product/shopmanagement/"
         "dot-peen-system-makes-marks-that-are-readable-after-coating")
U_EPCIS2 = "https://GS1.org/docs/epcis/epcis_2-0_launch.pdf"
U_CCYCN = "https://www.conceptosjuridicos.com/ar/articulos/codigo-civil-y-comercial-articulo-1298/"
U_COT = ("https://web.arba.gov.ar/sites/default/files/2024-02/"
         "COT%20C%C3%B3digo%20de%20Operaci%C3%B3n%20Traslado%20o%20Transporteggti.pdf")
U_SEG = "https://economis.com.ar/?p=438705"

U_ISO = "https://www.thecoresolution.com/clause-8-5-2-iso-9001-2015-explained"
U_HID = "https://tallyfy.com/products/pro/tracking-and-tasks/tasks/scanner-and-rfid-integration/"
U_COGNEX = "https://www.cognex.com/blogs/industrial-barcode-reader/solve-barcode-reading-challenges-with-newest-handheld-barcode-reader"
U_PRYOR = "https://machines.pryormarking.com/product/markmaster-networked-software/"
U_BRADY = "https://www.mecco.com/product-ethermark"
U_ZEBRA = "https://developer.zebra.com/blog/printing-websites-part-3"
U_ZEBRA_ET = ("https://www.atlasrfidstore.com/zebra-2-x-1-z-ultimate-3000t-thermal-transfer-label-for-desktop-printers-"
              "case-of-12-rolls-2-530-labels-per-roll/")
U_GSDL = "https://www.gs1uk.org/standards-services/get-market-ready/connect-to-consumer/guides-resources/how-to-use-the-gs1-uk-resolver-service"
U_195 = "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-195-1997-44765/texto"
U_UNECE = "https://unece.org/DAM/trans/danger/publi/unrec/rev13/Spanish/03_Part3.pdf"
U_CABA = "https://buenosaires.gob.ar/gcaba_historico/infraestructura/logistica-nocturna-en-carriles-exclusivos"

ORDEN = ["1kg", "2.5kg", "5kg", "10kg", "25kg", "50kg", "70kg", "100kg"]


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
               "revendidos · versión 3")
    p("Un número por recipiente, grabado en el cuerpo cuando se corta la chapa, que no se pierde nunca. Todo lo demás "
      "(etiqueta, QR, app, legajo) cuelga de ese número. Las normas se citan por cláusula, sin transcribirlas; donde "
      "un valor es una decisión de diseño y no un requisito se marca **criterio**. Las medidas de los cuerpos, la "
      "etiqueta, la oblea, los sellos, los triángulos del eje y la faja salen del modelo 3D de los planos "
      "(trazabilidad/cuerpos.json).")

    # ================================================================== 0
    add("h1", "0. Qué cambió en esta versión (tus 8 puntos)")
    tabla(["Pediste", "Qué hice"], [
        ["1. Que se entienda dónde va y cuánto perfora", "Renders del matafuego real de los planos con flechas (1.1), "
         "vista desde arriba con los ángulos (1.2) y corte de la pared **a escala** con lo que perfora y lo que queda "
         "(1.4)"],
        ["2. No una tablet por puesto; investigar", "El registro de cada puesto es la **hoja de ruta del lote** "
                                                    "(papel firmado). Se lee con un lector solo en etiquetado y en "
                                                    "despacho. Sección 2 con lo que encontré"],
        ["3. Cómo duran las etiquetas", "La etiqueta no tiene que durar 20 años: se renueva en cada servicio "
                                        "(IRAM 3517-2 9.4.14). El que dura es el grabado (sección 6)"],
        ["4. Intraplanta paso a paso", "Sección 3: los 10 pasos con quién, qué, con qué, cuánto tarda y qué pasa si "
                                       "falla"],
        ["5. Extraplanta exacto, con limitaciones", "Sección 4: del pedido a la instalación, paso a paso, con los "
                                                    "documentos y las restricciones legales y prácticas"],
        ["6. Tecnología y conexiones", "Sección 7: qué partes hay y cómo se conectan"],
        ["7. Interfaz, software y hardware; que se alimente de los Excel", "Sección 8: pantallas, equipos (casi todos "
         "ya previstos en el layout) y cómo el sistema lee el Plan mensual y asigna las series por lote"],
        ["8. Todo transparente", "Sección 9: quién ve qué, cómo se corrige un error sin borrar, qué indicadores da"],
        ["9. App en Vercel", "Siguiente paso, sobre este diseño"],
    ], [5, 12])

    # ================================================================== 1
    add("h1", "1. Dónde va todo y cuánto perfora")
    add("h2", "1.1 El matafuego real con cada cosa en su lugar")
    p("Renders del modelo 3D de los planos (mismas piezas, mismas medidas) con la franja grabada, el QR de serie, la "
      "etiqueta, la oblea y la faja de sustituto agregados donde van.")
    img("r5kg", "ABC 5 kg. Izquierda: lado etiqueta; la costura longitudinal queda debajo de la etiqueta. Centro: "
                "lado opuesto (contra la pared): la franja grabada abajo, en la pollera, y el QR de serie a media "
                "altura. Derecha: tres cuartos.")
    img("r1kg", "ABC 1 kg: igual que el 5 kg, con la franja encima del fondo (no tiene pollera).", 13)
    img("r25kg", "ABC 25 kg: la franja va del lado de la etiqueta, al costado de la costura y encima de los "
                 "triángulos del eje; del otro lado está la manga enrollada.", 15)
    add("h2", "1.2 Vista desde arriba: en qué ángulo va cada cosa")
    img("planta", "La costura es 0°. La etiqueta del fabricante la envuelve; la franja grabada va enfrente (180°) en "
                  "manuales y a un costado de la costura en carros.")
    add("h2", "1.3 Medidas exactas por modelo")
    img("mapas_2", "5 kg y 10 kg desarrollados (la chapa tal como la ve la marcadora, cara exterior arriba; los bordes "
                   "gruesos son la costura). Rojo: franja; amarillo: faja abierta; gris: etiqueta; violeta: oblea y "
                   "tarjeta AGC; rosa: sello IRAM; celeste: QR de serie.")
    img("mapas_3", "25 kg y 50 kg desarrollados: la franja arranca a 25 mm del borde de costura, encima de los "
                   "triángulos (gris oscuro).")
    filas = []
    for k in ORDEN:
        c, m = C[k], M[k]
        arco = m["L"] / c["R"] * 180 / 3.14159265
        lado = ("lado etiqueta, junto a la costura, encima de los triángulos" if m["carro"] else
                "lado pared (180° de la costura), bajo el QR")
        zona = ("pared a presión" if (m["carro"] or not c["pollera"]) else f"pollera ({g(c['pollera'])} mm)")
        filas.append([FT.NOMBRE[k], lado, f"{g(round(m['u0'], 1))} – {g(round(m['u1'], 1))}",
                      f"{g(m['z0'])} – {g(m['z1'])}", f"{g(round(arco))}°", zona, FT.PROF[k]])
    tabla(["Modelo", "Lado", "Desde el borde de costura (mm)", "Desde el borde inferior (mm)", "Arco", "Zona",
           "Profundidad (mm)"], filas, [1.6, 4.6, 2.6, 2.4, 1.2, 2.6, 2.0])
    add("h2", "1.4 Qué se graba y cuánto perfora")
    img("contenido", "Las tres franjas a escala: DataMatrix (lectura con cámara), texto que pide la norma (fabricante, "
                     "número, año; carros: presión de ensayo) y cuño DPS.")
    img("prof_escala", "Corte de la pared a escala: lo que perfora el punzón y lo que queda.")
    tabla(["Modelo", "Chapa", "Perfora", "Queda", "Por qué esa profundidad (criterio)"], [
        ["1 kg", "0,90 mm", "0,08 – 0,10 mm", "0,80 mm", "pared a presión: ≤ 10 % del espesor; la prueba hidráulica "
                                                         "al 100 % se hace después del grabado y valida la pared ya marcada"],
        ["2,5 / 5 / 10 kg", "1,25 / 1,60 / 2,0 mm", "0,20 – 0,25 mm", "≥ 1,0 mm", "es la pollera (debajo del fondo, no "
         "trabaja a presión): ≈ 3 veces la pintura de 70 µm para seguir legible después de repintar"],
        ["25 / 50 kg", "3,2 mm", "0,30 mm", "2,9 mm", "≤ 10 % del espesor y ≥ 3 veces la pintura"],
        ["70 / 100 kg", "4,75 mm", "0,40 – 0,45 mm", "4,3 mm", "ídem"],
    ], [2.4, 2.6, 2.4, 1.8, 7.8])
    p("Las profundidades son **criterio** hasta el ensayo: 5 chapas por espesor se graban, se cilindran, se sueldan, "
      "pasan la prueba hidráulica, se granallan, se pintan, se repintan y se leen. Se aprueba si el texto se lee a "
      "simple vista, el DataMatrix decodifica y la franja no se deforma en la prueba hidráulica.")
    add("h2", "1.5 La faja del sustituto no tapa el grabado")
    img("faja", "Antes y después: la faja del plano del sustituto rodeaba todo el borde inferior; ahora queda abierta "
                "sobre la franja (5 mm de luz a cada lado).")
    p("Base: la faja de sustituto va en el borde inferior, con 40 mm de alto como máximo (IRAM 3517-2 9.4.5 b); la de "
      "reserva, igual y «evitando tapar los datos grabados» (5.3). Ninguna exige dar la vuelta completa. En carros "
      "la franja está más arriba y la faja queda abajo, abierta entre los triángulos del eje. En el 2,5 kg la faja "
      "baja a 21 mm porque la actual pisa 6 mm la tarjeta AGC.")

    # ================================================================== 2
    add("h1", "2. Cómo funciona sin una tablet por puesto")
    add("h2", "2.1 Qué encontré")
    tabla(["Hallazgo", "Qué tomo para FLAMA", "Fuente"], [
        ["La identificación y trazabilidad de ISO 9001 (8.5.2) se resuelve con etiquetas, órdenes de trabajo u hojas "
         "de ruta y control por lote", "La hoja de ruta del lote es el registro de los puestos", f"[ISO 9001 8.5.2]({U_ISO})"],
        ["Un lector en modo teclado (HID) escribe lo leído en el campo activo de un formulario web, sin instalar nada",
         "El lector se enchufa a la PC de etiquetado y despacho y listo", f"[Tallyfy]({U_HID})"],
        ["Los lectores de mano para marcas directas leen micropercusión en superficies cilíndricas y oscuras; el "
         "fabricante informa lecturas en menos de 150 ms", "Uno en etiquetado, uno en recargas", f"[Cognex DataMan 8700]({U_COGNEX})"],
        ["El software de las marcadoras en red asigna números de serie desde una base de datos y evita duplicados",
         "El sistema asigna las series del lote y la marcadora solo graba", f"[Pryor]({U_PRYOR}) · [Brady]({U_BRADY})"],
        ["Las impresoras Zebra imprimen desde una página web con su servicio Browser Print", "La etiqueta sale de la "
         "misma pantalla donde se leyó el grabado", f"[Zebra]({U_ZEBRA})"],
        ["GS1 Digital Link: el QR es una dirección web que lleva el número de serie", "Un solo QR sirve al cliente y a "
         "FLAMA", f"[GS1 Digital Link]({U_GSDL})"],
    ], [7.4, 5.6, 4])
    add("h2", "2.2 Tres formas posibles")
    tabla(["Opción", "Cómo es", "Tiempo del operario", "Decisión"], [
        ["A. Tablet en cada puesto", "cada puesto lee y carga", "lectura + carga en todos los puestos", "No: lo que "
                                                                                                    "dijiste"],
        ["B. Hoja de ruta + lecturas en 2 puntos", "el papel firmado registra los puestos; se lee solo al etiquetar y "
         "al despachar", "una tilde por equipo en los controles y una lectura al etiquetar", "**Sí**"],
        ["C. Cámaras fijas en todos los puestos", "cámaras leen solas", "nada", "Futuro: caro de poner a punto"],
    ], [3.4, 5.6, 4.6, 3.4])
    p("**La idea clave:** el sistema ya sabe qué series tiene cada lote antes de empezar, porque las asigna a partir del "
      "Plan mensual. Durante el proceso solo hay que registrar lo que le pasa **al lote** (insumos y firmas) y las "
      "**excepciones** (los rechazos, con su número, que está grabado y se lee a simple vista).")

    # ================================================================== 3
    add("h1", "3. Intraplanta paso a paso")
    img("intra_pasos", "El lote de punta a punta: en qué pasos se escribe, en cuáles se lee y cuánto agrega a cada "
                       "operario.")
    img("hoja_ruta", "La hoja de ruta del lote (A4). La imprime PCP con las series ya cargadas y viaja dentro del "
                     "carro. Ejemplo con datos inventados.", 14)
    tabla(["Paso", "Quién y dónde", "Qué hace", "Con qué", "Qué queda en el sistema", "Si falla"], [
        ["1. Orden del lote", "PCP, oficina", "El sistema lee el Plan mensual del Excel de Aprovechamiento y propone los "
         "lotes de la semana; PCP confirma", "PC + impresora A4 (existen)", "OP, modelo, cantidad, series reservadas "
         "(26-000101…148), hoja de chapa", "—"],
        ["2. Grabado", "G2 + Pannier", "Carga el archivo de series del lote (o el primer número y la marcadora "
         "numera sola: confirmar con Pannier) y graba cada planchuela", "Pannier", "nada que tipear: las series ya "
                                                                                    "estaban asignadas", "Si una "
         "planchuela sale mal grabada se anula ese número en la hoja"],
        ["3. Cúpulas, cuellos, cilindrado, soldaduras", "puestos 4 a 12", "Una firma por lote en su renglón; anota o "
         "pega la etiqueta del lote de insumo (cúpulas, alambre, gas)", "lapicera", "llega en el cierre (paso 7)",
         "Rechazo: lo saca del carro y anota el número grabado"],
        ["4. Espesor y prueba hidráulica", "puestos 13 y 14", "Una tilde ✓ o ✗ por serie en la lista de la hoja",
         "lapicera", "ídem", "✗ sale del carro"],
        ["5. Granallado, pintura", "puestos 16 a 19", "Firma y lote de pintura", "lapicera", "ídem", "ídem"],
        ["6. Carga, presurización, pérdidas", "puestos 20 a 23", "Firma, lotes de polvo y válvulas; ✓ / ✗ por serie en "
                                                                 "carga y pérdidas", "lapicera; balanza y manómetro "
                                                                                    "como hoy", "ídem", "ídem"],
        ["7. Cierre de la hoja", "calidad, al final del lote", "Saca una foto de la hoja firmada desde el celular y "
         "marca los rechazos en la lista que muestra el sistema", "celular", "PDF de la hoja, insumos y rechazos del "
                                                                              "lote", "Sin cierre, el lote no se "
                                                                                      "puede etiquetar"],
        ["8. Etiquetado", "puesto 24 (manuales) / C-15 (carros)", "Lee el grabado de cada equipo con el lector; la "
         "impresora saca su etiqueta de serie y la de su caja", "PC + impresora (existen) + lector DPM USB",
         "evento IDENTIFICADO por serie", "Si la serie es un rechazo o de otro lote: la pantalla la bloquea"],
        ["9. Embalaje", "puesto 25", "Pega la etiqueta de caja, arma el pallet; al cerrar el pallet lee las cajas e "
                                    "imprime la etiqueta SSCC", "mismo lector", "caja → pallet", "Caja sin leer: el "
                                                                                                  "pallet no cierra"],
        ["10. Depósito de producto terminado", "PT", "Nada: el pallet ya está en el sistema", "—", "ubicación del "
                                                                                                 "pallet", "—"],
    ], [2.4, 2.4, 4.6, 2.6, 3.0, 2.8])
    p("**Carros:** igual, con dos diferencias. La pintura es tercerizada: al despachar al pintor se lee el grabado de "
      "cada carro con el lector (lista del envío) y al volver se lee de nuevo; el sistema avisa si falta alguno. Y el "
      "depósito retiene el lote hasta que aprueban los ensayos de lote (DOC-02 L1 a L5).")
    add("h2", "3.1 Qué controla cada firma (fuente: DOC-02 «Ensayos de fabricación ABC»)")
    tabla(["Puesto", "Qué se controla", "Regla"], [
        ["1 Recepción de chapa", "espesor, certificado de colada", "≥ espesor del plano (R1)"],
        ["9 a 12 Soldaduras", "inspección visual", "ISO 5817 nivel C (R2)"],
        ["13 Espesor", "espesor medido", "≥ espesor del plano"],
        ["14 Prueba hidráulica", "presión y tiempo", "3,5 MPa manuales / 4,0 MPa carros durante 1 min, sin caída, "
                                                     "pérdidas ni deformación (R3; IRAM 3517-2 9.7.5.2)"],
        ["15 Secado", "humedad interior", "sin agua ni condensado (R4; 9.8.2)"],
        ["19 Pintura", "espesor y adherencia", "DOC-01 (R5)"],
        ["20 Carga", "masa de polvo", "1 y 2,5 kg 0/+100 g; 5 y 10 kg 0/+300 g; carros ± 3 % (R6; IRAM 3517-2 tabla 3)"],
        ["22 Presurización", "presión", "N₂ seco a 1,4 MPa a 20 °C (R7)"],
        ["23 Pérdidas", "pérdida", "sin pérdida; control a 24 h (R8)"],
        ["24 Etiquetado", "masa total y marcado", "masa en tolerancia; etiqueta = grabado (R9)"],
    ], [3.6, 4, 9.4])
    add("h2", "3.2 El legajo que resulta (ejemplo inventado)")
    tabla(["Fecha", "Paso", "Dato", "Origen"], [
        ["02/03/26", "Orden", "OP 26-0412 · ABC 5 kg · series 101–148 · chapa H-0412 (colada 4521)", "Plan mensual + PCP"],
        ["02/03/26", "Grabado", "26-000123 grabado", "archivo de la Pannier"],
        ["03/03/26", "Soldaduras", "alambre AL-2602, gas G-77, cúpulas CU-0303 · firmas", "hoja (cierre)"],
        ["04/03/26", "PH", "26-000123 ✓ · 26-000117 ✗ fuga", "hoja (cierre)"],
        ["06/03/26", "Pintura · carga", "pintura PP-2603-2, polvo PO-2603, válvulas VA-118 · ✓", "hoja (cierre)"],
        ["10/03/26", "Cierre", "PDF de la hoja firmada por calidad", "celular"],
        ["10/03/26", "Etiquetado", "26-000123 identificado; caja C-88412", "lector + impresora"],
        ["10/03/26", "Embalaje", "pallet SSCC …0457", "lector"],
    ], [1.8, 2.4, 8.8, 4])

    # ================================================================== 4
    add("h1", "4. Extraplanta paso a paso: del camión al cliente")
    img("extra_pasos", "Cada traspaso: quién entrega, quién recibe y cómo queda registrado.")
    tabla(["Paso", "Quién", "Qué pasa", "Documento", "Cómo se registra", "Limitación"], [
        ["1. Pedido", "ventas", "Se arma el remito; el sistema le agrega el anexo de series y un QR",
         "remito y factura", "automático", "—"],
        ["2. Picking", "depósito PT", "Se juntan los pallets; si se arma un pallet mixto se leen las cajas",
         "anexo de series", "lector: pallet o cajas", "Pallet abierto: hay que leer caja por caja"],
        ["3. Carga", "depósito + chofer", "Equipos de pie, con el seguro puesto, sujetos con film y fajas; carros "
         "calzados", "carta de porte suscripta por el cargador (CCyCN art. 1298); COT de ARBA si supera los umbrales",
         "lectura de cada pallet al subir (sale ✓)", "Ver restricciones (4.1)"],
        ["4. Salida", "chofer", "Firma la carta de porte y lee con su celular el QR del remito: queda EN TRÁNSITO",
         "segundo ejemplar (art. 1299) y guía (art. 1300)", "celular del chofer, sin app", "Sin señal: queda "
                                                                                           "pendiente y se sincroniza"],
        ["5. Viaje", "transportista", "Recorrido y horario según destino", "—", "—", "El sistema no rastrea el "
                                                                                     "camión (no hace falta)"],
        ["6. Entrega al distribuidor", "distribuidor", "Cuenta, revisa, lee el QR del remito y confirma; marca "
         "faltantes o daños con foto", "remito firmado", "página web del remito (entra ✓)", "Si no confirma: el "
                                                                                             "chofer trae el remito "
                                                                                             "firmado y PCP lo carga"],
        ["7. Venta", "distribuidor", "Al vender, lee el QR del equipo: se registra a quién", "su factura",
         "celular", "No está obligado: incentivo = la garantía se activa al registrar (criterio)"],
        ["8. Instalación (llave en mano)", "instalador", "Cuelga el equipo con la parte superior a ≤ 1,5 m del piso "
         "(≤ 1 m si pesa más de 20 kg) y ≥ 0,10 m libre abajo (IRAM 3517-2 6.2.14); cartel a 2,0–2,5 m (7.3); "
         "lee el QR, saca foto y carga dirección y sector", "acta de entrega", "celular; firma el cliente",
         "Si el cliente instala solo: se registra cuando escanea el QR"],
        ["9. En servicio", "cliente", "El QR muestra vencimientos y permite pedir el servicio", "—", "—", "—"],
    ], [2.4, 2.0, 4.6, 3.0, 2.6, 3.0])
    add("h2", "4.1 Restricciones y limitaciones")
    tabla(["Tipo", "Restricción", "Fuente", "Qué hace el sistema"], [
        ["Legal", "Los extintores con gas son mercancía peligrosa UN 1044, clase 2.2, con disposición especial 225. "
                  "La Res. 195/97 exime de parte de los requisitos a las cantidades iguales o menores a la exenta de "
                  "su lista, pero nunca del matafuego del vehículo. **Falta confirmar** la cantidad exenta para UN "
                  "1044 en el texto vigente", f"[Res. 195/97]({U_195}); [ONU lista]({U_UNECE})",
         "Al armar la carga suma los equipos y avisa si se pasa del límite que se cargue"],
        ["Legal", "Carta de porte: la suscribe el cargador; hay segundo ejemplar y guía", f"[CCyCN 1298]({U_CCYCN})",
         "Imprime los datos del envío con el remito"],
        ["Legal", "COT de ARBA para traslados en la provincia según umbrales vigentes", f"[ARBA]({U_COT})",
         "Campo para el código COT en el despacho"],
        ["Ciudad", "En CABA, la carga y descarga en carriles exclusivos solo de 21 a 07 h, máximo 30 min",
         f"[GCBA]({U_CABA})", "Marca el horario en la hoja de ruta del camión"],
        ["Físico", "Equipos de pie, con seguro y precinto; rango de uso −20 a 50 °C (catálogo); carros calzados y "
                   "atados", "catálogo de los planos", "Lista de control en el despacho"],
        ["Información", "Distribuidores y clientes no están obligados a leer", "—",
         "Lo no leído queda en el último que lo tuvo; el cliente puede registrarlo al escanear"],
        ["Información", "Sin señal en la entrega", "—", "La página guarda y envía cuando hay señal; el papel firmado "
                                                        "es el respaldo"],
    ], [1.8, 7.6, 3.4, 4.2])

    # ================================================================== 5
    add("h1", "5. Retorno, recarga, seguros e inutilización")
    img("retorno", "Ciclo en servicio.")
    tabla(["Paso", "Qué pasa", "Fuente", "Registro"], [
        ["Aviso", "El sistema avisa antes del vencimiento: mantenimiento anual; PH cada 5 años en polvo", "9.2.1; anexo E",
         "automático"],
        ["Retiro", "Se deja un sustituto de igual clasificación y capacidad, con faja amarilla abierta y tarjeta "
                   "«sustituto habilitado»; el sistema parea sustituto ↔ equipo", "9.4.5; Res. 349/07 art. 32",
         "lectura de los dos QR"],
        ["Recepción", "Se lee el grabado (tablet e impresora ya previstas en recepción de recargas, más el lector)",
         "—", "evento RECIBIDO"],
        ["Revisión", "Inutilizar si: fecha o número faltante o adulterado, vida útil cumplida, soldaduras o masilla, "
                     "corrosión, quemado, daño mecánico; PH si hay daño menor o está vencida",
         "9.7.1.2; 9.7.1.3; 9.11; anexo F", "la pantalla aplica la regla"],
        ["Servicio", "Marbete del color del año con su número; recarga; precinto trazable; etiqueta de servicio con el "
                     "número de serie; registro 6 años", "9.6; 9.4.13; 9.4.14; 9.4.16", "ficha rev. n+1"],
        ["Devolución", "Equipo entra ✓, sustituto sale ✓", "—", "pareo cerrado"],
        ["Inutilización", "Se retira el agente; dos orificios ≥ 10 mm en lugar visible, lejos de la franja (criterio); "
                          "manguera cortada; acta del anexo G; 30 días en depósito; disposición final",
         "9.12; anexo G", "serie BLOQUEADO para siempre"],
        ["Seguros", "El QR muestra, a la fecha del siniestro, el último servicio, el marbete y la ubicación, con la "
                    "cadena de hashes como prueba de que no se editó", f"[seguro de incendio]({U_SEG})", "—"],
        ["Llamado a revisión", "Lote con problema → series → quién las tiene → aviso", "—", "consulta"],
    ], [2.4, 8.4, 3.4, 2.8])

    # ================================================================== 6
    add("h1", "6. Etiquetas: cuánto duran y qué pasa cuando se pierden")
    img("vida_etiqueta", "La etiqueta acompaña un año; el grabado, toda la vida.")
    p("La etiqueta **no tiene que durar 20 años**. En cada mantenimiento o recarga el recargador debe pegar una etiqueta "
      "nueva que lleve el número de serie del recipiente (IRAM 3517-2 9.4.14), y cuando se repinta la etiqueta vieja "
      "se va (9.10). Por eso cada etiqueta necesita durar alrededor de un año, y lo que dura toda la vida útil es el "
      "grabado. En cada servicio FLAMA imprime la etiqueta nueva con el mismo QR.")
    tabla(["Etiqueta", "Material", "Dónde", "Duración esperada", "Si se pierde"], [
        ["Serie (propios)", "poliéster con cinta de resina (sistema certificado UL 969 si el proveedor lo acredita)",
         "lado pared, a media altura (donde los planos ya ponen la etiqueta de serie)",
         f"el proveedor Zebra informa hasta 3 años interior y exterior ([ficha]({U_ZEBRA_ET})); hace falta 1",
         "se lee el grabado y se reimprime"],
        ["Revendido", "vinilo destructible (no se puede pasar a otro equipo)", "lejos de la etiqueta y del grabado "
                                                                               "del fabricante", "ídem",
         "se busca por fabricante + número + año grabados y se reimprime"],
        ["Servicio", "la del recargador (9.4.14)", "la que fija el recargador", "hasta el próximo servicio",
         "el recargador la repone"],
        ["Caja y pallet", "papel", "caja y pallet", "hasta abrir la caja", "no hace falta"],
    ], [2.4, 4.4, 3.8, 3.8, 2.6])
    img("etiquetas", "Las etiquetas del sistema con QR reales (se pueden escanear desde este documento).")
    add("h2", "6.1 Revendidos")
    p("El revendido tiene que venir grabado por su fabricante. IRAM 3523 5.1 (BC, Clase D) e IRAM 3525 5.1 (agua) lo "
      "exigen, y sin fecha o número no se puede mantener ni recargar (IRAM 3517-2 9.11; anexo F). FLAMA no lo graba: "
      "grabaría su nombre como fabricante en un recipiente ajeno. Al recibirlo:")
    bul("Se lee y fotografía el grabado del fabricante; la clave del equipo es fabricante + número + año.",
        "El sistema le da un ID FLAMA (R-AA-NNNNNN) e imprime su etiqueta de vinilo destructible con QR.",
        "Se cruza con la lista de series que manda el proveedor con el remito (pedirla en la orden de compra, "
        "criterio).",
        "Si no tiene grabado: no conforme, reclamo al proveedor, no se vende.")

    # ================================================================== 7
    add("h1", "7. Tecnología: qué partes hay y cómo se conectan")
    img("arquitectura", "Las partes del sistema y sus conexiones.")
    tabla(["Parte", "Qué hace", "Tecnología", "Cómo se conecta"], [
        ["Excel de producción (Sheets)", "Plan mensual por modelo (Aprovechamiento), MRP, BOM", "Google Sheets (ya "
         "existen, con IMPORTRANGE)", "la app lee el Plan mensual con la API de Google Sheets (cuenta de servicio, "
                                      "solo lectura)"],
        ["App web FLAMA", "Órdenes, lotes, series, eventos, custodia, etiquetas, página pública", "Next.js en Vercel",
         "navegador (HTTPS); no se instala nada en las PC"],
        ["Base de datos", "Guarda todo; cada evento con el hash del anterior", "Postgres administrado", "solo la app; "
                                                                                                     "copia diaria a "
                                                                                                     "Sheets"],
        ["Pannier", "Graba las series del lote", "su software", "archivo de series por USB o red; si no lo admite, "
                                                                 "número inicial y numeración propia de la máquina "
                                                                 "(confirmar)"],
        ["Impresora de etiquetas", "Etiqueta de serie, caja y pallet", "la ya prevista en etiquetado (T07 / C-15)",
         "desde el navegador: Zebra Browser Print o PDF"],
        ["Lector de mano DPM", "Lee el grabado y los QR", "lector industrial USB", "modo teclado: escribe en la pantalla"],
        ["Celulares", "Foto de la hoja, remitos, instalación, consulta del QR", "cualquier celular con cámara",
         "el QR abre una página web; no hay app que bajar"],
        ["QR", "Dirección web con el número de serie", "GS1 Digital Link (con GTIN) o dirección propia",
         "trazabilidad-flama.vercel.app/m/26-000123"],
    ], [3.2, 4.6, 3.8, 5.4])
    add("h2", "7.1 Cómo se alimenta de los Excel y asigna las series por lote")
    bul("Cada lunes PCP abre «Nueva orden»: la app lee del Plan mensual (hoja de Aprovechamiento, columna del mes) cuántos "
        "equipos de cada modelo hay que fabricar.",
        "Propone lotes del tamaño del carro de ese modelo (PCP puede cambiarlos) y reserva para cada lote un rango "
        "correlativo de series: 26-000101 a 26-000148.",
        "Genera el archivo para la Pannier y la hoja de ruta con las 48 series impresas.",
        "Las series ya pertenecen al lote: cuando el etiquetado lee 26-000123, el sistema sabe su lote, su chapa y "
        "todo lo que la hoja registró para ese lote. Así se asigna «por lote» sin cargar nada por equipo.",
        "Cuando calidad cierra la hoja, lo que se registró en papel pasa al lote y los rechazos quedan como eventos "
        "de su serie.")
    add("h2", "7.2 Si algo falla")
    tabla(["Falla", "Qué pasa"], [
        ["Se corta internet", "El papel sigue; la pantalla de etiquetado guarda las lecturas y las manda al volver la "
                              "conexión (criterio: modo sin conexión de la app)"],
        ["Se rompe el lector", "Se tipea el número grabado; queda marcado como lectura manual"],
        ["Se rompe la impresora", "Etiquetas en espera; el lote no sale hasta imprimirlas"],
        ["Error en la hoja", "No se borra: se corrige con un evento nuevo que dice quién y por qué"],
        ["Se cae la app", "Copia diaria en Sheets; los lotes en curso siguen en papel"],
    ], [4, 13])

    # ================================================================== 8
    add("h1", "8. Interfaz y hardware")
    img("pantallas", "Pantallas de la app (maqueta, datos inventados).")
    tabla(["Pantalla", "Quién", "Dónde y con qué", "Qué hace", "Tiempo"], [
        ["Nueva orden", "PCP", "PC de oficina", "Lee el Plan mensual, propone lotes, reserva series, imprime hoja y "
                                                "archivo", "minutos por semana"],
        ["Cierre de hoja", "Calidad", "celular", "Foto de la hoja y rechazos", "~1 min por lote (estimado)"],
        ["Etiquetado", "Operario 24 / C-15", "PC + impresora (existen) + lector", "Lee el grabado e imprime; bloquea "
                                                                                  "rechazos", "~2 s por equipo "
                                                                                              "(estimado)"],
        ["Embalaje y despacho", "Depósito", "misma PC y lector", "Cajas → pallet → remito", "1 lectura por caja"],
        ["Remito", "Chofer, distribuidor", "su celular", "Confirmar salida y recepción", "~1 min por entrega"],
        ["Instalación", "Instalador", "su celular", "Ubicación, foto, acta", "~1 min por equipo"],
        ["Recepción de recargas", "Recargas", "tablet e impresora (ya previstas) + lector", "Lee, aplica reglas, "
                                                                                           "imprime etiqueta", "—"],
        ["QR público", "Cliente, inspector", "su celular", "Solapa comercial y técnica con la historia", "—"],
        ["Tablero", "Dirección, calidad", "PC", "Indicadores (sección 9)", "—"],
    ], [2.6, 2.4, 3.6, 5.6, 2.8])
    p("**Hardware nuevo:** solo lectores de mano para marcas directas (uno en etiquetado de manuales, uno en carros y "
      "despacho, uno en recargas; a cotizar). Lo demás ya está previsto en el layout: impresoras de etiquetas en "
      "etiquetado (T07 y C-15), tablet e impresora en la recepción de recargas, PC e impresora en PCP, y los "
      "celulares de supervisores y choferes.")

    # ================================================================== 9
    add("h1", "9. Transparencia: quién ve qué y cómo se controla")
    tabla(["Quién", "Qué ve", "Qué puede hacer"], [
        ["Cliente (QR)", "solapa comercial: vigencia, vencimientos, historia en lenguaje simple", "pedir servicio, "
                                                                                                  "registrar ubicación"],
        ["Inspector DPS / AGC", "solapa técnica: fabricación, PH, servicios, custodia, hash", "consultar"],
        ["Recargador habilitado", "solapa técnica", "cargar servicios"],
        ["Distribuidor / instalador", "sus remitos y equipos", "confirmar recepción, venta, instalación"],
        ["FLAMA operación", "todo lo de su puesto", "registrar"],
        ["FLAMA calidad y dirección", "todo, incluidos lotes, operarios y parámetros", "corregir con un evento nuevo"],
    ], [3.6, 7.6, 5.8])
    tabla(["Indicador", "De dónde sale"], [
        ["Rendimiento por lote (aptos / grabados)", "series del lote − rechazos"],
        ["Rechazos por puesto, soldador, lote de chapa o insumo", "rechazos de la hoja"],
        ["Tiempo de ciclo del lote", "fecha de orden → etiquetado"],
        ["Equipos en cada custodia", "último traspaso"],
        ["Vencimientos del mes", "fichas de los equipos en servicio"],
        ["Numeración sin huecos", "cada serie está fabricada, anulada o dada de baja"],
    ], [8, 9])
    p(f"Nada se borra: cada corrección es un evento nuevo con autor y motivo, y cada evento guarda el hash del anterior "
      f"(modelo de eventos de [GS1 EPCIS 2.0]({U_EPCIS2})). Los registros se conservan al menos 6 años (IRAM 3517-2 "
      f"9.4.16).")

    # ================================================================== 10
    add("h1", "10. Fases y pendientes")
    tabla(["Fase", "Qué entra"], [
        ["0", "Ensayo de grabado; confirmar con Pannier y DTMAQ (archivo de series, DataMatrix); DPS (cuño en 1 kg y "
              "carros); cantidad exenta UN 1044 en la Res. 195/97 vigente"],
        ["1", "App: órdenes desde el Plan mensual, hoja de ruta, archivo de marcado, etiquetado con bloqueo, QR público"],
        ["2", "Despacho con pallets, remito con QR, confirmación de recepción, instalación, revendidos"],
        ["3", "Recargas con ficha rev. n+1, sustitutos, llamado a revisión, tablero"],
    ], [2, 15])
    bul("Profundidades (hoy criterio): ensayo.", "Pannier: ¿importa archivo de series o numera desde un valor inicial?",
        "DTMAQ: DataMatrix y tamaño de ventana.", "DPS: cuño en el cuerpo bajo (1 kg y carros).",
        "GTIN (alta en GS1 Argentina) o solo número de serie.", "Cantidad exenta UN 1044 y requisitos de transporte "
                                                               "vigentes.", "Umbrales vigentes del COT.")

    add("h1", "Fuentes")
    for t, u in (("ISO 9001:2015 8.5.2 explicado", U_ISO), ("Lectores en modo teclado (Tallyfy)", U_HID),
                 ("Cognex DataMan 8700", U_COGNEX), ("Pryor MarkMaster Networked", U_PRYOR),
                 ("Brady / Mecco EtherMark", U_BRADY), ("Zebra Browser Print", U_ZEBRA),
                 ("Etiquetas Zebra Z-Ultimate (UL 969)", U_ZEBRA_ET), ("GS1 Digital Link", U_GSDL),
                 ("GS1 EPCIS 2.0", U_EPCIS2), ("Res. 195/97 (texto)", U_195), ("Lista ONU de mercancías peligrosas",
                                                                               U_UNECE),
                 ("CCyCN art. 1298", U_CCYCN), ("ARBA: COT", U_COT), ("GCBA: logística nocturna", U_CABA),
                 ("Pannier ADP120160D", U_PANNIER), ("The Fabricator: micropercusión bajo pintura", U_FAB),
                 ("Seguro de incendio", U_SEG)):
        add("b", f"[{t}]({u})")
    add("b", "IRAM 3523 5.1 · IRAM 3525 5.1 · IRAM 3550 5.1 · IRAM 3517-2:2020 (5.3, 6.2.14, 7.3, 9.2, 9.4.5, 9.4.13, "
             "9.4.14, 9.4.16, 9.6, 9.7, 9.10, 9.11, 9.12, tabla 3, anexos E, F y G) · Res. 349/07 PBA (art. 32, anexo "
             "IV). Se citan, no se transcriben. Documentos FLAMA: DOC-01, DOC-02, planos FL_MAT y FL_SUS, modelo 3D.")
    return b


def main():
    fig = FT.todas(tempfile.mkdtemp(prefix="figs_traz_"))
    fig.update(F3.todas(tempfile.mkdtemp(prefix="figs_traz3_")))
    for k in ("r5kg", "r1kg", "r25kg"):
        fig[k] = os.path.join(AQUI, "render", k + ".png")
    render(bloques(fig), DOCX, "Sistema de trazabilidad FLAMA")
    print("ok", DOCX)


if __name__ == "__main__":
    main()
