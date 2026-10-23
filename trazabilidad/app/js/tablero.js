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

function tableroIntra() {
  const om = S.ordenes.filter(o => o.mes === D.mes), planT = D.plan.filter(p => p.tipo === "Terminado" || p.tipo === "Cilindro").reduce((a, p) => a + p.cant, 0);
  const hab = habiles(D.anio, D.mes), trans = hab.filter(d => d <= HOY).length, esperado = Math.round(planT * trans / hab.length);
  const enPT = om.filter(o => o.etapa >= E["Depósito PT"]).reduce((a, o) => a + aptos(o), 0);
  const cerr = om.filter(o => o.etapa >= E["Para etiquetar"]), tot = cerr.reduce((a, o) => a + o.cant, 0), rech = cerr.reduce((a, o) => a + o.rech.length, 0);
  const phF = cerr.reduce((a, o) => a + o.rech.filter(x => x.ensayo === "PH").length, 0);
  const wip = ETAPAS.slice(1, 7).map((e, i) => [e, om.filter(o => o.etapa === i + 1).reduce((a, o) => a + o.cant, 0), om.filter(o => o.etapa === i + 1).map(o => o.op.slice(-5)).join(" ")]);
  const ciclos = S.ordenes.filter(o => ciclo(o) && o.mes >= D.mes - 1).map(ciclo), cm = ciclos.length ? ciclos.reduce((a, x) => a + x, 0) / ciclos.length : 0;
  // capacidad de proceso de la carga por modelo (lotes cerrados del mes y del anterior)
  const cap = D.modelos.map(m => { const v = []; S.ordenes.filter(o => !o.cilindro && o.mes >= D.mes - 1 && o.etapa >= E["Para etiquetar"] && modeloBOM(o.modelo) === m).forEach(o => { for (let n = o.desde; n <= o.hasta; n++) if (!o.rech.some(x => x.n === n)) v.push(masaCarga(n, o)); });
    const st = stats(v); return st ? [m, st, cpk(st, m.min, m.max)] : null; }).filter(Boolean);
  const capOk = cap.filter(c => c[1].n >= 5 && isFinite(c[2])), cpkMin = capOk.length ? Math.min(...capOk.map(c => c[2])) : null; // n < 5: muestra insuficiente para estimar σ
  const ultimo = om.filter(o => !o.cilindro && o.etapa >= E["Para etiquetar"]).sort((a, b) => b.cant - a.cant)[0];
  const masas = ultimo ? Array.from({ length: ultimo.cant }, (_, i) => ultimo.desde + i).filter(n => !ultimo.rech.some(x => x.n === n)) : [];
  const lp = S.ordenes.filter(o => o.mes >= D.mes - 1 && o.etapa >= E["Para etiquetar"] && o.cant >= 20).map(o => ({ op: o.op, n: o.cant, x: o.rech.filter(r => r.ensayo === "PH").length }));
  const causas = CAUSAS.map(([c]) => [c, cerr.reduce((a, o) => a + o.rech.filter(x => x.causa === c).length, 0)]).sort((a, b) => b[1] - a[1]);
  const lotesMP = {}; om.filter(o => o.etapa > 0).forEach(o => Object.entries(o.insumos).forEach(([k, v]) => { const key = k + "|" + v.split(" · ")[0]; const x = lotesMP[key] || (lotesMP[key] = { ops: 0, u: 0 }); x.ops++; x.u += o.cant; }));
  const medV = S.medicion.filter(m => m.cada - dias(m.ult) <= 3);
  const partidas = [...new Set(om.map(o => o.partida))];
  return `<div class="kpis">
    <div class="kpi ${enPT >= esperado * 0.95 ? "ok" : "av"}"><span>Producción a depósito PT</span><b>${n0(enPT)}</b><small>de ${n0(planT)} del plan · esperado a hoy ${n0(esperado)} (${pct(enPT, esperado)})</small></div>
    <div class="kpi in"><span>En proceso (WIP)</span><b>${n0(wip.reduce((a, w) => a + w[1], 0))}</b><small>${om.filter(o => o.etapa > 0 && o.etapa < E["Depósito PT"]).length} órdenes abiertas</small></div>
    <div class="kpi ${rech / Math.max(1, tot) < 0.02 ? "ok" : "av"}"><span>Rendimiento a la primera</span><b>${pct(tot - rech, tot)}</b><small>${rech} rechazos en ${n0(tot)} cerrados</small></div>
    <div class="kpi ${phF / Math.max(1, tot) < 0.01 ? "ok" : "av"}"><span>Fallas en PH</span><b>${pct(phF, tot)}</b><small>${phF} de ${n0(tot)} · ${nf(PH.man, 1)} / ${nf(PH.car, 1)} MPa</small></div>
    <div class="kpi ${cpkMin >= 1.33 ? "ok" : cpkMin >= 1 ? "av" : "no"}"><span>Cpk de carga (peor modelo)</span><b>${cpkMin != null ? nf(cpkMin, 2) : "—"}</b><small>meta ≥ 1,33 (criterio) · modelos con n ≥ 5</small></div>
    <div class="kpi in"><span>Ciclo medio de orden</span><b>${nf(cm, 1)} d</b><small>emisión → depósito PT</small></div>
    <div class="kpi in"><span>Partidas DPS del mes</span><b>${partidas.length}</b><small>${n0(om.reduce((a, o) => a + o.cant, 0))} series reservadas</small></div>
    <div class="kpi ${medV.length ? "av" : "ok"}"><span>Medición por vencer</span><b>${medV.length}</b><small>de ${S.medicion.length} equipos</small></div></div>
  <div class="grilla">
    <div class="panel c6"><header><h2>Equipos en cada etapa</h2><span class="muted">unidades de las órdenes del mes</span></header><div class="cuerpo">${barrasH(wip.map(([e, v, ops]) => [e, v, ops]))}<div style="display:grid;grid-template-columns:minmax(120px,190px) 1fr 54px;gap:10px;font-size:13px;margin-top:6px;border-top:1px solid var(--line);padding-top:6px"><span>Depósito PT</span>${barra(enPT, planT, "var(--green)")}<b class="num">${n0(enPT)}</b></div></div></div>
    <div class="panel c6"><header><h2>Capacidad de proceso: carga</h2><span class="muted">BOM · banda de carga</span></header>${tabla(["Modelo", "n", "x̄ kg", "σ g", "Banda kg", "Cpk"], cap.map(([m, st, c]) => `<tr><td class="nw">${esc(m.nombre.replace("Extintor ", "").replace(/^(.*) sobre ruedas$/, "Carro $1"))}</td><td class="num">${st.n}</td><td class="num">${nf(st.m, 3)}</td><td class="num">${nf(st.sd * 1000, 0)}</td><td class="num nw">${nf(m.min, 2)}–${nf(m.max, 2)}</td><td class="num nw">${st.n < 5 || !isFinite(c) ? pill("n < 5", "gr") : pill(nf(c, 2), c >= 1.33 ? "ok" : c >= 1 ? "av" : "no")}</td></tr>`))}</div>
    <div class="panel c6"><header><h2>Carta I · masa de carga</h2><span class="muted">${ultimo ? `<a href="#" data-det="orden" data-id="${ultimo.op}">${ultimo.op}</a> · ${esc(ultimo.modelo)}` : ""}</span></header><div class="cuerpo">${ultimo ? cartaI(masas.map(n => masaCarga(n, ultimo)), modeloBOM(ultimo.modelo).min, modeloBOM(ultimo.modelo).max, masas.map(ser)) : `<p class="muted">Sin lotes cerrados</p>`}</div></div>
    <div class="panel c6"><header><h2>Carta p · fallas en PH por lote</h2><span class="muted">${MES_TXT[D.mes - 2] || ""} y ${MES_TXT[D.mes - 1]} · lotes de 20 u o más</span></header><div class="cuerpo">${cartaP(lp)}</div></div>
    <div class="panel c5"><header><h2>Rechazos por causa</h2><span class="muted">${MES_TXT[D.mes - 1]}</span></header><div class="cuerpo">${barrasH(causas, "var(--red)")}</div></div>
    <div class="panel c7"><header><h2>Lotes de insumo en uso</h2><span class="muted">${Object.keys(lotesMP).length} lotes en hojas de ruta del mes · 12 de mayor uso</span></header>${tabla(["Insumo", "Lote", "Órdenes", "Equipos"], Object.entries(lotesMP).sort((a, b) => b[1].u - a[1].u).slice(0, 12).map(([k, x]) => { const [ins, lote] = k.split("|"); return `<tr><td>${ins[0].toUpperCase() + ins.slice(1)}</td><td class="mono"><a href="#" data-a="trazaLote" data-q="${esc(lote)}">${esc(lote)}</a></td><td class="num">${x.ops}</td><td class="num">${n0(x.u)}</td></tr>`; }))}</div>
    <div class="panel c12"><header><h2>Órdenes del mes</h2><a href="#ordenes" data-v="ordenes" class="btn sm">Órdenes</a></header>${tabla(["Orden", "Modelo", "Tipo", "Cant", "Partida", "Etapa", "Avance", "Emisión", "Ciclo", "Aptos", "Rech", "Puesto actual"], om.map(o => { const h = hojaRuta(o).find(x => x.estado === "en curso");
      return `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td class="nw">${esc(o.modelo)}</td><td>${tipoEq(o)}</td><td class="num">${o.cant}</td><td class="mono">${o.partida}</td><td>${pill(ETAPAS[o.etapa], etapaPill(o.etapa))}</td><td style="width:110px">${barra(o.etapa, 8, o.etapa >= 7 ? "var(--green)" : "var(--blue)")}</td><td class="nw">${fecha(o.emision)}</td><td class="num">${ciclo(o) ? ciclo(o) + " d" : o.emision ? dias(o.emision) + " d" : "—"}</td><td class="num">${o.etapa >= E["Para etiquetar"] ? aptos(o) : "—"}</td><td class="num">${o.etapa >= E["Para etiquetar"] ? o.rech.length : "—"}</td><td class="muted">${h ? `${h.puesto} · ${esc(h.op)}` : "—"}</td></tr>`; }))}</div>
    <div class="panel c12"><header><h2>Equipos de medición</h2><span class="muted">la PH se bloquea si el contraste supera 15 días (Res. 349/07 art. 20)</span></header>${tabla(["Equipo", "Descripción", "Control", "Último", "Vence", "Estado"], S.medicion.map(m => { const f = m.cada - dias(m.ult); return `<tr><td class="mono">${m.id}</td><td>${esc(m.desc)}</td><td class="muted">${esc(m.tipo)}</td><td>${fecha(m.ult)}</td><td>${fecha(sumar(m.ult, m.cada))}</td><td>${f < 0 ? pill(`vencido hace ${-f} d`, "no") : f <= 3 ? pill(`vence en ${f} d`, "av") : pill(`${f} d`, "ok")}</td></tr>`; }))}</div>
    <div class="panel c12"><header><h2>Estadios de los lotes del mes</h2><a href="#estados" data-v="estados" class="btn sm">Estados del lote</a></header><div class="cuerpo">${ganttLotes(om.filter(o => o.etapa > 0))}</div></div>
    <div class="panel c7"><header><h2>AMFE de proceso: mayor riesgo</h2><a href="#amfe" data-v="amfe" class="btn sm">AMFE completo</a></header>${tabla(["ID", "Modo de falla", "S", "O", "D", "NPR"], amfe(false).slice(0, 6).map(f => `<tr><td class="mono">${f.id}</td><td>${esc(f.modo)}<br><span class="muted" style="font-size:11.5px">${esc(f.base)}</span></td><td class="num">${f.s}</td><td class="num">${f.O}</td><td class="num">${f.d}</td><td class="num">${nprPill(f)}</td></tr>`))}</div>
    <div class="panel c5"><header><h2>Plan de control</h2><span class="muted">DOC-02 · DOC-01</span></header>${tabla(["Cód.", "Característica", "Este mes"], PLAN.map(x => `<tr><td class="mono">${x.c}</td><td>${esc(x.car)}${x.inst.length ? `<br>${x.inst.map(medOk).join(" ")}` : ""}</td><td style="font-size:12.5px">${esc(x.vivo())}</td></tr>`))}</div>
    <div class="panel c12"><header><h2>Cómo llega cada dato a este tablero</h2><a href="#origen" data-a="irOrigenIntra" class="btn sm">Origen de los datos</a></header>${tablaFuente(FUENTE_INTRA)}</div>
  </div>`;
}

