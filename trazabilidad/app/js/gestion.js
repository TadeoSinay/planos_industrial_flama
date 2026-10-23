// ================================================================ gestión: tablero, desvíos, insumos, reportes y configuración
function estadoInsumo(m) {
  const st = S.insumos[m.cod], dia = m.anio26 / 240, plazo = +(m.pmax || m.pmin || 10);
  if (!dia) return { k: "gr", t: "sin consumo en " + D.anio, cob: null };
  const cob = st.stock / dia;
  // criterio: pedir cuando la cobertura no llega al plazo máximo más la mitad
  return cob < plazo ? { k: "no", t: "pedir ya", cob } : cob < plazo * 1.5 ? { k: "av", t: "pedir", cob } : { k: "ok", t: "ok", cob };
}

// ---------------------------------------------------------------- tablero
VISTAS.tablero = {
  titulo: "Tablero",
  sub: () => `${HOY.toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}`,
  html() {
    const om = S.ordenes.filter(o => o.mes === D.mes), plan = D.plan.filter(p => p.tipo === "Terminado").reduce((a, p) => a + p.cant, 0);
    const hechos = om.filter(o => o.etapa >= E["Depósito PT"]).reduce((a, o) => a + aptos(o), 0);
    const cerr = om.filter(o => o.etapa >= E["Para etiquetar"]), tot = cerr.reduce((a, o) => a + o.cant, 0), rech = cerr.reduce((a, o) => a + o.rech.length, 0);
    const hab = habiles(D.anio, D.mes), trans = hab.filter(d => d <= HOY).length, esperado = Math.round(plan * trans / hab.length);
    const pt = S.ordenes.filter(o => o.etapa === E["Depósito PT"]).reduce((a, o) => a + aptos(o), 0);
    const alertas = [];
    S.medicion.forEach(m => { const f = m.cada - dias(m.ult); if (f < 0) alertas.push(["no", `${m.id}: control vencido hace ${-f} días`, "calidad"]); else if (f <= 3) alertas.push(["av", `${m.id}: el contraste vence en ${f} día${f === 1 ? "" : "s"}`, "calidad"]); });
    S.reclamos.filter(vencido).forEach(x => alertas.push(["no", `${x.id} (${x.tipo.toLowerCase()}) fuera de plazo`, "reclamos"]));
    S.remitos.filter(r => r.estado === "Sin confirmar").forEach(r => alertas.push(["av", `${r.id}: recepción sin confirmar hace ${dias(r.fecha)} días`, "expedicion"]));
    S.ordenes.filter(o => o.etapa === E["Para cerrar"]).forEach(o => alertas.push(["in", `${o.op} terminó carga: falta cerrar el lote`, "calidad"]));
    const ped = D.insumos.filter(m => estadoInsumo(m).k === "no"); if (ped.length) alertas.push(["no", `${ped.length} insumos debajo del plazo de reposición`, "insumos"]);
    S.recargas.filter(r => r.inutil).forEach(r => alertas.push(["av", `${r.os}: labrar acta de inutilización`, "recargas"]));
    // avance diario: aptos acumulados por fecha de cierre contra el plan lineal
    const W = 640, H = 200, l = 40, rr = 16, t = 12, b = 26, X = i => l + (W - l - rr) * i / (hab.length - 1), Y = v => t + (H - t - b) * (1 - v / plan);
    let ac = 0; const real = hab.filter(d => d <= HOY).map((d, i) => { ac += om.filter(o => o.cierre && new Date(o.cierre).toDateString() === d.toDateString()).reduce((a, o) => a + aptos(o), 0); return [X(i), Y(Math.min(ac, plan)), ac, d]; });
    const graf = `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Avance de producción del mes">${[0, .5, 1].map(f => `<line x1="${l}" x2="${W - rr}" y1="${Y(plan * f)}" y2="${Y(plan * f)}" class="grid"/><text x="${l - 6}" y="${Y(plan * f) + 4}" text-anchor="end">${n0(plan * f)}</text>`).join("")}
      <line x1="${X(0)}" y1="${Y(0)}" x2="${X(hab.length - 1)}" y2="${Y(plan)}" stroke="var(--ink-3)" stroke-dasharray="4 4" stroke-width="1.5"/>
      <path d="${real.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join("")}" fill="none" stroke="var(--blue)" stroke-width="2.5"/>
      ${real.length ? `<circle cx="${real[real.length - 1][0]}" cy="${real[real.length - 1][1]}" r="4.5" fill="var(--blue)" stroke="var(--surface)" stroke-width="2"/><text x="${real[real.length - 1][0] + 8}" y="${real[real.length - 1][1] - 6}" class="t-ink" style="font-weight:600">${n0(real[real.length - 1][2])}</text>` : ""}
      <text x="${l}" y="${H - 6}">1 ${MES_TXT[D.mes - 1].slice(0, 3)}</text><text x="${W - rr}" y="${H - 6}" text-anchor="end">plan ${n0(plan)} (punteado)</text></svg>`;
    return `<div class="kpis">
      <a href="#ordenes" data-v="ordenes" class="kpi ${hechos >= esperado * 0.95 ? "ok" : "av"}"><span>Producción del mes</span><b>${n0(hechos)}</b><small>de ${n0(plan)} · esperado a hoy ${n0(esperado)}</small></a>
      <a href="#ordenes" data-v="ordenes" class="kpi in"><span>Órdenes en curso</span><b>${om.filter(o => o.etapa > 0 && o.etapa < E["Depósito PT"]).length}</b><small>${om.filter(o => o.etapa === 0).length} planificadas</small></a>
      <a href="#calidad" data-v="calidad" class="kpi ${rech / Math.max(1, tot) < 0.02 ? "ok" : "av"}"><span>Rendimiento a la primera</span><b>${pct(tot - rech, tot)}</b><small>${rech} rechazos</small></a>
      <a href="#expedicion" data-v="expedicion" class="kpi in"><span>Stock PT</span><b>${n0(pt)}</b><small>${S.remitos.filter(r => r.estado !== "Recibido").length} remitos abiertos</small></a>
      <a href="#recargas" data-v="recargas" class="kpi in"><span>Recargas abiertas</span><b>${S.recargas.filter(r => r.etapa < 5).length}</b><small>${S.recargas.filter(r => r.etapa === 4).length} listas para entregar</small></a>
      <a href="#reclamos" data-v="reclamos" class="kpi ${S.reclamos.some(vencido) ? "no" : "ok"}"><span>Reclamos abiertos</span><b>${S.reclamos.filter(x => x.etapa < 3).length}</b><small>${S.reclamos.filter(vencido).length} fuera de plazo</small></a></div>
      <div class="grilla"><div class="panel c7"><header><h2>Avance del mes</h2><span class="muted">equipos aptos ingresados a depósito</span></header><div class="cuerpo">${graf}</div></div>
      <div class="panel c5"><header><h2>Pendientes</h2><span class="muted">${alertas.length}</span></header><div class="cuerpo"><ul class="lista-alertas">${alertas.map(([k, t, v]) => `<li class="${k}"><span>${esc(t)}</span><a href="#${v}" data-v="${v}" class="btn sm">Ver</a></li>`).join("") || `<li class="in"><span>Sin pendientes</span></li>`}</ul></div></div>
      <div class="panel c12"><header><h2>Órdenes del mes</h2><a href="#ordenes" data-v="ordenes" class="btn sm">Todas</a></header>${tabla(["Orden", "Modelo", "Cant", "Etapa", "Avance", "Rech"], om.filter(o => o.etapa < E["Despachada"]).map(o => `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td>${esc(o.modelo)}</td><td class="num">${o.cant}</td><td>${pill(ETAPAS[o.etapa], etapaPill(o.etapa))}</td><td style="width:160px">${barra(o.etapa, 8)}</td><td class="num">${o.etapa >= E["Para etiquetar"] ? o.rech.length : "—"}</td></tr>`))}</div></div>`;
  },
};

