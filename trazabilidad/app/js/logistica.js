// ================================================================ extraplanta: expedición, instalaciones y equipos
const estRem = { "Preparado": "gr", "En tránsito": "vi", "Sin confirmar": "av", "Recibido": "ok" };
const uRem = r => r.ops.reduce((a, op) => a + aptos(S.ordenes.find(o => o.op === op)), 0);
const ok_ = v => v ? "✓" : `<b style="color:var(--red)">✗</b>`;

VISTAS.expedicion = {
  titulo: "Expedición",
  sub: () => "Stock de producto terminado, remitos con QR, salida del chofer y recepción del distribuidor",
  acciones: () => `<button class="btn pri" data-a="nuevoRemito">Nuevo remito</button>`,
  html() {
    const pt = S.ordenes.filter(o => o.etapa === E["Depósito PT"]);
    const rems = S.remitos.slice().reverse().filter(r => fil("rest", "abiertos") === "todos" || r.estado !== "Recibido").slice(0, 60);
    const sinConf = S.remitos.filter(r => r.estado === "Sin confirmar" || (r.estado === "En tránsito" && dias(r.fecha) > 2));
    const recib = S.remitos.filter(r => r.recibido), lead = recib.length ? recib.reduce((a, r) => a + dias(r.fecha, r.recibido), 0) / recib.length : 0;
    return `<div class="kpis"><div class="kpi in"><span>Equipos en depósito PT</span><b>${n0(pt.reduce((a, o) => a + aptos(o), 0))}</b><small>${pt.length} lotes</small></div>
      <div class="kpi in"><span>En tránsito</span><b>${S.remitos.filter(r => r.estado === "En tránsito").length}</b><small>remitos</small></div>
      <div class="kpi ${sinConf.length ? "av" : "ok"}"><span>Sin confirmar recepción</span><b>${sinConf.length}</b><small>más de 48 h: aviso a ventas</small></div>
      <div class="kpi ok"><span>Despacho → recepción</span><b>${nf(lead, 1)} d</b><small>promedio de ${recib.length} remitos</small></div>
      <div class="kpi ok"><span>Remitos del mes</span><b>${S.remitos.filter(r => new Date(r.fecha).getMonth() + 1 === D.mes).length}</b><small>${n0(S.remitos.filter(r => new Date(r.fecha).getMonth() + 1 === D.mes).reduce((a, r) => a + uRem(r), 0))} equipos</small></div></div>
      ${UI.f.nuevoRem ? formRemito() : ""}
      <div class="grilla"><div class="panel c5"><header><h2>Depósito PT</h2></header>${tabla(["Orden", "Modelo", "Equipos", "Pallet", ""], pt.map(o => `<tr><td class="mono"><a href="#" data-det="orden" data-id="${o.op}">${o.op}</a></td><td>${esc(o.modelo)}</td><td class="num">${aptos(o)}</td><td class="mono muted">${o.pallet.slice(-9)}</td><td class="num"><button class="btn sm" data-a="nuevoRemito" data-id="${o.op}">Despachar</button></td></tr>`), { vacio: "Depósito vacío" })}</div>
      <div class="panel c7"><header><h2>Remitos</h2>${chips("rest", [["abiertos", "Abiertos"], ["todos", "Últimos"]], "abiertos")}</header>${tabla(["Remito", "Fecha", "Cliente", "Transporte", "Equipos", "Estado"], rems.map(r => `<tr class="click" data-det="remito" data-id="${r.id}"><td class="mono nw">${r.id}</td><td class="nw">${fecha(r.fecha)}</td><td>${esc(cliente(r.cliente).nombre)}</td><td class="muted nw">${esc(r.transp || "—")} ${r.patente || ""}</td><td class="num">${uRem(r)}</td><td>${pill(r.estado, estRem[r.estado])}</td></tr>`), { vacio: "No hay remitos abiertos" })}</div></div>`;
  },
};
function formRemito() {
  const pt = S.ordenes.filter(o => o.etapa === E["Depósito PT"]), sel = UI.f.remSel || [];
  const u = pt.filter(o => sel.includes(o.op)).reduce((a, o) => a + aptos(o), 0);
  return `<div class="panel"><header><h2>Nuevo remito</h2><button class="btn sm" data-a="cancelarRemito">Cancelar</button></header><div class="cuerpo"><form class="form" data-f="crearRemito">
    <label class="campo">Cliente<select id="remCli">${S.clientes.filter(c => c.tipo === "Distribuidor").map(c => `<option value="${c.id}">${esc(c.nombre)}</option>`).join("")}</select></label>
    <label class="campo">Transporte<select id="remTr">${TRANSP.map((t, i) => `<option value="${i}">${t[0]} · ${t[1]}</option>`).join("")}</select></label>
    <label class="campo">COT de ARBA (si corresponde)<input id="remCot" placeholder="código COT"></label><span></span>
    <div class="campo ancho">Órdenes a despachar<div class="filtros">${pt.map(o => `<button type="button" aria-pressed="${sel.includes(o.op)}" data-a="remToggle" data-id="${o.op}">${o.op} · ${esc(o.modelo)} · ${aptos(o)} u</button>`).join("") || `<span class="muted">No hay stock en depósito</span>`}</div></div>
    <div class="ancho aviso av">${u} extintores UN 1044 clase 2.2: verificá la cantidad exenta de la Res. 195/97 antes de cargar. Carta de porte suscripta por FLAMA (CCyCN art. 1298).</div>
    <div class="ancho"><button class="btn pri" type="submit" ${sel.length ? "" : "disabled"}>Emitir remito</button></div></form></div></div>`;
}
ACC.nuevoRemito = el => { UI.f.nuevoRem = true; UI.f.remSel = el && el.dataset && el.dataset.id ? [el.dataset.id] : []; if (UI.vista !== "expedicion") ir("expedicion"); else { ACC.cerrarDetalle(); pintar(); } };
ACC.cancelarRemito = () => { UI.f.nuevoRem = false; pintar(); };
ACC.remToggle = el => { const s = UI.f.remSel || (UI.f.remSel = []), i = s.indexOf(el.dataset.id); i < 0 ? s.push(el.dataset.id) : s.splice(i, 1); pintar(); };
FORM.crearRemito = () => {
  const t = TRANSP[+$("#remTr").value];
  const r = { id: `R 0001-${String(++S.nRem).padStart(8, "0")}`, fecha: HOY, cliente: $("#remCli").value, ops: UI.f.remSel.slice(), estado: "Preparado", recibido: null, cot: $("#remCot").value, transp: t[0], patente: t[1], recibe: null };
  r.ops.forEach(op => { const o = S.ordenes.find(x => x.op === op); o.etapa = E["Despachada"]; o.remito = r.id; });
  S.remitos.push(r); UI.f.nuevoRem = false; registrar("Remito emitido", r.id, r.ops.join(", ")); r.ops.forEach(op => registrar("Despachado", op, r.id)); toast(`${r.id} emitido`); pintar(); abrirDetalle("remito", r.id);
};
DETALLES.remito = id => {
  const r = remito(id); if (!r) return null;
  const c = cliente(r.cliente), pie = r.estado === "Preparado" ? `<button class="btn pri" data-a="remSalida" data-id="${r.id}">Confirmar salida</button>`
    : r.estado !== "Recibido" ? `<button class="btn ok" data-a="remRecibido" data-id="${r.id}">Registrar recepción</button>` : "";
  return { titulo: r.id, sub: `${esc(c.nombre)} · ${fecha(r.fecha)}`, pie,
    cuerpo: `<div class="qrgrid" style="display:grid;grid-template-columns:110px 1fr;gap:14px;align-items:start"><div class="qr">${qr("https://trazabilidad-flama.vercel.app/r/" + r.id.replace(/\s/g, ""))}</div>
      <dl class="dl"><dt>Estado</dt><dd>${pill(r.estado, estRem[r.estado])}</dd><dt>Cliente</dt><dd><a href="#" data-det="cliente" data-id="${c.id}">${esc(c.nombre)}</a> · ${esc(c.loc)}</dd><dt>Transporte</dt><dd>${esc(r.transp || "—")} · ${r.patente || ""}</dd>
      <dt>Equipos</dt><dd>${uRem(r)} · UN 1044</dd><dt>Recibió</dt><dd>${r.recibido ? `${fecha(r.recibido)} · ${esc(r.recibe || "")}` : "—"}</dd><dt>COT</dt><dd class="mono">${esc(r.cot || "—")}</dd></dl></div>
      <div><h3>Órdenes y pallets</h3>${tabla(["Orden", "Modelo", "Equipos", "Pallet SSCC"], r.ops.map(op => { const o = S.ordenes.find(x => x.op === op); return `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td>${esc(o.modelo)}</td><td class="num">${aptos(o)}</td><td class="mono">${o.pallet}</td></tr>`; }))}</div>` };
};
ACC.remSalida = el => { const r = remito(el.dataset.id); r.estado = "En tránsito"; registrar("Salida confirmada por el chofer", r.id, `${r.transp} ${r.patente}`); toast("En tránsito"); pintar(); };
ACC.remRecibido = el => { const r = remito(el.dataset.id); r.estado = "Recibido"; r.recibido = HOY; r.recibe = "recepción del distribuidor"; registrar("Recepción confirmada", r.id, cliente(r.cliente).nombre); toast("Recepción registrada"); pintar(); };