function tableroExtra() {
  const c = { "En depósito PT": 0, "En tránsito": 0, "En distribuidor": 0, "Instalado": 0, "Inutilizado": 0 }, jur = { PBA: 0, CABA: 0 }, venc = {}, instMes = [], li = [];
  for (let n = 1; n <= maxSerie(); n++) {
    const e = equipo(n); if (c[e.estado] != null) c[e.estado]++;
    if (e.inst) { jur[cliente(e.inst.cliente).jur]++; if (new Date(e.inst.fecha).getMonth() + 1 === D.mes) instMes.push(e); if (e.remito && e.remito.recibido) li.push(dias(e.remito.recibido, e.inst.fecha)); }
    if (e.mant && (e.estado === "Instalado" || e.estado === "En distribuidor")) { const d = new Date(e.mant), k = d.getFullYear() * 12 + d.getMonth(); venc[k] = (venc[k] || 0) + 1; }
  }
  const k0 = HOY.getFullYear() * 12 + HOY.getMonth(), meses = Array.from({ length: 12 }, (_, i) => k0 + 1 + i).map(k => [MES_TXT[k % 12].slice(0, 3) + " " + String(Math.floor(k / 12)).slice(2), venc[k] || 0]);
  const recib = S.remitos.filter(r => r.recibido), lead = recib.length ? recib.reduce((a, r) => a + dias(r.fecha, r.recibido), 0) / recib.length : 0;
  const inst = li.length ? li.reduce((a, x) => a + x, 0) / li.length : 0;
  const sinConf = S.remitos.filter(r => r.estado === "Sin confirmar" || (r.estado === "En tránsito" && dias(r.fecha) > 2));
  const hab = habiles(D.anio, D.mes), trans = hab.filter(d => d <= HOY).length, planR = planRecargas(), hechas = Math.round(planR * trans / hab.length) + S.recargas.filter(r => r.etapa === 5).length;
  const rcAb = S.reclamos.filter(x => x.etapa < 3), enPlazo = S.reclamos.filter(x => !vencido(x)).length;
  const porTipo = {}; [...D.recargas.comercial, ...D.recargas.industrial].forEach(t => { porTipo[t.agente] = (porTipo[t.agente] || 0) + t.cant; });
  return `<div class="kpis">
    <div class="kpi ok"><span>Equipos en el mercado</span><b>${n0(c["En distribuidor"] + c.Instalado)}</b><small>${n0(c.Instalado)} instalados · ${n0(c["En distribuidor"])} en distribuidores</small></div>
    <div class="kpi in"><span>En tránsito</span><b>${n0(c["En tránsito"])}</b><small>${((k) => k + (k === 1 ? " remito" : " remitos"))(S.remitos.filter(r => r.estado === "En tránsito").length)} · COT vigente</small></div>
    <div class="kpi ${sinConf.length ? "av" : "ok"}"><span>Recepción sin confirmar</span><b>${sinConf.length}</b><small>remitos con más de 48 h</small></div>
    <div class="kpi in"><span>Despacho → recepción</span><b>${nf(lead, 1)} d</b><small>recepción → instalación ${nf(inst, 1)} d</small></div>
    <div class="kpi ok"><span>Instalaciones del mes</span><b>${instMes.length}</b><small>PBA ${n0(jur.PBA)} · CABA ${n0(jur.CABA)} en el año</small></div>
    <div class="kpi in"><span>Recargas del mes</span><b>${n0(hechas)}</b><small>de ${n0(planR)} del plan · ${S.recargas.filter(r => r.etapa < 5).length} abiertas</small></div>
    <div class="kpi ${enPlazo === S.reclamos.length ? "ok" : "av"}"><span>Reclamos en plazo</span><b>${pct(enPlazo, S.reclamos.length)}</b><small>${rcAb.length} abiertos</small></div>
    <div class="kpi ${S.retiros.some(x => x.estado !== "Cerrado") ? "no" : "ok"}"><span>Retiros preventivos</span><b>${S.retiros.filter(x => x.estado !== "Cerrado").length}</b><small>${S.retiros[0] ? `${S.retiros[0].id}: ${nf(100 * S.retiros[0].ubicados, 0)} % ubicado` : "ninguno"}</small></div></div>
  <div class="grilla">
    <div class="panel c6"><header><h2>Cadena de custodia</h2><span class="muted">series de ${D.anio} fuera de producción</span></header><div class="cuerpo">${barrasH([["FLAMA · depósito PT", c["En depósito PT"], "pallet SSCC"], ["Transportista", c["En tránsito"], "remito + COT"], ["Distribuidor", c["En distribuidor"], "comercializador inscripto"], ["Usuario", c.Instalado, "tarjeta DPS o SGM"], ["Inutilizados", c.Inutilizado, "acta anexo G"]], "var(--violet)")}</div></div>
    <div class="panel c6"><header><h2>Tarjetas oficiales por jurisdicción</h2></header><div class="cuerpo">${barrasH([["PBA · tarjeta DPS + estampilla", jur.PBA, "Res. 349/07"], ["CABA · SGM de la AGC", jur.CABA, "Res. 32-AGC/15"]], "var(--blue)")}
      <p class="muted" style="font-size:12.5px;margin:10px 0 0">Las tarjetas de CABA salen en el archivo batch de Reportes; las de PBA, en el libro de actas DPS.</p></div></div>
    <div class="panel c8"><header><h2>Vencimientos de mantenimiento</h2><span class="muted">próximos 12 meses · equipos en distribuidores y usuarios</span></header><div class="cuerpo">${columnas(meses, "var(--yellow)")}</div></div>
    <div class="panel c4"><header><h2>Remitos abiertos</h2></header>${tabla(["Remito", "Cliente", "Días", ""], S.remitos.filter(r => r.estado !== "Recibido").map(r => `<tr class="click" data-det="remito" data-id="${r.id}"><td class="mono nw">${r.id.slice(-8)}</td><td>${esc(cliente(r.cliente).nombre)}</td><td class="num">${dias(r.fecha)}</td><td>${pill(r.estado, estRem[r.estado])}</td></tr>`), { vacio: "Todo recibido" })}</div>
    <div class="panel c6"><header><h2>Recargas por etapa</h2><span class="muted">dos plantas</span></header><div class="cuerpo">${barrasH(ETAPAS_OS.slice(0, 5).map((e, i) => [e, S.recargas.filter(r => r.etapa === i && !r.inutil).length]).concat([["Para inutilizar", S.recargas.filter(r => r.inutil).length]]), "var(--blue)")}
      <p class="muted" style="font-size:12.5px;margin:8px 0 0">Con PH: ${S.recargas.filter(r => r.ph).length} · polvo bajo de peso (cambio total): ${S.recargas.filter(r => r.polvoBajo).length} · sustitutos prestados: ${S.recargas.filter(r => r.sustituto && r.etapa < 5).length}</p></div></div>
    <div class="panel c6"><header><h2>Plan de recargas por agente</h2><span class="muted">${MES_TXT[D.mes - 1]} · Aprovechamiento_Recargas</span></header><div class="cuerpo">${barrasH(Object.entries(porTipo).sort((a, b) => b[1] - a[1]).map(([k, v]) => [k, Math.round(v)]), "var(--green)")}</div></div>
    <div class="panel c6"><header><h2>Reclamos</h2></header>${tabla(["Tipo", "Abiertos", "Fuera de plazo", "Plazo"], Object.keys(PLAZO_RC).map(t => `<tr><td>${t}</td><td class="num">${S.reclamos.filter(x => x.tipo === t && x.etapa < 3).length}</td><td class="num">${S.reclamos.filter(x => x.tipo === t && vencido(x)).length}</td><td class="num">${PLAZO_RC[t]} d</td></tr>`))}</div>
    <div class="panel c6"><header><h2>Retiros preventivos</h2><a href="#traza" data-v="traza" class="btn sm">Traza y retiros</a></header>${tabla(["Retiro", "Lote", "Equipos", "Ubicados", "Estado"], S.retiros.map(x => { const a = afectados(x.lote); return `<tr><td class="mono">${x.id}</td><td class="mono">${esc(x.lote)}</td><td class="num">${a.length}</td><td class="num">${Math.round(a.length * x.ubicados)}</td><td>${pill(x.estado, x.estado === "Cerrado" ? "ok" : "no")}</td></tr>`; }), { vacio: "Sin retiros" })}</div>
    <div class="panel c7"><header><h2>AMFE de campo: mayor riesgo</h2><a href="#amfecampo" data-v="amfecampo" class="btn sm">AMFE de campo</a></header>${tabla(["ID", "Modo de falla", "S", "O", "D", "NPR"], amfe(true).slice(0, 6).map(f => `<tr><td class="mono">${f.id}</td><td>${esc(f.modo)}<br><span class="muted" style="font-size:11.5px">${esc(f.base)}</span></td><td class="num">${f.s}</td><td class="num">${f.O}</td><td class="num">${f.d}</td><td class="num">${nprPill(f)}</td></tr>`))}</div>
    <div class="panel c5"><header><h2>Estados del equipo</h2><a href="#estadoseq" data-v="estadoseq" class="btn sm">Ver estados</a></header><div class="cuerpo">${barrasH(ESTADOS_EQ.map(([e, , , reg]) => [e, censo().est[e] || 0, reg]), "var(--violet)")}</div></div>
    <div class="panel c12"><header><h2>Cómo llega cada dato a este tablero</h2><a href="#origen" data-a="irOrigenExtra" class="btn sm">Origen de los datos</a></header>${tablaFuente(FUENTE_EXTRA)}</div>
  </div>`;
}