// ---------------------------------------------------------------- desvíos
VISTAS.desvios = {
  titulo: "Desvíos",
  sub: () => "Registro de desvíos de proceso, proveedor, custodia y cliente, con causa y acción",
  acciones: () => `<button class="btn pri" data-a="nuevoRD">Nuevo desvío</button>`,
  html() {
    const f = fil("rdest", "abiertos"), xs = S.desvios.filter(d => f === "todos" || d.estado !== "Cerrado");
    const sev = { "Crítica": "no", "Mayor": "av", "Menor": "in" };
    return `<div class="kpis">${["Crítica", "Mayor", "Menor"].map(s => `<div class="kpi ${sev[s]}"><span>${s}s abiertas</span><b>${S.desvios.filter(d => d.sev === s && d.estado !== "Cerrado").length}</b></div>`).join("")}<div class="kpi ok"><span>Cerrados</span><b>${S.desvios.filter(d => d.estado === "Cerrado").length}</b></div></div>
      ${UI.f.nuevoRD ? `<div class="panel"><header><h2>Nuevo desvío</h2><button class="btn sm" data-a="cancelarRD">Cancelar</button></header><div class="cuerpo"><form class="form" data-f="crearRD">
        <label class="campo">Origen<select id="rdOri"><option>Proceso</option><option>Proveedor</option><option>Custodia</option><option>Cliente</option><option>Registro</option></select></label>
        <label class="campo">Severidad<select id="rdSev"><option>Menor</option><option>Mayor</option><option>Crítica</option></select></label>
        <label class="campo">Referencia (orden, serie, lote, remito)<input id="rdRef"></label><label class="campo">Responsable<input id="rdResp" value="Calidad"></label>
        <label class="campo ancho">Qué pasó<input id="rdQue"></label><div class="ancho"><button class="btn pri" type="submit">Registrar</button></div></form></div></div>` : ""}
      <div class="panel"><header><h2>Registro</h2>${chips("rdest", [["abiertos", "Abiertos"], ["todos", "Todos"]], "abiertos")}</header>${tabla(["Desvío", "Fecha", "Origen", "Qué pasó", "Referencia", "Severidad", "Responsable", "Estado"], xs.map(d => `<tr class="click" data-det="desvio" data-id="${d.id}"><td class="mono nw">${d.id}</td><td class="nw">${fecha(d.fecha)}</td><td>${d.origen}</td><td>${esc(d.que)}</td><td class="mono nw">${esc(d.ref)}</td><td>${pill(d.sev, sev[d.sev])}</td><td>${esc(d.resp)}</td><td>${pill(d.estado, d.estado === "Cerrado" ? "ok" : d.estado === "Abierto" ? "no" : "av")}</td></tr>`), { vacio: "Sin desvíos abiertos" })}</div>`;
  },
};
ACC.nuevoRD = () => { UI.f.nuevoRD = true; pintar(); };
ACC.cancelarRD = () => { UI.f.nuevoRD = false; pintar(); };
FORM.crearRD = () => { const d = { id: `RD-${AA}-${String(S.nRd++).padStart(3, "0")}`, fecha: HOY, origen: $("#rdOri").value, sev: $("#rdSev").value, ref: $("#rdRef").value || "—", resp: $("#rdResp").value, que: $("#rdQue").value || "(sin descripción)", estado: "Abierto", causa: "", accion: "" };
  S.desvios.unshift(d); UI.f.nuevoRD = false; registrar("Desvío abierto", d.id); toast(`${d.id} registrado`); pintar(); abrirDetalle("desvio", d.id); };
