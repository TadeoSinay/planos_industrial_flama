// ================================================================ manual de seguimiento y trazabilidad (MT-01)
const INSUMOS = { "H-0412": "chapa LAF 1,6 mm · colada 4521", "CU-0303": "cúpulas embutidas", "AL-2602": "alambre MAG", "G-77": "gas de protección Ar + CO₂",
  "PP-2603-2": "pintura en polvo roja", "PO-2603": "polvo ABC 90 % (ejemplo: partida de 1.000 kg)", "VA-118": "válvulas F510" };
const PROCS = [
  ["P-01", "Emisión de órdenes y reserva de series", "PCP", "orden", ["Abrir «Nueva orden»: la app lee el Plan mensual del mes.", "Revisar tamaños de lote (carro del modelo) y agrupación en partidas ≥ 100 u.", "Confirmar: se reservan las series correlativas del año.", "Imprimir hojas de ruta y enviar el archivo a la marcadora."], "OP en la base · hoja de ruta F-01", "Series sin huecos ni repetidas: la base lo impide."],
  ["P-02", "Grabado de la planchuela", "Operario G2", "grabado", ["Cargar el archivo de la OP en la Pannier.", "Apoyar contra topes y marcar; la máquina avanza sola.", "Si sale mal, anular la serie en la hoja (no se reutiliza)."], "Evento GRABADO por serie", "Control visual del primer grabado de cada lote (profundidad y legibilidad)."],
  ["P-03", "Registro en puestos", "Operarios 4 a 23", "puestos", ["Firmar una vez por lote y anotar el lote de cada insumo.", "En espesor, PH, carga y pérdidas: ✓ o ✗ por equipo.", "Sacar del carro el equipo con ✗, con su número a la vista."], "Hoja de ruta F-01 firmada", "PH solo con manómetro contrastado hace ≤ 15 días (Res. 349/07 art. 20)."],
  ["P-04", "Cierre de lote y visado", "Calidad + responsable técnico", "cierre", ["Fotografiar la hoja completa.", "Confirmar rechazos propuestos y abrir un RD por cada uno.", "El RT visa la planilla de ensayos de la partida (anexo I C)."], "Foto + planilla F-02 + RD", "Sin cierre no hay etiquetado."],
  ["P-05", "Identificación final", "Etiquetado", "etiquetado", ["Leer el grabado con el lector.", "Pegar la etiqueta QR y la estampilla de fabricación DPS que asigna la app.", "Si la pantalla bloquea, separar el equipo y avisar a calidad."], "Evento IDENTIFICADO + estampilla", "Estampillas solo de FLAMA y numeradas en el libro (art. 46)."],
  ["P-06", "Embalaje, pallet y despacho", "Embalaje y depósito PT", "embalaje", ["Leer cada caja y cerrar el pallet (SSCC).", "Leer el pallet al subirlo; emitir remito con anexo de series y QR.", "Controlar cantidad exenta de carga peligrosa y COT."], "AGREGACION + CUSTODIA", "Un pallet sin leer no deja cerrar el remito."],
  ["P-07", "Recepción por el distribuidor", "Comercializador", "distribuidor", ["Escanear el QR del remito, contar y revisar.", "Marcar daños con foto; se abre un RD.", "Confirmar la recepción."], "CUSTODIA", "Sin confirmación en 48 h, alerta a ventas."],
  ["P-08", "Instalación y entrega", "Instalador", "instalacion", ["Escanear el QR del equipo instalado.", "Cargar ubicación y datos de la jurisdicción (tarjeta DPS o SGM).", "Verificar alturas; leer el aviso de datos al titular; firmar el acta F-03."], "CUSTODIA + garantía", "Alturas IRAM 3517-2 6.2.14 y 7.3."],
  ["P-09", "Reclamos", "Atención al cliente", "reclamo", ["Recibir (QR, mail o teléfono) y dar número.", "Clasificar; si es de seguridad, sustituto ≤ 48 h.", "Investigar con la traza; responder por escrito con la vía de conciliación.", "Cerrar y pasar la causa a Desvíos."], "RECLAMOS F-08", "Plazos de la política AC-01."],
  ["P-10", "Recarga y mantenimiento", "Recargas", "recarga", ["Leer el grabado; emitir presupuesto F-04 y dejar sustituto habilitado.", "Revisar según IRAM 3517-2 9.7 y anexo F.", "Recargar, grabar la fecha en el tubo de pesca, poner marbete, precinto y etiqueta nueva.", "Cerrar ficha rev. n y enviar la constancia F-05."], "FICHAS + SGM / libro DPS", "Polvo bajo de peso: cambio total (art. 33)."],
  ["P-11", "Inutilización", "Recargas + RT", "inutilizacion", ["Labrar el acta F-06 con el motivo.", "Inutilizar según IRAM 3517-2 9.12 y, en PBA, cortar la rosca (art. 27).", "Avisar al propietario; 30 días en depósito.", "Bloquear la serie y asentar en SGM / libro."], "SERIES = BAJA · acta", "Una serie bloqueada no se puede recargar ni reetiquetar."],
  ["P-12", "Retiro preventivo", "Calidad + dirección", null, ["Buscar el lote sospechoso en el buscador (punto 9).", "Bloquear las series en stock y las del distribuidor.", "Avisar a cada titular con el texto aprobado y coordinar el cambio sin costo.", "Cerrar cuando el 100 % esté ubicado o justificado."], "DESVIOS + lista de series", "Simulacro una vez por semestre (criterio)."],
];
const RACI = [["Emitir OP y series", "R", "", "", "I", "", ""], ["Grabar y registrar en puestos", "I", "R", "C", "", "", ""], ["Cerrar lote y visar", "", "C", "R", "A", "", ""], ["Etiquetar y estampillar", "", "R", "C", "I", "", ""],
  ["Despachar y seguir la custodia", "C", "R", "", "", "I", ""], ["Instalar y entregar", "", "", "", "", "R", "C"], ["Responder reclamos", "", "", "C", "C", "", "R"], ["Recargar e inutilizar", "", "", "C", "A", "R", "I"], ["Retiro preventivo", "C", "C", "R", "A", "C", "R"]];

