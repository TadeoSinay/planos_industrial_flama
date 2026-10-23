// ================================================================ estado de la empresa
// De los Excel del proyecto: órdenes y series del año, plan del mes, plan de recargas, insumos y política de stock (MRP),
// modelos (BOM), capacidad por puesto, pallets, zonas y tasas. Nada se inventa: los registros de la operación (etapas,
// firmas, rechazos, pesadas, ensayos, identificación, remitos, clientes, instalaciones, recargas, reclamos, desvíos)
// arrancan vacíos y los carga quien opera el sistema. Cada registro queda como evento con su hash encadenado.
const ETAPAS = ["Planificada", "Corte y grabado", "Armado y soldadura", "PH y pintura", "Carga y armado final", "Para cerrar", "Para etiquetar", "Depósito PT", "Despachada"];
const E = Object.fromEntries(ETAPAS.map((e, i) => [e, i]));
const ETAPAS_OS = ["Recibido", "Presupuesto enviado", "En taller", "Control final", "Listo para entregar", "Entregado"];
const ETAPAS_RC = ["Recibido", "En análisis", "Respondido", "Cerrado"];
const CAUSAS = [["Fuga en PH", "PH"], ["Pérdida en válvula", "Pérd."], ["Espesor fuera de tolerancia", "Esp."], ["Golpe o pintura", "Visual"], ["Carga fuera de tolerancia", "Carga"]];
const PH = { man: 3.5, car: 4.0 };                     // MPa, 1 min (DOC-02)
const N2 = 1.4;                                        // MPa de presurización (DOC-02)
const ESPESOR = { "1 kg": 0.9, "2,5 kg": 1.25, "5 kg": 1.6, "10 kg": 2.0, "25 kg": 3.2, "50 kg": 3.2, "70 kg": 4.75, "100 kg": 4.75 };   // mm, planos FL_REC
const kgDe = m => (m.match(/(\d+(?:,\d+)?) kg/) || [])[1] + " kg";
const USUARIO = "T. Sinay";                            // quien opera esta sesión: firma cada registro
// puestos de la hoja de ruta (procesos W-MAN y W-CAR): [etapa, puesto, operación, equipo de Aprovechamiento_*, insumo que se anota]
const PUESTOS = {
  Manuales: [[1, "2", "Corte y grabado de la planchuela", "Guillotinas Ermaksan HGS 2600-6 y QC12Y · Pannier ADP120160D", "chapa"],
    [2, "4-7", "Embutido de cúpulas y fondos, cuello", "Prensa Sangiacomo + Cena PRE-1 · Pannier MB-21", "cupulas"],
    [2, "8-12", "Soldadura de cuello, longitudinal y circunferencial", "Firesafer FS-HFM1, cilindradora y soldadoras Firesafer · Del Fabro 30 t · Pilman SWM-400", "alambre"],
    [3, "13", "Espesor y prueba hidráulica", "Melisam MR017 · banco Firesafer FS-JD12A", null], [3, "14-15", "Secado y granallado", "Secadora Yukon · AirBlast G-100", null],
    [3, "16-19", "Detección y corrección de defectos, pintura en polvo", "Mesa de inspección · amoladora · línea de pintura Firesafer", "pintura"],
    [4, "20-21", "Carga de polvo y armado de válvula", "Cargadora Firesafer FS-A10 / Yukon M-000121 · llave dinamométrica", "polvo"],
    [4, "22", "Presurización con N₂", "Pinza Yukon M-000150 + pack N₂", "valvula"], [4, "23", "Control de pérdidas", "Tanque de inmersión inoxidable", null],
    [6, "24", "Etiquetado e identificación", "Zebra ZD421 + lector DPM", null], [7, "25", "Embalaje y pallet", "Armadora de cajas + envolvedora EDOS PS 5", null]],
  Carros: [[1, "C-2", "Corte, marcado y cilindrado", "Guillotinas Ermaksan · DTMAQ MPE 150130 · roladora W12 8 × 1500", "chapa"],
    [2, "C-4", "Punteo y soldadura longitudinal", "Virador Serecon ZJ R-410 · ZH-1300 Dragon Welding", "alambre"],
    [2, "C-6", "Cupla, armado circunferencial y accesorios", "VEVOR 30 kg · virador USA Tools 1.000 kg · MIG/MAG Pampa 300", "cupulas"],
    [3, "C-8", "Prueba hidráulica", "Yukon M-000200", null], [3, "C-9", "Secado", "Melisam MR011", null],
    [3, "C-10", "Pintura en polvo (tercerizada)", "Pulmón de despacho y recepción de pintados", "pintura"],
    [4, "C-12", "Montaje, manga y precinto", "Puesto manual, estaciones A y C", null], [4, "C-13", "Carga de polvo y presurización", "Yukon M-000121 + balanza 300 kg + N₂", "polvo"],
    [4, "C-14", "Pérdidas, inspección final y ensayos de lote", "Sala de pérdidas 5 × 5 m + Yukon M-000200", "valvula"],
    [6, "C-15", "Etiquetado e identificación", "Mesa de etiquetado + lector DPM", null], [7, "C-16", "Depósito de PT y despacho", "Autoelevador + tarima de carga", null]],
};
const CLAVE = `flama-gestion-${D.anio}-${D.mes}-${D.lotes.length}-real1`;

