// ================================================================ análisis de desvíos: cartas de control, Pareto y registro de desvíos (RD)
// Las órdenes y cantidades son las del Plan mensual; rechazos, masas y reclamos son simulados con semilla fija.
const DV = (() => {
  const r = semilla(2026), lt = lotesMes(), N = lt.reduce((a, l) => a + l.cant, 0);
  // carta I de masa de carga del lote en recorrido (tolerancia ABC 5 kg: 0 / +300 g)
  const masas = SERIES.map((s, i) => s === REJ ? null : Math.round(i === 31 ? 5268 : normal(r, 5140, 33)));
  const v = masas.filter(x => x != null), media = v.reduce((a, x) => a + x, 0) / v.length;
  const mr = v.slice(1).map((x, i) => Math.abs(x - v[i])), mrb = mr.reduce((a, x) => a + x, 0) / mr.length;
  const lcs = media + 2.66 * mrb, lci = media - 2.66 * mrb;
  // carta p de fallas en PH por lote del mes
  const ph = lt.filter(l => l.cant >= 20).map((l, i) => ({ op: l.op, n: l.cant, x: l.op === DEMO.op ? 1 : i === 3 ? 5 : Math.floor(r() * 2.2) }));   // lotes de cola chicos fuera: su LCS no dice nada
  const fph = ph.reduce((a, q) => a + q.x, 0);
  const causas = [["Fuga en PH", fph], ["Pérdida en válvula", 9], ["Espesor fuera de tolerancia", 6], ["Golpe o pintura", 5], ["Carga fuera de tolerancia", 4], ["Grabado ilegible", 2]].sort((a, b) => b[1] - a[1]);
  const rech = causas.reduce((a, c) => a + c[1], 0);
  const pb = ph.reduce((a, q) => a + q.x, 0) / ph.reduce((a, q) => a + q.n, 0);
  ph.forEach(q => { q.p = q.x / q.n; q.lcs = pb + 3 * Math.sqrt(pb * (1 - pb) / q.n); });
  return { N, causas, rech, masas, media, lcs, lci, ph, pb, lt };
})();
const SEV = { "Crítica": "var(--red)", "Mayor": "var(--yellow)", "Menor": "var(--blue)" };
const RDS = [
  { id: "031", origen: "Proceso", que: `Fuga en el cordón longitudinal en PH · ${REJ}`, ref: DEMO.op, sev: "Mayor", estado: "Cerrado", resp: "Mantenimiento",
    porq: ["¿Por qué fugó? Poro en el cordón longitudinal.", "¿Por qué hubo poro? Falta de gas en el arranque.", "¿Por qué faltó gas? Boquilla de la soldadora 10 con salpicaduras.", "¿Por qué no se limpió? No había frecuencia definida."], accion: "Limpieza de boquilla cada 50 cordones y cambio cada 500.", verif: "0 fugas en los 3 lotes siguientes." },
  { id: "032", origen: "Proceso", que: `Carta de carga fuera de control: 5,268 kg en ${SERIES[31]} (dentro de tolerancia)`, ref: "balanza B-2", sev: "Menor", estado: "Abierto", resp: "Calidad",
    porq: ["¿Por qué subió la masa? La balanza marcaba 25 g de menos.", "¿Por qué? No se hizo cero al cambiar la bolsa de polvo.", "¿Por qué? El cero es manual y no está en la hoja."], accion: "Cero obligatorio en la pantalla de carga al cambiar de bolsa.", verif: "Pendiente: 2 lotes sin puntos fuera de control." },
  { id: "033", origen: "Custodia", que: `Equipo golpeado en tránsito · ${SERIES[5]}`, ref: "R 0001-00004521", sev: "Menor", estado: "En curso", resp: "Depósito PT",
    porq: ["¿Por qué se golpeó? Se movió la fila exterior del pallet.", "¿Por qué? El pallet no llevaba esquineros.", "¿Por qué? No están en la instrucción de 5 kg."], accion: "Esquineros en todos los pallets de manuales.", verif: "Pendiente: 10 despachos sin daño." },
  { id: "034", origen: "Proceso", que: `${DV.ph[3] ? DV.ph[3].op : "OP"}: 5 fallas en PH, sobre el límite de la carta p`, ref: "cúpulas CU-0298", sev: "Crítica", estado: "Cerrado", resp: "Calidad + compras",
    porq: ["¿Por qué tantas fallas? Fugas en el bordón cúpula-cuerpo.", "¿Por qué? Bordón de las cúpulas fuera de medida.", "¿Por qué? Lote CU-0298 con matriz gastada.", "¿Por qué pasó la recepción? Se controlaba 1 de cada 200."], accion: "Lote retenido y re-ensayado al 100 %; muestreo de recepción 1 cada 50.", verif: "Carta p dentro de límites 4 semanas." },
  { id: "035", origen: "Custodia", que: "Remito R 0001-00004498 sin confirmar 72 h", ref: "Distribuidor Oeste", sev: "Menor", estado: "Cerrado", resp: "Ventas",
    porq: ["¿Por qué no confirmó? El distribuidor no tenía usuario.", "¿Por qué? El alta se hacía después del primer envío."], accion: "Alta de usuarios antes del primer despacho.", verif: "Confirmaciones ≤ 48 h en el mes." },
  { id: "036", origen: "Cliente", que: `Reclamo de seguridad RC-${AA}-000116 respondido a las 27 h (plazo 24 h)`, ref: `${AA}-001198`, sev: "Mayor", estado: "Abierto", resp: "Atención",
    porq: ["¿Por qué se pasó? Entró un viernes a las 18 h.", "¿Por qué nadie lo vio? No hay guardia de fin de semana.", "¿Por qué? El plazo de 24 h no estaba en la guardia."], accion: "Guardia de fin de semana solo para reclamos de seguridad, con aviso al celular.", verif: "Pendiente: 100 % de seguridad en plazo por 2 meses." },
  { id: "037", origen: "Registro", que: "Contraste del manómetro PH-M2 a los 17 días (máximo 15)", ref: "Res. 349/07 art. 20", sev: "Mayor", estado: "Cerrado", resp: "Calidad",
    porq: ["¿Por qué se pasó? El técnico estaba de licencia.", "¿Por qué no lo hizo otro? No había suplente asignado."], accion: "Alerta 3 días antes y suplente designado; la app bloquea la PH al día 16.", verif: "Sin vencimientos en 3 meses." },
  { id: "038", origen: "Registro", que: "2 lecturas manuales en etiquetado por grabado poco profundo", ref: "Pannier · punzón", sev: "Menor", estado: "Abierto", resp: "Producción",
    porq: ["¿Por qué no leyó? Grabado de 0,12 mm.", "¿Por qué tan poco? Punzón con desgaste.", "¿Por qué no se vio antes? No se mide la profundidad."], accion: "Medir profundidad en la primera planchuela de cada lote.", verif: "Pendiente: 0 lecturas manuales en 5 lotes." },
];
const REGLAS = [
  ["Prueba hidráulica con ✗", "1 equipo", "hoja de ruta (cierre)", "bloquea la serie y abre un RD"],
  ["Fallas en PH de un lote", "sobre el LCS de la carta p", "cierre de lote", "retiene el lote para re-ensayo"],
  ["Masa de carga", "fuera de 5,00-5,30 kg (DOC-02)", "carga", "rechazo y RD"],
  ["Carta de carga", "1 punto fuera de 3 σ o 7 seguidos del mismo lado", "carga", "aviso a calidad (sin rechazo)"],
  ["Contraste del manómetro de PH", "más de 15 días (Res. 349/07 art. 20)", "calidad", "bloquea la PH"],
  ["Recepción sin confirmar", "más de 48 h (criterio)", "custodia", "aviso a ventas"],
  ["Reclamo de seguridad", "sin contacto a las 24 h (criterio)", "reclamos", "sube al jefe de calidad"],
  ["Pedido de datos personales", "a 2 días del vencimiento legal", "reclamos", "aviso a atención"],
  ["Mantenimiento vencido", "el mes siguiente al vencimiento", "fichas", "aviso al titular y al recargador"],
];