// ---------------------------------------------------------------- instalaciones
function instalados(desde = sumar(HOY, -60)) { const out = []; for (let n = maxSerie(); n >= 1 && out.length < 400; n--) { const e = equipo(n); if (e.inst && new Date(e.inst.fecha) >= desde) out.push(e); } return out.sort((a, b) => new Date(b.inst.fecha) - new Date(a.inst.fecha)); }
VISTAS.instalaciones = {
  titulo: "Instalaciones",
  sub: () => "Entrega al usuario: datos de la tarjeta oficial (DPS en PBA, SGM en CABA), ubicación, alturas (IRAM 3517-2 6.2.14 y 7.3) y garantía",
  acciones: () => `<button class="btn pri" data-a="nuevaInst">Registrar instalación</button>`,
  html() {
    const xs = instalados(), mes = xs.filter(e => new Date(e.inst.fecha).getMonth() + 1 === D.mes);
    let tot = 0, caba = 0; for (let n = 1; n <= maxSerie(); n++) { const e = equipo(n); if (e.inst) { tot++; if (cliente(e.inst.cliente).jur === "CABA") caba++; } }
    return `<div class="kpis"><div class="kpi ok"><span>Equipos instalados</span><b>${n0(tot)}</b><small>en ${D.anio}</small></div><div class="kpi in"><span>Instalados este mes</span><b>${mes.length}</b></div>
      <div class="kpi in"><span>Tarjetas DPS (PBA)</span><b>${n0(tot - caba)}</b><small>tarjeta + estampilla de control</small></div><div class="kpi in"><span>Tarjetas SGM (CABA)</span><b>${n0(caba)}</b><small>proceso batch de la AGC</small></div>
      <div class="kpi ok"><span>Garantías vigentes</span><b>${n0(xs.filter(e => new Date(e.garantia) > HOY).length)}</b><small>6 meses desde la entrega (Ley 24.240 art. 11)</small></div></div>
      ${UI.f.nuevaInst ? formInst() : ""}
      <div class="panel"><header><h2>Últimas instalaciones</h2><span class="muted">últimos 60 días</span></header>${tabla(["Serie", "Modelo", "Usuario", "Jurisd.", "Ubicación", "Parte sup.", "Cartel", "Tarjeta", "Instalador", "Fecha", "Garantía"], xs.slice(0, 80).map(e => { const c = cliente(e.inst.cliente);
        return `<tr class="click" data-det="equipo" data-id="${e.n}"><td class="mono">${e.s}</td><td class="nw">${esc(e.o.modelo)}</td><td>${esc(c.nombre)}</td><td>${c.jur}</td><td>${esc(e.inst.ubic)}</td><td class="num">${nf(e.inst.alt, 2)} ${ok_(e.inst.alt <= 1.5 && e.inst.alt >= 0.1)}</td><td class="num">${nf(e.inst.cartel, 2)} ${ok_(e.inst.cartel >= 2 && e.inst.cartel <= 2.5)}</td><td class="mono nw">${esc(e.inst.tarjeta)}</td><td>${esc(e.inst.instalador)}</td><td class="nw">${fecha(e.inst.fecha)}</td><td class="nw">${fecha(e.garantia)}</td></tr>`; }))}</div>`;
  },
};
function formInst() {
  const v = UI.f.inst || {}, alt = +(v.alt ?? 1.35), car = +(v.car ?? 2.2), okA = alt >= 0.1 && alt <= 1.5, okC = car >= 2 && car <= 2.5;
  return `<div class="panel"><header><h2>Registrar instalación</h2><button class="btn sm" data-a="cancelarInst">Cancelar</button></header><div class="cuerpo"><form class="form" data-f="crearInst">
    <label class="campo">Serie (equipo en el distribuidor)<input id="inSerie" value="${esc(v.serie || "")}" placeholder="${AA}-000000" data-in2="serie"></label>
    <label class="campo">Usuario<select id="inCli">${S.clientes.filter(c => c.tipo !== "Distribuidor").map(c => `<option value="${c.id}" ${v.cli === c.id ? "selected" : ""}>${esc(c.nombre)} · ${c.jur}</option>`).join("")}</select></label>
    <label class="campo">Ubicación<select id="inUb">${UBIC.map(u => `<option>${u}</option>`).join("")}</select></label><label class="campo">Instalador<select id="inInst">${OPER.map(u => `<option>${u}</option>`).join("")}</select></label>
    <label class="campo">Parte superior del equipo (m)<input id="inAlt" type="number" step="0.05" value="${alt}" data-in2="alt"></label><label class="campo">Cartel (m)<input id="inCar" type="number" step="0.05" value="${car}" data-in2="car"></label>
    <div class="ancho filtros"><span class="pill ${okA ? "ok" : "no"}">${okA ? "✓" : "✗"} 0,10 a 1,5 m (6.2.14)</span><span class="pill ${okC ? "ok" : "no"}">${okC ? "✓" : "✗"} cartel 2,0 a 2,5 m (7.3)</span></div>
    <label class="ancho" style="display:flex;gap:8px;font-size:13px"><input type="checkbox" id="inCons" checked> El titular recibió el aviso de datos personales (Ley 25.326 art. 6) y el certificado de garantía (Ley 24.240 art. 14)</label>
    <div class="ancho"><button class="btn pri" type="submit" ${okA && okC ? "" : "disabled"}>Registrar y emitir tarjeta</button></div></form></div></div>`;
}
ACC.nuevaInst = el => { UI.f.nuevaInst = true; UI.f.inst = { serie: el && el.dataset && el.dataset.id ? ser(+el.dataset.id) : "" }; if (UI.vista !== "instalaciones") ir("instalaciones"); else pintar(); };
ACC.cancelarInst = () => { UI.f.nuevaInst = false; pintar(); };
FORM.crearInst = () => {
  const n = numSerie($("#inSerie").value.trim()), e = n && equipo(n);
  if (!e || e.estado !== "En distribuidor" || e.tipo !== "Matafuego") return toast("La serie tiene que ser un matafuego que esté en un distribuidor");
  const c = cliente($("#inCli").value);
  S.inst[n] = { cliente: c.id, fecha: HOY, ubic: $("#inUb").value, alt: +$("#inAlt").value, cartel: +$("#inCar").value, instalador: $("#inInst").value,
    tarjeta: c.jur === "CABA" ? `SGM ${String(hashN("t" + n) % 1e7).padStart(7, "0")}` : `DPS T-${AA}-${String(hashN("t" + n) % 1e6).padStart(6, "0")}` };
  UI.f.nuevaInst = false; registrar("Instalado · garantía emitida", ser(n), `${c.nombre} · ${S.inst[n].tarjeta}`); toast(`${ser(n)} instalado`); ir("equipo", n);
};

