// ================================================================ tablero técnico: intraplanta y extraplanta
// ---------------------------------------------------------------- gráficos SVG (un eje, marcas finas, valores en el texto)
function cartaI(v, lie, lse, etiquetas = []) {
  const st = stats(v); if (!st) return `<p class="muted">Sin datos</p>`;
  const mr = v.slice(1).map((x, i) => Math.abs(x - v[i])), mrb = mr.reduce((a, x) => a + x, 0) / Math.max(1, mr.length);
  const lcs = st.m + 2.66 * mrb, lci = st.m - 2.66 * mrb, lo = Math.min(lie, lci, ...v) - (lse - lie) * 0.05, hi = Math.max(lse, lcs, ...v) + (lse - lie) * 0.05;
  const W = 760, H = 230, l = 46, rr = 92, t = 10, b = 22, X = i => l + (W - l - rr) * i / Math.max(1, v.length - 1), Y = y => t + (H - t - b) * (hi - y) / (hi - lo);
  const lin = (y, txt, col, dash) => `<line x1="${l}" x2="${W - rr}" y1="${Y(y)}" y2="${Y(y)}" stroke="${col}" stroke-width="1.3" ${dash ? 'stroke-dasharray="5 4"' : ""}/><text x="${W - rr + 6}" y="${Y(y) + 4}">${txt} ${nf(y, 3)}</text>`;
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Carta de valores individuales">${lin(lse, "LSE", "var(--ink-3)")}${lin(lie, "LIE", "var(--ink-3)")}${lin(lcs, "LCS", "var(--red)", 1)}${lin(lci, "LCI", "var(--red)", 1)}${lin(st.m, "x̄", "var(--ink-2)")}
    <path d="${v.map((y, i) => (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(y).toFixed(1)).join("")}" fill="none" stroke="var(--blue)" stroke-width="1.4" opacity=".6"/>
    ${v.map((y, i) => { const f = y > lcs || y < lci; return `<circle cx="${X(i)}" cy="${Y(y)}" r="${f ? 4.5 : 3}" fill="${f ? "var(--red)" : "var(--blue)"}"><title>${esc(etiquetas[i] || i + 1)} · ${nf(y, 3)} kg</title></circle>`; }).join("")}
    <text x="${l}" y="${H - 4}">serie 1</text><text x="${W - rr}" y="${H - 4}" text-anchor="end">serie ${v.length}</text></svg>`;
}
function cartaP(ls) {
  if (!ls.length) return `<p class="muted">Sin lotes cerrados</p>`;
  const tot = ls.reduce((a, q) => a + q.n, 0), pb = ls.reduce((a, q) => a + q.x, 0) / tot;
  ls.forEach(q => { q.p = q.x / q.n; q.lcs = pb + 3 * Math.sqrt(pb * (1 - pb) / q.n); });
  const W = 760, H = 220, l = 42, rr = 12, t = 10, b = 34, max = Math.max(0.04, ...ls.map(q => Math.max(q.p, q.lcs))) * 1.1, bw = (W - l - rr) / ls.length;
  const X = i => l + bw * (i + 0.5), Y = y => t + (H - t - b) * (1 - y / max);
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Carta p de fallas en prueba hidráulica">${[0, max / 2, max].map(y => `<line x1="${l}" x2="${W - rr}" y1="${Y(y)}" y2="${Y(y)}" class="grid"/><text x="${l - 5}" y="${Y(y) + 4}" text-anchor="end">${nf(100 * y, 1)}%</text>`).join("")}
    <line x1="${l}" x2="${W - rr}" y1="${Y(pb)}" y2="${Y(pb)}" stroke="var(--ink-2)"/><path d="${ls.map((q, i) => `${i ? "L" : "M"}${(X(i) - bw / 2).toFixed(1)} ${Y(q.lcs).toFixed(1)}H${(X(i) + bw / 2).toFixed(1)}`).join("")}" fill="none" stroke="var(--red)" stroke-dasharray="5 4" stroke-width="1.3"/>
    ${ls.map((q, i) => `<circle cx="${X(i)}" cy="${Y(q.p)}" r="${q.p > q.lcs ? 5 : 3.5}" fill="${q.p > q.lcs ? "var(--red)" : "var(--blue)"}"><title>${q.op} · ${q.x} de ${q.n} · LCS ${nf(100 * q.lcs, 1)} %</title></circle>${ls.length <= 26 ? `<text x="${X(i)}" y="${H - b + 14}" text-anchor="middle" style="font-size:9.5px">${q.op.slice(-5)}</text>` : ""}`).join("")}
    <text x="${W - rr}" y="${H - 4}" text-anchor="end">p̄ ${nf(100 * pb, 2)} % · LCS según tamaño de lote</text></svg>`;
}
function barrasH(items, color = "var(--blue)", fmt = n0) {
  const max = Math.max(1, ...items.map(x => x[1]));
  return items.map(([k, v, sub]) => `<div style="display:grid;grid-template-columns:minmax(120px,190px) 1fr 54px;gap:10px;align-items:center;margin:5px 0;font-size:13px"><span>${esc(k)}${sub ? `<br><small class="muted">${esc(sub)}</small>` : ""}</span>${barra(v, max, color)}<b class="num">${fmt(v)}</b></div>`).join("");
}
function columnas(items, color = "var(--blue)") {
  const W = 760, H = 190, l = 30, b = 26, t = 12, max = Math.max(1, ...items.map(x => x[1])), bw = (W - l) / items.length;
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Vencimientos por mes">${items.map(([k, v], i) => { const h = (H - b - t) * v / max, x = l + i * bw + 4;
    return `<rect x="${x}" y="${H - b - h}" width="${bw - 8}" height="${Math.max(h, 1)}" rx="3" fill="${color}"><title>${k}: ${v}</title></rect><text x="${x + (bw - 8) / 2}" y="${H - b - h - 4}" text-anchor="middle" class="t-ink" style="font-size:10.5px">${v ? n0(v) : ""}</text><text x="${x + (bw - 8) / 2}" y="${H - 8}" text-anchor="middle" style="font-size:10px">${k}</text>`; }).join("")}</svg>`;
}

// ---------------------------------------------------------------- vista
VISTAS.tablero = {
  titulo: "Tablero",
  sub: () => `${HOY.toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long", year: "numeric" })} · ${habiles(D.anio, D.mes).filter(d => d <= HOY).length} de ${habiles(D.anio, D.mes).length} días hábiles`,
  acciones: () => `<div class="filtros" role="tablist">${[["intra", "Trazabilidad intraplanta"], ["extra", "Trazabilidad extraplanta"]].map(([k, t]) => `<button role="tab" aria-pressed="${fil("tab", "intra") === k}" data-a="filtro" data-k="tab" data-v="${k}">${t}</button>`).join("")}</div>`,
  html() { return fil("tab", "intra") === "intra" ? tableroIntra() : tableroExtra(); },
};