// ---------------------------------------------------------------- gráficos SVG (un eje, marcas finas, tooltip en cada marca)
function graficoPareto() {
  const W = 640, fila = 34, H = DV.causas.length * fila + 34, x0 = 190, x1 = W - 120, max = DV.causas[0][1];
  let acum = 0;
  const filas = DV.causas.map(([c, n], i) => {
    acum += n; const y = 14 + i * fila, w = (x1 - x0) * n / max, pct = acum / DV.rech * 100;
    return `<g data-tip="${esc(c)}: ${n} rechazos · ${nf(n / DV.rech * 100, 0)} % del total · acumulado ${nf(pct, 0)} %"><rect x="0" y="${y - 4}" width="${W}" height="${fila - 2}" fill="transparent"/>
      <text x="${x0 - 10}" y="${y + 13}" text-anchor="end" class="t-ink">${esc(c)}</text>
      <rect x="${x0}" y="${y}" width="${Math.max(w, 2)}" height="18" rx="3" fill="var(--chart-2)"/>
      <text x="${x0 + w + 8}" y="${y + 13}" class="t-ink" style="font-weight:600">${n}</text>
      <text x="${W - 4}" y="${y + 13}" text-anchor="end">${nf(pct, 0)} % acum.</text></g>`;
  }).join("");
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Pareto de rechazos por causa">
    <line x1="${x0}" x2="${x0}" y1="6" y2="${H - 22}" class="eje"/>${filas}
    <text x="${x0}" y="${H - 4}">0</text><text x="${x1}" y="${H - 4}" text-anchor="middle">${max}</text></svg>`;
}
function graficoCarga() {
  const W = 1000, H = 300, l = 46, rr = 70, t = 14, b = 30, lo = 4980, hi = 5320;
  const X = i => l + (W - l - rr) * i / (SERIES.length - 1), Y = v => t + (H - t - b) * (hi - v) / (hi - lo);
  const pts = DV.masas.map((m, i) => m == null ? null : [X(i), Y(m), m, i]).filter(Boolean);
  const linea = pts.map((p, k) => (k ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join("");
  const lim = (v, txt, cls, col) => `<line x1="${l}" x2="${W - rr}" y1="${Y(v)}" y2="${Y(v)}" stroke="${col}" stroke-width="1.5" class="${cls}"/><text x="${W - rr + 6}" y="${Y(v) + 4}">${txt}</text>`;
  const grid = [5000, 5100, 5200, 5300].map(v => `<line x1="${l}" x2="${W - rr}" y1="${Y(v)}" y2="${Y(v)}" class="grid"/><text x="${l - 6}" y="${Y(v) + 4}" text-anchor="end">${nf(v / 1000, 1)}</text>`).join("");
  const marcas = pts.map(([x, y, m, i]) => { const fuera = m > DV.lcs || m < DV.lci;
    return `<g data-tip="${SERIES[i]} · ${nf(m / 1000, 3)} kg${fuera ? " · fuera de control (RD-" + AA + "-032)" : ""}"><circle cx="${x}" cy="${y}" r="9" fill="transparent"/><circle cx="${x}" cy="${y}" r="${fuera ? 5 : 3.5}" fill="${fuera ? "var(--red)" : "var(--chart-2)"}" stroke="var(--surface)" stroke-width="1.5"/></g>`; }).join("");
  const f = pts.find(p => p[2] > DV.lcs);
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Carta de control de la masa de carga del lote">${grid}
    ${lim(5000, "LIE 5,00", "", "var(--ink-3)")}${lim(5300, "LSE 5,30", "", "var(--ink-3)")}${lim(DV.lcs, "LCS " + nf(DV.lcs / 1000, 3), "lim", "var(--red)")}${lim(DV.lci, "LCI " + nf(DV.lci / 1000, 3), "lim", "var(--red)")}${lim(DV.media, "x̄ " + nf(DV.media / 1000, 3), "", "var(--ink-2)")}
    <path d="${linea}" fill="none" stroke="var(--chart-2)" stroke-width="1.5" opacity=".55"/>${marcas}
    ${f ? `<text x="${f[0] + 8}" y="${f[1] - 8}" class="t-ink" style="font-weight:600">${SERIES[f[3]]}</text>` : ""}
    <text x="${l}" y="${H - 8}">equipo 1</text><text x="${W - rr}" y="${H - 8}" text-anchor="end">equipo ${SERIES.length}</text><text x="${l - 6}" y="${t - 2}" text-anchor="end">kg</text></svg>`;
}
function graficoP() {
  const W = 640, H = 240, l = 46, rr = 20, t = 14, b = 44, n = DV.ph.length, max = Math.max(0.1, ...DV.ph.map(q => Math.max(q.p, q.lcs))) * 1.1;
  const X = i => l + (W - l - rr) * (i + .5) / n, Y = v => t + (H - t - b) * (1 - v / max), bw = (W - l - rr) / n;
  const grid = [0, .02, .04, .06, .08].filter(v => v <= max).map(v => `<line x1="${l}" x2="${W - rr}" y1="${Y(v)}" y2="${Y(v)}" class="grid"/><text x="${l - 6}" y="${Y(v) + 4}" text-anchor="end">${nf(v * 100, 0)} %</text>`).join("");
  const lcs = DV.ph.map((q, i) => `${i ? "L" : "M"}${(X(i) - bw / 2).toFixed(1)} ${Y(q.lcs).toFixed(1)}H${(X(i) + bw / 2).toFixed(1)}`).join("");
  const marcas = DV.ph.map((q, i) => { const fuera = q.p > q.lcs, demo = q.op === DEMO.op;
    return `<g data-tip="${q.op} · ${q.x} de ${q.n} con falla (${nf(q.p * 100, 1)} %) · LCS ${nf(q.lcs * 100, 1)} %"><rect x="${X(i) - bw / 2}" y="${t}" width="${bw}" height="${H - t - b}" fill="transparent"/>
      <circle cx="${X(i)}" cy="${Y(q.p)}" r="${fuera ? 5.5 : 4}" fill="${fuera ? "var(--red)" : "var(--chart-2)"}" stroke="${demo ? "var(--ink)" : "var(--surface)"}" stroke-width="${demo ? 2 : 1.5}"/>
      <text x="${X(i)}" y="${H - b + 16}" text-anchor="middle" style="font-size:10px">${q.op.slice(-2)}</text></g>`; }).join("");
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Carta p de fallas en prueba hidráulica por lote">${grid}
    <line x1="${l}" x2="${W - rr}" y1="${Y(DV.pb)}" y2="${Y(DV.pb)}" stroke="var(--ink-2)" stroke-width="1.2"/><path d="${lcs}" fill="none" stroke="var(--red)" stroke-width="1.5" class="lim"/>${marcas}
    <text x="${l}" y="${H - 8}">orden de ${MES} (últimos dígitos)</text><text x="${W - rr}" y="${H - 8}" text-anchor="end">p̄ ${nf(DV.pb * 100, 1)} % · LCS escalonado por tamaño de lote</text></svg>`;
}

function vistaDesvios() {
  const fpy = 1 - DV.rech / DV.N, fuera = DV.masas.filter(m => m != null && (m > DV.lcs || m < DV.lci)).length, pFuera = DV.ph.filter(q => q.p > q.lcs).length;
  const abiertos = RDS.filter(r => r.estado !== "Cerrado").length;
  const tiles = [["ok", nf(fpy * 100, 1) + " %", "rendimiento a la primera", `${DV.rech} rechazos en ${n0(DV.N)} equipos`], [pFuera ? "no" : "ok", pFuera, "lotes sobre el LCS de la carta p", "fallas en PH"],
    [fuera ? "av" : "ok", fuera, "puntos fuera de control", "masa de carga del lote"], ["av", "1", "recepción sin confirmar > 48 h", "custodia"], ["av", "92 %", "reclamos en plazo", "seguridad: 1 vencido"], [abiertos ? "av" : "ok", abiertos, "desvíos abiertos", `${RDS.length} en el mes`]];
  const filtro = S.desv.sev, lista = RDS.filter(r => filtro === "todas" || (filtro === "abiertos" ? r.estado !== "Cerrado" : r.sev === filtro));
  return `<div class="cabeza wrap"><div class="cabeza-in"><div><div class="ceja">Análisis de desvíos</div><h1>Lo que salió distinto, y por qué</h1>
    <p>Las cartas y el Pareto se arman solos con los eventos de la base. Cada desvío tiene causa, acción y verificación; nada se cierra sin la prueba de que no volvió a pasar.</p></div>
    <div class="doc-id">${D.mesNombre} ${D.anio} · ${DV.lt.length} órdenes de manuales<br>Órdenes reales del Plan mensual · rechazos, masas y reclamos simulados</div></div></div>
  <div class="cuerpo wrap"><div class="pila">
    <div class="tiles">${tiles.map(([c, v, t, s]) => `<div class="tile ${c}"><b>${v}</b><span>${esc(t)}</span><small>${esc(s)}</small></div>`).join("")}</div>
    <div class="dos-col">
      <div class="bloque"><h3>Rechazos por causa</h3><p class="sub">Pareto del mes: las dos primeras causas son el ${nf((DV.causas[0][1] + DV.causas[1][1]) / DV.rech * 100, 0)} % de los rechazos.</p>${graficoPareto()}</div>
      <div class="bloque"><h3>Fallas en PH por lote</h3><p class="sub">Carta p de las órdenes de 20 equipos o más. El punto con borde oscuro es el lote del recorrido (${esc(DEMO.op)}).</p>${graficoP()}</div>
    </div>
    <div class="bloque"><h3>Masa de carga del lote ${esc(DEMO.op)}</h3><p class="sub">Carta de valores individuales. Los límites de especificación (DOC-02: 5 kg, 0/+300 g) son grises; los de control, rojos punteados. El ${esc(REJ)} no se cargó: falló la PH.</p>${graficoCarga()}</div>
    <div class="bloque"><div class="fila" style="justify-content:space-between"><div><h3>Registro de desvíos</h3><p class="sub" style="margin:0">Tocá un desvío para ver los porqués, la acción y cómo se verifica.</p></div>
      <div class="filtros" role="group" aria-label="Filtrar desvíos">${["todas", "abiertos", "Crítica", "Mayor", "Menor"].map(k => `<button aria-pressed="${filtro === k}" data-a="filtroRD" data-k="${k}">${k === "todas" ? "Todos" : k === "abiertos" ? "Abiertos" : k}</button>`).join("")}</div></div>
      <div class="tscroll" style="margin-top:12px"><table class="tabla"><thead><tr><th>RD</th><th>Origen</th><th>Qué pasó</th><th>Referencia</th><th>Severidad</th><th>Responsable</th><th>Estado</th></tr></thead><tbody>
      ${lista.map(r => `<tr data-a="abrirRD" data-k="${r.id}" style="cursor:pointer"><td class="mono nw">RD-${AA}-${r.id}</td><td>${esc(r.origen)}</td><td>${esc(r.que)}</td><td class="mono nw">${esc(r.ref)}</td><td class="nw"><span class="sev" style="background:${SEV[r.sev]}"></span>${r.sev}</td><td>${esc(r.resp)}</td><td><span class="pill ${r.estado === "Cerrado" ? "ok" : r.estado === "Abierto" ? "no" : "av"}">${r.estado}</span></td></tr>
        ${S.desv.abierto === r.id ? `<tr class="rd-det"><td></td><td colspan="6"><b>5 porqués</b><ol class="porques">${r.porq.map(p => `<li>${esc(p)}</li>`).join("")}</ol><dl class="dl" style="grid-template-columns:110px 1fr"><dt>Acción</dt><dd>${esc(r.accion)}</dd><dt>Verificación</dt><dd>${esc(r.verif)}</dd></dl></td></tr>` : ""}`).join("") || `<tr><td colspan="7" class="nota">No hay desvíos con ese filtro.</td></tr>`}</tbody></table></div></div>
    <div class="bloque"><h3>Reglas que abren un desvío solas</h3><p class="sub">La app las revisa con cada evento; los umbrales marcados «criterio» los fija FLAMA.</p>
      <div class="tscroll"><table class="tabla"><thead><tr><th>Qué se mira</th><th>Umbral</th><th>Dónde</th><th>Qué hace la app</th></tr></thead><tbody>${REGLAS.map(f => `<tr>${f.map(c => `<td>${esc(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div></div>
  </div></div>`;
}
Object.assign(ACC, {
  filtroRD(el) { S.desv.sev = el.dataset.k; pintar(); },
  abrirRD(el) { S.desv.abierto = S.desv.abierto === el.dataset.k ? null : el.dataset.k; pintar(); },
});
