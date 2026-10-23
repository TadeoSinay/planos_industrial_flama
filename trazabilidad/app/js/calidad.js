// ================================================================ calidad: AMFE, plan de control, estados y origen de los datos
// AMFE de proceso (intraplanta) y de campo (extraplanta) con puntajes de 1 a 10 adaptados del manual AIAG FMEA 4.ª ed.
// S y D: criterio del equipo de FLAMA. O: se calcula con los registros del sistema cuando los hay (rechazos, remitos,
// recargas, reclamos, retiros); si no, queda como criterio y lo dice. Plan de control: DOC-02 (R1-R9, L1-L5) y DOC-01.
const O_ESCALA = [[0.1, 10, "1 en 10 o más"], [0.05, 9, "1 en 20"], [0.02, 8, "1 en 50"], [0.01, 7, "1 en 100"], [0.002, 6, "1 en 500"], [0.0005, 5, "1 en 2.000"], [0.0001, 4, "1 en 10.000"], [0.00001, 3, "1 en 100.000"]];
const ocurrencia = p => (O_ESCALA.find(([lim]) => p >= lim) || [0, 2])[1];
const S_ESCALA = [[10, "Afecta la seguridad sin aviso o incumple la ley"], [9, "Afecta la seguridad con aviso (manómetro en rojo, pérdida visible)"], [8, "El equipo pierde su función principal"], [7, "La función principal se degrada (descarga o alcance menor)"], [6, "Pierde una función secundaria (identificación, trazabilidad)"], [5, "Se degrada una función secundaria (protección, aspecto)"], [4, "Defecto de aspecto que nota la mayoría"], [3, "Defecto que nota el cliente atento"], [2, "Defecto que nota un especialista"], [1, "Sin efecto"]];
const D_ESCALA = [[1, "No puede pasar: lo impide el diseño o el sistema"], [2, "El sistema detecta la causa en el puesto y bloquea"], [3, "Ensayo o lectura automática en el puesto, 100 %"], [4, "Ensayo 100 % con instrumento en un puesto posterior"], [5, "Medición del operario con instrumento, 100 %"], [6, "Medición por muestreo"], [7, "Inspección visual 100 %"], [8, "Inspección visual por muestreo"], [9, "Control al azar"], [10, "Sin control"]];
const accionNPR = (s, o, d) => s * o * d >= 100 || (s >= 9 && o >= 4);   // regla de prioridad (criterio)