function traza(q) {
  const t0 = performance.now(), Q = q.trim().toUpperCase();
  let atras = [], adelante = [], titulo = "", nota = "";
  const serie = SERIES.find(s => s === Q || s.replace("-", "") === Q.replace("-", ""));
  if (serie) {
    const rej = serie === REJ;
    titulo = `Serie ${serie} · ${DEMO.modelo}`;
    atras = [`<b>${esc(DEMO.op)}</b> · partida ${PARTIDA.id} · ${MES} ${D.anio}`, `<b>H-0412</b> · ${INSUMOS["H-0412"]}`, `<b>CU-0303</b> cúpulas · <b>AL-2602</b> / <b>G-77</b> soldadura`, `<b>PP-2603-2</b> pintura · <b>PO-2603</b> polvo · <b>VA-118</b> válvula`,
      `PH 3,5 MPa 1 min ${rej ? "<b style='color:var(--red)'>✗ fuga → RD-" + AA + "-031</b>" : "✓"} · espesor ✓ · carga ${rej ? "—" : "5,14 kg ✓"}`, `firmas: J. Pérez (puestos) · M. Ruiz (calidad) · A. Ferreyra (RT)`];
    adelante = rej ? [`<b>RECHAZO</b> · no se etiquetó · a scrap con acta`] : [`caja <b>C-${serie.slice(3)}</b> → pallet <b>SSCC …0457</b>`, `remito <b>R 0001-00004521</b> · Transportes Ruta 3`, `<b>Matafuegos Sur</b> (comercializador)`,
      serie === CLI ? `<b>Panadería La Espiga</b> · Av. Mitre 1450 · instalado` : `en stock del distribuidor`, serie === OTRO ? `<b>inutilizado</b> en ${MES} ${D.anio + 1} · acta AG-${+AA + 1}-0019` : `próximo mantenimiento ${MES} ${D.anio + 1}`];
  } else if (INSUMOS[Q]) {
    const n = PARTIDA.u - 1;
    titulo = `Lote de insumo ${Q} · ${INSUMOS[Q]}`;
    atras = [`proveedor y remito de compra en FLAMA_MRP › lotes de insumo`, `certificado de calidad del proveedor archivado`];
    adelante = [`<b>${PARTIDA.ops.length} órdenes</b>: ${PARTIDA.ops.map(l => l.op).join(", ")}`, `<b>${n} equipos</b> aptos con este lote (1 rechazo en PH)`, `series ${AA}-${String(PARTIDA.ops[0].desde).padStart(6, "0")} a ${AA}-${String(PARTIDA.ops[PARTIDA.ops.length - 1].hasta).padStart(6, "0")}`,
      `<b>3 distribuidores</b> · <b>41 titulares</b> con datos de contacto (ejemplo)`, `stock en FLAMA: 0 · en distribuidores: 62 (ejemplo)`];
    nota = "Para un retiro preventivo: bloquear estas series, avisar a los titulares y seguir el avance en Desvíos.";
  } else if (D.lotes.some(l => l.op.toUpperCase() === Q || l.op.replace(" ", "").toUpperCase() === Q.replace(" ", ""))) {
    const l = D.lotes.find(l => l.op.toUpperCase() === Q || l.op.replace(" ", "").toUpperCase() === Q.replace(" ", ""));
    titulo = `${l.op} · ${l.modelo} · ${l.cant} u`;
    atras = [`Plan mensual de ${D.mesNombre} ${D.anio} (${l.modelo.startsWith("Carro") ? D.rangos.car : D.rangos.man})`];
    adelante = [`series ${AA}-${String(l.desde).padStart(6, "0")} a ${AA}-${String(l.hasta).padStart(6, "0")}`, l.op === DEMO.op ? `${SERIES.length - 1} aptos · 1 rechazo · despachado en R 0001-00004521` : `estado según avance de planta`];
  } else if (/4521/.test(Q)) {
    titulo = "Remito R 0001-00004521";
    atras = [`pallet <b>SSCC …0457</b> · ${esc(DEMO.op)}`]; adelante = [`<b>${SERIES.length - 1} equipos</b> → Matafuegos Sur`, `chofer AB123CD · ${S.salida ? "en tránsito" : "pendiente"} · ${S.recibido ? "recibido" : "sin confirmar"}`];
  } else return `<div class="aviso av" style="margin-top:12px">No encontré «${esc(q)}». Probá con una serie (${esc(SERIES[0])}), una orden (${esc(DEMO.op)}), un lote de insumo (PO-2603) o el remito 4521.</div>`;
  const ms = performance.now() - t0;
  return `<div style="margin-top:14px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:baseline"><b style="font:700 18px/1.1 var(--f-display);letter-spacing:.04em;text-transform:uppercase">${titulo}</b><span class="nota" style="color:var(--band-ink-2)">respondido en ${nf(ms, 1)} ms · meta ≤ 2 min</span></div>
    <div class="traza"><div class="lado"><h5>← Hacia atrás: de dónde viene</h5><ul class="arbol">${atras.map(x => `<li>${x}</li>`).join("")}</ul></div>
    <div class="lado"><h5>Hacia adelante: dónde está →</h5><ul class="arbol">${adelante.map(x => `<li>${x}</li>`).join("")}</ul></div></div>${nota ? `<div class="aviso in" style="margin-top:12px">${nota}</div>` : ""}`;
}