// ---------------------------------------------------------------- equipos
VISTAS.equipos = {
  titulo: "Equipos",
  sub: () => `${n0(maxSerie())} series de ${D.anio} (matafuegos y cilindros) · ${ser(1)} a ${ser(maxSerie())} · más las etiquetas de servicio de recargas`,
  acciones: () => `<button class="btn" data-a="csvEquipos">Copiar página para Sheets</button>`,
  html() {
    const est = fil("eest", "Todos"), mod = fil("emod", "Todos"), tip = fil("etip", "Todos"), q = (UI.f.eq || "").trim();
    const max = maxSerie(), lista = [], conteo = {};
    for (let n = max; n >= 1; n--) {
      const e = equipo(n); conteo[e.estado] = (conteo[e.estado] || 0) + 1;
      if (lista.length >= 2000 || (q && !e.s.includes(q)) || (mod !== "Todos" && e.o.modelo !== mod) || (tip !== "Todos" && e.tipo !== tip) || (est !== "Todos" && e.estado !== est)) continue;
      lista.push(e);
    }
    const p = UI.pag.equipos || 0, pag = lista.slice(p * 50, p * 50 + 50); UI.eqPag = pag;
    return `<div class="kpis">${["En producción", "En depósito PT", "En tránsito", "En distribuidor", "Instalado", "Rechazado", "Inutilizado"].map(k => `<a href="#" class="kpi ${estadoPill[k] === "ok" ? "ok" : estadoPill[k] === "no" ? "no" : "in"}" data-a="filtro" data-k="eest" data-v="${k}"><span>${k}</span><b>${n0(conteo[k] || 0)}</b></a>`).join("")}</div>
      <div class="panel"><header><div class="filtros"><input id="eq" type="search" placeholder="Serie" value="${esc(q)}" aria-label="Buscar serie" data-in="eq">
        ${chips("etip", [["Todos", "Todos"], ["Matafuego", "Matafuegos"], ["Cilindro", "Cilindros"]], "Todos")}
        <select aria-label="Modelo" data-k="emod" data-cambio="filtroSel"><option>Todos</option>${[...new Set(S.ordenes.map(o => o.modelo))].map(m => `<option ${mod === m ? "selected" : ""}>${esc(m)}</option>`).join("")}</select>
        <select aria-label="Estado" data-k="eest" data-cambio="filtroSel"><option>Todos</option>${Object.keys(estadoPill).map(k => `<option ${est === k ? "selected" : ""}>${k}</option>`).join("")}</select></div><span class="muted">${n0(lista.length)}${lista.length === 2000 ? "+" : ""} equipos</span></header>
      ${tabla(["Serie", "Tipo", "Modelo", "Orden", "Fabricado", "Estado", "Custodia", "Mantenimiento"], pag.map(e => `<tr class="click" data-det="equipo" data-id="${e.n}"><td class="mono">${e.s}</td><td>${e.tipo}</td><td class="nw">${esc(e.o.modelo)}</td><td class="mono nw">${e.o.op}</td><td class="nw">${fecha(e.fab)}</td><td>${pill(e.estado, estadoPill[e.estado])}</td><td>${esc(e.custodia)}</td><td class="nw">${e.tipo === "Cilindro" ? "—" : fecha(e.mant)}</td></tr>`), { vacio: "Ningún equipo con ese filtro" })}
      <div class="paginas">página ${p + 1} de ${Math.max(1, Math.ceil(lista.length / 50))} <button class="btn sm" data-a="pag" data-d="-1" ${p ? "" : "disabled"}>‹</button><button class="btn sm" data-a="pag" data-d="1" ${(p + 1) * 50 < lista.length ? "" : "disabled"}>›</button></div></div>`;
  },
};
ACC.pag = el => { UI.pag[UI.vista] = Math.max(0, (UI.pag[UI.vista] || 0) + +el.dataset.d); pintar(); };
ACC.csvEquipos = () => copiar(["serie\ttipo\tmodelo\torden\tfabricado\testado\tcustodia\tmantenimiento", ...(UI.eqPag || []).map(e => [e.s, e.tipo, e.o.modelo, e.o.op, fecha(e.fab), e.estado, e.custodia, fecha(e.mant)].join("\t"))].join("\n"));