// ---------------------------------------------------------------- AMFE de proceso: un modo de falla por fila
// o: { causa } toma la tasa de rechazos registrados de esa causa; { n, nota } es criterio
const AMFE_P = [
  { id: "P-01", pto: "Recepción · 2 / C-2", op: "Chapa y corte", modo: "Espesor de chapa bajo el nominal", efecto: "El recipiente no resiste la presión: rotura en servicio", s: 10, causa: "Bobina fuera de especificación", prev: "Certificado de colada en la recepción (R1)", det: "Micrómetro MIC-1 por bobina (R1) y PH 100 % (R3)", d: 4, o: { causa: "Espesor fuera de tolerancia" }, acc: "Medir el espesor también al iniciar cada orden", resp: "Calidad" },
  { id: "P-02", pto: "2 / C-2", op: "Grabado del número", modo: "Número ilegible, repetido o salteado", efecto: "Sin trazabilidad: el equipo no se puede recargar (IRAM 3517-2 anexo F)", s: 9, causa: "Serie tipeada a mano; marcadora mal reglada", prev: "El sistema asigna las series del lote; la marcadora no se tipea", det: "Lector DPM en etiquetado lee el 100 % y compara con el lote", d: 2, o: { n: 2, nota: "prevenido por el sistema" }, acc: "—", resp: "Producción" },
  { id: "P-03", pto: "4-7", op: "Embutido de cúpulas", modo: "Bordón fuera de medida", efecto: "Mal encastre y fuga en la soldadura", s: 7, causa: "Matriz del proveedor gastada", prev: "Recepción de cúpulas 1 cada 50 (RD-064)", det: "Calibre pasa / no pasa en el encastre; PH 100 %", d: 4, o: { n: 4, nota: "1 desvío de proveedor en el año" }, acc: "Pedir al proveedor el control de la matriz", resp: "Compras" },
  { id: "P-04", pto: "8-12 / C-4", op: "Soldadura MAG", modo: "Poro o falta de penetración en el cordón", efecto: "Fuga en PH; rotura en servicio si escapa", s: 10, causa: "Boquilla con salpicaduras; parámetros fuera de la WPS", prev: "WPS ISO 15614-1, soldador ISO 9606-1, limpieza cada 50 cordones (RD-061)", det: "Visual 100 % ISO 5817 C (R2), PH 100 % (R3), rotura por lote (L1)", d: 4, o: { causa: "Fuga en PH" }, acc: "Registrar el soldador por serie para cortar la causa", resp: "Producción" },
  { id: "P-05", pto: "13 / C-8", op: "Prueba hidráulica", modo: "PH a menos presión o menos de 60 s", efecto: "Se libera un recipiente defectuoso", s: 10, causa: "Manómetro sin contrastar; el operario corta antes", prev: "PH bloqueada si el contraste de PH-M1 / PH-M2 supera 15 días (Res. 349/07 art. 20)", det: "Presión y tiempo por serie en la hoja; revisión al cierre", d: 5, o: { n: 2, nota: "bloqueo del sistema" }, acc: "Registrador de presión con salida a la base", resp: "Calidad" },
  { id: "P-06", pto: "14-15 / C-9", op: "Secado", modo: "Humedad en el interior", efecto: "El polvo se apelmaza y el equipo no descarga", s: 10, causa: "Ciclo de horno corto", prev: "Ciclo de horno fijo por modelo", det: "Visual del interior 100 % (R4)", d: 7, o: { n: 3, nota: "criterio" }, acc: "Cámara de inspección interior, como en recarga (IRAM 3517-2 9.8.2)", resp: "Producción" },
  { id: "P-07", pto: "16-19 / C-10", op: "Pintura en polvo", modo: "Película bajo 60 µm o mala adherencia", efecto: "Corrosión prematura; menor vida útil", s: 5, causa: "Pistola mal reglada; pretratamiento agotado", prev: "Control del baño de pretratamiento (DOC-01)", det: "EP-1 por lote (ISO 2808), cuadriculado ISO 2409, MEK por turno", d: 6, o: { causa: "Golpe o pintura" }, acc: "Medir 5 puntos en el primer recipiente de cada turno", resp: "Calidad" },
  { id: "P-08", pto: "20-21 / C-13", op: "Carga de polvo", modo: "Masa fuera de la banda de carga", efecto: "Descarga y alcance menores (por defecto)", s: 7, causa: "Balanza sin cero al cambiar la bolsa; polvo húmedo", prev: "Cero obligatorio en la pantalla (RD-062); recinto HR ≤ 70 %", det: "Pesada 100 % con B-1 / B-2 (R6), carta I y Cpk", d: 3, o: { causa: "Carga fuera de tolerancia" }, acc: "Cero automático de la balanza al cambiar la bolsa", resp: "Calidad" },
  { id: "P-09", pto: "20-21 / C-13", op: "Carga de polvo", modo: "Polvo de otro lote o sin certificado", efecto: "Agente fuera de especificación; traza equivocada", s: 8, causa: "Bolsa sin identificar en el puesto", prev: "Lote anotado en la hoja de ruta; FIFO en el almacén", det: "Certificado IRAM 3569 por lote (L4)", d: 6, o: { n: 3, nota: "criterio" }, acc: "Leer el código del lote en la cargadora", resp: "Almacén" },
  { id: "P-10", pto: "22 / C-13", op: "Presurización", modo: "Presión de N₂ fuera de la zona verde", efecto: "Descarga incompleta; manómetro en rojo en el usuario", s: 9, causa: "Regulador desajustado", prev: "Regulador verificado con el patrón MP-PAT (R7)", det: "Lectura del manómetro del equipo, 100 % (R7)", d: 5, o: { n: 3, nota: "criterio" }, acc: "Verificar el regulador con el patrón al empezar cada turno", resp: "Producción" },
  { id: "P-11", pto: "23 / C-14", op: "Control de pérdidas", modo: "Pérdida por válvula o junta sin detectar", efecto: "Equipo despresurizado en el usuario", s: 9, causa: "Junta tórica fuera de especificación; inmersión corta", prev: "Certificado de válvulas por partida (L5)", det: "Inmersión 100 % (R8) y control de presión a 24 h", d: 4, o: { causa: "Pérdida en válvula" }, acc: "Control de presión a 24 h sobre una muestra de cada lote", resp: "Calidad" },
  { id: "P-12", pto: "24 / C-15", op: "Etiquetado", modo: "Etiqueta o estampilla de otra serie", efecto: "Datos equivocados en campo y en la tarjeta DPS", s: 6, causa: "Etiquetas impresas por lote y pegadas a mano", prev: "Una etiqueta por lectura del grabado", det: "El sistema compara grabado y QR y bloquea rechazos", d: 2, o: { n: 2, nota: "prevenido por el sistema" }, acc: "—", resp: "Producción" },
  { id: "P-13", pto: "25 / C-16", op: "Embalaje", modo: "Golpe al armar o mover el pallet", efecto: "Abolladura o pintura dañada", s: 5, causa: "Pallet sin esquineros (RD-063)", prev: "Esquineros en todos los pallets de manuales", det: "Revisión en la recepción del distribuidor", d: 8, o: { n: 4, nota: "1 desvío de custodia en el año" }, acc: "Esquineros y film en todos los pallets", resp: "Depósito PT" },
];
// ---------------------------------------------------------------- AMFE de campo (logística, uso y servicio)
// o: función que devuelve [casos, base, texto] con los registros del sistema
const AMFE_C = [
  { id: "C-01", etapa: "Transporte", modo: "Equipo golpeado en tránsito", efecto: "Abolladura en la cúpula; recipiente a revisar", s: 7, causa: "Carga sin fajas ni esquineros", prev: "Lista de carga en el despacho (equipos de pie, fajados)", det: "Recepción con foto de daños en la página del remito", d: 5, o: () => [S.desvios.filter(x => x.origen === "Custodia").length, censo().despachados, "desvíos de custodia / equipos despachados"], acc: "Foto de la carga antes de salir", resp: "Depósito PT" },
  { id: "C-02", etapa: "Recepción", modo: "Recepción no confirmada en 48 h", efecto: "La custodia queda abierta: traza incompleta", s: 6, causa: "El distribuidor no lee el QR del remito", prev: "QR del remito y aviso automático a las 48 h", det: "Tablero: remitos sin confirmar", d: 2, o: () => [S.remitos.filter(r => r.estado === "Sin confirmar" || (r.estado === "En tránsito" && dias(r.fecha) > 2)).length, S.remitos.length, "remitos sin confirmar / remitos"], acc: "Que el chofer traiga el remito firmado si no confirma", resp: "Expedición" },
  { id: "C-03", etapa: "Instalación", modo: "Altura o cartel fuera de IRAM 3517-2", efecto: "El usuario no alcanza o no ve el equipo", s: 7, causa: "Instalador sin la regla de alturas", prev: "El formulario no acepta alturas fuera de 6.2.14 y 7.3", det: "Control periódico trimestral (IRAM 3517-2 8.2)", d: 2, o: () => { const xs = instalados(sumar(HOY, -365)); return [xs.filter(e => e.inst.alt > 1.5 || e.inst.cartel < 2 || e.inst.cartel > 2.5).length, xs.length, "instalaciones fuera de rango / instalaciones"]; }, acc: "—", resp: "Instaladores" },
  { id: "C-04", etapa: "Uso", modo: "Mantenimiento anual vencido", efecto: "El equipo puede no funcionar en un incendio", s: 10, causa: "El usuario no recibe el aviso", prev: "Aviso 30 días antes desde el QR (criterio)", det: "Tablero: vencimientos de los próximos 12 meses", d: 3, o: () => [censo().mantVencido, censo().mercado, "equipos con mantenimiento vencido / en el mercado"], acc: "Aviso al usuario y al distribuidor 30 días antes", resp: "Atención" },
  { id: "C-05", etapa: "Uso", modo: "Pérdida de presión en el usuario", efecto: "Manómetro en rojo: el equipo no sirve hasta recargarlo", s: 9, causa: "Junta de la válvula; golpe", prev: "Control de pérdidas en fábrica (R8)", det: "Control periódico: manómetro en zona verde (IRAM 3517-2 8.2)", d: 5, o: () => [S.reclamos.filter(x => /presión|zona roja/i.test(x.texto)).length, censo().mercado, "reclamos por presión / equipos en el mercado"], acc: "Aviso trimestral desde el QR para el control periódico", resp: "Calidad" },
  { id: "C-06", etapa: "Recarga", modo: "Polvo bajo de peso o apelmazado", efecto: "Descarga incompleta", s: 8, causa: "Humedad o vibración durante el uso", prev: "Cambio total del polvo (Res. 349/07 art. 33)", det: "Pesada y revisión del polvo en la recarga", d: 3, o: () => { const abc = S.recargas.filter(r => r.agente === "ABC"); return [abc.filter(r => r.polvoBajo).length, abc.length, "recargas ABC con polvo bajo de peso / recargas ABC"]; }, acc: "Indicar en el QR que no se guarde en lugares húmedos", resp: "Recargas" },
  { id: "C-07", etapa: "Recarga", modo: "Recipiente no apto (corrosión, golpe, soldadura) que entra a recarga", efecto: "Rotura si se recarga y vuelve al mercado", s: 10, causa: "Ambiente corrosivo; golpe", prev: "Criterios de inutilización en la OS (IRAM 3517-2 9.7.1.3)", det: "Visual y PH en la recarga; el estado Inutilizado bloquea la etiqueta", d: 3, o: () => [S.recargas.filter(r => r.inutil).length, S.recargas.length, "OS para inutilizar / OS abiertas"], acc: "Foto obligatoria del recipiente al recibirlo", resp: "Recargas" },
  { id: "C-08", etapa: "Recarga", modo: "PH vencida sin detectar", efecto: "Recipiente sin reensayar en servicio", s: 9, causa: "Ficha incompleta", prev: "El sistema calcula el vencimiento de PH por serie (anexo E)", det: "Bloqueo al abrir la OS", d: 2, o: () => [0, S.recargas.length, "OS con PH vencida sin hacer"], acc: "—", resp: "Recargas" },
  { id: "C-09", etapa: "Atención", modo: "Reclamo de seguridad fuera de plazo", efecto: "El usuario sigue con un equipo dudoso", s: 8, causa: "Sin guardia de fin de semana", prev: "Guardia para reclamos de seguridad (RD-065)", det: "Tablero: reclamos en plazo", d: 2, o: () => [S.reclamos.filter(vencido).length, S.reclamos.length, "reclamos fuera de plazo / reclamos"], acc: "Medir la guardia: reclamos de seguridad respondidos en 24 h", resp: "Atención" },
  { id: "C-10", etapa: "Retiro", modo: "Equipo afectado que no se ubica", efecto: "Queda en uso un equipo con un insumo defectuoso", s: 9, causa: "Venta e instalación sin registrar", prev: "Garantía activada al leer el QR en la venta (criterio)", det: "Avance del retiro por lote", d: 4, o: () => { const x = S.retiros[0]; if (!x) return [0, 1, "sin retiros"]; const a = afectados(x.lote).length; return [Math.round(a * (1 - x.ubicados)), a, `equipos sin ubicar del ${x.id}`]; }, acc: "Pedir la lectura del QR en cada venta del distribuidor", resp: "Calidad" },
  { id: "C-11", etapa: "Identificación", modo: "Etiqueta QR perdida o ilegible", efecto: "Se demora la identificación del equipo", s: 4, causa: "Intemperie; limpieza con solventes", prev: "Grabado en el cuerpo como respaldo", det: "Lector del grabado en recarga", d: 3, o: () => [null, null, "criterio: 3"], acc: "—", resp: "Recargas" },
  { id: "C-12", etapa: "Uso", modo: "Equipo con vida útil vencida en uso", efecto: "Recipiente envejecido en servicio", s: 10, causa: "El usuario no conoce la fecha", prev: "La fecha de fabricación está grabada y en el QR", det: "El sistema bloquea la recarga a los 20 años (Res. 349/07 art. 26)", d: 2, o: () => [0, censo().mercado, "equipos con vida útil vencida / en el mercado"], acc: "—", resp: "Recargas" },
];