// despacho del mes según el plan y palletizado_PT: por modelo, sin mezclar pallets (criterio de cálculo)
function despachoMes() {
  return D.plan.filter(p => p.tipo === "Terminado" || p.tipo === "Cilindro").map(p => {
    const kg = kgDe(p.producto), cil = p.tipo === "Cilindro", carro = !cil && p.linea === "Carros";
    const por = cil ? D.pallets.cil[kg] : carro ? D.pallets.furgon[kg] : D.pallets.man[kg];
    return { prod: p.producto, cant: p.cant, por, unid: carro ? "furgón" : "pallet", n: por ? Math.ceil(p.cant / por) : null };
  });
}
const vacio = t => `<div class="cuerpo"><p class="muted" style="margin:0">${t}</p></div>`;
const aprovBarra = (v, um) => `<div style="display:grid;grid-template-columns:1fr 46px;gap:8px;align-items:center">${barra(v * 100, 100, v >= um ? "var(--red)" : v >= um * 0.8 ? "var(--yellow)" : "var(--blue)")}<b class="num">${nf(100 * v, 0)} %</b></div>`;

function tableroIntra() {
  const om = S.ordenes.filter(o => o.mes === D.mes), planT = D.plan.filter(p => p.tipo === "Terminado" || p.tipo === "Cilindro").reduce((a, p) => a + p.cant, 0);
  const cap = D.cap, um = cap.umbral, cuM = cap.man.slice().sort((a, b) => b.aprov - a.aprov)[0], cuC = cap.car.slice().sort((a, b) => b.aprov - a.aprov)[0];
  const des = despachoMes(), pal = des.filter(x => x.unid === "pallet").reduce((a, x) => a + (x.n || 0), 0);
  const lib = om.filter(o => o.etapa > 0), enPT = om.filter(o => o.etapa >= E["Depósito PT"]).reduce((a, o) => a + aptos(o), 0);
  const cerr = S.ordenes.filter(o => o.etapa >= E["Para etiquetar"]), tot = cerr.reduce((a, o) => a + o.cant, 0), rech = cerr.reduce((a, o) => a + o.rech.length, 0);
  const medOkN = S.medicion.filter(m => estadoMed(m)[1] === "ok").length;
  const wip = ETAPAS.slice(1, 7).map((e, i) => [e, om.filter(o => o.etapa === i + 1).reduce((a, o) => a + o.cant, 0), om.filter(o => o.etapa === i + 1).map(o => o.op.slice(-5)).join(" ")]);
  const capK = cpkModelos(), ultimo = cerr.filter(o => !o.cilindro && Object.keys(o.pesadas || {}).length >= 2).slice(-1)[0];
  const lp = cerr.filter(o => o.cant >= 20).map(o => ({ op: o.op, n: o.cant, x: o.rech.filter(r => r.ensayo === "PH").length }));
  const causas = CAUSAS.map(([c]) => [c, cerr.reduce((a, o) => a + o.rech.filter(x => x.causa === c).length, 0)]).sort((a, b) => b[1] - a[1]);
  return `<div class="kpis">
    <div class="kpi in"><span>Plan del mes</span><b>${n0(planT)}</b><small>${om.length} órdenes · Plan mensual de Aprovechamiento_Manuales y _Carros</small></div>
    <div class="kpi in"><span>Series reservadas</span><b class="mono" style="font-size:18px">${om.length ? ser(om[0].desde) : "—"}</b><small>a ${om.length ? ser(om[om.length - 1].hasta) : "—"} · ${[...new Set(om.map(o => o.partida))].length} partidas DPS</small></div>
    <div class="kpi ${cuM.aprov >= um ? "no" : "ok"}"><span>Cuello de botella manuales ${D.anio}</span><b>${nf(100 * cuM.aprov, 1)} %</b><small>${esc(cuM.puesto)} · umbral ${nf(100 * um, 0)} %</small></div>
    <div class="kpi ${cuC.aprov >= um ? "no" : "ok"}"><span>Cuello de botella carros ${D.anio}</span><b>${nf(100 * cuC.aprov, 1)} %</b><small>${esc(cuC.puesto)}</small></div>
    <div class="kpi in"><span>Pallets del mes</span><b>${n0(pal)}</b><small>${((k) => k + (k === 1 ? " camión" : " camiones"))(Math.ceil(pal / D.pallets.camion))} de ${D.pallets.camion} pallets · palletizado_PT</small></div>
    <div class="kpi ${lib.length ? "in" : ""}"><span>Órdenes liberadas</span><b>${lib.length}</b><small>de ${om.length} del mes · registradas</small></div>
    <div class="kpi ${enPT ? "ok" : ""}"><span>A depósito PT</span><b>${n0(enPT)}</b><small>equipos identificados y paletizados en el mes</small></div>
    <div class="kpi ${tot ? "ok" : ""}"><span>Rendimiento a la primera</span><b>${tot ? pct(tot - rech, tot) : "—"}</b><small>${tot ? `${rech} rechazos en ${n0(tot)} cerrados` : "sin lotes cerrados registrados"}</small></div>
    <div class="kpi ${medOkN === S.medicion.length ? "ok" : "no"}"><span>Medición con control vigente</span><b>${medOkN} de ${S.medicion.length}</b><small>sin contraste de PH no se cierra</small></div></div>
  <div class="grilla">
    <div class="panel c12"><header><h2>Plan del mes</h2><span class="muted">Plan mensual · ${MES_TXT[D.mes - 1]} ${D.anio}</span></header>${tabla(["Producto", "Tipo", "Línea", "Cant", "Órdenes", "Liberadas", "En depósito o despachadas", "Avance"], D.plan.filter(p => p.tipo === "Terminado" || p.tipo === "Cilindro").map(p => {
      const os = om.filter(o => o.modelo === p.producto), hec = os.filter(o => o.etapa >= E["Depósito PT"]).reduce((a, o) => a + aptos(o), 0);
      return `<tr><td>${esc(p.producto)}</td><td>${esc(p.tipo)}</td><td>${p.linea}</td><td class="num">${n0(p.cant)}</td><td class="num">${os.length}</td><td class="num">${os.filter(o => o.etapa > 0).length}</td><td class="num">${n0(hec)}</td><td style="width:140px">${barra(hec, p.cant, "var(--green)")}</td></tr>`; }))}</div>
    <div class="panel c6"><header><h2>Aprovechamiento por puesto · manuales ${D.anio}</h2><span class="muted">Aprovechamiento_Manuales › Resumen cap.</span></header>${tabla(["N°", "Puesto", "t (s/u)", "Disp.", "Máq.", "Aprovechamiento"], cap.man.map(x => `<tr><td class="num">${x.n}</td><td title="${esc(x.maq)}">${esc(x.puesto)}${x.pasa < 1 ? ` <span class="muted">(${nf(100 * x.pasa, 0)} % pasa)</span>` : ""}</td><td class="num">${nf(x.t, 1)}</td><td class="num">${nf(100 * x.disp, 1)} %</td><td class="num">${x.nmaq}</td><td style="min-width:150px">${aprovBarra(x.aprov, um)}</td></tr>`))}</div>
    <div class="panel c6"><header><h2>Aprovechamiento por puesto · carros ${D.anio}</h2><span class="muted">Aprovechamiento_Carros › Resumen Capacidad</span></header>${tabla(["N°", "Puesto", "t 25/50/70/100 kg (min/u)", "Disp.", "Aprovechamiento"], cap.car.map(x => `<tr><td class="num">${esc(x.n)}</td><td title="${esc(x.maq)}">${esc(x.puesto)}</td><td class="num nw">${x.tmin.map(v => nf(v, 1)).join(" · ")}</td><td class="num">${nf(100 * x.disp, 1)} %</td><td style="min-width:150px">${aprovBarra(x.aprov, um)}</td></tr>`))}</div>
    <div class="panel c6"><header><h2>Equipos en cada etapa</h2><span class="muted">órdenes del mes · según lo registrado</span></header>${lib.length ? `<div class="cuerpo">${barrasH(wip)}</div>` : vacio("Ninguna orden del mes liberada todavía. Se libera desde Órdenes y cada etapa se registra con la hoja de ruta.")}</div>
    <div class="panel c6"><header><h2>Capacidad de proceso: carga</h2><span class="muted">pesadas registradas · banda del BOM</span></header>${capK.length ? tabla(["Modelo", "n", "x̄ kg", "σ g", "Banda kg", "Cpk"], capK.map(c => `<tr><td>${esc(c.m.nombre.replace("Extintor ", ""))}</td><td class="num">${c.n}</td><td class="num">${nf(c.st.m, 3)}</td><td class="num">${nf(c.st.sd * 1000, 0)}</td><td class="num nw">${nf(c.m.min, 2)}–${nf(c.m.max, 2)}</td><td class="num">${c.n < 5 || c.cpk == null ? pill("n < 5", "gr") : pill(nf(c.cpk, 2), c.cpk >= 1.33 ? "ok" : c.cpk >= 1 ? "av" : "no")}</td></tr>`)) : vacio("Sin pesadas registradas: se cargan al cerrar cada lote (archivo de la balanza o valores de la hoja).")}</div>
    <div class="panel c6"><header><h2>Carta I · masa de carga</h2><span class="muted">${ultimo ? `<a href="#" data-det="orden" data-id="${ultimo.op}">${ultimo.op}</a>` : "último lote con pesadas"}</span></header>${ultimo ? `<div class="cuerpo">${(() => { const ks = Object.keys(ultimo.pesadas).map(Number).sort((a, b) => a - b); return cartaI(ks.map(n => ultimo.pesadas[n]), modeloBOM(ultimo.modelo).min, modeloBOM(ultimo.modelo).max, ks.map(ser)); })()}</div>` : vacio("Sin pesadas registradas.")}</div>
    <div class="panel c6"><header><h2>Carta p · fallas en PH por lote</h2><span class="muted">lotes cerrados de 20 u o más</span></header>${lp.length ? `<div class="cuerpo">${cartaP(lp)}</div>` : vacio("Sin lotes cerrados registrados.")}</div>
    <div class="panel c5"><header><h2>Rechazos por causa</h2><span class="muted">lotes cerrados</span></header>${rech ? `<div class="cuerpo">${barrasH(causas, "var(--red)")}</div>` : vacio("Sin rechazos registrados.")}</div>
    <div class="panel c7"><header><h2>Equipos de medición</h2><span class="muted">equipos del proyecto · Res. 349/07 art. 20</span></header>${tabla(["Equipo", "Descripción", "Último control", "Estado"], S.medicion.map(m => `<tr><td class="mono">${m.id}</td><td>${esc(m.desc)}</td><td>${fecha(m.ult)}</td><td>${pill(...estadoMed(m))}</td></tr>`))}</div>
    <div class="panel c12"><header><h2>Órdenes del mes</h2><a href="#ordenes" data-v="ordenes" class="btn sm">Órdenes</a></header>${tabla(["Orden", "Modelo", "Tipo", "Cant", "Series", "Partida", "Etapa", "Liberada", "Puesto en curso"], om.map(o => { const h = hojaRuta(o).find(x => x.estado === "en curso");
      return `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td class="nw">${esc(o.modelo)}</td><td>${tipoEq(o)}</td><td class="num">${o.cant}</td><td class="mono nw">${ser(o.desde)} → ${ser(o.hasta).slice(3)}</td><td class="mono">${o.partida}</td><td>${pill(ETAPAS[o.etapa], etapaPill(o.etapa))}</td><td class="nw">${fecha(o.emision)}</td><td class="muted">${h ? esc(h.puesto + " · " + h.op) : "—"}</td></tr>`; }))}</div>
    <div class="panel c12"><header><h2>Estadios de los lotes del mes</h2><a href="#estados" data-v="estados" class="btn sm">Estados del lote</a></header>${lib.length ? `<div class="cuerpo">${ganttLotes(lib)}</div>` : vacio("Sin lotes liberados: el Gantt se arma con los cambios de etapa registrados.")}</div>
    <div class="panel c7"><header><h2>AMFE de proceso: mayor riesgo</h2><a href="#amfe" data-v="amfe" class="btn sm">AMFE completo</a></header>${tabla(["ID", "Modo de falla", "S", "O", "D", "NPR"], amfe(false).slice(0, 6).map(f => `<tr><td class="mono">${f.id}</td><td>${esc(f.modo)}<br><span class="muted" style="font-size:11.5px">${esc(f.base)}</span></td><td class="num">${f.s}</td><td class="num">${f.O}</td><td class="num">${f.d}</td><td class="num">${nprPill(f)}</td></tr>`))}</div>
    <div class="panel c5"><header><h2>Plan de control</h2><span class="muted">DOC-02 · DOC-01</span></header>${tabla(["Cód.", "Característica", "Registrado"], PLAN.map(x => `<tr><td class="mono">${x.c}</td><td>${esc(x.car)}${x.inst.length ? `<br>${x.inst.map(medOk).join(" ")}` : ""}</td><td style="font-size:12.5px">${esc(x.vivo())}</td></tr>`))}</div>
    <div class="panel c12"><header><h2>Cómo llega cada dato a este tablero</h2><a href="#origen" data-a="irOrigenIntra" class="btn sm">Origen de los datos</a></header>${tablaFuente(FUENTE_INTRA)}</div>
  </div>`;
}