DETALLES.desvio = id => {
  const d = S.desvios.find(x => x.id === id); if (!d) return null;
  return { titulo: d.id, sub: `${d.origen} · ${d.sev} · ${fecha(d.fecha)}`,
    pie: d.estado !== "Cerrado" ? `<button class="btn ok" data-a="rdCerrar" data-id="${d.id}">Cerrar con verificación</button>` : "",
    cuerpo: `<dl class="dl"><dt>Qué pasó</dt><dd>${esc(d.que)}</dd><dt>Referencia</dt><dd class="mono">${esc(d.ref)}</dd><dt>Responsable</dt><dd>${esc(d.resp)}</dd><dt>Estado</dt><dd>${esc(d.estado)}</dd></dl>
      <form class="form" data-f="guardarRD"><input type="hidden" id="rdId" value="${d.id}"><label class="campo ancho">Causa raíz<textarea id="rdCausa" rows="2">${esc(d.causa)}</textarea></label>
      <label class="campo ancho">Acción correctiva<textarea id="rdAccion" rows="2">${esc(d.accion)}</textarea></label><div class="ancho"><button class="btn" type="submit">Guardar</button></div></form>` };
};
FORM.guardarRD = () => { const d = S.desvios.find(x => x.id === $("#rdId").value); d.causa = $("#rdCausa").value; d.accion = $("#rdAccion").value; if (d.estado === "Abierto" && d.accion) d.estado = "En curso"; registrar("Desvío actualizado", d.id); toast("Guardado"); pintar(); };
ACC.rdCerrar = el => { const d = S.desvios.find(x => x.id === el.dataset.id); d.estado = "Cerrado"; registrar("Desvío cerrado", d.id); toast(`${d.id} cerrado`); pintar(); };