// ---------------------------------------------------------------- censo del mercado (se recalcula cuando cambian los eventos)
let CENSO = null;
function censo() {
  const k = S.eventos.length + "|" + Object.keys(S.inst).length + "|" + Object.keys(S.bajas).length;
  if (CENSO && CENSO.k === k) return CENSO;
  const c = { k, est: {}, mercado: 0, despachados: 0, mantVencido: 0, phVencido: 0 };
  for (let n = 1; n <= maxSerie(); n++) {
    const e = equipo(n); c.est[e.estado] = (c.est[e.estado] || 0) + 1;
    if (e.remito) c.despachados++;
    if (e.estado === "Instalado" || e.estado === "En distribuidor") { c.mercado++; if (e.mant && new Date(e.mant) < HOY) c.mantVencido++; if (e.phVence && new Date(e.phVence) < HOY) c.phVencido++; }
  }
  return (CENSO = c);
}
// tasa de rechazos por causa: lotes cerrados del año
function tasasRechazo() {
  const cerr = S.ordenes.filter(o => o.etapa >= E["Para etiquetar"]), u = cerr.reduce((a, o) => a + o.cant, 0), por = {};
  cerr.forEach(o => o.rech.forEach(x => { por[x.causa] = (por[x.causa] || 0) + 1; }));
  return { u, por };
}
function filaAMFE(f, campo) {
  let O, base;
  if (campo) { const [x, n, txt] = f.o(); if (x == null) { O = 3; base = txt; } else { O = n ? ocurrencia(x / n) : 2; base = `${n0(x)} de ${n0(n)} · ${txt}`; } }
  else if (f.o.causa) { const t = tasasRechazo(), x = t.por[f.o.causa] || 0; O = ocurrencia(x / t.u); base = `${n0(x)} de ${n0(t.u)} · ${f.o.causa.toLowerCase()}`; }
  else { O = f.o.n; base = f.o.nota === "criterio" ? "criterio" : "criterio: " + f.o.nota; }
  return Object.assign({}, f, { O, base, npr: f.s * O * f.d, accion: accionNPR(f.s, O, f.d) });
}
const amfe = campo => (campo ? AMFE_C : AMFE_P).map(f => filaAMFE(f, campo)).sort((a, b) => b.npr - a.npr);
const nprPill = f => pill(String(f.npr), f.accion ? "no" : f.npr >= 60 ? "av" : "ok");

// ---------------------------------------------------------------- plan de control (DOC-02 y DOC-01)
const medOk = id => { const m = S.medicion.find(x => x.id === id); return !m ? "" : vencida(m) ? pill(`${id} vencido`, "no") : pill(`${id} vigente`, "ok"); };
const lotesMes = () => S.ordenes.filter(o => o.mes === D.mes && o.etapa >= E["Para etiquetar"]);
const PLAN = [
  { c: "R1", pto: "Recepción · 2", car: "Espesor de chapa", esp: "≥ nominal del plano FL_REC (0,9 a 4,75 mm)", met: "Certificado de colada + micrómetro", inst: ["MIC-1"], mue: "por bobina", reg: "Ingreso de MP en Insumos: colada y espesor medido", rea: "Bobina retenida, aviso a compras y RD", vivo: () => `${tasasRechazo().por["Espesor fuera de tolerancia"] || 0} rechazos en el año` },
  { c: "R2", pto: "8-12 / C-4", car: "Soldaduras", esp: "ISO 5817 nivel C: sin fisuras, poros abiertos ni falta de penetración", met: "Visual", inst: [], mue: "100 %", reg: "Firma del soldador en la hoja de ruta", rea: "Reparar según la WPS o rechazar; RD si se repite en el turno (criterio)", vivo: () => `${S.ordenes.filter(o => o.mes === D.mes && o.etapa > E["Armado y soldadura"]).length} lotes firmados en el mes` },
  { c: "R3", pto: "13 / C-8", car: "Prueba hidráulica", esp: "3,5 MPa manuales · 4,0 MPa carros · 1 min, sin caída ni deformación", met: "Banco PH con manómetro contrastado", inst: ["PH-M1", "PH-M2"], mue: "100 %", reg: "Tilde ✓ / ✗ por serie en la hoja; rechazos al cierre", rea: "La serie sale del lote con su número; 2 seguidas: revisar soldadura (criterio)", vivo: () => { const l = lotesMes(), u = l.reduce((a, o) => a + o.cant, 0), x = l.reduce((a, o) => a + o.rech.filter(r => r.ensayo === "PH").length, 0); return `${n0(u)} ensayadas · ${x} fallas (${pct(x, u)})`; } },
  { c: "R4", pto: "14-15 / C-9", car: "Interior seco", esp: "Sin agua ni condensación (IRAM 3517-2 4.3.3.4)", met: "Visual", inst: [], mue: "100 %", reg: "Firma en la hoja de ruta", rea: "Volver al horno", vivo: () => `${S.ordenes.filter(o => o.mes === D.mes && o.etapa > E["PH y pintura"]).length} lotes en el mes` },
  { c: "R5", pto: "16-19 / C-10", car: "Pintura: espesor, adherencia y curado", esp: "60 a 100 µm, ningún punto < 80 % · ISO 2409 clase 0 ó 1 · MEK sin ablandamiento", met: "Medidor de película (ISO 2808), cuadriculado, frote MEK", inst: ["EP-1"], mue: "por lote; MEK por turno", reg: "5 lecturas y clase de adherencia al cerrar el lote", rea: "Repintar el lote", vivo: () => { const l = lotesMes().map(ensayosLote).filter(Boolean), mn = l.length ? Math.min(...l.flatMap(x => x.pintura.lect)) : null; return l.length ? `${l.length} lotes · mínimo ${nf(mn, 0)} µm` : "sin lotes"; } },
  { c: "R6", pto: "20-21 / C-13", car: "Masa de carga", esp: "1 y 2,5 kg: 0 / +100 g · 5 y 10 kg: 0 / +300 g · rodantes +3 %", met: "Balanza calibrada", inst: ["B-1", "B-2"], mue: "100 %", reg: "Archivo de pesadas de la balanza o valor en la hoja", rea: "Corregir la carga; carta fuera de control: RD", vivo: () => { const xs = cpkModelos().filter(c => c.n >= 5); return xs.length ? `Cpk mínimo ${nf(Math.min(...xs.map(c => c.cpk)), 2)}` : "sin datos"; } },
  { c: "R7", pto: "22 / C-13", car: "Presión de servicio", esp: "N₂ 1,4 MPa a 20 °C; aguja en zona verde", met: "Manómetro del equipo verificado con el patrón", inst: ["MP-PAT"], mue: "100 %", reg: "Tilde en la hoja de ruta", rea: "Ajustar el regulador y repetir", vivo: () => `${n0(lotesMes().filter(o => !o.cilindro).reduce((a, o) => a + aptos(o), 0))} equipos en el mes` },
  { c: "R8", pto: "23 / C-14", car: "Estanqueidad", esp: "Sin burbujas en inmersión; presión estable a las 24 h (criterio)", met: "Cuba de inmersión", inst: [], mue: "100 %", reg: "Tilde ✓ / ✗ por serie", rea: "Cambiar la junta o la válvula y repetir", vivo: () => { const k = lotesMes().reduce((a, o) => a + o.rech.filter(r => r.ensayo === "Pérd.").length, 0); return `${k} ${k === 1 ? "pérdida" : "pérdidas"} en el mes`; } },
  { c: "R9", pto: "24 / C-15", car: "Pesada final y marcado", esp: "Masa en tolerancia; etiqueta, serie, sello IRAM, fecha, precinto y seguro", met: "Lector del grabado + impresora", inst: [], mue: "100 %", reg: "Lectura → evento IDENTIFICADO", rea: "Rechazo u otro lote: la pantalla bloquea", vivo: () => `${n0(S.ordenes.filter(o => o.mes === D.mes).reduce((a, o) => a + (o.etapa >= E["Depósito PT"] ? aptos(o) : o.etiquetados), 0))} identificados en el mes` },
  { c: "L1", pto: "Laboratorio", car: "Rotura (destructivo)", esp: "≥ 2 × Pe; rotura dúctil, sin fragmentar, fuera de la costura del cuello", met: "Presurizar con agua hasta romper", inst: ["MP-PAT"], mue: "1 por lote o turno de soldadura", reg: "Planilla F-02 por partida, visada por el RT", rea: "Lote retenido; RD y reensayo de 2 muestras (criterio)", vivo: () => { const l = lotesMes().map(o => [o, ensayosLote(o)]); return `${l.length} lotes · ${l.filter(([, x]) => x.rotura.p >= x.rotura.min).length} aprobados`; } },
  { c: "L2", pto: "Laboratorio", car: "Expansión volumétrica", esp: "Permanente ≤ 10 % de la total", met: "Camisa de agua a Pe", inst: ["MP-PAT"], mue: "1 por lote", reg: "Planilla F-02", rea: "Lote retenido", vivo: () => { const l = lotesMes().map(ensayosLote); return l.length ? `máximo ${nf(Math.max(...l.map(x => x.expansion.pct)), 1)} %` : "—"; } },
  { c: "L3", pto: "Laboratorio", car: "Descarga y alcance", esp: "Manuales ≥ 8 s y ≥ 85 %; 25 kg ≥ 10 s; 50 / 70 kg ≥ 15 s; 100 kg ≥ 30 s; alcance de catálogo", met: "Banco de descarga", inst: [], mue: "1 por lote", reg: "Planilla F-02", rea: "Lote retenido; revisar carga y válvula", vivo: () => { const l = lotesMes().filter(o => !o.cilindro).map(ensayosLote); return `${l.length} lotes · mínimo ${l.length ? nf(Math.min(...l.map(x => x.descarga.pct)), 0) : "—"} % descargado`; } },
  { c: "L4", pto: "Recepción", car: "Polvo ABC", esp: "Certificado IRAM 3569 del lote; humedad y fluidez", met: "Revisión del certificado", inst: [], mue: "por lote de polvo", reg: "Ingreso de MP: lote y certificado", rea: "Lote de polvo retenido", vivo: () => `${new Set(lotesMes().filter(o => o.insumos.polvo).map(o => o.insumos.polvo)).size} lotes de polvo en uso` },
  { c: "L5", pto: "Recepción", car: "Manómetros y válvulas", esp: "Certificado IRAM 3533; válvula probada a Pe", met: "Revisión del certificado + prueba", inst: ["MP-PAT"], mue: "por partida", reg: "Ingreso de MP: partida y certificado", rea: "Partida retenida", vivo: () => `${new Set(lotesMes().filter(o => o.insumos.valvula).map(o => o.insumos.valvula)).size} partidas de válvulas en uso` },
];
function cpkModelos() {
  return D.modelos.map(m => { const v = []; S.ordenes.filter(o => !o.cilindro && o.mes >= D.mes - 1 && o.etapa >= E["Para etiquetar"] && modeloBOM(o.modelo) === m).forEach(o => { for (let n = o.desde; n <= o.hasta; n++) if (!o.rech.some(x => x.n === n)) v.push(masaCarga(n, o)); });
    const st = stats(v); return st ? { m, n: st.n, cpk: cpk(st, m.min, m.max) } : null; }).filter(Boolean);
}

