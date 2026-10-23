// ================================================================ estado de la empresa
// Real (de los Excel): órdenes y series del año (matafuegos y cilindros), plan del mes, plan de recargas, insumos y
// política de stock (MRP), modelos (BOM). De prueba (semilla fija): en qué etapa está cada orden, rechazos, mediciones,
// clientes, remitos, instalaciones, recargas, reclamos, desvíos, retiros y stock físico. Las acciones del usuario se
// guardan en este navegador con su hash encadenado.
const ETAPAS = ["Planificada", "Corte y grabado", "Armado y soldadura", "PH y pintura", "Carga y armado final", "Para cerrar", "Para etiquetar", "Depósito PT", "Despachada"];
const E = Object.fromEntries(ETAPAS.map((e, i) => [e, i]));
const ETAPAS_OS = ["Recibido", "Presupuesto enviado", "En taller", "Control final", "Listo para entregar", "Entregado"];
const ETAPAS_RC = ["Recibido", "En análisis", "Respondido", "Cerrado"];
const CAUSAS = [["Fuga en PH", "PH"], ["Pérdida en válvula", "Pérd."], ["Espesor fuera de tolerancia", "Esp."], ["Golpe o pintura", "Visual"], ["Carga fuera de tolerancia", "Carga"]];
const PH = { man: 3.5, car: 4.0 };                     // MPa, 1 min (DOC-02)
const N2 = 1.4;                                        // MPa de presurización (DOC-02)
const ESPESOR = { "1 kg": 0.9, "2,5 kg": 1.25, "5 kg": 1.6, "10 kg": 2.0, "25 kg": 3.2, "50 kg": 3.2, "70 kg": 4.75, "100 kg": 4.75 };   // mm, planos FL_REC
const kgDe = m => (m.match(/(\d+(?:,\d+)?) kg/) || [])[1] + " kg";
const OPER = ["J. Pérez", "M. Gómez", "L. Ríos", "C. Acosta", "R. Benítez", "S. Díaz", "F. Molina", "A. Quiroga", "N. Paz", "E. Ortiz"];
const CALIDAD = "M. Ruiz", RT = "Ing. A. Ferreyra";
const TRANSP = [["Transportes Ruta 3", "AB123CD"], ["Logística Sur", "AE456FG"], ["Fletes Avellaneda", "AC789HJ"]];
// puestos de la hoja de ruta: [etapa en la que se hacen, puesto, operación, equipo, insumo que se anota]
const PUESTOS = {
  Manuales: [[1, "2", "Corte y grabado de la planchuela", "Guillotina G2 + Pannier", "chapa"], [2, "4-7", "Embutido de cúpulas y fondos", "Prensa", "cupulas"],
    [2, "8-12", "Soldadura MAG de cuerpo, cuello y fondo", "Soldadoras MAG", "alambre"], [3, "13", "Prueba hidráulica", "Banco PH · manómetro PH-M1", null],
    [3, "14-15", "Secado y granallado", "Horno · granalladora", null], [3, "16-19", "Pintura en polvo y curado", "Cabina + horno", "pintura"],
    [4, "20-21", "Carga de polvo y armado de válvula", "Cargadora · balanza B-1", "polvo"], [4, "22", "Presurización con N₂", "Regulador + manómetro", "valvula"],
    [4, "23", "Control de pérdidas", "Cuba", null], [6, "24", "Etiquetado e identificación", "Lector + impresora", null], [7, "25", "Embalaje y pallet", "Lector", null]],
  Carros: [[1, "C-2", "Corte, grabado y rolado", "Guillotina + Pannier + roladora", "chapa"], [2, "C-4", "Soldadura longitudinal y circunferencial", "Soldadoras", "alambre"],
    [2, "C-6", "Cupla, patas y triángulos del eje", "Soldadoras", "cupulas"], [3, "C-8", "Prueba hidráulica", "Banco PH · manómetro PH-M2", null],
    [3, "C-9", "Secado y granallado", "Horno · granalladora", null], [3, "C-10", "Pintura en polvo y curado", "Cabina + horno", "pintura"],
    [4, "C-12", "Tren rodante, manguera y lanza", "Banco de armado", null], [4, "C-13", "Carga y presurización", "Balanza B-2", "polvo"],
    [4, "C-14", "Control de pérdidas", "Agua jabonosa", "valvula"], [6, "C-15", "Etiquetado e identificación", "Lector + impresora", null], [7, "C-16", "Despacho en pallet", "Lector", null]],
};
const CLAVE = `flama-gestion-${D.anio}-${D.mes}-${D.lotes.length}-v3`;