// ---------------------------------------------------------------- insumos
VISTAS.insumos = {
  titulo: "Insumos",
  sub: () => `${D.insumos.length} materiales del MRP · consumo de ${D.anio} (CONSOLIDADO) y plazos de entrega de POLITICA_STOCK`,
  html() {
    const f = fil("iest", "pedir"), q = (UI.f.iq || "").toUpperCase();
    const xs = D.insumos.map(m => [m, estadoInsumo(m)]).filter(([m, e]) => (f === "todos" || (f === "pedir" ? e.k === "no" || e.k === "av" : e.k === f)) && (!q || (m.cod + m.mat + m.prov).toUpperCase().includes(q)));
    return `<div class="kpis"><div class="kpi no"><span>Pedir ya</span><b>${D.insumos.filter(m => estadoInsumo(m).k === "no").length}</b><small>la cobertura no llega al plazo</small></div><div class="kpi av"><span>Pedir</span><b>${D.insumos.filter(m => estadoInsumo(m).k === "av").length}</b><small>cobertura menor a 1,5 × plazo (criterio)</small></div><div class="kpi ok"><span>Cubiertos</span><b>${D.insumos.filter(m => estadoInsumo(m).k === "ok").length}</b></div></div>
      <div class="panel"><header><div class="filtros"><input id="iq" type="search" placeholder="Código, material o proveedor" value="${esc(UI.f.iq || "")}" data-in="iq" aria-label="Buscar insumo">${chips("iest", [["pedir", "A pedir"], ["ok", "Cubiertos"], ["gr", "Sin consumo"], ["todos", "Todos"]], "pedir")}</div><span class="muted">${xs.length}</span></header>
      ${tabla(["Código", "Material", "Proveedor", "Stock", "Consumo/día", "Cobertura", "Plazo (días háb.)", "Estado"], xs.map(([m, e]) => `<tr class="click" data-det="insumo" data-id="${esc(m.cod)}"><td class="mono nw">${esc(m.cod)}</td><td>${esc(m.mat)}</td><td>${esc(m.prov)}</td><td class="num nw">${nf(S.insumos[m.cod].stock, 1)} ${esc(m.um)}</td><td class="num">${nf(m.anio26 / 240, 2)}</td><td class="num">${e.cob == null ? "—" : n0(e.cob) + " d"}</td><td class="num">${m.pmin === m.pmax ? m.pmin : `${m.pmin}-${m.pmax}`}</td><td>${pill(e.t, e.k)}</td></tr>`), { vacio: "Nada para pedir" })}</div>`;
  },
};
DETALLES.insumo = cod => {
  const m = D.insumos.find(x => x.cod === cod); if (!m) return null;
  const st = S.insumos[cod], e = estadoInsumo(m);
  return { titulo: esc(m.cod), sub: esc(m.mat), pie: `<button class="btn pri" data-a="ingresoMP" data-id="${esc(cod)}">Registrar ingreso</button>`,
    cuerpo: `<dl class="dl"><dt>Proveedor</dt><dd>${esc(m.prov)}</dd><dt>Stock</dt><dd>${nf(st.stock, 1)} ${esc(m.um)} · ${pill(e.t, e.k)}</dd><dt>Lote vigente</dt><dd class="mono">${esc(st.lote)} · ingresó ${fecha(st.ingreso)}</dd>
      <dt>Consumo ${D.anio}</dt><dd>${nf(m.anio26, 1)} ${esc(m.um)}/año · ${nf(m.anio26 / 240, 2)} por día hábil</dd><dt>Plazo de entrega</dt><dd>${m.pmin} a ${m.pmax} días hábiles</dd>
      <dt>Política 2035 (MRP)</dt><dd>punto de pedido ${nf(m.pdp, 1)} · stock de seguridad ${nf(m.seg, 1)} ${esc(m.um)}</dd></dl>
      <form class="form" data-f="ingresoMP"><input type="hidden" id="mpCod" value="${esc(cod)}"><label class="campo">Cantidad (${esc(m.um)})<input id="mpCant" type="number" min="0" step="any" value="${Math.ceil(m.anio26 / 240 * (+m.pmax || 10) * 2)}"></label><label class="campo">Lote del proveedor<input id="mpLote" value="${esc(m.cod.split("/")[0])}-${AA}${String(D.mes).padStart(2, "0")}-${(hashN(st.lote) % 8) + 2}"></label></form>` };
};
ACC.ingresoMP = () => FORM.ingresoMP();
FORM.ingresoMP = () => { const cod = $("#mpCod").value, st = S.insumos[cod], q = +$("#mpCant").value || 0; st.stock = Math.round((st.stock + q) * 10) / 10; st.lote = $("#mpLote").value; st.ingreso = HOY; registrar("Ingreso de insumo", cod, `${q} · lote ${st.lote}`); toast(`${cod}: +${q}`); pintar(); };