function tableroExtra() {
  const c = censo().est, jur = { PBA: 0, CABA: 0 }, venc = {};
  Object.entries(S.inst).forEach(([n, i]) => { const cl = cliente(i.cliente); if (jur[cl.jur] != null) jur[cl.jur]++; });
  for (const n of Object.keys(S.ident)) { const e = equipo(+n); if (e.mant && (e.estado === "Instalado" || e.estado === "En distribuidor")) { const d = new Date(e.mant), k = d.getFullYear() * 12 + d.getMonth(); venc[k] = (venc[k] || 0) + 1; } }
  const k0 = HOY.getFullYear() * 12 + HOY.getMonth(), meses = Array.from({ length: 12 }, (_, i) => k0 + 1 + i).map(k => [MES_TXT[k % 12].slice(0, 3) + " " + String(Math.floor(k / 12)).slice(2), venc[k] || 0]);
  const des = despachoMes(), pal = des.filter(x => x.unid === "pallet").reduce((a, x) => a + (x.n || 0), 0), fur = des.filter(x => x.unid === "furgón").reduce((a, x) => a + (x.n || 0), 0);
  const planR = planRecargas(), porTipo = {}; [...D.recargas.comercial, ...D.recargas.industrial].forEach(t => { porTipo[t.agente] = (porTipo[t.agente] || 0) + t.cant; });
  const recib = S.remitos.filter(r => r.recibido), lead = recib.length ? recib.reduce((a, r) => a + dias(r.salida || r.fecha, r.recibido), 0) / recib.length : null;
  const sinConf = sinConfirmar(), rcAb = S.reclamos.filter(x => x.etapa < 3), mercado = (c["En distribuidor"] || 0) + (c.Instalado || 0);
  const z = D.zonas, zr = Object.fromEntries(z.recargas), zn = Object.fromEntries(z.nuevas);
  return `<div class="kpis">
    <div class="kpi in"><span>Despacho planificado del mes</span><b>${n0(pal)} pallets</b><small>${((k) => k + (k === 1 ? " camión" : " camiones"))(Math.ceil(pal / D.pallets.camion))} Sider · ${n0(fur)} ${fur === 1 ? "furgón" : "furgones"} de carros · palletizado_PT</small></div>
    <div class="kpi in"><span>Recargas del plan</span><b>${n0(planR)}</b><small>${MES_TXT[D.mes - 1]} · Aprovechamiento_Recargas</small></div>
    ${(() => { const zt = z.recargas.filter(([k]) => k !== "PBA Interior").sort((a, b) => b[1] - a[1])[0]; return `<div class="kpi in"><span>Zona propia con más recargas</span><b style="font-size:18px">${esc(zt[0])}</b><small>${nf(100 * zt[1], 1)} % · Indexado Dim Técnico ${D.anio} (sin PBA Interior)</small></div>`; })()}
    <div class="kpi ${S.remitos.length ? "in" : ""}"><span>Remitos registrados</span><b>${S.remitos.length}</b><small>${S.remitos.filter(r => r.estado === "En tránsito").length} en tránsito</small></div>
    <div class="kpi ${sinConf.length ? "av" : ""}"><span>Recepción sin confirmar</span><b>${sinConf.length}</b><small>más de 48 h desde la salida</small></div>
    <div class="kpi in"><span>Salida → recepción</span><b>${lead == null ? "—" : nf(lead, 1) + " d"}</b><small>${recib.length} recepciones registradas</small></div>
    <div class="kpi ${mercado ? "ok" : ""}"><span>Equipos en el mercado</span><b>${n0(mercado)}</b><small>${n0(c.Instalado || 0)} instalados registrados</small></div>
    <div class="kpi ${rcAb.length ? "av" : ""}"><span>Reclamos abiertos</span><b>${rcAb.length}</b><small>${S.reclamos.filter(vencido).length} fuera de plazo</small></div></div>
  <div class="grilla">
    <div class="panel c6"><header><h2>Plan de despacho del mes</h2><span class="muted">plan × unidades por pallet o furgón (palletizado_PT)</span></header>${tabla(["Producto", "Cant", "Por pallet / furgón", "Pallets / furgones"], des.map(x => `<tr><td>${esc(x.prod)}</td><td class="num">${n0(x.cant)}</td><td class="num">${x.por ? `${x.por} por ${x.unid}` : "—"}</td><td class="num">${x.n == null ? "—" : n0(x.n)}</td></tr>`))}<p class="muted" style="font-size:12.5px;margin:8px 14px 12px">Pallets por modelo, sin mezclar. Camión Sider GyL: ${D.pallets.camion} pallets; camión chico: ${D.pallets.chico}.</p></div>
    <div class="panel c6"><header><h2>Plan de recargas por agente</h2><span class="muted">${MES_TXT[D.mes - 1]} · dos plantas</span></header><div class="cuerpo">${barrasH(Object.entries(porTipo).sort((a, b) => b[1] - a[1]).map(([k, v]) => [k, Math.round(v)]), "var(--green)")}</div></div>
    <div class="panel c12"><header><h2>Mercado por zona · ${D.anio}</h2><span class="muted">MRP_MP › Indexado Dim Técnico · PBA Interior la atienden distribuidores ajenos</span></header>${tabla(["Zona", "% de las recargas", "", "% de las unidades nuevas revendidas", ""], z.recargas.map(([k]) => `<tr><td>${esc(k)}</td><td class="num">${nf(100 * zr[k], 1)} %</td><td style="width:22%">${barra(zr[k], 0.2, "var(--blue)")}</td><td class="num">${zn[k] != null ? nf(100 * zn[k], 1) + " %" : "—"}</td><td style="width:22%">${barra(zn[k] || 0, 0.2, "var(--violet)")}</td></tr>`))}</div>
    <div class="panel c6"><header><h2>Cadena de custodia</h2><span class="muted">series de ${D.anio} · según lo registrado</span></header><div class="cuerpo">${barrasH([["Planificado", c.Planificado || 0, "sin liberar"], ["En producción", c["En producción"] || 0, "hoja de ruta"], ["FLAMA · depósito PT", c["En depósito PT"] || 0, "identificado y en pallet"], ["Transportista", c["En tránsito"] || 0, "remito + COT"], ["Distribuidor", c["En distribuidor"] || 0, "recepción confirmada"], ["Usuario", c.Instalado || 0, "tarjeta DPS o SGM"], ["Inutilizados", c.Inutilizado || 0, "acta"]], "var(--violet)")}</div></div>
    <div class="panel c6"><header><h2>Tarjetas oficiales por jurisdicción</h2></header>${jur.PBA + jur.CABA ? `<div class="cuerpo">${barrasH([["PBA · tarjeta DPS", jur.PBA, "Res. 349/07"], ["CABA · SGM de la AGC", jur.CABA, "Res. 32-AGC/15"]])}</div>` : vacio("Sin instalaciones registradas.")}</div>
    <div class="panel c8"><header><h2>Vencimientos de mantenimiento</h2><span class="muted">próximos 12 meses · equipos identificados en distribuidores y usuarios</span></header>${Object.keys(venc).length ? `<div class="cuerpo">${columnas(meses, "var(--yellow)")}</div>` : vacio("Sin equipos identificados en el mercado: el vencimiento es un año después de la identificación (IRAM 3517-2 9.2.1).")}</div>
    <div class="panel c4"><header><h2>Remitos abiertos</h2></header>${tabla(["Remito", "Cliente", "Estado"], S.remitos.filter(r => r.estado !== "Recibido").map(r => `<tr class="click" data-det="remito" data-id="${r.id}"><td class="mono nw">${r.id.slice(-8)}</td><td>${esc(cliente(r.cliente).nombre)}</td><td>${pill(r.estado, estRem[r.estado])}</td></tr>`), { vacio: "Sin remitos abiertos" })}</div>
    <div class="panel c6"><header><h2>Recargas por etapa</h2><span class="muted">órdenes de servicio registradas</span></header>${S.recargas.length ? `<div class="cuerpo">${barrasH(ETAPAS_OS.slice(0, 5).map((e, i) => [e, S.recargas.filter(r => r.etapa === i && !r.inutil).length]).concat([["Para inutilizar", S.recargas.filter(r => r.inutil).length]]))}</div>` : vacio("Sin órdenes de servicio registradas.")}</div>
    <div class="panel c6"><header><h2>Reclamos y retiros</h2></header>${tabla(["Tipo", "Abiertos", "Fuera de plazo", "Plazo"], Object.keys(PLAZO_RC).map(t => `<tr><td>${t}</td><td class="num">${S.reclamos.filter(x => x.tipo === t && x.etapa < 3).length}</td><td class="num">${S.reclamos.filter(x => x.tipo === t && vencido(x)).length}</td><td class="num">${PLAZO_RC[t]} d</td></tr>`))}<p class="muted" style="font-size:12.5px;margin:8px 14px 12px">Retiros preventivos abiertos: ${S.retiros.filter(x => x.estado !== "Cerrado").length}.</p></div>
    <div class="panel c7"><header><h2>AMFE de campo: mayor riesgo</h2><a href="#amfecampo" data-v="amfecampo" class="btn sm">AMFE de campo</a></header>${tabla(["ID", "Modo de falla", "S", "O", "D", "NPR"], amfe(true).slice(0, 6).map(f => `<tr><td class="mono">${f.id}</td><td>${esc(f.modo)}<br><span class="muted" style="font-size:11.5px">${esc(f.base)}</span></td><td class="num">${f.s}</td><td class="num">${f.O}</td><td class="num">${f.d}</td><td class="num">${nprPill(f)}</td></tr>`))}</div>
    <div class="panel c5"><header><h2>Estados del equipo</h2><a href="#estadoseq" data-v="estadoseq" class="btn sm">Ver estados</a></header><div class="cuerpo">${barrasH(ESTADOS_EQ.map(([e, , , reg]) => [e, c[e] || 0, reg]), "var(--violet)")}</div></div>
    <div class="panel c12"><header><h2>Cómo llega cada dato a este tablero</h2><a href="#origen" data-a="irOrigenExtra" class="btn sm">Origen de los datos</a></header>${tablaFuente(FUENTE_EXTRA)}</div>
  </div>`;
}