const TOC = [["1", "objeto", "Objeto y alcance"], ["2", "referencias", "Referencias normativas"], ["3", "definiciones", "Definiciones"], ["4", "responsabilidades", "Responsabilidades"], ["5", "identificacion", "Identificación del equipo"],
  ["6", "registros", "Registros"], ["7", "procedimientos", "Procedimientos"], ["8", "buscar", "Buscar la traza"], ["9", "retiro", "Retiro preventivo"], ["10", "correcciones", "Correcciones"], ["11", "contingencias", "Contingencias"], ["12", "indicadores", "Indicadores"], ["13", "formularios", "Formularios"]];

function vistaManual() {
  const sec = (n, id, t, html) => `<section id="m-${id}"><h2><span>${n}</span>${esc(t)}</h2>${html}</section>`;
  const tabla = (cab, filas, cls = "") => `<div class="tscroll"><table class="tabla ${cls}"><thead><tr>${cab.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${filas.map(f => `<tr>${f.map(c => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  return `<div class="cabeza wrap"><div class="cabeza-in"><div><div class="ceja">Manual de seguimiento y trazabilidad</div><h1>Cómo se sigue cada equipo</h1>
    <p>Quién hace qué, dónde queda escrito y cómo se encuentra cualquier equipo, lote o insumo en menos de dos minutos, desde la chapa hasta la inutilización.</p></div>
    <div class="doc-id">MT-01 · rev. 0 · ${D.mesNombre} ${D.anio}<br>Elaboró: Calidad · Aprobó: Responsable técnico<br>Alcance: matafuegos ABC FLAMA y recargas</div></div></div>
  <div class="manual wrap"><nav class="toc" aria-label="Índice del manual">${TOC.map(([n, id, t]) => `<a href="#manual" data-m="${id}"><span>${n}</span>${esc(t)}</a>`).join("")}</nav>
  <article class="doc">
  ${sec(1, "objeto", "Objeto y alcance", `<p>Este manual fija cómo FLAMA identifica cada matafuego, qué se registra en cada etapa y cómo se reconstruye su historia. Cubre los manuales ABC de 1 a 10 kg, los carros de 25 a 100 kg, los sustitutos y el servicio de recarga. <b>No cubre</b> los equipos revendidos de otras marcas, salvo cuando entran a recarga: ahí se identifican con la etiqueta de servicio.</p>
    <p>La unidad de trazabilidad es <b>la serie</b> (un equipo). La unidad de registro en planta es <b>el lote</b> (lo que entra en un carro) y la unidad del certificado de fabricación es <b>la partida</b> (≥ 100 u, Res. 349/07 art. 21).</p>`)}
  ${sec(2, "referencias", "Referencias normativas", tabla(["Norma", "Para qué se usa acá"], [
    ["<b>IRAM 3517-2</b> 6.2.14, 7.3, 9.4.5, 9.4.13-9.4.16, 9.6, 9.7, 9.10-9.12, anexos E, F y G", "instalación, mantenimiento, sustituto, precinto, etiqueta, registros, marbete, inutilización"],
    ["<b>Res. 349/07</b> (PBA, Dec. 4.992/90) art. 7, 9, 19-29, 32, 33, 43-46 y anexos I-IV", "responsable operativo y técnico, planillas, libro de actas, contraste, tarjetas y estampillas DPS, vida útil, inutilización"],
    ["<b>Res. 32-AGC/15</b> (CABA) anexos I-III", "tarjeta de identificación, SGM y proceso batch"],
    ["<b>DOC-02</b> FLAMA (R1-R9, L1-L5)", "presiones y tolerancias de ensayo y carga"],
    ["<b>Ley 24.240</b> y <b>Ley 25.326</b>", "atención al cliente y datos personales (política AC-01)"],
    ["<b>IRAM-ISO 10002</b>", "tratamiento de reclamos"]]))}
  ${sec(3, "definiciones", "Definiciones", `<dl class="dl" style="grid-template-columns:150px 1fr">${[["Serie", "número único del equipo: año + correlativo (26-001736). Se graba y no se reutiliza."], ["Lote", "equipos de un modelo que viajan juntos en un carro con una hoja de ruta."], ["Partida", "lotes agrupados hasta ≥ 100 u para el certificado de fabricación DPS."], ["OP", "orden de producción de un lote, emitida desde el Plan mensual."], ["Evento", "lo que pasó (qué, cuándo, dónde, quién) con el hash del evento anterior."], ["Custodia", "quién tiene el equipo: FLAMA, transportista, distribuidor o usuario."], ["Ficha", "estado técnico del equipo: rev. 0 de fábrica y rev. n de cada servicio."], ["RD", "registro de desvío: algo que salió distinto de lo previsto, con su causa y acción."], ["Sustituto habilitado", "equipo de FLAMA que reemplaza al del cliente mientras está en servicio."]].map(([a, b]) => `<dt><b>${a}</b></dt><dd>${b}</dd>`).join("")}</dl>`)}
  ${sec(4, "responsabilidades", "Responsabilidades", tabla(["Actividad", "PCP", "Producción", "Calidad", "Resp. técnico", "Recargas / instalador", "Atención"], RACI.map(f => f.map((c, i) => i ? `<b style="color:${{ R: "var(--red)", A: "var(--ink)", C: "var(--blue)", I: "var(--ink-3)" }[c] || "inherit"}">${c}</b>` : c))) + `<p class="nota">R: lo hace · A: lo aprueba · C: se lo consulta · I: se le informa. El responsable técnico y el responsable operativo de taller son los de la Res. 349/07 art. 7 y 8.</p>`)}
  ${sec(5, "identificacion", "Identificación del equipo", tabla(["Elemento", "Dónde", "Lo pone", "Se renueva", "Base"], [
    ["Grabado <b>FLAMA S.A. N° serie año</b> + cuño DPS", "franja de la pollera, lado pared", "G2 · Pannier", "nunca", "Res. 349/07 anexo IV · IRAM 3517-2 anexo F"],
    ["Etiqueta de serie con QR (45 × 25)", "debajo de la franja, lado pared", "etiquetado", "en cada servicio, mismo QR", "IRAM 3517-2 9.4.14"],
    ["Estampilla de fabricación DPS", "junto a la etiqueta del fabricante", "etiquetado", "—", "Res. 349/07 art. 21-23"],
    ["Tarjeta DPS / tarjeta SGM", "colgada del cuello", "instalador o recargador", "en cada servicio", "Res. 349/07 art. 21 · Res. 32-AGC/15"],
    ["Marbete del año", "cuello", "recargador", "anual", "IRAM 3517-2 9.6"],
    ["Precinto numerado", "seguro de la palanca", "fábrica / recargador", "en cada servicio", "IRAM 3517-2 9.4.13"],
    ["Oblea de PH", "cuerpo", "quien hace la PH", "cada 5 años", "Res. 349/07 art. 29 · anexo E"],
    ["Fecha en el tubo de pesca", "tubo de pesca", "recargador", "en cada servicio", "Res. 349/07 art. 28"],
    ["Faja amarilla de sustituto", "base, sin tapar la franja", "recargas", "—", "IRAM 3517-2 9.4.5"]]) +
    `<h3>Lo que se ve hoy en el mercado</h3><p>Relevamiento en planta de clientes: tarjetas con QR propio de cada recargador, obleas y tarjetas oficiales superpuestas. FLAMA suma su QR sin tapar ninguna.</p>
    <div class="fotos-campo">${[["campo_tarjeta", "Tarjeta de recargador con QR y modelo aprobado"], ["campo_qr", "Etiqueta de servicio con QR sobre el cuerpo"], ["campo_oblea", "Oblea de control y tarjeta pegadas al recipiente"]].map(([k, c]) => foto(k) ? `<figure><img src="${foto(k)}" alt="${esc(c)}" loading="lazy"><figcaption>${esc(c)}</figcaption></figure>` : "").join("")}</div>`)}
  ${sec(6, "registros", "Registros", tabla(["Registro", "Soporte", "Quién", "Se guarda"], [
    ["Hoja de ruta F-01", "papel en el carro + foto en la base", "producción · calidad", "vida útil + 6 años (criterio)"],
    ["Planilla de ensayos por partida F-02", "base, visada por el RT", "calidad · RT", "6 años mínimo (IRAM 3517-2 9.4.16)"],
    ["Libro de actas DPS", "libro rubricado; la app arma los asientos", "RT", "según autoridad (Res. 349/07 art. 19)"],
    ["Contraste de manómetros", "base", "calidad", "cada 15 días (art. 20)"],
    ["Calibración del patrón", "certificado", "calidad", "cada 2 años (art. 15 l)"],
    ["Eventos con hash", "base Postgres + copia nocturna en Sheets", "todos", "vida útil + 6 años (criterio)"],
    ["Fichas de servicio F-05", "base + constancia al cliente", "recargas", "6 años mínimo"],
    ["Actas de inutilización F-06", "base + papel firmado", "recargas · RT", "6 años mínimo"],
    ["Reclamos F-08 y desvíos F-07", "base", "atención · calidad", "6 años (criterio)"]]) + `<p>La base de datos con datos de titulares se inscribe en el registro de la Agencia de Acceso a la Información Pública (Ley 25.326 art. 21).</p>`)}
  ${sec(7, "procedimientos", "Procedimientos", PROCS.map(([c, t, q, paso, pasos, reg, ctl]) => `<details class="proc"><summary><b>${c}</b><span>${esc(t)}</span><small>${esc(q)}</small></summary><div>
    <ol>${pasos.map(p => `<li>${esc(p)}</li>`).join("")}</ol><dl class="dl"><dt>Registro</dt><dd>${esc(reg)}</dd><dt>Control</dt><dd>${esc(ctl)}</dd></dl>
    ${paso ? `<button class="btn sm" data-v="recorrido" data-paso="${paso}" style="margin-top:10px">Verlo en el recorrido →</button>` : ""}</div></details>`).join(""))}
  ${sec(8, "buscar", "Buscar la traza", `<p>Cualquier persona autorizada encuentra un equipo, un lote, una orden o un remito desde la PC o el celular. La meta es responder en <b>menos de 2 minutos</b> (criterio) y se prueba con un simulacro por semestre.</p>
    <div class="buscador"><form data-f="traza"><input id="trazaq" value="${esc(S.manual.q || CLI)}" aria-label="Serie, lote, orden o remito" autocomplete="off"><button class="btn pri" type="submit">Buscar</button></form>
    <div class="sug">Probá: ${[CLI, REJ, "PO-2603", DEMO.op, "4521"].map(x => `<button data-a="trazaSug" data-q="${esc(x)}">${esc(x)}</button>`).join("")}</div><div id="trazaRes">${traza(S.manual.q || CLI)}</div></div>`)}
  ${sec(9, "retiro", "Retiro preventivo", `<p>Si un insumo o un lote resulta defectuoso (por ejemplo, una partida de polvo que falla el puffer), calidad busca el lote de insumo y obtiene todas las series afectadas, dónde están y a quién avisar. Se sigue <b>P-12</b>.</p>
    <ol><li>Buscar el lote de insumo (por ejemplo <span class="mono">PO-2603</span>) y descargar la lista de series.</li><li>Bloquear las series: la app no deja etiquetar, despachar ni recargar sin pasar por calidad.</li><li>Avisar a distribuidores y titulares con un texto claro, sin alarmar, con el cambio sin costo.</li><li>Seguir el avance en Desvíos hasta ubicar el 100 %.</li></ol>`)}
  ${sec(10, "correcciones", "Correcciones", `<p>En la base <b>nada se borra ni se pisa</b>. Un error se corrige con un evento nuevo que apunta al anterior, con motivo y firma; la cadena de hashes muestra si alguien tocó un registro viejo.</p><p>En papel, toda enmienda la salva el responsable técnico; si no, se considera dato falso (Res. 349/07 art. 43 y 45).</p>`)}
  ${sec(11, "contingencias", "Contingencias", tabla(["Si pasa esto", "Se hace esto"], [
    ["Se corta internet en planta", "la hoja de ruta sigue en papel; el cierre y el etiquetado se cargan al volver (la PC guarda la cola)"],
    ["El lector no lee el grabado", "se tipea el número; queda marcado como lectura manual y se revisa en el cierre"],
    ["Se pierde la etiqueta QR", "el recargador lee el grabado y reimprime con el mismo QR"],
    ["Grabado ilegible y sin etiqueta", "sin número de serie no hay trazabilidad: se inutiliza (IRAM 3517-2 anexo F)"],
    ["Se cae la base", "se trabaja con la copia nocturna en Sheets; los eventos del día se cargan desde las hojas"],
    ["Falta el contraste del manómetro", "la PH queda bloqueada hasta contrastar (Res. 349/07 art. 20)"]]))}
  ${sec(12, "indicadores", "Indicadores", tabla(["Indicador", "Cálculo", "Meta (criterio)"], [
    ["Rendimiento a la primera", "aptos sin retrabajo / grabados", "≥ 98 %"], ["Traza completa", "series con todos sus eventos / series despachadas", "100 %"], ["Custodia confirmada a tiempo", "recepciones confirmadas ≤ 48 h / despachos", "≥ 95 %"],
    ["Reclamos en plazo", "reclamos respondidos en plazo / reclamos", "≥ 95 %; seguridad 100 %"], ["Tiempo de búsqueda", "simulacro: de la pregunta a la lista de series", "≤ 2 min"], ["Desvíos cerrados", "RD cerrados con acción verificada / RD abiertos hace más de 30 días", "≥ 90 %"]]) + `<p>Se miden en la vista <a href="#desvios" data-v="desvios">Desvíos</a>.</p>`)}
  ${sec(13, "formularios", "Formularios", tabla(["Código", "Formulario", "Dónde se genera"], [["F-01", "Hoja de ruta del lote", "PCP · al emitir la OP"], ["F-02", "Planilla de ensayos por partida (anexo I C)", "calidad · al cerrar"], ["F-03", "Acta de instalación y garantía", "instalador · celular"], ["F-04", "Presupuesto de servicio", "recepción de recargas"], ["F-05", "Ficha y constancia de servicio", "taller de recargas"], ["F-06", "Acta de inutilización (anexo G)", "recargas · RT"], ["F-07", "Registro de desvío", "automático o manual"], ["F-08", "Reclamo", "cliente · QR, mail o teléfono"]]))}
  </article></div>`;
}

Object.assign(ACC, {
  trazaSug(el) { S.manual.q = el.dataset.q; const i = $("#trazaq"); if (i) i.value = S.manual.q; $("#trazaRes").innerHTML = traza(S.manual.q); },
});
FORM.traza = () => { S.manual.q = $("#trazaq").value; $("#trazaRes").innerHTML = traza(S.manual.q); };