// ---------------------------------------------------------------- reportes
const REPORTES = {
  dps: ["Libro de actas DPS · estampillas de fabricación", "PBA · Res. 349/07 art. 19 y 21-23", () => {
    const out = ["serie\tmodelo\torden\tpartida\testampilla\tfecha"];
    S.ordenes.filter(o => o.mes === D.mes && o.etapa >= E["Depósito PT"]).forEach(o => { const rs = new Set(o.rech.map(x => x.n)); for (let n = o.desde; n <= o.hasta; n++) if (!rs.has(n)) out.push([ser(n), o.modelo, o.op, o.partida, estampilla(n), fecha(o.cierre)].join("\t")); });
    return out.join("\n"); }],
  sgm: ["SGM de la AGC · archivo para el proceso batch", "CABA · Res. 32-AGC/15 anexo II art. 4", () => {
    const out = ["cuit;razon_social;rubro;ubicacion;fabricante;recargador;agente;capacidad;serie;fecha_fabricacion;vida_util;fecha_ph;fecha_mantenimiento"];
    const max = S.ordenes[S.ordenes.length - 1].hasta;
    for (let n = 1; n <= max; n++) { const e = equipo(n); if (e.estado === "Instalado" && e.cliente.jur === "CABA") out.push([e.cliente.cuit, e.cliente.nombre, e.cliente.tipo, e.cliente.loc, "FLAMA S.A.", "FLAMA S.A.", "polvo ABC", e.o.modelo.replace(/.*ABC /, ""), e.s, fecha(e.fab), fecha(e.vida), fecha(e.fab), fecha(e.mant)].join(";")); }
    return out.join("\n"); }],
  venc: ["Vencimientos de mantenimiento · próximos 60 días", "IRAM 3517-2 9.2 · aviso al cliente", () => {
    const out = ["serie\tmodelo\tcliente\tvence"], max = S.ordenes[S.ordenes.length - 1].hasta;
    for (let n = 1; n <= max; n++) { const e = equipo(n); if (e.mant && dias(HOY, e.mant) >= 0 && dias(HOY, e.mant) <= 60) out.push([e.s, e.o.modelo, e.custodia, fecha(e.mant)].join("\t")); }
    return out.length > 1 ? out.join("\n") : "Sin vencimientos en los próximos 60 días: los primeros equipos FLAMA vencen en enero de " + (D.anio + 1) + "."; }],
  prod: ["Producción del mes por modelo", "FLAMA_Trazabilidad › Rendimiento (Sheets)", () => {
    const out = ["modelo\tplan\tordenes\tcerrados\taptos\trechazos"];
    D.plan.filter(p => p.tipo === "Terminado").forEach(p => { const os = S.ordenes.filter(o => o.mes === D.mes && o.modelo === p.producto), c = os.filter(o => o.etapa >= E["Para etiquetar"]);
      out.push([p.producto, p.cant, os.length, c.reduce((a, o) => a + o.cant, 0), c.reduce((a, o) => a + aptos(o), 0), c.reduce((a, o) => a + o.rech.length, 0)].join("\t")); });
    return out.join("\n"); }],
  eventos: ["Registro de eventos de esta sesión", "acciones hechas en el sistema", () => ["fecha\tevento\treferencia\tdetalle\tusuario", ...S.eventos.map(e => [new Date(e.t).toLocaleString("es-AR"), e.tipo, e.ref, e.detalle, e.quien].join("\t"))].join("\n")],
};
VISTAS.reportes = {
  titulo: "Reportes",
  sub: () => "Salidas para la autoridad de aplicación, para Sheets y para avisos a clientes",
  html() {
    const k = fil("rep", "dps"), [t, base, fn] = REPORTES[k], txt = fn(), filas = txt.split("\n").length - 1;
    return `<div class="grilla"><div class="panel c4"><header><h2>Reportes</h2></header><div class="cuerpo" style="display:flex;flex-direction:column;gap:6px">${Object.entries(REPORTES).map(([id, [tt, bb]]) => `<button class="btn" style="justify-content:flex-start;white-space:normal;text-align:left;${id === k ? "border-color:var(--ink)" : ""}" data-a="filtro" data-k="rep" data-v="${id}"><span><b>${esc(tt)}</b><br><span class="muted" style="font-weight:400">${esc(bb)}</span></span></button>`).join("")}</div></div>
      <div class="panel c8"><header><h2>${esc(t)}</h2><div class="acciones"><span class="muted">${filas > 0 ? n0(filas) + " filas" : ""}</span><button class="btn pri" data-a="copiarRep">Copiar</button></div></header><div class="cuerpo"><pre class="salida" id="repTxt">${esc(txt.split("\n").slice(0, 120).join("\n"))}${filas > 120 ? "\n…" : ""}</pre></div></div></div>`;
  },
};
ACC.copiarRep = () => copiar(REPORTES[fil("rep", "dps")][2]());

