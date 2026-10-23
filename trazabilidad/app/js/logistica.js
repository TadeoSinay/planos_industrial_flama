// ================================================================ logística: expedición y equipos
const estRem = { "Preparado": "gr", "En tránsito": "vi", "Sin confirmar": "av", "Recibido": "ok" };
const uRem = r => r.ops.reduce((a, op) => a + aptos(S.ordenes.find(o => o.op === op)), 0);

VISTAS.expedicion = {
  titulo: "Expedición",
  sub: () => "Stock de producto terminado, remitos y confirmación de recepción",
  acciones: () => `<button class="btn pri" data-a="nuevoRemito">Nuevo remito</button>`,
  html() {
    const pt = S.ordenes.filter(o => o.etapa === E["Depósito PT"]);
    const porModelo = {}; pt.forEach(o => porModelo[o.modelo] = (porModelo[o.modelo] || 0) + aptos(o));
    const rems = S.remitos.slice().reverse().filter(r => fil("rest", "abiertos") === "todos" || r.estado !== "Recibido").slice(0, 60);
    const sinConf = S.remitos.filter(r => r.estado === "Sin confirmar" || (r.estado === "En tránsito" && dias(r.fecha) > 2));
    return `<div class="kpis"><div class="kpi in"><span>Equipos en depósito PT</span><b>${n0(Object.values(porModelo).reduce((a, b) => a + b, 0))}</b><small>${pt.length} lotes</small></div>
      <div class="kpi vi" style="border-left-color:var(--violet)"><span>En tránsito</span><b>${S.remitos.filter(r => r.estado === "En tránsito").length}</b><small>remitos</small></div>
      <div class="kpi ${sinConf.length ? "av" : "ok"}"><span>Sin confirmar recepción</span><b>${sinConf.length}</b><small>más de 48 h: aviso a ventas</small></div>
      <div class="kpi ok"><span>Remitos del mes</span><b>${S.remitos.filter(r => new Date(r.fecha).getMonth() + 1 === D.mes).length}</b><small>${n0(S.remitos.filter(r => new Date(r.fecha).getMonth() + 1 === D.mes).reduce((a, r) => a + uRem(r), 0))} equipos</small></div></div>
      ${UI.f.nuevoRem ? formRemito() : ""}
      <div class="grilla"><div class="panel c5"><header><h2>Depósito PT</h2></header>${tabla(["Orden", "Modelo", "Equipos", ""], pt.map(o => `<tr><td class="mono"><a href="#" data-det="orden" data-id="${o.op}">${o.op}</a></td><td>${esc(o.modelo)}</td><td class="num">${aptos(o)}</td><td class="num"><button class="btn sm" data-a="nuevoRemito" data-id="${o.op}">Despachar</button></td></tr>`), { vacio: "Depósito vacío" })}</div>
      <div class="panel c7"><header><h2>Remitos</h2>${chips("rest", [["abiertos", "Abiertos"], ["todos", "Últimos"]], "abiertos")}</header>${tabla(["Remito", "Fecha", "Cliente", "Equipos", "Estado"], rems.map(r => `<tr class="click" data-det="remito" data-id="${r.id}"><td class="mono nw">${r.id}</td><td class="nw">${fecha(r.fecha)}</td><td>${esc(cliente(r.cliente).nombre)}</td><td class="num">${uRem(r)}</td><td>${pill(r.estado, estRem[r.estado])}</td></tr>`), { vacio: "No hay remitos abiertos" })}</div></div>`;
  },
};
function formRemito() {
  const pt = S.ordenes.filter(o => o.etapa === E["Depósito PT"]), sel = UI.f.remSel || [];
  const u = pt.filter(o => sel.includes(o.op)).reduce((a, o) => a + aptos(o), 0);
  return `<div class="panel"><header><h2>Nuevo remito</h2><button class="btn sm" data-a="cancelarRemito">Cancelar</button></header><div class="cuerpo"><form class="form" data-f="crearRemito">
    <label class="campo">Cliente<select id="remCli">${S.clientes.filter(c => c.tipo === "Distribuidor").map(c => `<option value="${c.id}">${esc(c.nombre)}</option>`).join("")}</select></label>
    <label class="campo">COT de ARBA (si corresponde)<input id="remCot" placeholder="código COT"></label>
    <div class="campo ancho">Órdenes a despachar<div class="filtros">${pt.map(o => `<button type="button" aria-pressed="${sel.includes(o.op)}" data-a="remToggle" data-id="${o.op}">${o.op} · ${esc(o.modelo)} · ${aptos(o)} u</button>`).join("") || `<span class="muted">No hay stock en depósito</span>`}</div></div>
    <div class="ancho aviso av">${u} extintores UN 1044 clase 2.2: verificá la cantidad exenta de la Res. 195/97 antes de cargar.</div>
    <div class="ancho"><button class="btn pri" type="submit" ${sel.length ? "" : "disabled"}>Emitir remito</button></div></form></div></div>`;
}
ACC.nuevoRemito = el => { UI.f.nuevoRem = true; UI.f.remSel = el && el.dataset && el.dataset.id ? [el.dataset.id] : []; if (UI.vista !== "expedicion") ir("expedicion"); else { ACC.cerrarDetalle(); pintar(); } };
ACC.cancelarRemito = () => { UI.f.nuevoRem = false; pintar(); };
ACC.remToggle = el => { const s = UI.f.remSel || (UI.f.remSel = []), i = s.indexOf(el.dataset.id); i < 0 ? s.push(el.dataset.id) : s.splice(i, 1); pintar(); };
FORM.crearRemito = () => {
  const r = { id: `R 0001-${String(++S.nRem).padStart(8, "0")}`, fecha: HOY, cliente: $("#remCli").value, ops: UI.f.remSel.slice(), estado: "Preparado", recibido: null, cot: $("#remCot").value };
  r.ops.forEach(op => { const o = S.ordenes.find(x => x.op === op); o.etapa = E["Despachada"]; o.remito = r.id; });
  S.remitos.push(r); UI.f.nuevoRem = false; registrar("Remito emitido", r.id, r.ops.join(", ")); toast(`${r.id} emitido`); pintar(); abrirDetalle("remito", r.id);
};
DETALLES.remito = id => {
  const r = remito(id); if (!r) return null;
  const c = cliente(r.cliente), pie = r.estado === "Preparado" ? `<button class="btn pri" data-a="remSalida" data-id="${r.id}">Confirmar salida</button>`
    : r.estado !== "Recibido" ? `<button class="btn ok" data-a="remRecibido" data-id="${r.id}">Registrar recepción</button>` : "";
  return { titulo: r.id, sub: `${esc(c.nombre)} · ${fecha(r.fecha)}`, pie,
    cuerpo: `<div style="display:grid;grid-template-columns:110px 1fr;gap:14px;align-items:start"><div class="qr">${qr("https://trazabilidad-flama.vercel.app/r/" + r.id.replace(/\s/g, ""))}</div>
      <dl class="dl"><dt>Estado</dt><dd>${pill(r.estado, estRem[r.estado])}</dd><dt>Cliente</dt><dd><a href="#" data-det="cliente" data-id="${c.id}">${esc(c.nombre)}</a> · ${esc(c.loc)}</dd><dt>Equipos</dt><dd>${uRem(r)}</dd><dt>Recibido</dt><dd>${fecha(r.recibido)}</dd>${r.cot ? `<dt>COT</dt><dd class="mono">${esc(r.cot)}</dd>` : ""}</dl></div>
      <div><h3>Órdenes</h3>${tabla(["Orden", "Modelo", "Equipos", "Series"], r.ops.map(op => { const o = S.ordenes.find(x => x.op === op); return `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td>${esc(o.modelo)}</td><td class="num">${aptos(o)}</td><td class="mono nw">${ser(o.desde)} → ${ser(o.hasta).slice(3)}</td></tr>`; }))}</div>` };
};
ACC.remSalida = el => { const r = remito(el.dataset.id); r.estado = "En tránsito"; registrar("Salida confirmada por el chofer", r.id); toast("En tránsito"); pintar(); };
ACC.remRecibido = el => { const r = remito(el.dataset.id); r.estado = "Recibido"; r.recibido = HOY; registrar("Recepción confirmada", r.id, cliente(r.cliente).nombre); toast("Recepción registrada"); pintar(); };