function semillaEstado() {
  const r = semilla(2026 * 100 + D.mes);
  const clientes = [
    ["DI-01", "Matafuegos Sur", "Distribuidor", "Avellaneda", "PBA"], ["DI-02", "Seguridad Oeste", "Distribuidor", "Morón", "PBA"],
    ["DI-03", "Extintores del Norte", "Distribuidor", "San Isidro", "PBA"], ["DI-04", "Prevención Capital", "Distribuidor", "CABA", "CABA"],
    ["DI-05", "Protección Integral Lanús", "Distribuidor", "Lanús", "PBA"], ["DI-06", "Fuego Cero", "Distribuidor", "La Plata", "PBA"],
    ["CL-01", "Panadería La Espiga", "Comercio", "Avellaneda", "PBA"], ["CL-02", "Hotel Rivera", "Hotelería", "Quilmes", "PBA"],
    ["CL-03", "Consorcio Corrientes 2210", "Consorcio", "CABA", "CABA"], ["CL-04", "Supermercado El Trébol", "Supermercado", "Lomas de Zamora", "PBA"],
    ["CL-05", "Clínica San Martín", "Salud", "San Martín", "PBA"], ["CL-06", "Taller Ruta 3", "Automotor", "La Matanza", "PBA"],
    ["CL-07", "Depósito Dock Sud", "Industria", "Avellaneda", "PBA"], ["CL-08", "Escuela Técnica 14", "Educación", "CABA", "CABA"],
    ["CL-09", "Estación de Servicio Mitre", "Automotor", "Avellaneda", "PBA"], ["CL-10", "Frigorífico La Pampa", "Industria", "Esteban Echeverría", "PBA"],
    ["CL-11", "Oficinas Paseo Colón", "Oficinas", "CABA", "CABA"], ["CL-12", "Gimnasio Alvear", "Comercio", "Temperley", "PBA"],
  ].map(([id, nombre, tipo, loc, jur]) => ({ id, nombre, tipo, loc, jur, cuit: `30-7${String(hashN(id) % 10000000).padStart(7, "0")}-${hashN(nombre) % 10}` }));
  const dist = clientes.filter(c => c.tipo === "Distribuidor");

  // órdenes: meses anteriores despachadas; el mes en curso avanza con los días hábiles transcurridos
  const ordenes = D.lotes.map(l => Object.assign({}, l, { linea: l.carro ? "Carros" : "Manuales", etapa: E["Despachada"], rech: [], etiquetados: l.cant, remito: null }));
  ordenes.forEach(o => {
    const hab = habiles(D.anio, o.mes), del = ordenes.filter(x => x.mes === o.mes && x.linea === o.linea), i = del.indexOf(o);
    o.emision = hab[Math.min(hab.length - 1, Math.floor(i / del.length * (hab.length - 6)))];
    o.cierre = hab[Math.min(hab.length - 1, Math.floor((i + 1) / del.length * (hab.length - 1)))];
    if (o.cierre < o.emision) o.cierre = o.emision;
    const n = Math.round(o.cant * (o.carro ? 0.012 : 0.016) + (r() < 0.35 ? 1 : 0));   // rechazos de prueba ≈ 1,5 %
    const usados = new Set();
    for (let k = 0; k < Math.min(n, o.cant - 1); k++) {
      let s; do { s = o.desde + Math.floor(r() * o.cant); } while (usados.has(s));
      usados.add(s); let c = r() < 0.45 ? CAUSAS[0] : elegir(r, CAUSAS); if (o.cilindro && (c[1] === "Carga" || c[1] === "Pérd.")) c = CAUSAS[0];
      o.rech.push({ n: s, causa: c[0], ensayo: c[1] });
    }
  });
  const actual = ordenes.filter(o => o.mes === D.mes);
  const plano = { Manuales: [8, 8, 8, 8, 8, 8, 7, 7, 6, 5, 4, 1, 3, 2], Carros: [8, 7, 3, 2, 0, 1] };   // etapa de cada orden del mes, en orden
  for (const lin of ["Manuales", "Carros"]) actual.filter(o => o.linea === lin).forEach((o, i) => {
    o.etapa = plano[lin][i] ?? 0;
    if (o.etapa < E["Depósito PT"]) o.cierre = null;
    if (o.etapa === 0) o.emision = null;
    if (o.etapa < E["Para cerrar"]) o.rech = [];
    if (o.etapa === E["Para etiquetar"]) o.etiquetados = Math.floor((o.cant - o.rech.length) * 0.4);
    else if (o.etapa < E["Para etiquetar"]) o.etiquetados = 0;
  });
  // partidas DPS: órdenes del mismo modelo y mes agrupadas hasta 100 u (Res. 349/07 art. 21)
  const pm = {}, MOD = [...new Set(D.lotes.map(l => l.modelo))];
  ordenes.forEach(o => { const k = o.mes + o.modelo, p = pm[k] || (pm[k] = { g: 1, u: 0 });
    o.partida = `P-${AA}-${String(o.mes).padStart(2, "0")}-${String.fromCharCode(65 + MOD.indexOf(o.modelo))}${p.g}`;
    p.u += o.cant; if (p.u >= 100) { p.g++; p.u = 0; } });
  ordenes.forEach(o => { const m = String(o.mes).padStart(2, "0"), h = hashN(o.op);
    o.insumos = { chapa: `H-${m}${(h % 90) + 10} · colada ${4400 + (h % 300)}`, cupulas: `CU-${AA}${m}`, alambre: `AL-${AA}${m} · G-${(h % 40) + 60}`, pintura: `PP-${AA}${m}-${(h % 3) + 1}` };
    if (!o.cilindro) Object.assign(o.insumos, { polvo: `PO-${AA}${m}`, valvula: `VA-${(hashN(o.modelo) % 80) + 100}-${m}` });
    o.pallet = `00 0779 ${String(1000000 + (h % 899999)).padStart(7, "0")} ${h % 10}`; });

  // remitos: lo despachado se agrupa de a 1 a 3 órdenes por distribuidor
  const remitos = []; let nr = 4300;
  for (let m = 1; m <= D.mes; m++) {
    const desp = ordenes.filter(o => o.mes === m && o.etapa === E["Despachada"]);
    for (let i = 0; i < desp.length;) {
      const k = 1 + Math.floor(r() * 3), grupo = desp.slice(i, i + k); i += k;
      const f = grupo.reduce((a, o) => o.cierre > a ? o.cierre : a, grupo[0].cierre), sale = sumar(f, 1 + Math.floor(r() * 3)), t = elegir(r, TRANSP);
      const rem = { id: `R 0001-${String(++nr).padStart(8, "0")}`, fecha: sale, cliente: elegir(r, dist).id, ops: grupo.map(o => o.op), estado: "Recibido", recibido: sumar(sale, 1),
        transp: t[0], patente: t[1], recibe: elegir(r, ["L. Gómez", "P. Sosa", "D. Vera", "G. Luna"]), cot: `COT ${String(hashN("cot" + nr) % 1e8).padStart(8, "0")}` };
      grupo.forEach(o => o.remito = rem.id); remitos.push(rem);
    }
  }
  const ult = remitos.filter(x => x.fecha.getMonth() + 1 === D.mes).sort((a, b) => a.fecha - b.fecha);
  if (ult.length) Object.assign(ult[ult.length - 1], { estado: "En tránsito", recibido: null, fecha: sumar(HOY, -1) });
  if (ult.length > 1) Object.assign(ult[ult.length - 2], { estado: "Sin confirmar", recibido: null, fecha: sumar(HOY, -3) });

  // recargas abiertas: tipos según el plan del mes de las dos plantas
  const tipos = [...D.recargas.comercial.map(t => Object.assign({ planta: "Comercial" }, t)), ...D.recargas.industrial.map(t => Object.assign({ planta: "Industrial" }, t))].filter(t => t.cant > 0);
  const totalRec = tipos.reduce((a, t) => a + t.cant, 0);
  const tipoAl = () => { let x = r() * totalRec; for (const t of tipos) { x -= t.cant; if (x <= 0) return t; } return tipos[0]; };
  const recargas = []; let no = 2200;
  for (let i = 0; i < 38; i++) {
    const t = tipoAl(), et = i < 7 ? 0 : i < 12 ? 1 : i < 24 ? 2 : i < 29 ? 3 : i < 35 ? 4 : 5, c = elegir(r, clientes);
    const f = sumar(HOY, -Math.min(9, Math.floor((6 - et) * 0.8 + r() * 3)));
    recargas.push({ os: `OS-${AA}-${String(++no).padStart(5, "0")}`, fecha: f, planta: t.planta, tipo: t.tipo, agente: t.agente, cliente: c.id,
      marca: "Otra marca", nro: `${(hashN(no) % 900000) + 100000}`, fab: 2014 + (hashN("f" + no) % 11), etiqueta: `S-${AA}-${String(30000 + no).padStart(6, "0")}`, etapa: et,
      sustituto: r() < 0.7 ? `SUS-${(hashN(no) % 120) + 1}` : null, ph: r() < 0.2, polvoBajo: t.agente === "ABC" && r() < 0.12,
      presupuesto: Math.round((t.agente === "CO₂" ? 18000 : 14000) * (1 + r() * 0.6) / 100) * 100, inutil: null, tecnico: elegir(r, OPER) });
  }
  recargas[3].inutil = "Corrosión en la pollera (IRAM 3517-2 9.7.1.3 b)"; recargas[3].etapa = 2;

  const reclamos = [
    { id: `RC-${AA}-000109`, fecha: sumar(HOY, -12), cliente: "CL-01", serie: ser(4310), tipo: "Atención o entrega", texto: "El instalador no dejó el acta firmada.", etapa: 3 },
    { id: `RC-${AA}-000112`, fecha: sumar(HOY, -7), cliente: "DI-02", serie: ser(4802), tipo: "Garantía", texto: "La manguera llegó fisurada.", etapa: 2 },
    { id: `RC-${AA}-000115`, fecha: sumar(HOY, -3), cliente: "CL-04", serie: `S-${AA}-032215`, tipo: "Servicio de recarga", texto: "Después de la recarga pierde presión.", etapa: 1 },
    { id: `RC-${AA}-000116`, fecha: sumar(HOY, -2), cliente: "CL-07", serie: ser(4977), tipo: "Seguridad", texto: "Se cayó y tiene un golpe en la cúpula.", etapa: 1 },
    { id: `RC-${AA}-000117`, fecha: sumar(HOY, 0), cliente: "CL-02", serie: ser(5012), tipo: "Seguridad", texto: "El manómetro marca en la zona roja.", etapa: 0 },
    { id: `RC-${AA}-000118`, fecha: sumar(HOY, -1), cliente: "CL-03", serie: "—", tipo: "Datos personales", texto: "Pide qué datos tienen de su consorcio.", etapa: 1 },
  ];
  const mesAnt = ordenes.filter(o => o.mes === D.mes - 1 && o.rech.length);
  const desvios = [
    { id: `RD-${AA}-061`, fecha: sumar(HOY, -15), origen: "Proceso", que: "Fuga en cordón longitudinal en PH", ref: mesAnt[0] ? mesAnt[0].op : "—", sev: "Mayor", resp: "Mantenimiento", estado: "Cerrado", causa: "Boquilla de la soldadora 10 con salpicaduras; sin frecuencia de limpieza", accion: "Limpieza cada 50 cordones y cambio cada 500" },
    { id: `RD-${AA}-062`, fecha: sumar(HOY, -9), origen: "Proceso", que: "Masa de carga fuera de control (dentro de tolerancia)", ref: "Balanza B-1", sev: "Menor", estado: "Abierto", resp: "Calidad", causa: "No se hace cero al cambiar la bolsa de polvo", accion: "Cero obligatorio en la pantalla de carga" },
    { id: `RD-${AA}-063`, fecha: sumar(HOY, -6), origen: "Custodia", que: "Equipo golpeado en tránsito", ref: remitos.length > 3 ? remitos[remitos.length - 4].id : "—", sev: "Menor", estado: "En curso", resp: "Depósito PT", causa: "Pallet sin esquineros", accion: "Esquineros en todos los pallets de manuales" },
    { id: `RD-${AA}-064`, fecha: sumar(HOY, -4), origen: "Proveedor", que: "Lote de cúpulas con bordón fuera de medida", ref: `CU-${AA}09`, sev: "Crítica", estado: "Cerrado", resp: "Calidad + compras", causa: "Matriz del proveedor gastada; recepción 1 cada 200", accion: "Re-ensayo 100 % y recepción 1 cada 50" },
    { id: `RD-${AA}-065`, fecha: sumar(HOY, -2), origen: "Cliente", que: "Reclamo de seguridad respondido a las 27 h (plazo 24 h)", ref: `RC-${AA}-000116`, sev: "Mayor", estado: "Abierto", resp: "Atención", causa: "Sin guardia de fin de semana", accion: "Guardia para reclamos de seguridad" },
  ];
  // retiro preventivo de prueba: un lote de válvulas de septiembre con aviso del proveedor
  const vSep = ordenes.find(o => o.mes === D.mes - 1 && o.modelo === "ABC 5 kg");
  const retiros = vSep ? [{ id: `RP-${AA}-01`, fecha: sumar(HOY, -5), lote: vSep.insumos.valvula, motivo: "Aviso del proveedor: juntas tóricas de un lote de válvulas fuera de especificación", estado: "Abierto", ubicados: 0.62 }] : [];
  const insumos = {};
  D.insumos.forEach(m => { const dia = m.anio26 / 240, cob = 4 + Math.floor(r() * 50); insumos[m.cod] = { stock: Math.round(dia * cob * 10) / 10 || Math.round(r() * 20), lote: `${m.cod.split("/")[0]}-${AA}${String(D.mes).padStart(2, "0")}-${(hashN(m.cod) % 9) + 1}`, ingreso: sumar(HOY, -cob % 20) }; });
  const medicion = [
    { id: "PH-M1", desc: "Manómetro banco PH manuales (0-7 MPa)", ult: sumar(HOY, -6), cada: 15, tipo: "Contraste con patrón (Res. 349/07 art. 20)" },
    { id: "PH-M2", desc: "Manómetro banco PH carros (0-10 MPa)", ult: sumar(HOY, -13), cada: 15, tipo: "Contraste con patrón (Res. 349/07 art. 20)" },
    { id: "MP-PAT", desc: "Manómetro patrón Ø100 (0-14 MPa)", ult: sumar(HOY, -410), cada: 730, tipo: "Calibración del fabricante (Res. 349/07 art. 15 l)" },
    { id: "B-1", desc: "Balanza de carga manuales (división 10 g)", ult: sumar(HOY, -150), cada: 365, tipo: "Calibración anual (criterio)" },
    { id: "B-2", desc: "Balanza de carga carros (división 50 g)", ult: sumar(HOY, -340), cada: 365, tipo: "Calibración anual (criterio)" },
  ];
  return { clientes, ordenes, remitos, recargas, reclamos, desvios, retiros, insumos, medicion, inst: {}, bajas: {}, eventos: [], nRc: 119, nRd: 66, nOs: no, nRem: nr };
}