// ---------------------------------------------------------------- estados: qué dispara cada uno y cómo se registra
const ESTADOS_LOTE = [
  ["Planificada", "El Plan mensual del Excel de Aprovechamiento trae la orden", "PCP · oficina", "Automático al leer el Excel; series reservadas", "PCP la libera con la hoja de ruta impresa"],
  ["Corte y grabado", "PCP libera la orden", "Puesto 2 / C-2", "Hoja de ruta: firma, lote de chapa y colada", "Planchuelas grabadas con las series del lote"],
  ["Armado y soldadura", "Termina el corte", "Puestos 4-12 / C-4, C-6", "Firmas, lotes de cúpulas y alambre; rechazos con su número", "Soldaduras con visual R2"],
  ["PH y pintura", "Termina la soldadura", "Puestos 13-19 / C-8 a C-10", "Tilde ✓ / ✗ de PH por serie; lote de pintura", "PH (R3), secado (R4) y pintura (R5)"],
  ["Carga y armado final", "Termina la pintura", "Puestos 20-23 / C-12 a C-14", "Lotes de polvo y válvulas; pesadas; ✓ / ✗ de pérdidas", "Carga (R6), N₂ (R7) y pérdidas (R8)"],
  ["Para cerrar", "Termina el control de pérdidas", "Calidad", "Foto de la hoja firmada; rechazos marcados en la lista; ensayos de lote L1-L5", "Visado del RT; bloqueado si el contraste de PH venció o hay un desvío abierto"],
  ["Para etiquetar", "Calidad cierra y el RT visa", "Puesto 24 / C-15", "Lector del grabado: evento IDENTIFICADO por serie", "Todas las series aptas identificadas"],
  ["Depósito PT", "Se arma y lee el pallet", "Puesto 25 / C-16 · depósito", "Lectura de cajas → etiqueta SSCC", "Remito con el anexo de series"],
  ["Despachada", "Sale el remito", "Depósito PT · chofer", "QR del remito leído por el chofer", "Sigue en extraplanta"],
];
const ESTADOS_EQ = [
  ["En producción", "La serie está en un lote abierto", "Planta", "Hoja de ruta del lote"],
  ["Para etiquetar", "El lote se cerró y visó", "Puesto 24 / C-15", "Visado de calidad"],
  ["En depósito PT", "Se leyó el grabado y se identificó", "Depósito PT", "Lector DPM: IDENTIFICADO; pallet SSCC"],
  ["En tránsito", "El chofer leyó el QR del remito", "Transportista", "Celular del chofer (página web, sin app)"],
  ["En distribuidor", "El distribuidor confirmó la recepción", "Distribuidor", "Página del remito: confirma, faltantes y daños con foto"],
  ["Instalado", "El instalador registró el equipo", "Usuario", "Formulario de instalación: ubicación, alturas, tarjeta DPS o SGM"],
  ["Rechazado", "Falló un ensayo de rutina", "Planta", "Marca en la lista del lote al cerrar; sale con su número"],
  ["Inutilizado", "No aprueba la revisión en recarga o cumplió 20 años", "Recargas", "OS con motivo (IRAM 3517-2 9.7.1.3); baja con acta"],
];
const COL_ETAPA = ["var(--ink-3)", "var(--blue)", "var(--blue)", "var(--blue)", "var(--blue)", "var(--yellow)", "var(--yellow)", "var(--violet)", "var(--green)"];
const OPA_ETAPA = [0.35, 0.35, 0.55, 0.75, 0.95, 0.6, 1, 0.85, 1];
const horas = (a, b) => (new Date(b) - new Date(a)) / 36e5;
const durTxt = h => h == null ? "—" : h < 24 ? nf(h, 1) + " h" : nf(h / 24, 1) + " d";
function tiempoMedio(e) {
  const xs = S.ordenes.filter(o => o.mes >= D.mes - 1 && o.etapa > e).map(o => estadios(o)[e]).filter(x => x && x.desde && x.hasta).map(x => horas(x.desde, x.hasta));
  return xs.length ? xs.reduce((a, x) => a + x, 0) / xs.length : null;
}
// Gantt de los lotes del mes: un renglón por orden, un tramo por estadio
function ganttLotes(ords) {
  const ini = new Date(D.anio, D.mes - 1, 1), fin = new Date(D.anio, D.mes, 1), ahora = new Date(+HOY + 17 * 36e5);
  const W = 1100, l = 112, rr = 8, t = 20, fila = 17, H = t + ords.length * fila + 22, X = d => l + (W - l - rr) * Math.max(0, Math.min(1, (new Date(d) - ini) / (fin - ini)));
  const dias_ = (fin - ini) / 864e5, ticks = Array.from({ length: dias_ }, (_, i) => i + 1).filter(d => d === 1 || d % 5 === 0);
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Estadios de los lotes del mes">
    ${ticks.map(d => { const x = X(new Date(D.anio, D.mes - 1, d)); return `<line x1="${x}" x2="${x}" y1="${t - 4}" y2="${H - 18}" stroke="var(--line)"/><text x="${x}" y="${t - 8}" text-anchor="middle">${d}</text>`; }).join("")}
    <line x1="${X(ahora)}" x2="${X(ahora)}" y1="${t - 4}" y2="${H - 18}" stroke="var(--red)" stroke-dasharray="4 3"/><text x="${X(ahora) + 3}" y="${H - 6}" fill="var(--red)">hoy</text>
    ${ords.map((o, i) => { const y = t + i * fila, es = estadios(o);
      return `<text x="4" y="${y + 11}" style="font-family:var(--f-mono)">${esc(o.op.slice(-5))} ${esc(kgDe(o.modelo))}${o.carro ? " C" : ""}</text>` + es.filter(x => x.e > 0 && x.desde).map(x => {
        if (x.e === E["Despachada"]) return `<path d="M${X(x.desde)} ${y + 2}l5 5.5-5 5.5-5-5.5z" fill="var(--green)"><title>${o.op} · despachada ${fecha(x.desde)}</title></path>`;
        const a = X(x.desde), b = X(x.hasta || ahora); return `<rect x="${a}" y="${y + 2}" width="${Math.max(2, b - a)}" height="11" rx="2" fill="${COL_ETAPA[x.e]}" opacity="${OPA_ETAPA[x.e]}" ${x.hasta ? "" : 'stroke="var(--ink)" stroke-width="1"'}><title>${o.op} · ${x.nombre} · ${durTxt(horas(x.desde, x.hasta || ahora))}${x.hasta ? "" : " (en curso)"}</title></rect>`; }).join("");
    }).join("")}
    </svg><div class="leyenda">${ETAPAS.slice(1).map((e, i) => `<span><i style="background:${COL_ETAPA[i + 1]};opacity:${OPA_ETAPA[i + 1]}"></i>${esc(e)}</span>`).join("")}</div>`;
}

// ---------------------------------------------------------------- origen de los datos
// [dato, dónde nace, instrumento, quién, cuándo, cómo llega al sistema, validación, alimenta]
const ORIGEN_INTRA = [
  ["Orden y series", "Plan mensual (Aprovechamiento_Manuales y _Carros)", "Excel", "PCP", "al planificar la semana", "El sistema lee el Excel y reserva las series del año", "series únicas, sin huecos", "Órdenes, estados, Gantt"],
  ["Lote de cada insumo", "Puestos 2 a 22", "Etiqueta del lote del proveedor", "Operario", "al empezar cada insumo", "Anotado en la hoja de ruta → foto al cierre → calidad lo carga", "el lote tiene que existir en Insumos", "Traza, lotes en uso, retiros"],
  ["Firma, fecha y hora de cada puesto", "Todos los puestos", "Hoja de ruta F-01", "Operario", "al terminar el lote en el puesto", "Papel en el carro → foto al cierre", "sin firmas el lote no cierra", "Hoja de ruta, estadios, ciclo"],
  ["Espesor de chapa", "Recepción y puesto 2", "Micrómetro MIC-1", "Calidad", "por bobina", "Formulario de ingreso de MP", "≥ nominal del plano", "R1, AMFE P-01"],
  ["Resultado de PH por serie", "Puesto 13 / C-8", "Banco PH + PH-M1 / PH-M2", "Operario de PH", "100 %", "Tilde ✓ / ✗ en la lista de series; los ✗ se marcan al cierre", "PH bloqueada si el contraste venció", "FPY, carta p, AMFE P-04"],
  ["Espesor y adherencia de pintura", "Puestos 16-19 / C-10", "EP-1, cuadriculado", "Calidad", "por lote", "Cierre del lote: 5 lecturas y clase", "60-100 µm; clase 0-1", "R5, AMFE P-07"],
  ["Masa de carga por serie", "Puestos 20-21 / C-13", "Balanza B-1 / B-2", "Operario de carga", "100 %", "Archivo de pesadas de la balanza subido al cierre, o valor anotado (criterio: según la balanza que se compre)", "banda del BOM", "Carta I, Cpk, AMFE P-08"],
  ["Presión de N₂ y pérdidas", "Puestos 22-23 / C-13, C-14", "Manómetro del equipo, cuba", "Operario", "100 %", "Tilde ✓ / ✗ en la hoja", "zona verde; sin burbujas", "FPY, AMFE P-10 y P-11"],
  ["Rechazos (serie y causa)", "Cualquier puesto", "Número grabado", "Operario → calidad", "cuando pasa", "Anotado en la hoja; calidad lo marca en la lista al cerrar", "la serie es del lote", "Pareto, FPY, O del AMFE"],
  ["Ensayos de lote L1-L5", "Laboratorio", "Rotura, camisa de agua, banco de descarga, certificados", "Calidad", "por lote o partida", "Planilla F-02 por partida, visada por el RT", "criterios DOC-02", "Plan de control, visado"],
  ["Contraste y calibración", "Laboratorio", "Patrón MP-PAT", "Calidad", "PH cada 15 días", "Formulario de equipos de medición", "vencido → bloqueo", "Equipos de medición, retención"],
  ["Identificación", "Puesto 24 / C-15", "Lector DPM USB + impresora", "Operario", "100 %", "Lectura del grabado → evento IDENTIFICADO", "rechazo u otro lote: bloqueado", "Identificados, estampillas"],
  ["Pallet", "Puesto 25 / C-16", "Mismo lector", "Operario", "por pallet", "Lectura de las cajas → etiqueta SSCC", "caja sin leer: no cierra", "Depósito PT"],
];
const ORIGEN_EXTRA = [
  ["Remito y anexo de series", "Depósito PT", "Sistema", "Depósito PT", "al despachar", "Automático desde los pallets leídos", "solo series en depósito PT", "Expedición, custodia"],
  ["Salida", "Camión", "QR del remito en el celular", "Chofer", "al salir", "Lectura del QR (página web, sin app) → EN TRÁNSITO", "patente y COT", "En tránsito, lead time"],
  ["Recepción", "Distribuidor", "QR del remito", "Distribuidor", "al recibir", "Confirma; marca faltantes o daños con foto", "más de 48 h sin confirmar: aviso", "Sin confirmar, AMFE C-02"],
  ["Venta", "Distribuidor", "QR del equipo", "Distribuidor", "al vender", "Lectura → a quién se vendió", "—", "Custodia, retiros"],
  ["Instalación", "Usuario", "QR + foto", "Instalador", "al instalar", "Formulario: ubicación, alturas, cartel, tarjeta DPS o SGM", "IRAM 3517-2 6.2.14 y 7.3", "Instalaciones, jurisdicciones"],
  ["Control periódico", "Usuario", "QR del equipo", "Usuario o recargador", "trimestral (IRAM 3517-2 8.2)", "Registro en la página del QR (criterio)", "—", "AMFE C-04 y C-05"],
  ["Consulta y reclamo", "Usuario", "QR, mail o teléfono", "Usuario → atención", "cuando quiere", "Página pública /m/serie; formulario → acuse con número y plazo", "sin datos del dueño en la página", "Reclamos en plazo"],
  ["Orden de servicio", "Planta de recargas", "Lector del grabado + tablet", "Recepción de recargas", "al recibir", "OS con fabricante, número y año", "PH vencida o 20 años: bloqueo", "Recargas, AMFE C-07 y C-08"],
  ["Ensayos de recarga", "Taller de recargas", "Banco PH, balanza", "Técnico", "por equipo", "Resultado en la OS (DOC-03)", "criterios IRAM 3517-2", "AMFE C-06, inutilizados"],
  ["Tarjetas oficiales", "PCP", "Libro de actas DPS · archivo SGM", "PCP", "por partida / mensual", "Reporte generado por el sistema", "Res. 349/07 · Res. 32-AGC/15", "Jurisdicciones"],
  ["Retiro preventivo", "Calidad", "Traza del lote", "Calidad", "al abrirlo", "Equipos ubicados por QR o llamado", "—", "Retiros, AMFE C-10"],
];
// diagrama del flujo de datos: fuentes → captura → base → salidas
function flujoDatos(extra) {
  const fu = extra ? [["Remito con QR", "depósito PT"], ["Celular del chofer", "salida"], ["Página del remito", "distribuidor"], ["QR del equipo", "venta, instalación, control"], ["OS de recarga", "lector + tablet"], ["Reclamo", "QR · mail · teléfono"]]
    : [["Plan mensual", "Excel de Aprovechamiento"], ["Hoja de ruta F-01", "papel + foto al cierre"], ["Balanza B-1 / B-2", "archivo de pesadas"], ["Banco PH", "✓ / ✗ por serie"], ["Laboratorio", "planilla F-02 · L1-L5"], ["Lector DPM", "etiquetado y pallet"]];
  const sal = extra ? ["Custodia y estados del equipo", "Tablero extraplanta", "AMFE de campo", "Tarjetas DPS / SGM"] : ["Estadios del lote", "Tablero intraplanta", "AMFE y plan de control", "Libro de actas DPS"];
  const W = 1100, H = 30 + fu.length * 46, bw = 190, bx = W / 2 - bw / 2, fw = 250, sx = W - 290;
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Flujo de los datos">
    <defs><marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--ink-3)"/></marker></defs>
    ${fu.map(([a, b], i) => { const y = 15 + i * 46; return `<rect x="8" y="${y}" width="${fw}" height="36" rx="7" fill="var(--surface-2)" stroke="var(--line)"/><text x="20" y="${y + 15}" class="t-ink" style="font-weight:600">${esc(a)}</text><text x="20" y="${y + 29}">${esc(b)}</text><path d="M${fw + 8} ${y + 18}C${fw + 120} ${y + 18} ${bx - 110} ${H / 2} ${bx - 4} ${H / 2}" fill="none" stroke="var(--ink-3)" marker-end="url(#fl)"/>`; }).join("")}
    <rect x="${bx}" y="${H / 2 - 40}" width="${bw}" height="80" rx="10" fill="var(--blue)" fill-opacity=".12" stroke="var(--blue)"/><text x="${W / 2}" y="${H / 2 - 12}" text-anchor="middle" class="t-ink" style="font-weight:700">Base de datos</text><text x="${W / 2}" y="${H / 2 + 6}" text-anchor="middle">eventos con hash</text><text x="${W / 2}" y="${H / 2 + 22}" text-anchor="middle">SHA-256 encadenado</text>
    ${sal.map((x, i) => { const y = H / 2 - 92 + i * 48; return `<path d="M${bx + bw} ${H / 2}C${bx + bw + 90} ${H / 2} ${sx - 100} ${y + 18} ${sx - 4} ${y + 18}" fill="none" stroke="var(--ink-3)" marker-end="url(#fl)"/><rect x="${sx}" y="${y}" width="282" height="36" rx="7" fill="var(--surface)" stroke="var(--line)"/><text x="${sx + 14}" y="${y + 22}" class="t-ink" style="font-weight:600">${esc(x)}</text>`; }).join("")}</svg>`;
}
// conteos del mes por fuente: cuántos registros llegaron por cada vía
function registrosMes(extra) {
  const om = S.ordenes.filter(o => o.mes === D.mes), cerr = om.filter(o => o.etapa >= E["Para etiquetar"]), rm = S.remitos.filter(r => new Date(r.fecha).getMonth() + 1 === D.mes);
  if (!extra) return [["Hojas de ruta abiertas", om.filter(o => o.etapa > 0 && o.etapa < E["Para etiquetar"]).length], ["Hojas cerradas (foto)", cerr.length], ["Resultados de PH", cerr.reduce((a, o) => a + o.cant, 0)],
    ["Pesadas de carga", cerr.filter(o => !o.cilindro).reduce((a, o) => a + aptos(o), 0)], ["Planillas F-02 (L1-L5)", cerr.length], ["Lecturas del lector DPM", om.reduce((a, o) => a + (o.etapa >= E["Depósito PT"] ? aptos(o) : o.etiquetados), 0)]];
  return [["Remitos emitidos", rm.length], ["Salidas leídas por el chofer", rm.filter(r => r.estado !== "Preparado").length], ["Recepciones confirmadas", rm.filter(r => r.recibido).length],
    ["Instalaciones registradas", instalados(new Date(D.anio, D.mes - 1, 1)).length], ["Órdenes de servicio", S.recargas.length], ["Reclamos recibidos", S.reclamos.filter(x => new Date(x.fecha).getMonth() + 1 === D.mes).length]];
}
// tabla compacta para el tablero: de dónde sale cada indicador
const FUENTE_INTRA = [["Producción a depósito PT", "lecturas del lector en el pallet", "lector DPM", "en el momento"], ["WIP y estadios", "firmas de la hoja de ruta", "foto al cierre", "al cerrar cada lote"], ["FPY, fallas en PH, Pareto", "✓ / ✗ y rechazos de la hoja", "banco PH, cuba, visual", "al cerrar cada lote"],
  ["Cpk y carta I", "pesadas por serie", "balanza B-1 / B-2", "al cerrar cada lote"], ["Carta p", "fallas de PH por lote", "banco PH", "al cerrar cada lote"], ["Lotes de insumo", "lotes anotados por puesto", "hoja de ruta", "al cerrar cada lote"], ["Equipos de medición", "contrastes y calibraciones", "patrón MP-PAT", "al registrarlos"], ["AMFE (O)", "rechazos del año por causa", "base de datos", "en el momento"]];
