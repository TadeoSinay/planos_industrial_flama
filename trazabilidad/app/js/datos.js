// ================================================================ estado de la empresa
// Real (de los Excel): órdenes y series del año, plan del mes, plan de recargas, insumos y política de stock (MRP), modelos
// (BOM). De prueba (semilla fija): en qué etapa está cada orden, rechazos, clientes, remitos, recargas, reclamos, desvíos
// y stock físico. Las acciones del usuario se guardan en este navegador.
const ETAPAS = ["Planificada", "Corte y grabado", "Armado y soldadura", "PH y pintura", "Carga y armado final", "Para cerrar", "Para etiquetar", "Depósito PT", "Despachada"];
const E = Object.fromEntries(ETAPAS.map((e, i) => [e, i]));
const ETAPAS_OS = ["Recibido", "Presupuesto enviado", "En taller", "Control final", "Listo para entregar", "Entregado"];
const ETAPAS_RC = ["Recibido", "En análisis", "Respondido", "Cerrado"];
const CAUSAS = [["Fuga en PH", "PH"], ["Pérdida en válvula", "Pérd."], ["Espesor fuera de tolerancia", "Esp."], ["Golpe o pintura", "Visual"], ["Carga fuera de tolerancia", "Carga"]];
const PH = { man: "3,5 MPa · 1 min", car: "4,0 MPa · 1 min" };   // DOC-02
const CLAVE = `flama-gestion-${D.anio}-${D.mes}-${D.lotes.length}-v2`;

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
  const dist = clientes.filter(c => c.tipo === "Distribuidor"), finales = clientes.filter(c => c.tipo !== "Distribuidor");

  // órdenes: meses anteriores despachadas; el mes en curso avanza con los días hábiles transcurridos
  const ordenes = D.lotes.map(l => Object.assign({}, l, { linea: l.carro ? "Carros" : "Manuales", etapa: E["Despachada"], rech: [], etiquetados: l.cant, remito: null }));
  ordenes.forEach(o => {
    const hab = habiles(D.anio, o.mes), del = ordenes.filter(x => x.mes === o.mes && x.linea === o.linea), i = del.indexOf(o);
    o.emision = hab[0];
    o.cierre = hab[Math.min(hab.length - 1, Math.floor((i + 1) / del.length * (hab.length - 1)))];
    const n = Math.round(o.cant * (o.carro ? 0.012 : 0.016) + (r() < 0.35 ? 1 : 0));   // rechazos de prueba ≈ 1,5 %
    const usados = new Set();
    for (let k = 0; k < Math.min(n, o.cant - 1); k++) {
      let s; do { s = o.desde + Math.floor(r() * o.cant); } while (usados.has(s));
      usados.add(s); const c = r() < 0.45 ? CAUSAS[0] : elegir(r, CAUSAS); o.rech.push({ n: s, causa: c[0], ensayo: c[1] });
    }
  });
  const actual = ordenes.filter(o => o.mes === D.mes);
  const plano = { Manuales: [8, 8, 8, 8, 8, 8, 7, 7, 6, 5, 4, 1], Carros: [8, 7, 3, 2, 0] };   // etapa de cada orden del mes, en orden
  for (const lin of ["Manuales", "Carros"]) actual.filter(o => o.linea === lin).forEach((o, i) => {
    o.etapa = plano[lin][i] ?? 0;
    if (o.etapa < E["Depósito PT"]) o.cierre = null;
    if (o.etapa < E["Para cerrar"]) o.rech = [];
    if (o.etapa === E["Para etiquetar"]) o.etiquetados = Math.floor((o.cant - o.rech.length) * 0.4);
    else if (o.etapa < E["Para etiquetar"]) o.etiquetados = 0;
  });
  // partidas DPS: órdenes del mismo modelo y mes agrupadas hasta 100 u (Res. 349/07 art. 21)
  const pm = {}, MOD = [...new Set(D.lotes.map(l => l.modelo))];
  ordenes.forEach(o => { const k = o.mes + o.modelo, p = pm[k] || (pm[k] = { g: 1, u: 0 });
    o.partida = `P-${AA}-${String(o.mes).padStart(2, "0")}-${String.fromCharCode(65 + MOD.indexOf(o.modelo))}${p.g}`;
    p.u += o.cant; if (p.u >= 100) { p.g++; p.u = 0; } });
  ordenes.forEach(o => { const m = String(o.mes).padStart(2, "0"); o.insumos = { chapa: `H-${m}${(hashN(o.op) % 90) + 10}`, polvo: `PO-${AA}${m}`, valvula: `VA-${(hashN(o.modelo) % 80) + 100}`, pintura: `PP-${AA}${m}-${(hashN(o.op) % 3) + 1}` }; });

  // remitos: lo despachado se agrupa de a 1 a 3 órdenes por distribuidor
  const remitos = []; let nr = 4300;
  for (let m = 1; m <= D.mes; m++) {
    const desp = ordenes.filter(o => o.mes === m && o.etapa === E["Despachada"]);
    for (let i = 0; i < desp.length;) {
      const k = 1 + Math.floor(r() * 3), grupo = desp.slice(i, i + k); i += k;
      const f = grupo[grupo.length - 1].cierre, sale = sumar(f, 1 + Math.floor(r() * 3));
      const rem = { id: `R 0001-${String(++nr).padStart(8, "0")}`, fecha: sale, cliente: elegir(r, dist).id, ops: grupo.map(o => o.op), estado: "Recibido", recibido: sumar(sale, 1) };
      grupo.forEach(o => o.remito = rem.id); remitos.push(rem);
    }
  }
  // los dos últimos del mes siguen abiertos: uno viajando y otro entregado sin confirmar
  const ult = remitos.filter(x => x.fecha.getMonth() + 1 === D.mes).sort((a, b) => a.fecha - b.fecha);
  if (ult.length) Object.assign(ult[ult.length - 1], { estado: "En tránsito", recibido: null, fecha: sumar(HOY, -1) });
  if (ult.length > 1) Object.assign(ult[ult.length - 2], { estado: "Sin confirmar", recibido: null, fecha: sumar(HOY, -3) });
  remitos.forEach(x => { if (x.fecha > HOY) x.fecha = HOY; });

  // recargas abiertas: tipos según el plan del mes de las dos plantas
  const tipos = [...D.recargas.comercial.map(t => Object.assign({ planta: "Comercial" }, t)), ...D.recargas.industrial.map(t => Object.assign({ planta: "Industrial" }, t))].filter(t => t.cant > 0);
  const totalRec = tipos.reduce((a, t) => a + t.cant, 0);
  const tipoAl = () => { let x = r() * totalRec; for (const t of tipos) { x -= t.cant; if (x <= 0) return t; } return tipos[0]; };
  const marcas = ["Otra marca", "Otra marca", "Otra marca", "FLAMA"];
  const recargas = []; let no = 2200;
  for (let i = 0; i < 38; i++) {
    const t = tipoAl(), et = i < 7 ? 0 : i < 12 ? 1 : i < 24 ? 2 : i < 29 ? 3 : i < 35 ? 4 : 5, c = elegir(r, clientes);
    const f = sumar(HOY, -Math.min(9, Math.floor((6 - et) * 0.8 + r() * 3)));
    recargas.push({ os: `OS-${AA}-${String(++no).padStart(5, "0")}`, fecha: f, planta: t.planta, tipo: t.tipo, agente: t.agente, cliente: c.id,
      marca: elegir(r, marcas), etiqueta: `S-${AA}-${String(30000 + no).padStart(6, "0")}`, etapa: et, sustituto: r() < 0.7 ? `SUS-${(hashN(no) % 120) + 1}` : null,
      ph: r() < 0.2, polvoBajo: t.agente === "ABC" && r() < 0.12, presupuesto: Math.round((t.agente === "CO₂" ? 18000 : 14000) * (1 + r() * 0.6) / 100) * 100, inutil: null });
  }
  recargas[3].inutil = "Corrosión en la pollera (IRAM 3517-2 9.7.1.3 b)"; recargas[3].etapa = 2;

  const reclamos = [
    { id: `RC-${AA}-000109`, fecha: sumar(HOY, -12), cliente: "CL-01", serie: ser(4310), tipo: "Atención o entrega", texto: "El instalador no dejó el acta firmada.", etapa: 3 },
    { id: `RC-${AA}-000112`, fecha: sumar(HOY, -7), cliente: "DI-02", serie: ser(4802), tipo: "Garantía", texto: "La manguera llegó fisurada.", etapa: 2 },
    { id: `RC-${AA}-000115`, fecha: sumar(HOY, -3), cliente: "CL-04", serie: `S-${AA}-031981`, tipo: "Servicio de recarga", texto: "Después de la recarga pierde presión.", etapa: 1 },
    { id: `RC-${AA}-000116`, fecha: sumar(HOY, -2), cliente: "CL-07", serie: ser(4977), tipo: "Seguridad", texto: "Se cayó y tiene un golpe en la cúpula.", etapa: 1 },
    { id: `RC-${AA}-000117`, fecha: sumar(HOY, 0), cliente: "CL-02", serie: ser(5012), tipo: "Seguridad", texto: "El manómetro marca en la zona roja.", etapa: 0 },
    { id: `RC-${AA}-000118`, fecha: sumar(HOY, -1), cliente: "CL-03", serie: "—", tipo: "Datos personales", texto: "Pide qué datos tienen de su consorcio.", etapa: 1 },
  ];
  const mesAnt = ordenes.filter(o => o.mes === D.mes - 1 && o.rech.length);
  const desvios = [
    { id: `RD-${AA}-061`, fecha: sumar(HOY, -15), origen: "Proceso", que: "Fuga en cordón longitudinal en PH", ref: mesAnt[0] ? mesAnt[0].op : "—", sev: "Mayor", resp: "Mantenimiento", estado: "Cerrado", causa: "Boquilla de la soldadora 10 con salpicaduras; sin frecuencia de limpieza", accion: "Limpieza cada 50 cordones y cambio cada 500" },
    { id: `RD-${AA}-062`, fecha: sumar(HOY, -9), origen: "Proceso", que: "Masa de carga fuera de control (dentro de tolerancia)", ref: "Balanza B-2", sev: "Menor", estado: "Abierto", resp: "Calidad", causa: "No se hace cero al cambiar la bolsa de polvo", accion: "Cero obligatorio en la pantalla de carga" },
    { id: `RD-${AA}-063`, fecha: sumar(HOY, -6), origen: "Custodia", que: "Equipo golpeado en tránsito", ref: remitos.length > 3 ? remitos[remitos.length - 4].id : "—", sev: "Menor", estado: "En curso", resp: "Depósito PT", causa: "Pallet sin esquineros", accion: "Esquineros en todos los pallets de manuales" },
    { id: `RD-${AA}-064`, fecha: sumar(HOY, -4), origen: "Proveedor", que: "Lote de cúpulas con bordón fuera de medida", ref: "CU-2609", sev: "Crítica", estado: "Cerrado", resp: "Calidad + compras", causa: "Matriz del proveedor gastada; recepción 1 cada 200", accion: "Re-ensayo 100 % y recepción 1 cada 50" },
    { id: `RD-${AA}-065`, fecha: sumar(HOY, -2), origen: "Cliente", que: "Reclamo de seguridad respondido a las 27 h (plazo 24 h)", ref: `RC-${AA}-000116`, sev: "Mayor", estado: "Abierto", resp: "Atención", causa: "Sin guardia de fin de semana", accion: "Guardia para reclamos de seguridad" },
  ];
  const insumos = {};
  D.insumos.forEach(m => { const dia = m.anio26 / 240, cob = 4 + Math.floor(r() * 50); insumos[m.cod] = { stock: Math.round(dia * cob * 10) / 10 || Math.round(r() * 20), lote: `${m.cod.split("/")[0]}-${AA}${String(D.mes).padStart(2, "0")}-${(hashN(m.cod) % 9) + 1}`, ingreso: sumar(HOY, -cob % 20) }; });
  const medicion = [
    { id: "PH-M1", desc: "Manómetro banco PH manuales (0-7 MPa)", ult: sumar(HOY, -6), cada: 15, tipo: "Contraste con patrón (Res. 349/07 art. 20)" },
    { id: "PH-M2", desc: "Manómetro banco PH carros (0-10 MPa)", ult: sumar(HOY, -13), cada: 15, tipo: "Contraste con patrón (Res. 349/07 art. 20)" },
    { id: "MP-PAT", desc: "Manómetro patrón Ø100 (0-14 MPa)", ult: sumar(HOY, -410), cada: 730, tipo: "Calibración del fabricante (Res. 349/07 art. 15 l)" },
    { id: "B-1", desc: "Balanza de carga manuales (división 10 g)", ult: sumar(HOY, -150), cada: 365, tipo: "Calibración anual (criterio)" },
    { id: "B-2", desc: "Balanza de carga carros (división 50 g)", ult: sumar(HOY, -340), cada: 365, tipo: "Calibración anual (criterio)" },
  ];
  return { clientes, ordenes, remitos, recargas, reclamos, desvios, insumos, medicion, eventos: [], nRc: 119, nRd: 66, nOs: no, nRem: nr };
}