// estado inicial: solo el plan. Partidas DPS por modelo y mes hasta 100 u (Res. 349/07 art. 21)
function estadoInicial() {
  const ordenes = D.lotes.map(l => Object.assign({}, l, { linea: l.carro ? "Carros" : "Manuales", etapa: 0, emision: null, cierre: null, rech: [], etiquetados: 0,
    remito: null, reg: {}, hist: [], pesadas: {}, lab: null, visado: null, insumos: {}, pallet: null }));
  const pm = {}, MOD = [...new Set(D.lotes.map(l => l.modelo))];
  ordenes.forEach(o => { const k = o.mes + o.modelo, p = pm[k] || (pm[k] = { g: 1, u: 0 });
    o.partida = `P-${AA}-${String(o.mes).padStart(2, "0")}-${String.fromCharCode(65 + MOD.indexOf(o.modelo))}${p.g}`;
    p.u += o.cant; if (p.u >= 100) { p.g++; p.u = 0; } });
  // equipos de medición del proyecto (Aprovechamiento_*): sin control registrado hasta que se cargue
  const medicion = [
    { id: "PH-M1", desc: "Manómetro del banco de PH Firesafer FS-JD12A (manuales)", ult: null, cada: 15, tipo: "Contraste con patrón (Res. 349/07 art. 20)" },
    { id: "PH-M2", desc: "Manómetro de la máquina de prueba Yukon M-000200 (carros)", ult: null, cada: 15, tipo: "Contraste con patrón (Res. 349/07 art. 20)" },
    { id: "MP-PAT", desc: "Manómetro patrón (modelo a definir)", ult: null, cada: null, tipo: "Calibración en laboratorio (Res. 349/07 art. 15 l)" },
    { id: "ESP-1", desc: "Medidor de espesores Melisam MR017", ult: null, cada: null, tipo: "Calibración: frecuencia a definir con el fabricante" },
    { id: "B-1", desc: "Balanza de la cargadora Firesafer FS-A10 / Yukon M-000121 (manuales)", ult: null, cada: null, tipo: "Calibración: frecuencia a definir" },
    { id: "B-2", desc: "Balanza 300 kg de la cargadora Yukon M-000121 (carros)", ult: null, cada: null, tipo: "Calibración: frecuencia a definir" },
    { id: "EP-1", desc: "Medidor de espesor de película ISO 2808 (modelo a definir)", ult: null, cada: null, tipo: "Verificación con láminas patrón: frecuencia a definir" },
  ];
  return { clientes: [], ordenes, remitos: [], recargas: [], reclamos: [], desvios: [], retiros: [], insumos: {}, medicion, ident: {}, inst: {}, bajas: {},
    eventos: [], nCl: 0, nRc: 0, nRd: 0, nOs: 0, nRem: 0, nRp: 0 };
}

let S;
function cargar() {
  try { const g = localStorage.getItem(CLAVE); if (g) { S = JSON.parse(g); return; } } catch (e) {}
  S = estadoInicial();
}
function guardar() { try { localStorage.setItem(CLAVE, JSON.stringify(S)); } catch (e) {} }
function reiniciar() { try { localStorage.removeItem(CLAVE); } catch (e) {} S = estadoInicial(); }
// cada evento guarda el hash SHA-256 del anterior: si alguien toca un registro viejo, la cadena se rompe
let CADENA = Promise.resolve();
function registrar(tipo, ref, detalle = "") {
  const e = { t: new Date().toISOString(), tipo, ref, detalle, quien: USUARIO, prev: null, hash: null };
  S.eventos.unshift(e); guardar();
  CADENA = CADENA.then(async () => {        // en orden: cada hash necesita el del evento anterior
    const i = S.eventos.indexOf(e); e.prev = i + 1 < S.eventos.length ? S.eventos[i + 1].hash : "0".repeat(64);
    e.hash = await sha256(e.prev + e.t + tipo + ref + detalle + e.quien); guardar();
  });
}
const ahoraISO = () => new Date().toISOString();
// pasa la orden a la etapa e y lo deja en su historia de estados
function cambiarEtapa(o, e) { o.etapa = e; o.hist.push({ e, t: ahoraISO() }); if (e === 1 && !o.emision) o.emision = ahoraISO(); if (e === E["Depósito PT"]) o.cierre = ahoraISO(); }