const FUENTE_EXTRA = [["En tránsito", "lectura del QR del remito", "celular del chofer", "en el momento"], ["Sin confirmar", "falta de lectura en 48 h", "página del remito", "en el momento"], ["Lead times", "fechas de salida, recepción e instalación", "QR del remito y del equipo", "en el momento"], ["Custodia", "último traspaso leído", "QR", "en el momento"],
  ["Jurisdicciones", "tarjeta cargada al instalar", "formulario de instalación", "al instalar"], ["Vencimientos", "fecha de fabricación + 1 año / 5 años", "cálculo del sistema", "diario"], ["Recargas", "órdenes de servicio", "lector + tablet de recargas", "en el momento"], ["Reclamos", "formulario de atención", "QR · mail · teléfono", "en el momento"]];
const tablaFuente = xs => tabla(["Indicador", "Dato de origen", "Con qué", "Se actualiza"], xs.map(([a, b, c, d]) => `<tr><td>${esc(a)}</td><td>${esc(b)}</td><td class="muted">${esc(c)}</td><td class="nw">${esc(d)}</td></tr>`));

// ---------------------------------------------------------------- vistas
const tablaAMFE = (xs, campo) => tabla(["ID", campo ? "Etapa" : "Puesto · operación", "Modo de falla → efecto", "Causa", "Controles actuales", "S", "O", "D", "NPR", "Acción"],
  xs.map(f => `<tr><td class="mono">${f.id}</td><td>${campo ? esc(f.etapa) : `<span class="mono nw">${esc(f.pto)}</span><br><span class="muted">${esc(f.op)}</span>`}</td><td style="min-width:190px"><b>${esc(f.modo)}</b><br><span class="muted">→ ${esc(f.efecto)}</span></td><td>${esc(f.causa)}</td>
    <td style="min-width:200px;font-size:12.5px"><span class="muted">Prevención:</span> ${esc(f.prev)}<br><span class="muted">Detección:</span> ${esc(f.det)}</td><td class="num">${f.s}</td>
    <td class="num"><b>${f.O}</b><div class="muted" style="font-size:11px;max-width:120px;margin-left:auto">${esc(f.base)}</div></td><td class="num">${f.d}</td><td class="num">${nprPill(f)}</td>
    <td style="min-width:150px">${f.accion ? `<b>${esc(f.acc)}</b>` : esc(f.acc)}<br><span class="muted">${esc(f.resp)}</span></td></tr>`));