let S;
function cargar() {
  try { const g = localStorage.getItem(CLAVE); if (g) { S = JSON.parse(g); return; } } catch (e) {}
  S = semillaEstado();
}
function guardar() { try { localStorage.setItem(CLAVE, JSON.stringify(S)); } catch (e) {} }
function reiniciar() { try { localStorage.removeItem(CLAVE); } catch (e) {} S = semillaEstado(); }
function registrar(tipo, ref, detalle = "") { S.eventos.unshift({ t: new Date().toISOString(), tipo, ref, detalle, quien: "T. Sinay" }); guardar(); }

// ---------------------------------------------------------------- consultas
const cliente = id => S.clientes.find(c => c.id === id) || { nombre: id, id };
const ordenDe = n => { let a = 0, b = S.ordenes.length - 1; while (a <= b) { const m = (a + b) >> 1, o = S.ordenes[m]; if (n < o.desde) b = m - 1; else if (n > o.hasta) a = m + 1; else return o; } return null; };
const remito = id => S.remitos.find(r => r.id === id);
const modeloBOM = nombre => D.modelos.find(m => (m.nombre + " ").includes(nombre.replace("Carro ", "") + " "));
function masaCarga(n, o) {      // masa de carga de prueba dentro de la banda del BOM, determinística por serie
  const m = modeloBOM(o.modelo); if (!m) return null;
  const r = semilla(n), u = (r() + r() + r()) / 3;
  return m.min + (m.max - m.min) * (0.25 + 0.5 * u);
}
function equipo(n) {
  const o = ordenDe(n); if (!o) return null;
  const rech = o.rech.find(x => x.n === n), h = hashN("eq" + n) % 100;
  const e = { n, s: ser(n), o, rech, fab: o.cierre, estado: "En producción", custodia: "FLAMA", cliente: null, instalado: null };
  if (rech && o.etapa >= E["Para cerrar"]) { e.estado = "Rechazado"; return e; }
  if (o.etapa === E["Para etiquetar"]) e.estado = (n - o.desde) < o.etiquetados + o.rech.filter(x => x.n < n).length ? "En depósito PT" : "Para etiquetar";
  if (o.etapa === E["Depósito PT"]) e.estado = "En depósito PT";
  if (o.etapa === E["Despachada"] && o.remito) {
    const rm = remito(o.remito);
    e.remito = rm; e.custodia = rm.estado === "En tránsito" ? "Transportista" : cliente(rm.cliente).nombre;
    e.estado = rm.estado === "En tránsito" ? "En tránsito" : "En distribuidor";
    const edad = dias(rm.fecha);
    if (rm.estado === "Recibido" && h < Math.min(85, edad * 1.2)) {
      const finales = S.clientes.filter(c => c.tipo !== "Distribuidor"), c = finales[hashN("cl" + n) % finales.length];
      e.estado = "Instalado"; e.cliente = c; e.custodia = c.nombre; e.instalado = sumar(rm.fecha, 3 + (h % Math.max(1, edad - 3)));
    }
  }
  if (e.fab) { e.mant = sumar(e.fab, 365); e.phVence = sumar(e.fab, 365 * 5); e.vida = sumar(e.fab, 365 * 20); }
  return e;
}
const estadoPill = { "En producción": "gr", "Para etiquetar": "av", "En depósito PT": "in", "En tránsito": "vi", "En distribuidor": "in", "Instalado": "ok", "Rechazado": "no", "Inutilizado": "no" };
const etapaPill = i => i === E["Despachada"] ? "ok" : i === E["Depósito PT"] ? "in" : i >= E["Para cerrar"] ? "av" : i === 0 ? "gr" : "vi";