// ---------------------------------------------------------------- equipos
VISTAS.equipos = {
  titulo: "Equipos",
  sub: () => `${n0(S.ordenes[S.ordenes.length - 1].hasta)} series de ${D.anio} · ${ser(1)} a ${ser(S.ordenes[S.ordenes.length - 1].hasta)}`,
  acciones: () => `<button class="btn" data-a="csvEquipos">Copiar página para Sheets</button>`,
  html() {
    const est = fil("eest", "Todos"), mod = fil("emod", "Todos"), q = (UI.f.eq || "").trim();
    const max = S.ordenes[S.ordenes.length - 1].hasta, lista = [];
    for (let n = max; n >= 1 && lista.length < 2000; n--) {
      if (q && !ser(n).includes(q)) continue;
      const o = ordenDe(n); if (mod !== "Todos" && o.modelo !== mod) continue;
      const e = equipo(n); if (est !== "Todos" && e.estado !== est) continue; lista.push(e);
    }
    const p = UI.pag.equipos || 0, pag = lista.slice(p * 50, p * 50 + 50);
    const conteo = {}; for (let n = 1; n <= max; n++) { const e = equipo(n); conteo[e.estado] = (conteo[e.estado] || 0) + 1; }
    UI.eqPag = pag;
    return `<div class="kpis">${["En producción", "En depósito PT", "En tránsito", "En distribuidor", "Instalado", "Rechazado"].map(k => `<a href="#" class="kpi ${estadoPill[k] === "ok" ? "ok" : estadoPill[k] === "no" ? "no" : "in"}" data-a="filtro" data-k="eest" data-v="${k}"><span>${k}</span><b>${n0(conteo[k] || 0)}</b></a>`).join("")}</div>
      <div class="panel"><header><div class="filtros"><input id="eq" type="search" placeholder="Serie" value="${esc(q)}" aria-label="Buscar serie" data-in="eq">
        <select aria-label="Modelo" data-k="emod" data-cambio="filtroSel"><option>Todos</option>${[...new Set(S.ordenes.map(o => o.modelo))].map(m => `<option ${mod === m ? "selected" : ""}>${esc(m)}</option>`).join("")}</select>
        <select aria-label="Estado" data-k="eest" data-cambio="filtroSel"><option>Todos</option>${Object.keys(estadoPill).filter(k => k !== "Inutilizado").map(k => `<option ${est === k ? "selected" : ""}>${k}</option>`).join("")}</select></div><span class="muted">${n0(lista.length)}${lista.length === 2000 ? "+" : ""} equipos</span></header>
      ${tabla(["Serie", "Modelo", "Orden", "Fabricado", "Estado", "Custodia", "Mantenimiento"], pag.map(e => `<tr class="click" data-det="equipo" data-id="${e.n}"><td class="mono">${e.s}</td><td class="nw">${esc(e.o.modelo)}</td><td class="mono nw">${e.o.op}</td><td class="nw">${fecha(e.fab)}</td><td>${pill(e.estado, estadoPill[e.estado])}</td><td>${esc(e.custodia)}</td><td class="nw">${fecha(e.mant)}</td></tr>`), { vacio: "Ningún equipo con ese filtro" })}
      <div class="paginas">página ${p + 1} de ${Math.max(1, Math.ceil(lista.length / 50))} <button class="btn sm" data-a="pag" data-d="-1" ${p ? "" : "disabled"}>‹</button><button class="btn sm" data-a="pag" data-d="1" ${(p + 1) * 50 < lista.length ? "" : "disabled"}>›</button></div></div>`;
  },
};
ACC.pag = el => { UI.pag[UI.vista] = Math.max(0, (UI.pag[UI.vista] || 0) + +el.dataset.d); pintar(); };
ACC.csvEquipos = () => copiar(["serie\tmodelo\torden\tfabricado\testado\tcustodia\tmantenimiento", ...(UI.eqPag || []).map(e => [e.s, e.o.modelo, e.o.op, fecha(e.fab), e.estado, e.custodia, fecha(e.mant)].join("\t"))].join("\n"));
DETALLES.equipo = id => {
  const e = equipo(+id); if (!e) return null;
  const o = e.o, m = modeloBOM(o.modelo), masa = !e.rech && o.etapa >= E["Para etiquetar"] ? masaCarga(e.n, o) : null;
  const hist = [[o.emision, "Orden emitida", o.op], [o.etapa >= 1 ? o.emision : null, "Grabado en la planchuela", "G2 · Pannier"],
    [o.etapa >= E["Para etiquetar"] ? (o.cierre || HOY) : null, e.rech ? "Rechazado: " + e.rech.causa : "Ensayos aprobados", e.rech ? "calidad" : `PH ${o.carro ? PH.car : PH.man}`, e.rech],
    [!e.rech && o.etapa >= E["Depósito PT"] ? o.cierre : null, "Identificado · estampilla " + estampilla(e.n), "puesto 24"],
    [e.remito ? e.remito.fecha : null, "Despachado", e.remito ? e.remito.id : ""], [e.remito && e.remito.recibido ? e.remito.recibido : null, "Recibido", e.remito ? cliente(e.remito.cliente).nombre : ""],
    [e.instalado, "Instalado", e.cliente ? e.cliente.nombre : ""], [e.mant, "Mantenimiento anual", "vence", false, true]];
  return { titulo: e.s, sub: `${esc(o.modelo)} · ${pill(e.estado, estadoPill[e.estado])}`,
    cuerpo: `<div style="display:grid;grid-template-columns:120px 1fr;gap:14px;align-items:start"><div class="qr">${qr(D.url + e.s)}</div>
      <dl class="dl"><dt>Orden</dt><dd><a href="#" data-det="orden" data-id="${o.op}">${o.op}</a> · ${o.partida}</dd><dt>Fabricado</dt><dd>${fecha(e.fab)}</dd><dt>Custodia</dt><dd>${esc(e.custodia)}</dd>
      <dt>Carga</dt><dd>${masa ? `${nf(masa, 3)} kg (${nf(m.min, 2)}-${nf(m.max, 2)})` : "—"}</dd><dt>Prueba hidráulica</dt><dd>${e.phVence ? "vence " + fecha(e.phVence) : "—"}</dd><dt>Vida útil</dt><dd>${e.vida ? "hasta " + fecha(e.vida) : "—"}</dd></dl></div>
      <div><h3>Historia</h3><ul class="tl">${hist.filter(h => h[0] || h[4]).map(([f, t, d, no, fut]) => `<li class="${no ? "no" : fut || !f || new Date(f) > HOY ? "p" : ""}"><time>${fecha(f)}</time><i></i><span><b>${esc(t)}</b>${d ? ` · ${esc(d)}` : ""}</span></li>`).join("")}</ul></div>
      <div><h3>Insumos del lote</h3><dl class="dl">${Object.entries(o.insumos).map(([k, v]) => `<dt>${k[0].toUpperCase() + k.slice(1)}</dt><dd><a href="#" class="mono" data-det="loteMP" data-id="${v}">${v}</a></dd>`).join("")}</dl></div>` };
};
DETALLES.loteMP = id => {
  const os = S.ordenes.filter(o => Object.values(o.insumos).includes(id)); if (!os.length) return null;
  const u = os.reduce((a, o) => a + aptos(o), 0), dists = new Set(os.filter(o => o.remito).map(o => remito(o.remito).cliente));
  return { titulo: `Lote ${id}`, sub: `${os.length} órdenes · ${n0(u)} equipos aptos`,
    pie: `<button class="btn" data-a="copiarSeries" data-id="${id}">Copiar series</button>`,
    cuerpo: `<div class="kpis"><div class="kpi in"><span>Equipos</span><b>${n0(u)}</b></div><div class="kpi in"><span>Distribuidores</span><b>${dists.size}</b></div><div class="kpi in"><span>En depósito</span><b>${n0(os.filter(o => o.etapa === E["Depósito PT"]).reduce((a, o) => a + aptos(o), 0))}</b></div></div>
      ${tabla(["Orden", "Modelo", "Equipos", "Etapa", "Remito"], os.map(o => `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td>${esc(o.modelo)}</td><td class="num">${aptos(o)}</td><td>${pill(ETAPAS[o.etapa], etapaPill(o.etapa))}</td><td class="mono nw">${o.remito || "—"}</td></tr>`))}` };
};
ACC.copiarSeries = el => { const out = []; S.ordenes.filter(o => Object.values(o.insumos).includes(el.dataset.id)).forEach(o => { const rs = new Set(o.rech.map(x => x.n)); for (let n = o.desde; n <= o.hasta; n++) if (!rs.has(n)) out.push(ser(n)); }); copiar(out.join("\n")); };