function vistaAMFE(def) {
  const tab = fil("qtab", def), p = amfe(false), c = amfe(true);
  const kp = xs => `<div class="kpis"><div class="kpi in"><span>Modos de falla</span><b>${xs.length}</b><small>${xs.filter(f => f.s >= 9).length} con S ≥ 9</small></div>
    <div class="kpi ${xs.some(f => f.accion) ? "no" : "ok"}"><span>Con acción requerida</span><b>${xs.filter(f => f.accion).length}</b><small>NPR ≥ 100 o S ≥ 9 con O ≥ 4 (criterio)</small></div>
    <div class="kpi av"><span>NPR máximo</span><b>${xs[0].npr}</b><small>${esc(xs[0].id)} · ${esc(xs[0].modo)}</small></div>
    <div class="kpi in"><span>O desde los registros</span><b>${xs.filter(f => !/^criterio/.test(f.base)).length} de ${xs.length}</b><small>el resto, criterio del equipo</small></div></div>`;
  const tabs = [["proc", "AMFE de proceso · intraplanta"], ["campo", "AMFE de campo · extraplanta"], ["plan", "Plan de control"], ["esc", "Escalas y regla"]];
  let cuerpo = "";
  if (tab === "proc") cuerpo = kp(p) + `<div class="panel"><header><h2>AMFE de proceso</h2><span class="muted">ordenado por NPR · O calculada con ${n0(tasasRechazo().u)} unidades cerradas en ${D.anio}</span></header>${tablaAMFE(p, false)}</div>`;
  if (tab === "campo") cuerpo = kp(c) + `<div class="panel"><header><h2>AMFE de campo</h2><span class="muted">transporte, instalación, uso, recarga, atención y retiros · O de los registros del sistema</span></header>${tablaAMFE(c, true)}</div>`;
  if (tab === "plan") cuerpo = `<div class="panel"><header><h2>Plan de control</h2><span class="muted">DOC-02 (R1-R9 de rutina, L1-L5 por lote) y DOC-01 (pintura)</span></header>${tabla(["Cód.", "Puesto", "Característica y especificación", "Método e instrumento", "Muestra", "Cómo llega al sistema", "Plan de reacción", "Este mes"],
    PLAN.map(x => `<tr><td class="mono"><b>${x.c}</b></td><td class="mono" style="font-size:12px">${esc(x.pto)}</td><td style="min-width:200px"><b>${esc(x.car)}</b><br><span class="muted">${esc(x.esp)}</span></td><td style="min-width:140px">${esc(x.met)}${x.inst.length ? `<br>${x.inst.map(medOk).join(" ")}` : ""}</td><td>${esc(x.mue)}</td><td>${esc(x.reg)}</td><td class="muted">${esc(x.rea)}</td><td style="min-width:120px">${esc(x.vivo())}</td></tr>`))}</div>`;
  if (tab === "esc") cuerpo = `<div class="grilla"><div class="panel c4"><header><h2>Severidad (S)</h2></header>${tabla(["S", "Efecto"], S_ESCALA.map(([k, t]) => `<tr><td class="num">${k}</td><td>${esc(t)}</td></tr>`))}</div>
    <div class="panel c4"><header><h2>Ocurrencia (O)</h2></header>${tabla(["O", "Tasa"], O_ESCALA.map(([, k, t]) => `<tr><td class="num">${k}</td><td>${t}</td></tr>`).concat([`<tr><td class="num">2</td><td>menos de 1 en 100.000 o sin casos</td></tr>`, `<tr><td class="num">1</td><td>impedido por el diseño</td></tr>`]))}</div>
    <div class="panel c4"><header><h2>Detección (D)</h2></header>${tabla(["D", "Control"], D_ESCALA.map(([k, t]) => `<tr><td class="num">${k}</td><td>${esc(t)}</td></tr>`))}</div>
    <div class="panel c12"><div class="cuerpo"><p style="margin:0">Escalas adaptadas del manual AIAG FMEA 4.ª ed. La <b>O</b> se calcula sola con los registros del sistema y cambia cuando se cierran lotes, se confirman remitos o entran reclamos. <b>S</b> y <b>D</b> son criterio del equipo de FLAMA y se revisan cuando cambia el proceso, un control o aparece un desvío. Regla de acción (criterio): NPR = S × O × D ≥ 100, o S ≥ 9 con O ≥ 4.</p></div></div></div>`;
  return `<div class="filtros" role="tablist">${tabs.map(([k, t]) => `<button role="tab" aria-pressed="${tab === k}" data-a="filtro" data-k="qtab" data-v="${k}">${t}</button>`).join("")}</div>` + cuerpo;
}
VISTAS.amfe = { titulo: "AMFE y plan de control", sub: () => "Modos de falla del proceso y del campo, con la ocurrencia calculada de los registros, y los controles de DOC-02 y DOC-01", html: () => vistaAMFE("proc") };
VISTAS.amfecampo = { titulo: "AMFE de campo", sub: () => "Qué puede fallar después de que el equipo sale de la planta y cómo se detecta", html: () => vistaAMFE("campo") };