// ---------------------------------------------------------------- consultas
const cliente = id => S.clientes.find(c => c.id === id) || { nombre: id || "—", id, jur: "" };
const ordenDe = n => { let a = 0, b = S.ordenes.length - 1; while (a <= b) { const m = (a + b) >> 1, o = S.ordenes[m]; if (n < o.desde) b = m - 1; else if (n > o.hasta) a = m + 1; else return o; } return null; };
const remito = id => S.remitos.find(r => r.id === id);
const modeloBOM = nombre => D.modelos.find(m => (m.nombre + " ").includes(nombre.replace("Carro ", "").replace("Cilindros ", "") + " "));
const maxSerie = () => S.ordenes[S.ordenes.length - 1].hasta;
const tipoEq = o => o.cilindro ? "Cilindro" : "Matafuego";
const masaCarga = (n, o) => o.pesadas && o.pesadas[n] != null ? o.pesadas[n] : null;   // pesada registrada al cerrar el lote
const sinControl = m => !m || (m.cada ? !m.ult || dias(m.ult) > m.cada : false);         // PH bloqueada si el contraste no está vigente
const estadoMed = m => !m.ult ? ["sin registro", m.cada ? "no" : "gr"] : m.cada && dias(m.ult) > m.cada ? ["vencido", "no"] : ["vigente", "ok"];
function hojaRuta(o) {
  return PUESTOS[o.linea].filter(p => !(o.cilindro && /Carga|Presuriz|pérdidas|válvula/.test(p[2]))).map(p => {
    const r = o.reg[p[1]];
    return { etapa: p[0], puesto: p[1], op: p[2], equipo: p[3], insumo: r && r.lote || null, firma: r ? r.quien : null, fecha: r ? r.t : null,
      estado: r ? "hecho" : o.etapa === p[0] || (p[0] === E["Para etiquetar"] && o.etapa === p[0]) ? "en curso" : "pendiente", lleva: p[4] };
  });
}
// estadios del lote: entrada y salida de cada estado, de su historia registrada
function estadios(o) {
  const out = [{ e: 0, nombre: ETAPAS[0], desde: null, hasta: (o.hist[0] || {}).t || null }];
  o.hist.forEach((h, i) => out.push({ e: h.e, nombre: ETAPAS[h.e], desde: h.t, hasta: (o.hist[i + 1] || {}).t || null }));
  return out;
}
// descarga (s) y alcance (m) de catálogo, DOC-02 tabla 2: criterio del ensayo L3
const CATALOGO = { "1 kg": [8, 9, 2, 3], "2,5 kg": [9, 12, 3, 4], "5 kg": [10, 13, 5, 6], "10 kg": [18, 22, 6, 7], "25 kg": [40, 40, 5, 6], "50 kg": [45, 45, 6, 7], "70 kg": [50, 50, 7, 8], "100 kg": [55, 55, 8, 9] };
const descargaMin = o => { const kg = kgDe(o.modelo); return o.carro ? (kg === "25 kg" ? 10 : kg === "100 kg" ? 30 : 15) : 8; };
const ensayosLote = o => o.lab || null;            // L1-L5 y pintura, registrados al cerrar
// retención: un lote para cerrar o etiquetar no avanza si su manómetro de PH no tiene contraste vigente o tiene un desvío abierto
function retenido(o) {
  if (o.etapa < E["Para cerrar"] || o.etapa > E["Para etiquetar"]) return [];
  const m = S.medicion.find(x => x.id === (o.carro ? "PH-M2" : "PH-M1")), out = [];
  if (sinControl(m)) out.push(`${m.id} sin contraste vigente`);
  S.desvios.filter(d => d.estado !== "Cerrado" && d.ref === o.op).forEach(d => out.push(`desvío ${d.id} abierto`));
  return out;
}
// resultado por serie: lo registrado al cerrar (✗ de la hoja y pesadas); sin cierre no hay resultado
function ensayos(n, o) {
  if (o.etapa < E["Para etiquetar"]) return null;
  const rech = o.rech.find(x => x.n === n), corta = !!rech && ["Esp.", "PH"].includes(rech.ensayo);
  return { ph: { p: o.carro ? PH.car : PH.man, t: 60, ok: !(rech && rech.ensayo === "PH"), man: o.carro ? "PH-M2" : "PH-M1" },
    // rechazado en espesor o PH: sale de la línea antes de cargar, no tiene carga, N₂ ni pérdidas
    carga: o.cilindro || corta ? null : { kg: masaCarga(n, o), ok: !(rech && rech.ensayo === "Carga") }, n2: o.cilindro || corta ? null : N2,
    perd: o.cilindro || corta ? null : !(rech && rech.ensayo === "Pérd."), visual: !(rech && rech.ensayo === "Visual"), esp: !(rech && rech.ensayo === "Esp."), rech };
}
function equipo(n) {
  const o = ordenDe(n); if (!o) return null;
  const rech = o.rech.find(x => x.n === n), id = S.ident[n];
  const e = { n, s: ser(n), o, tipo: tipoEq(o), rech, fab: id || null, estado: o.etapa === 0 ? "Planificado" : "En producción", custodia: "FLAMA", cliente: null, inst: null };
  if (S.bajas[n]) Object.assign(e, { estado: "Inutilizado", baja: S.bajas[n] });
  else if (rech) e.estado = "Rechazado";
  else if (o.etapa >= E["Para etiquetar"]) {
    e.estado = id ? "En depósito PT" : "Para etiquetar";
    const rm = o.remito && remito(o.remito);
    if (rm && rm.estado !== "Preparado") { e.remito = rm; e.estado = rm.estado === "Recibido" ? "En distribuidor" : "En tránsito"; e.custodia = rm.estado === "Recibido" ? cliente(rm.cliente).nombre : "Transportista " + rm.transp; }
    if (S.inst[n]) { e.estado = "Instalado"; e.inst = S.inst[n]; e.cliente = cliente(e.inst.cliente); e.custodia = e.cliente.nombre; }
  }
  if (e.fab) { e.mant = sumar(e.fab, 365); e.phVence = sumar(e.fab, 365 * 5); e.vida = sumar(e.fab, 365 * 20); }   // IRAM 3517-2 9.2.1 y anexo E; Res. 349/07 art. 26
  if (e.inst) e.garantia = sumar(e.inst.fecha, 182);                                                                 // Ley 24.240: 6 meses
  return e;
}
function historia(e) {
  const o = e.o, ev = [];
  o.hist.forEach(h => ev.push([h.t, h.e === 1 ? "Orden liberada" : "Pasa a " + ETAPAS[h.e], `${o.op} · partida ${o.partida}`, "PCP"]));
  hojaRuta(o).filter(p => p.fecha && p.etapa < E["Para etiquetar"]).forEach(p => ev.push([p.fecha, p.op, `puesto ${p.puesto}${p.insumo ? " · " + p.insumo : ""}`, p.firma]));
  if (o.visado) ev.push([o.visado.t, e.rech ? "Rechazado: " + e.rech.causa : "Lote cerrado y visado", e.rech ? "sale del lote con su número" : `visado ${o.visado.quien}`, o.visado.quien, !!e.rech]);
  if (S.ident[e.n]) ev.push([S.ident[e.n], "Identificado", "lectura del grabado · etiqueta QR", "puesto " + (o.carro ? "C-15" : "24")]);
  if (e.remito) {
    ev.push([e.remito.fecha, "Despachado", `${e.remito.id}${e.remito.cot ? " · " + e.remito.cot : ""}`, "Depósito PT"]);
    if (e.remito.salida) ev.push([e.remito.salida, "Salida confirmada", `${e.remito.transp} · ${e.remito.patente}`, "chofer"]);
    if (e.remito.recibido) ev.push([e.remito.recibido, "Recibido por el distribuidor", cliente(e.remito.cliente).nombre, e.remito.recibe || ""]);
  }
  if (e.inst) ev.push([e.inst.fecha, "Instalado", `${cliente(e.inst.cliente).nombre} · ${e.inst.ubic} · ${e.inst.tarjeta}`, e.inst.instalador]);
  if (e.baja) ev.push([e.baja.fecha, "Inutilizado · baja", e.baja.motivo, "Recargas"]);
  return ev.sort((a, b) => new Date(a[0]) - new Date(b[0]));
}
const estadoPill = { "Planificado": "gr", "En producción": "gr", "Para etiquetar": "av", "En depósito PT": "in", "En tránsito": "vi", "En distribuidor": "in", "Instalado": "ok", "Rechazado": "no", "Inutilizado": "no" };
const etapaPill = i => i === E["Despachada"] ? "ok" : i === E["Depósito PT"] ? "in" : i >= E["Para cerrar"] ? "av" : i === 0 ? "gr" : "vi";