// ---------------------------------------------------------------- configuración
VISTAS.config = {
  titulo: "Configuración",
  sub: () => "Modelos, parámetros y usuarios",
  html() {
    return `<div class="grilla"><div class="panel c7"><header><h2>Modelos (BOM)</h2></header>${tabla(["Código", "Equipo", "IRAM", "Carga", "Mínima", "Máxima"], D.modelos.map(m => `<tr><td class="mono">${esc(m.cod)}</td><td>${esc(m.nombre)}</td><td>${m.iram}</td><td class="num">${nf(m.carga, 1)} ${m.um}</td><td class="num">${nf(m.min, 2)}</td><td class="num">${nf(m.max, 2)}</td></tr>`))}</div>
      <div class="panel c5"><header><h2>Parámetros</h2></header><div class="cuerpo"><dl class="dl">
        <dt>Tamaño de lote</dt><dd>1 kg 60 · 2,5 y 5 kg 48 · 10 kg 24 · carros 25-50 kg 4, 70-100 kg 2 (lo que entra en el carro interno)</dd>
        <dt>Prueba hidráulica</dt><dd>manuales ${PH.man} · carros ${PH.car} (DOC-02)</dd><dt>Contraste manómetros</dt><dd>cada 15 días; la PH se bloquea al vencer</dd>
        <dt>Partida DPS</dt><dd>100 u o más por certificado</dd><dt>Plazos de reclamos</dt><dd>seguridad 24 h · resto 2 días hábiles · datos personales 10 días</dd>
        <dt>Recepción sin confirmar</dt><dd>aviso a las 48 h</dd><dt>Vida útil</dt><dd>20 años desde la fabricación</dd><dt>Series</dt><dd>año + correlativo de 6 dígitos, sin reutilizar</dd></dl></div></div>
      <div class="panel c7"><header><h2>Usuarios y permisos</h2></header>${tabla(["Rol", "Usuarios", "Puede"], [["PCP", "2", "órdenes, remitos, reportes"], ["Producción", "18", "avanzar etapas, etiquetado"], ["Calidad", "3", "cerrar lotes, equipos de medición, desvíos"], ["Responsable técnico", "1", "visar cierres e inutilizaciones"], ["Recargas", "6", "órdenes de servicio, sustitutos"], ["Atención al cliente", "2", "reclamos, clientes"], ["Distribuidor / chofer", "externos", "confirmar salida y recepción desde el QR del remito"]].map(f => `<tr>${f.map(c => `<td>${esc(c)}</td>`).join("")}</tr>`))}</div>
      <div class="panel c5"><header><h2>Datos</h2></header><div class="cuerpo" style="display:flex;flex-direction:column;gap:10px">
        <dl class="dl"><dt>Origen real</dt><dd>Plan mensual (Aprovechamiento_Manuales y _Carros), Aprovechamiento_Recargas, FLAMA_MRP, FLAMA_BOM</dd><dt>De prueba</dt><dd>estado de cada orden, rechazos, clientes, remitos, recargas, reclamos, desvíos y stock</dd><dt>Eventos de la sesión</dt><dd>${S.eventos.length}</dd></dl>
        <button class="btn" data-a="reiniciar">Restablecer datos de prueba</button></div></div></div>`;
  },
};
ACC.reiniciar = () => { reiniciar(); toast("Datos de prueba restablecidos"); pintar(); };