// ---------------------------------------------------------------- historial de un equipo
VISTAS.equipo = {
  titulo: () => esc(typeof UI.param === "number" ? ser(UI.param) : UI.param),
  sub: () => { if (typeof UI.param !== "number") { const r = S.recargas.find(x => x.etiqueta === UI.param); return r ? `${esc(r.tipo)} · ${esc(r.marca)} n° ${esc(r.nro)} · equipo de cliente en servicio` : ""; }
    const e = equipo(UI.param); return e ? `${esc(e.o.modelo)} · ${e.tipo.toLowerCase()} · ${pill(e.estado, estadoPill[e.estado])}` : ""; },
  acciones: () => { const e = typeof UI.param === "number" ? equipo(UI.param) : null;
    return `<a href="#equipos" data-v="equipos" class="btn">← Equipos</a>` + (e && e.estado === "En distribuidor" && e.tipo === "Matafuego" ? `<button class="btn pri" data-a="nuevaInst" data-id="${e.n}">Registrar instalación</button>` : "")
      + (e && e.estado === "Instalado" ? `<button class="btn" data-a="aRecarga" data-id="${e.s}">Recibir para servicio</button><button class="btn" data-a="inutilizarEq" data-id="${e.n}">Inutilizar</button>` : "")
      + (e ? `<button class="btn" data-a="trazaSerie" data-id="${e.s}">Ver traza</button>` : ""); },
  html() {
    if (typeof UI.param !== "number") return paginaServicio(UI.param);
    const e = equipo(UI.param); if (!e) return `<div class="aviso av">No existe la serie ${esc(UI.param)}.</div>`;
    const o = e.o, ens = ensayos(e.n, o), m = modeloBOM(o.modelo), c = e.inst ? cliente(e.inst.cliente) : null, rem = e.remito;
    const serv = S.recargas.filter(r => r.nro === e.s), recl = S.reclamos.filter(r => r.serie === e.s);
    const ident = `<div class="panel c5"><header><h2>Identificación</h2></header><div class="cuerpo qrgrid" style="display:grid;grid-template-columns:130px 1fr;gap:14px;align-items:start"><div class="qr">${qr(D.url + e.s)}</div>
      <dl class="dl" style="grid-template-columns:110px 1fr"><dt>Grabado</dt><dd class="mono">FLAMA S.A. N° ${e.s} ${AA} DPS</dd><dt>Dónde</dt><dd>${o.carro ? "franja en dos renglones entre los triángulos del eje" : "franja de la pollera, lado pared"}</dd>
      <dt>Estampilla</dt><dd class="mono">${o.etapa >= E["Depósito PT"] && !e.rech ? estampilla(e.n) : "—"}</dd><dt>Etiqueta</dt><dd>QR 45 × 25 · ${esc(D.url + e.s)}</dd><dt>Producto</dt><dd>${esc(m ? m.nombre : o.modelo)}${o.cilindro ? " · recipiente vacío" : ""} · IRAM ${m ? m.iram : "—"}</dd></dl></div></div>`;
    const estado = `<div class="panel c7"><header><h2>Estado y vencimientos</h2></header><div class="cuerpo"><dl class="dl"><dt>Estado</dt><dd>${pill(e.estado, estadoPill[e.estado])}</dd><dt>Custodia</dt><dd>${esc(e.custodia)}</dd>
      <dt>Fabricado</dt><dd>${fecha(e.fab)}</dd>${o.cilindro ? `<dt>Comprador</dt><dd>${rem ? esc(cliente(rem.cliente).nombre) : "—"} (recargador o fabricante que lo completa)</dd>` : `<dt>Garantía</dt><dd>${e.garantia ? "hasta " + fecha(e.garantia) + " (6 meses desde la entrega)" : "empieza con la entrega al usuario"}</dd>
      <dt>Mantenimiento</dt><dd>${e.mant ? "vence " + fecha(e.mant) + " (IRAM 3517-2 9.2)" : "—"}</dd>`}<dt>Prueba hidráulica</dt><dd>${e.phVence ? "próxima " + fecha(e.phVence) + " (cada 5 años, anexo E)" : "—"}</dd>
      <dt>Vida útil</dt><dd>${e.vida ? "hasta " + fecha(e.vida) + " (20 años, Res. 349/07 art. 26)" : "—"}</dd>${c ? `<dt>Tarjeta oficial</dt><dd class="mono">${esc(e.inst.tarjeta)}</dd>` : ""}${e.baja ? `<dt>Baja</dt><dd>${esc(e.baja.motivo)} · acta ${esc(e.baja.acta)}</dd>` : ""}</dl></div></div>`;
    const gene = `<div class="panel c6"><header><h2>Hacia atrás: de dónde viene</h2></header><div class="cuerpo"><dl class="dl"><dt>Orden</dt><dd><a href="#" data-det="orden" data-id="${o.op}">${o.op}</a> · partida ${o.partida}</dd>
      ${Object.entries(o.insumos).map(([k, v]) => `<dt>${k[0].toUpperCase() + k.slice(1)}</dt><dd class="mono"><a href="#" data-a="trazaLote" data-q="${esc(v.split(" · ")[0])}">${esc(v)}</a></dd>`).join("")}
      <dt>Medición</dt><dd>PH ${o.carro ? "PH-M2" : "PH-M1"} · balanza ${o.carro ? "B-2" : "B-1"} · patrón MP-PAT</dd></dl>
      <h3 style="margin-top:12px">Puestos</h3>${tabla(["Puesto", "Operación", "Firma", "Fecha"], hojaRuta(o).filter(h => h.etapa < E["Para etiquetar"]).map(h => `<tr><td class="mono">${h.puesto}</td><td>${esc(h.op)}</td><td>${esc(h.firma || "—")}</td><td class="nw">${h.fecha ? fecha(h.fecha) : "—"}</td></tr>`))}</div></div>`;
    const ensP = `<div class="panel c6"><header><h2>Ensayos de fábrica</h2></header><div class="cuerpo">${ens ? `<dl class="dl"><dt>Espesor</dt><dd>${nf(ens.esp.med, 2)} mm medido · ${nf(ens.esp.nom, 2)} mm de plano ${ok_(ens.esp.ok)}</dd>
      <dt>Prueba hidráulica</dt><dd>${nf(ens.ph.p, 1)} MPa · ${ens.ph.t} s · manómetro ${ens.ph.man} ${ok_(ens.ph.ok)}</dd>${ens.carga ? `<dt>Carga</dt><dd>${ens.carga.kg ? nf(ens.carga.kg, 3) + " kg" : "—"} · banda ${nf(m.min, 2)}-${nf(m.max, 2)} ${ok_(ens.carga.ok)}</dd><dt>Presurización</dt><dd>N₂ ${nf(ens.n2, 1)} MPa</dd><dt>Pérdidas</dt><dd>${ok_(ens.perd)}</dd>` : ""}
      <dt>Visual</dt><dd>${ok_(ens.visual)}</dd><dt>Resultado</dt><dd>${e.rech ? pill(e.rech.causa, "no") : pill("apto", "ok")}</dd><dt>Visado</dt><dd>${CALIDAD} · ${RT}</dd></dl>` : `<p class="muted" style="margin:0">El lote todavía no se cerró.</p>`}</div></div>`;
    const cust = [["FLAMA · depósito PT", o.etapa >= E["Depósito PT"] ? fecha(o.cierre) : "—", o.etapa >= E["Depósito PT"] ? `pallet SSCC ${o.pallet}` : "—"],
      ["Transportista", rem ? fecha(rem.fecha) : "—", rem ? `${rem.transp} · ${rem.patente} · ${rem.id}` : ""], ["Distribuidor", rem && rem.recibido ? fecha(rem.recibido) : "—", rem ? `${cliente(rem.cliente).nombre}${rem.recibe ? " · recibió " + rem.recibe : ""}` : ""],
      ...(o.cilindro ? [] : [["Usuario", e.inst ? fecha(e.inst.fecha) : "—", c ? `${c.nombre} · CUIT ${c.cuit} · ${c.loc} (${c.jur})` : ""]])];
    const custP = `<div class="panel c6"><header><h2>Hacia adelante: cadena de custodia</h2></header>${tabla(["Tenedor", "Desde", "Documento"], cust.map(([a, b, d]) => `<tr><td>${a}</td><td class="nw">${b}</td><td class="muted">${esc(d)}</td></tr>`))}</div>`;
    const instP = o.cilindro ? "" : `<div class="panel c6"><header><h2>Instalación</h2></header><div class="cuerpo">${e.inst ? `<dl class="dl"><dt>Usuario</dt><dd>${esc(c.nombre)} · ${esc(c.tipo)}</dd><dt>Ubicación</dt><dd>${esc(e.inst.ubic)}</dd>
      <dt>Parte superior</dt><dd>${nf(e.inst.alt, 2)} m ${ok_(e.inst.alt <= 1.5)} (IRAM 3517-2 6.2.14)</dd><dt>Cartel</dt><dd>${nf(e.inst.cartel, 2)} m ${ok_(e.inst.cartel >= 2 && e.inst.cartel <= 2.5)} (7.3)</dd>
      <dt>Tarjeta</dt><dd class="mono">${esc(e.inst.tarjeta)}</dd><dt>Instalador</dt><dd>${esc(e.inst.instalador)} · ${fecha(e.inst.fecha)}</dd></dl>` : `<p class="muted" style="margin:0">Todavía no se entregó al usuario.</p>`}</div></div>`;
    const servP = `<div class="panel c6"><header><h2>Servicios y reclamos</h2></header><div class="cuerpo">${serv.length || recl.length ? tabla(["Fecha", "Registro", "Estado"], [...serv.map(r => `<tr class="click" data-det="recarga" data-id="${r.os}"><td>${fecha(r.fecha)}</td><td class="mono">${r.os} · ficha rev. 1</td><td>${pill(ETAPAS_OS[r.etapa], "in")}</td></tr>`), ...recl.map(r => `<tr class="click" data-det="reclamo" data-id="${r.id}"><td>${fecha(r.fecha)}</td><td class="mono">${r.id} · ${esc(r.tipo)}</td><td>${pill(ETAPAS_RC[r.etapa], r.etapa === 3 ? "ok" : "av")}</td></tr>`)]) : `<p class="muted" style="margin:0">${o.cilindro ? "Sin servicios: se vendió vacío." : `Ficha rev. 0 de fábrica. Primer mantenimiento: ${fecha(e.mant)}.`}</p>`}</div></div>`;
    const hist = historia(e);
    const histP = `<div class="panel c12"><header><h2>Historial</h2><span class="muted">cada evento guarda el hash del anterior</span></header>${tabla(["Fecha", "Evento", "Detalle", "Quién", "Hash"], [...hist.map(([f, t, d, q, no]) => `<tr><td class="nw">${new Date(f).toLocaleString("es-AR", { day: "2-digit", month: "2-digit", year: "2-digit", hour: "2-digit", minute: "2-digit" })}</td><td>${no ? `<b style="color:var(--red)">${esc(t)}</b>` : esc(t)}</td><td class="muted">${esc(d)}</td><td>${esc(q || "")}</td><td class="mono muted" data-hash="${esc(e.s + f + t + d)}">…</td></tr>`),
      ...S.eventos.filter(x => x.ref === e.s).map(x => `<tr><td class="nw">${new Date(x.t).toLocaleString("es-AR")}</td><td>${esc(x.tipo)}</td><td class="muted">${esc(x.detalle)}</td><td>${esc(x.quien)}</td><td class="mono muted">${x.hash ? x.hash.slice(0, 16) + "…" : "…"}</td></tr>`)])}</div>`;
    return `<div class="grilla">${ident}${estado}${gene}${ensP}${custP}${instP}${servP}${histP}</div>`;
  },
};
function paginaServicio(et) {
  const r = S.recargas.find(x => x.etiqueta === et); if (!r) return `<div class="aviso av">No encontré la etiqueta ${esc(et)}.</div>`;
  const c = cliente(r.cliente), edad = D.anio - r.fab, phToca = edad > 0 && edad % 5 === 0;
  return `<div class="grilla"><div class="panel c5"><header><h2>Identificación</h2></header><div class="cuerpo qrgrid" style="display:grid;grid-template-columns:130px 1fr;gap:14px"><div class="qr">${qr(D.url + r.etiqueta)}</div>
    <dl class="dl" style="grid-template-columns:110px 1fr"><dt>Etiqueta</dt><dd class="mono">${r.etiqueta}</dd><dt>Equipo</dt><dd>${esc(r.tipo)} · ${esc(r.marca)}</dd><dt>N° del fabricante</dt><dd class="mono">${esc(r.nro)}</dd><dt>Fabricado</dt><dd>${r.fab}</dd><dt>Usuario</dt><dd>${esc(c.nombre)} · ${c.jur}</dd></dl></div></div>
    <div class="panel c7"><header><h2>Estado</h2></header><div class="cuerpo"><dl class="dl"><dt>Servicio actual</dt><dd><a href="#" data-det="recarga" data-id="${r.os}">${r.os}</a> · ${pill(r.inutil ? "a inutilizar" : ETAPAS_OS[r.etapa], r.inutil ? "no" : "in")}</dd>
      <dt>Vida útil</dt><dd>hasta ${r.fab + 20} ${r.fab + 20 < D.anio ? pill("vencida: inutilizar", "no") : pill("vigente", "ok")}</dd><dt>Prueba hidráulica</dt><dd>${phToca || r.ph ? "corresponde este año (anexo E)" : `próxima en ${r.fab + Math.ceil(Math.max(1, edad) / 5) * 5}`}</dd>
      <dt>Tarjeta oficial</dt><dd>${c.jur === "CABA" ? "SGM: se carga en el proceso batch al cerrar" : "tarjeta DPS + estampilla de control al cerrar"}</dd><dt>Sustituto</dt><dd>${r.sustituto || "no"}</dd></dl></div></div>
    <div class="panel c12"><header><h2>Fichas de servicio</h2></header>${tabla(["Rev.", "Fecha", "Servicio", "Agente", "Precinto", "Responsable"], [[1, fecha(r.fecha), r.inutil ? "Inutilización" : `Recarga${r.ph ? " + PH" : ""}${r.polvoBajo ? " · cambio total de polvo" : ""}`, r.agente, r.etapa >= 4 ? `P-${AA}-${String(hashN(r.os) % 1e5).padStart(5, "0")}` : "—", r.tecnico]].map(f => `<tr>${f.map(x => `<td>${esc(x)}</td>`).join("")}</tr>`))}</div></div>`;
}
ACC.trazaSerie = el => { UI.f.trq = el.dataset.id; ir("traza"); };
ACC.aRecarga = el => { UI.f.nuevaOS = true; UI.f.osSerie = el.dataset.id; ir("recargas"); };
ACC.inutilizarEq = el => { const n = +el.dataset.id; S.bajas[n] = { fecha: HOY, motivo: "Condición de inutilización en la revisión (IRAM 3517-2 anexo F)", acta: `AG-${AA}-${String(hashN("ag" + n) % 1e4).padStart(4, "0")}` };
  registrar("Inutilizado · acta", ser(n), S.bajas[n].acta); toast(`${ser(n)} dado de baja`); pintar(); };