VISTAS.estados = {
  titulo: "Estados del lote",
  sub: () => "Cada estado: qué lo dispara, quién lo registra, con qué, y qué control hay que pasar para salir",
  html() {
    const om = S.ordenes.filter(o => o.mes === D.mes), ret = S.ordenes.filter(o => retenido(o).length);
    const cnt = e => S.ordenes.filter(o => o.etapa === e && (e < E["Despachada"] || o.mes === D.mes)).length;
    return `<div class="estados-flujo">${ESTADOS_LOTE.map(([e], i) => `<a href="#ordenes" data-a="irOrdenes" data-v="${["plan", "curso", "curso", "curso", "curso", "cerrar", "etiq", "pt", "desp"][i]}" class="estado-caja" style="--c:${COL_ETAPA[i]}"><small>${i}</small><b>${esc(e)}</b><span>${cnt(i)} ${cnt(i) === 1 ? "lote" : "lotes"}</span></a>`).join('<span class="flecha">→</span>')}</div>
      <div class="grilla">
      <div class="panel c12"><header><h2>Estadios de los lotes del mes</h2><span class="muted">un tramo por estado, de la hoja de ruta, el visado y el remito · borde oscuro: estado actual</span></header><div class="cuerpo">${ganttLotes(om.filter(o => o.etapa > 0))}</div></div>
      <div class="panel c12"><header><h2>Cómo entra y sale un lote de cada estado</h2></header>${tabla(["#", "Estado", "Entra cuando", "Quién y dónde", "Cómo se registra", "Para salir", "Lotes ahora", "Tiempo medio"],
        ESTADOS_LOTE.map(([e, ent, q, reg, sal], i) => `<tr><td class="num">${i}</td><td>${pill(e, etapaPill(i))}</td><td>${esc(ent)}</td><td>${esc(q)}</td><td>${esc(reg)}</td><td class="muted">${esc(sal)}</td><td class="num">${cnt(i)}</td><td class="num">${i > 0 && i < 8 ? durTxt(tiempoMedio(i)) : "—"}</td></tr>`))}
        <p class="muted" style="font-size:12.5px;margin:8px 14px 12px">Tiempo medio: lotes de ${MES_TXT[D.mes - 2] || ""} y ${MES_TXT[D.mes - 1]} que ya salieron del estado. Despachada cuenta solo las del mes.</p></div>
      <div class="panel c6"><header><h2>Lotes retenidos</h2><span class="muted">no avanzan hasta resolver la causa</span></header>${ret.length ? tabla(["Orden", "Estado", "Motivo"], ret.map(o => `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td>${pill(ETAPAS[o.etapa], "av")}</td><td>${esc(retenido(o).join(" · "))}</td></tr>`)) : `<div class="cuerpo"><p class="muted" style="margin:0">Ningún lote retenido.</p></div>`}</div>
      <div class="panel c6"><header><h2>Estados de cada serie dentro del lote</h2></header><div class="cuerpo"><ul class="lista-alertas">
        <li><b>Apta</b><span>sigue con el lote; se identifica en el puesto 24 / C-15</span></li><li><b>Rechazada</b><span>falló un ensayo de rutina: sale del lote con su número y su causa</span></li>
        <li><b>Muestra de laboratorio</b><span>recipiente del lote usado en L1 rotura (destructivo)</span></li><li><b>Inutilizada</b><span>baja con acta; el número no se reutiliza</span></li></ul></div></div></div>`;
  },
};
VISTAS.estadoseq = {
  titulo: "Estados del equipo",
  sub: () => "Por dónde pasa cada matafuego o cilindro fuera de la planta y cómo llega cada traspaso al sistema",
  html() {
    const c = censo().est, tl = S.remitos.filter(r => r.recibido), lead = tl.length ? tl.reduce((a, r) => a + dias(r.fecha, r.recibido), 0) / tl.length : null;
    return `<div class="estados-flujo">${ESTADOS_EQ.slice(0, 6).map(([e], i) => `<a href="#equipos" data-a="irEquipos" data-v="${e}" class="estado-caja" style="--c:${["var(--ink-3)", "var(--yellow)", "var(--violet)", "var(--blue)", "var(--blue)", "var(--green)"][i]}"><b>${esc(e)}</b><span>${n0(c[e] || 0)} equipos</span></a>`).join('<span class="flecha">→</span>')}</div>
      <div class="grilla"><div class="panel c12"><header><h2>Cómo cambia de estado cada equipo</h2></header>${tabla(["Estado", "Entra cuando", "Custodia", "Cómo se registra", "Equipos"], ESTADOS_EQ.map(([e, ent, cu, reg]) => `<tr><td>${pill(e, estadoPill[e])}</td><td>${esc(ent)}</td><td>${esc(cu)}</td><td>${esc(reg)}</td><td class="num">${n0(c[e] || 0)}</td></tr>`))}
        <p class="muted" style="font-size:12.5px;margin:8px 14px 12px">Despacho → recepción: ${lead == null ? "—" : nf(lead, 1) + " d"} en promedio. Lo que nadie leyó queda en el último que lo tuvo.</p></div>
      <div class="panel c6"><header><h2>Orden de servicio (recarga)</h2></header>${tabla(["Estado", "Cómo se registra", "OS"], ETAPAS_OS.map((e, i) => `<tr><td>${esc(e)}</td><td class="muted">${esc(["lector del grabado + tablet en la recepción", "presupuesto enviado por mail o WhatsApp", "ensayos de DOC-03 en el taller", "control final con el checklist", "etiqueta y tarjeta impresas", "entrega con remito y sustituto devuelto"][i])}</td><td class="num">${S.recargas.filter(r => r.etapa === i && !r.inutil).length}</td></tr>`))}</div>
      <div class="panel c6"><header><h2>Reclamo</h2></header>${tabla(["Estado", "Cómo se registra", "Reclamos"], ETAPAS_RC.map((e, i) => `<tr><td>${esc(e)}</td><td class="muted">${esc(["QR, mail o teléfono: acuse con número y plazo", "traza del equipo: lote, insumos, ensayos", "respuesta por escrito con la vía de conciliación", "encuesta de una pregunta; la causa pasa a Desvíos"][i])}</td><td class="num">${S.reclamos.filter(x => x.etapa === i).length}</td></tr>`))}</div></div>`;
  },
};
VISTAS.origen = {
  titulo: "Origen de los datos",
  sub: () => "Cómo se mide cada cosa y cómo llega al sistema, dentro de la planta y fuera de ella",
  acciones: () => `<div class="filtros" role="tablist">${[["intra", "Intraplanta"], ["extra", "Extraplanta"]].map(([k, t]) => `<button role="tab" aria-pressed="${fil("otab", "intra") === k}" data-a="filtro" data-k="otab" data-v="${k}">${t}</button>`).join("")}</div>`,
  html() {
    const ex = fil("otab", "intra") === "extra", rs = registrosMes(ex);
    return `<div class="kpis">${rs.map(([k, v]) => `<div class="kpi in"><span>${esc(k)}</span><b>${n0(v)}</b><small>${MES_TXT[D.mes - 1]}</small></div>`).join("")}</div>
      <div class="grilla"><div class="panel c12"><header><h2>Flujo de los datos</h2><span class="muted">${ex ? "nadie necesita una app: se lee el QR con la cámara del celular" : "sin tablet por puesto: hoja de ruta + lecturas en etiquetado y pallet"}</span></header><div class="cuerpo">${flujoDatos(ex)}</div></div>
      <div class="panel c12"><header><h2>Cada dato: dónde nace y cómo llega</h2></header>${tabla(["Dato", "Dónde nace", "Instrumento", "Quién", "Cuándo", "Cómo llega al sistema", "Validación", "Alimenta"],
        (ex ? ORIGEN_EXTRA : ORIGEN_INTRA).map(r => `<tr>${r.map((x, i) => `<td class="${i === 0 ? "" : i === 2 || i === 6 ? "muted" : ""}">${i === 0 ? `<b>${esc(x)}</b>` : esc(x)}</td>`).join("")}</tr>`))}</div></div>`;
  },
};