let S;
function cargar() {
  try { const g = localStorage.getItem(CLAVE); if (g) { S = JSON.parse(g); return; } } catch (e) {}
  S = semillaEstado();
}
function guardar() { try { localStorage.setItem(CLAVE, JSON.stringify(S)); } catch (e) {} }
function reiniciar() { try { localStorage.removeItem(CLAVE); } catch (e) {} S = semillaEstado(); }
// cada evento guarda el hash SHA-256 del anterior: si alguien toca un registro viejo, la cadena se rompe
let CADENA = Promise.resolve();
function registrar(tipo, ref, detalle = "") {
  const e = { t: new Date().toISOString(), tipo, ref, detalle, quien: "T. Sinay", prev: null, hash: null };
  S.eventos.unshift(e); guardar();
  CADENA = CADENA.then(async () => {        // en orden: cada hash necesita el del evento anterior
    const i = S.eventos.indexOf(e); e.prev = i + 1 < S.eventos.length ? S.eventos[i + 1].hash : "0".repeat(64);
    e.hash = await sha256(e.prev + e.t + tipo + ref + detalle + e.quien); guardar();
  });
}

// ---------------------------------------------------------------- consultas
const cliente = id => S.clientes.find(c => c.id === id) || { nombre: id, id };
const ordenDe = n => { let a = 0, b = S.ordenes.length - 1; while (a <= b) { const m = (a + b) >> 1, o = S.ordenes[m]; if (n < o.desde) b = m - 1; else if (n > o.hasta) a = m + 1; else return o; } return null; };
const remito = id => S.remitos.find(r => r.id === id);
const modeloBOM = nombre => D.modelos.find(m => (m.nombre + " ").includes(nombre.replace("Carro ", "").replace("Cilindros ", "") + " "));
const maxSerie = () => S.ordenes[S.ordenes.length - 1].hasta;
const tipoEq = o => o.cilindro ? "Cilindro" : "Matafuego";
function masaCarga(n, o) {      // masa de carga de prueba dentro de la banda del BOM, determinística por serie
  const m = modeloBOM(o.modelo); if (!m || o.cilindro) return null;
  const r = semilla(n), u = (r() + r() + r()) / 3;
  return m.min + (m.max - m.min) * (0.25 + 0.5 * u);
}
// fecha y hora en que cada puesto firmó la hoja de ruta (de prueba, entre la emisión y el cierre)
function hojaRuta(o) {
  const ps = PUESTOS[o.linea].filter(p => !(o.cilindro && /Carga|Presuriz|pérdidas|válvula/.test(p[2])));
  const ini = o.emision ? new Date(o.emision) : null, fin = o.cierre ? new Date(o.cierre) : HOY, span = ini ? Math.max(1, (fin - ini) / 864e5) : 0;
  const enDia = {}; // horas crecientes dentro de cada día: el orden del historial respeta la secuencia de puestos
  return ps.map((p, i) => {
    // el embalaje (25 / C-16) es lo que pone al lote en depósito PT: en esa etapa ya está hecho
    const hecho = o.etapa > p[0] || (p[0] === E["Depósito PT"] && o.etapa === p[0]), enCurso = !hecho && o.etapa === p[0];
    const d = Math.floor(span * i / ps.length), k = enDia[d] = (enDia[d] || 0) + 1;
    const f = ini ? new Date(+ini + d * 864e5 + (6 + 1.6 * k) * 36e5 + (hashN(i + o.op) % 50) * 6e4) : null;
    return { etapa: p[0], puesto: p[1], op: p[2], equipo: p[3], insumo: p[4] ? o.insumos[p[4]] : null, firma: hecho ? OPER[hashN(o.op + p[1]) % OPER.length] : null, fecha: hecho ? f : null, estado: hecho ? "hecho" : enCurso ? "en curso" : "pendiente" };
  });
}
function ensayos(n, o) {
  const r = semilla(n * 7 + 3), rech = o.rech.find(x => x.n === n), kg = kgDe(o.modelo), nom = ESPESOR[kg] || 1.6;
  const cerrado = o.etapa >= E["Para etiquetar"];
  if (!cerrado) return null;
  const corta = !!rech && ["Esp.", "PH"].includes(rech.ensayo);
  return { esp: { nom, med: nom * (0.985 + 0.04 * r()), ok: !(rech && rech.ensayo === "Esp.") },
    ph: { p: o.carro ? PH.car : PH.man, t: 60, ok: !(rech && rech.ensayo === "PH"), man: o.carro ? "PH-M2" : "PH-M1" },
    // rechazado en espesor o PH: sale de la línea antes de cargar, no tiene carga, N₂ ni pérdidas
    carga: o.cilindro || corta ? null : { kg: masaCarga(n, o), ok: !(rech && rech.ensayo === "Carga") }, n2: o.cilindro || corta ? null : N2,
    perd: o.cilindro || corta ? null : !(rech && rech.ensayo === "Pérd."), visual: !(rech && rech.ensayo === "Visual"), rech };
}
const UBIC = ["salón de ventas", "depósito", "cocina", "pasillo PB", "oficina", "playa de carga", "sala de máquinas", "recepción"];
function equipo(n) {
  const o = ordenDe(n); if (!o) return null;
  const rech = o.rech.find(x => x.n === n), h = hashN("eq" + n) % 100;
  const e = { n, s: ser(n), o, tipo: tipoEq(o), rech, fab: o.cierre, estado: "En producción", custodia: "FLAMA", cliente: null, inst: null };
  if (S.bajas[n]) { Object.assign(e, { estado: "Inutilizado", baja: S.bajas[n] }); }
  else if (rech && o.etapa >= E["Para cerrar"]) { e.estado = "Rechazado"; return e; }
  else {
    if (o.etapa === E["Para etiquetar"]) e.estado = (n - o.desde) < o.etiquetados + o.rech.filter(x => x.n < n).length ? "En depósito PT" : "Para etiquetar";
    if (o.etapa === E["Depósito PT"]) e.estado = "En depósito PT";
    if (o.etapa === E["Despachada"] && o.remito) {
      const rm = remito(o.remito);
      e.remito = rm; e.custodia = rm.estado === "En tránsito" || rm.estado === "Preparado" ? "Transportista" : cliente(rm.cliente).nombre;
      e.estado = rm.estado === "En tránsito" || rm.estado === "Preparado" ? "En tránsito" : "En distribuidor";
      const edad = dias(rm.fecha), manual = S.inst[n];
      if (manual) { e.estado = "Instalado"; e.cliente = cliente(manual.cliente); e.custodia = e.cliente.nombre; e.inst = manual; }
      else if (!o.cilindro && rm.estado === "Recibido" && h < Math.min(85, edad * 1.2)) {
        const finales = S.clientes.filter(c => c.tipo !== "Distribuidor"), c = finales[hashN("cl" + n) % finales.length], q = semilla(n);
        e.estado = "Instalado"; e.cliente = c; e.custodia = c.nombre;
        e.inst = { cliente: c.id, fecha: sumar(rm.recibido || rm.fecha, 2 + (h % Math.max(1, edad - 3))), ubic: UBIC[hashN("u" + n) % UBIC.length], alt: Math.round((1.15 + q() * 0.3) * 100) / 100,
          cartel: Math.round((2.05 + q() * 0.4) * 100) / 100, instalador: OPER[hashN("i" + n) % OPER.length], tarjeta: c.jur === "CABA" ? `SGM ${String(hashN("t" + n) % 1e7).padStart(7, "0")}` : `DPS T-${AA}-${String(hashN("t" + n) % 1e6).padStart(6, "0")}` };
      }
    }
  }
  if (e.fab) { e.mant = sumar(e.fab, 365); e.phVence = sumar(e.fab, 365 * 5); e.vida = sumar(e.fab, 365 * 20); }
  if (e.inst) e.garantia = sumar(e.inst.fecha, 182);
  return e;
}
// historia completa del equipo: lo que lo identifica, cada paso con su fecha y su responsable
function historia(e) {
  const o = e.o, ev = [], hr = hojaRuta(o), ens = ensayos(e.n, o);
  // fechas guardadas por día (emisión, cierre, remito): se les pone la hora típica del evento; las cargadas en la app ya traen hora
  const hora = (d, h) => { if (!d) return d; const x = new Date(d); return x.getHours() || x.getMinutes() ? x : new Date(+x + h * 36e5); };
  if (o.emision) ev.push([hora(o.emision, 7), "Orden emitida", `${o.op} · partida ${o.partida}`, "PCP"]);
  hr.filter(p => p.fecha && p.etapa < E["Para etiquetar"]).forEach(p => ev.push([p.fecha, p.op, `puesto ${p.puesto}${p.insumo ? " · " + p.insumo : ""}`, p.firma]));
  if (ens) ev.push([hora(o.cierre || HOY, 17), e.rech ? "Rechazado: " + e.rech.causa : "Lote cerrado y visado", e.rech ? "sale del lote con su número" : `RT ${RT}`, CALIDAD, !!e.rech]);
  if (!e.rech && ["En depósito PT", "En tránsito", "En distribuidor", "Instalado", "Inutilizado"].includes(e.estado)) { const p = hr.find(x => x.etapa === E["Para etiquetar"]); ev.push([p && p.fecha || o.cierre, "Identificado", `estampilla DPS ${estampilla(e.n)} · etiqueta QR`, p && p.firma]); }
  if (e.remito) {
    ev.push([hora(e.remito.fecha, 8), "Despachado", `${e.remito.id} · pallet SSCC ${o.pallet}`, "Depósito PT"]);
    ev.push([hora(e.remito.fecha, 8.5), "Salida confirmada", `${e.remito.transp} · ${e.remito.patente}`, "chofer"]);
    if (e.remito.recibido) ev.push([hora(e.remito.recibido, 14), "Recibido por el distribuidor", cliente(e.remito.cliente).nombre, e.remito.recibe]);
  }
  if (e.inst) ev.push([e.inst.fecha, "Instalado", `${cliente(e.inst.cliente).nombre} · ${e.inst.ubic} · ${e.inst.tarjeta}`, e.inst.instalador]);
  if (e.baja) ev.push([e.baja.fecha, "Inutilizado · baja", e.baja.motivo, "Recargas"]);
  return ev.sort((a, b) => new Date(a[0]) - new Date(b[0]));
}
const estadoPill = { "En producción": "gr", "Para etiquetar": "av", "En depósito PT": "in", "En tránsito": "vi", "En distribuidor": "in", "Instalado": "ok", "Rechazado": "no", "Inutilizado": "no" };
const etapaPill = i => i === E["Despachada"] ? "ok" : i === E["Depósito PT"] ? "in" : i >= E["Para cerrar"] ? "av" : i === 0 ? "gr" : "vi";
const estampilla = n => "F-" + String(80000 + (n % 100000)).padStart(6, "0");