// ---------------------------------------------------------------- pestañas nuevas de la página del lote
function tabEstadios(o) {
  const es = estadios(o), ahora = new Date(+HOY + 17 * 36e5), ret = retenido(o);
  return `${ret.length ? `<div class="aviso no">Lote retenido: ${esc(ret.join(" · "))}.</div>` : ""}<div class="panel"><header><h2>Estadios del lote</h2><span class="muted">entrada y salida de cada estado · de la hoja de ruta, el visado y el remito</span></header>
    ${tabla(["#", "Estado", "Entró", "Salió", "Duración", "Cómo se registró"], es.map(x => `<tr><td class="num">${x.e}</td><td>${pill(x.nombre, etapaPill(x.e))}</td><td class="nw">${x.desde ? new Date(x.desde).toLocaleString("es-AR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) : "plan mensual"}</td>
      <td class="nw">${x.hasta ? new Date(x.hasta).toLocaleString("es-AR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) : x.e === E["Despachada"] ? "—" : pill("en curso", "av")}</td><td class="num">${x.desde && x.e < E["Despachada"] ? durTxt(horas(x.desde, x.hasta || ahora)) : "—"}</td><td class="muted">${esc(ESTADOS_LOTE[x.e][3])}</td></tr>`))}</div>
    <div class="panel"><header><h2>Línea de tiempo</h2></header><div class="cuerpo">${ganttLotes([o])}</div></div>`;
}
function tabEnsayosLote(o) {
  const x = ensayosLote(o);
  if (!x) return `<div class="aviso in">Los ensayos de lote (DOC-02 L1-L5) y los controles de pintura (DOC-01) se hacen con el lote para cerrar y quedan en la planilla F-02 de la partida ${esc(o.partida)}.</div>`;
  const ok = b => b ? pill("aprobado", "ok") : pill("no aprobado", "no"), mn = Math.min(...x.pintura.lect);
  const filas = [["L1", "Rotura (destructivo)", `${nf(x.rotura.p, 2)} MPa`, `≥ ${nf(x.rotura.min, 1)} MPa (2 × Pe)`, ok(x.rotura.p >= x.rotura.min), "MP-PAT"],
    ["L2", "Expansión volumétrica", `${nf(x.expansion.pct, 1)} % permanente`, "≤ 10 % de la total", ok(x.expansion.pct <= x.expansion.max), "MP-PAT"]];
  if (x.descarga) filas.push(["L3", "Descarga y alcance", `${nf(x.descarga.s, 1)} s · ${nf(x.descarga.pct, 0)} % · ${nf(x.descarga.alc, 1)} m`, `≥ ${x.descarga.min} s y ≥ 85 % · catálogo ${x.descarga.cat[0]}${x.descarga.cat[1] !== x.descarga.cat[0] ? "/" + x.descarga.cat[1] : ""} s, ${x.descarga.cat[2]}/${x.descarga.cat[3]} m`, ok(x.descarga.s >= x.descarga.min && x.descarga.pct >= 85), "banco de descarga"],
    ["L4", "Polvo ABC", x.polvo, "certificado IRAM 3569", ok(true), "certificado"], ["L5", "Manómetros y válvulas", x.valvula, "certificado IRAM 3533; válvula a Pe", ok(true), "certificado"]);
  filas.push(["DOC-01", "Espesor de película", x.pintura.lect.map(v => nf(v, 0)).join(" · ") + " µm", "60 a 100 µm; ningún punto < 80 % del nominal", ok(mn >= 48 && x.pintura.lect.reduce((a, v) => a + v, 0) / 5 >= 60), "EP-1"], ["DOC-01", "Adherencia", "clase " + x.pintura.adh, "ISO 2409 clase 0 ó 1", ok(x.pintura.adh <= 1), "cuadriculado"], ["DOC-01", "Curado", "sin ablandamiento", "frote MEK (ASTM D5402)", ok(x.pintura.mek), "MEK"]);
  return `<div class="panel"><header><h2>Ensayos de lote y de pintura</h2><span class="muted">planilla F-02 · partida ${esc(o.partida)} · visado ${esc(RT)}</span></header>${tabla(["Ensayo", "Qué", "Resultado", "Criterio", "Estado", "Instrumento"], filas.map(r => `<tr><td class="mono">${r[0]}</td><td>${esc(r[1])}</td><td class="mono">${esc(r[2])}</td><td class="muted">${esc(r[3])}</td><td>${r[4]}</td><td class="muted">${esc(r[5])}</td></tr>`))}
    <p class="muted" style="font-size:12.5px;margin:8px 14px 12px">L1 usa un recipiente de muestra del lote (se destruye). Criterios de DOC-02 3.2 y DOC-01 4.</p></div>`;
}
ACC.irOrdenes = el => { UI.f.oest = el.dataset.v; UI.f.omes = D.mes; ir("ordenes"); };
ACC.irEquipos = el => { UI.f.eest = el.dataset.v; ir("equipos"); };
ACC.irOrigenExtra = () => { UI.f.otab = "extra"; ir("origen"); };
ACC.irOrigenIntra = () => { UI.f.otab = "intra"; ir("origen"); };
