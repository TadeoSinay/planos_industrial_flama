// ================================================================ producción: órdenes, calidad y etiquetado
const aptos = o => o.cant - o.rech.length;
const fil = (k, def) => UI.f[k] ?? def;
const chips = (k, ops, def) => `<div class="filtros" role="group">${ops.map(([v, t]) => `<button aria-pressed="${fil(k, def) === v}" data-a="filtro" data-k="${k}" data-v="${v}">${esc(t)}</button>`).join("")}</div>`;
ACC.filtro = el => { UI.f[el.dataset.k] = el.dataset.v; UI.pag[UI.vista] = 0; pintar(); };
const medicionPH = o => S.medicion.find(m => m.id === (o.carro ? "PH-M2" : "PH-M1"));
const vencida = m => dias(m.ult) > m.cada;

// ---------------------------------------------------------------- órdenes
VISTAS.ordenes = {
  titulo: "Órdenes de producción",
  sub: () => `Plan mensual de ${MES_TXT[D.mes - 1]} ${D.anio} · Aprovechamiento_Manuales ${D.rangos.man} y Aprovechamiento_Carros ${D.rangos.car}`,
  acciones: () => `<button class="btn" data-a="csvOrdenes">Copiar para Sheets</button>`,
  html() {
    const mes = +fil("omes", D.mes), lin = fil("olin", "Todas"), est = fil("oest", "todas");
    const ops = S.ordenes.filter(o => o.mes === mes && (lin === "Todas" || o.linea === lin) &&
      (est === "todas" || (est === "curso" && o.etapa > 0 && o.etapa < E["Para cerrar"]) || (est === "cerrar" && o.etapa === E["Para cerrar"]) ||
       (est === "etiq" && o.etapa === E["Para etiquetar"]) || (est === "pt" && o.etapa === E["Depósito PT"]) || (est === "desp" && o.etapa === E["Despachada"]) || (est === "plan" && o.etapa === 0)));
    const plan = D.plan.filter(p => p.tipo === "Terminado").map(p => {
      const os = S.ordenes.filter(o => o.mes === D.mes && o.modelo === p.producto);
      const fin = os.filter(o => o.etapa >= E["Depósito PT"]).reduce((a, o) => a + aptos(o), 0);
      return `<tr><td>${esc(p.producto)}</td><td>${p.linea}</td><td class="num">${n0(p.cant)}</td><td class="num">${os.length}</td><td class="num">${n0(fin)}</td><td style="width:160px">${barra(fin, p.cant, "var(--green)")}</td></tr>`; });
    return `<div class="panel"><header><h2>Plan del mes</h2><span class="muted">${n0(D.plan.filter(p => p.tipo === "Terminado").reduce((a, p) => a + p.cant, 0))} equipos terminados${D.plan.some(p => p.tipo !== "Terminado") ? " · además " + D.plan.filter(p => p.tipo !== "Terminado").map(p => `${p.cant} × ${p.producto}`).join(", ") + " (se venden vacíos, sin serie de equipo)" : ""}</span></header>${tabla(["Producto", "Línea", "Plan", "Órdenes", "Aptos en PT", "Avance"], plan)}</div>
      <div class="panel"><header><div class="filtros"><select aria-label="Mes" data-k="omes" data-cambio="filtroSel">${Array.from({ length: D.mes }, (_, i) => `<option value="${i + 1}" ${mes === i + 1 ? "selected" : ""}>${MES_TXT[i]} ${D.anio}</option>`).reverse().join("")}</select>
        ${chips("olin", [["Todas", "Todas"], ["Manuales", "Manuales"], ["Carros", "Carros"]], "Todas")}</div>
        ${chips("oest", [["todas", "Todas"], ["plan", "Planificadas"], ["curso", "En proceso"], ["cerrar", "Para cerrar"], ["etiq", "Para etiquetar"], ["pt", "En depósito"], ["desp", "Despachadas"]], "todas")}</header>
      ${tabla(["Orden", "Modelo", "Cant", "Series", "Partida DPS", "Etapa", "Avance", "Rech", "Cierre"], ops.map(o => `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono nw">${o.op}</td><td class="nw">${esc(o.modelo)}</td><td class="num">${o.cant}</td>
        <td class="mono nw">${ser(o.desde)} → ${ser(o.hasta).slice(3)}</td><td class="mono">${o.partida}</td><td>${pill(ETAPAS[o.etapa], etapaPill(o.etapa))}</td><td style="width:120px">${barra(o.etapa, 8, o.etapa >= 7 ? "var(--green)" : "var(--blue)")}</td>
        <td class="num">${o.etapa >= E["Para etiquetar"] ? o.rech.length : "—"}</td><td class="nw">${fecha(o.cierre)}</td></tr>`), { vacio: "No hay órdenes con ese filtro" })}</div>`;
  },
};
ACC.filtroSel = el => { UI.f[el.dataset.k] = el.value; pintar(); };
ACC.csvOrdenes = () => copiar(["orden\tmodelo\tcant\tserie_desde\tserie_hasta\tpartida\tetapa\trechazos\tcierre", ...S.ordenes.filter(o => o.mes === D.mes).map(o => [o.op, o.modelo, o.cant, ser(o.desde), ser(o.hasta), o.partida, ETAPAS[o.etapa], o.rech.length, fecha(o.cierre)].join("\t"))].join("\n"));

DETALLES.orden = op => {
  const o = S.ordenes.find(x => x.op === op); if (!o) return null;
  const m = modeloBOM(o.modelo), med = medicionPH(o), rem = o.remito && remito(o.remito);
  const sig = o.etapa < E["Para cerrar"] ? ETAPAS[o.etapa + 1] : null;
  const rechSet = new Set(o.rech.map(x => x.n));
  const pie = o.etapa === 0 ? `<button class="btn pri" data-a="avanzarOrden" data-id="${o.op}">Liberar a producción</button>`
    : o.etapa < E["Para cerrar"] ? `<button class="btn pri" data-a="avanzarOrden" data-id="${o.op}">Pasar a ${esc(sig)}</button>`
    : o.etapa === E["Para cerrar"] ? `<button class="btn ok" data-a="cerrarOrden" data-id="${o.op}" ${vencida(med) ? "disabled" : ""}>Cerrar lote</button>`
    : o.etapa === E["Para etiquetar"] ? `<button class="btn pri" data-a="aEtiquetado" data-id="${o.op}">Ir a etiquetado</button>`
    : o.etapa === E["Depósito PT"] ? `<button class="btn pri" data-a="nuevoRemito" data-id="${o.op}">Armar remito</button>` : "";
  return { titulo: o.op, sub: `${esc(o.modelo)} · ${o.cant} u · ${o.linea} · partida ${o.partida}`, pie,
    cuerpo: `<div class="etapas">${ETAPAS.map((e, i) => `<span class="${i < o.etapa ? "hecha" : i === o.etapa ? "actual" : ""}">${esc(e)}</span>`).join("")}</div>
      ${o.etapa === E["Para cerrar"] && vencida(med) ? `<div class="aviso no">El manómetro ${med.id} tiene el contraste vencido (${dias(med.ult)} días). Registralo en Calidad para poder cerrar.</div>` : ""}
      <div><h3>Datos</h3><dl class="dl"><dt>Series</dt><dd class="mono">${ser(o.desde)} a ${ser(o.hasta)}</dd><dt>Emitida</dt><dd>${fecha(o.emision)}</dd><dt>Cerrada</dt><dd>${fecha(o.cierre)}</dd>
        <dt>Prueba hidráulica</dt><dd>${o.carro ? PH.car : PH.man} · manómetro ${med.id}</dd><dt>Carga</dt><dd>${m ? `${nf(m.min, 2)} a ${nf(m.max, 2)} kg (BOM)` : "—"}</dd>
        <dt>Remito</dt><dd>${rem ? `<a href="#" data-det="remito" data-id="${rem.id}">${rem.id}</a> · ${esc(cliente(rem.cliente).nombre)}` : "—"}</dd></dl></div>
      <div><h3>Lotes de insumo</h3><dl class="dl">${Object.entries(o.insumos).map(([k, v]) => `<dt>${k[0].toUpperCase() + k.slice(1)}</dt><dd><a href="#" class="mono" data-det="loteMP" data-id="${v}">${v}</a></dd>`).join("")}</dl></div>
      <div><h3>Rechazos</h3>${o.etapa < E["Para etiquetar"] ? `<p class="muted" style="margin:0">Se cargan al cerrar el lote.</p>` : o.rech.length ? tabla(["Serie", "Ensayo", "Causa"], o.rech.map(x => `<tr class="click" data-det="equipo" data-id="${x.n}"><td class="mono">${ser(x.n)}</td><td>${x.ensayo}</td><td>${esc(x.causa)}</td></tr>`)) : `<p class="muted" style="margin:0">Sin rechazos.</p>`}</div>
      <div><h3>Series (${o.cant})</h3><div class="series">${Array.from({ length: o.cant }, (_, i) => o.desde + i).map(n => `<span class="${rechSet.has(n) && o.etapa >= E["Para etiquetar"] ? "no" : o.etapa >= E["Depósito PT"] ? "ok" : ""}" data-det="equipo" data-id="${n}" style="cursor:pointer">${ser(n)}</span>`).join("")}</div></div>` };
};
ACC.avanzarOrden = el => { const o = S.ordenes.find(x => x.op === el.dataset.id); o.etapa++; if (o.etapa === 1) o.emision = HOY; registrar(o.etapa === 1 ? "Orden liberada" : "Orden en " + ETAPAS[o.etapa], o.op); toast(`${o.op}: ${ETAPAS[o.etapa]}`); pintar(); };
ACC.cerrarOrden = el => {
  const o = S.ordenes.find(x => x.op === el.dataset.id), r = semilla(hashN(o.op));
  const n = Math.round(o.cant * 0.015 + (r() < 0.4 ? 1 : 0));
  for (let k = 0; k < Math.min(n, o.cant - 1); k++) { const c = r() < 0.5 ? CAUSAS[0] : elegir(r, CAUSAS); o.rech.push({ n: o.desde + Math.floor(r() * o.cant), causa: c[0], ensayo: c[1] }); }
  o.rech = o.rech.filter((x, i, a) => a.findIndex(y => y.n === x.n) === i);
  o.etapa = E["Para etiquetar"]; o.etiquetados = 0;
  registrar("Lote cerrado y visado", o.op, `${o.rech.length} rechazos`); toast(`${o.op} cerrado · ${o.rech.length} rechazo${o.rech.length === 1 ? "" : "s"}`); pintar();
};
ACC.aEtiquetado = el => { UI.f.etqOp = el.dataset.id; ir("etiquetado"); };

// ---------------------------------------------------------------- calidad
VISTAS.calidad = {
  titulo: "Calidad",
  sub: () => `Cierre de lotes, equipos de medición y resultados de ensayo de ${MES_TXT[D.mes - 1]}`,
  html() {
    const mes = S.ordenes.filter(o => o.mes === D.mes && o.etapa >= E["Para etiquetar"]);
    const tot = mes.reduce((a, o) => a + o.cant, 0), rech = mes.reduce((a, o) => a + o.rech.length, 0);
    const causas = CAUSAS.map(([c]) => [c, mes.reduce((a, o) => a + o.rech.filter(x => x.causa === c).length, 0)]).sort((a, b) => b[1] - a[1]);
    const max = Math.max(1, ...causas.map(c => c[1]));
    const cerrar = S.ordenes.filter(o => o.etapa === E["Para cerrar"]);
    return `<div class="kpis"><div class="kpi ${rech / Math.max(1, tot) < 0.02 ? "ok" : "av"}"><span>Rendimiento a la primera</span><b>${pct(tot - rech, tot)}</b><small>${rech} rechazos en ${n0(tot)} equipos cerrados</small></div>
      <div class="kpi ${cerrar.length ? "av" : "ok"}"><span>Lotes para cerrar</span><b>${cerrar.length}</b><small>sin cierre no se etiqueta</small></div>
      <div class="kpi ${S.medicion.some(vencida) ? "no" : "ok"}"><span>Equipos de medición vencidos</span><b>${S.medicion.filter(vencida).length}</b><small>de ${S.medicion.length}</small></div>
      <div class="kpi in"><span>Desvíos abiertos</span><b>${S.desvios.filter(d => d.estado !== "Cerrado").length}</b><small>ver Desvíos</small></div></div>
      <div class="grilla"><div class="panel c7"><header><h2>Lotes para cerrar</h2></header>${tabla(["Orden", "Modelo", "Cant", "Manómetro", ""], cerrar.map(o => { const m = medicionPH(o);
        return `<tr><td class="mono"><a href="#" data-det="orden" data-id="${o.op}">${o.op}</a></td><td>${esc(o.modelo)}</td><td class="num">${o.cant}</td><td>${m.id} ${vencida(m) ? pill("contraste vencido", "no") : pill("ok", "ok")}</td><td class="num"><button class="btn sm ok" data-a="cerrarOrden" data-id="${o.op}" ${vencida(m) ? "disabled" : ""}>Cerrar lote</button></td></tr>`; }), { vacio: "No hay lotes esperando cierre" })}</div>
      <div class="panel c5"><header><h2>Rechazos por causa</h2><span class="muted">${MES_TXT[D.mes - 1]}</span></header><div class="cuerpo">${causas.map(([c, v]) => `<div style="display:grid;grid-template-columns:170px 1fr 28px;gap:8px;align-items:center;margin:6px 0;font-size:13px"><span>${esc(c)}</span>${barra(v, max, "var(--red)")}<b class="num">${v}</b></div>`).join("")}</div></div>
      <div class="panel c12"><header><h2>Equipos de medición</h2><span class="muted">la prueba hidráulica se bloquea si el contraste del manómetro supera 15 días</span></header>${tabla(["Equipo", "Descripción", "Control", "Último", "Próximo", "Estado", ""], S.medicion.map(m => {
        const falta = m.cada - dias(m.ult);
        return `<tr><td class="mono">${m.id}</td><td>${esc(m.desc)}</td><td>${esc(m.tipo)}</td><td class="nw">${fecha(m.ult)}</td><td class="nw">${fecha(sumar(m.ult, m.cada))}</td><td>${falta < 0 ? pill(`vencido hace ${-falta} d`, "no") : falta <= 3 ? pill(`vence en ${falta} d`, "av") : pill(`${falta} d`, "ok")}</td><td class="num"><button class="btn sm" data-a="registrarControl" data-id="${m.id}">Registrar control</button></td></tr>`; }))}</div>
      <div class="panel c12"><header><h2>Ensayos por orden</h2></header>${tabla(["Orden", "Modelo", "Cant", "Aptos", "Rech", "%", "Causas"], mes.map(o => `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td>${esc(o.modelo)}</td><td class="num">${o.cant}</td><td class="num">${aptos(o)}</td><td class="num">${o.rech.length}</td><td class="num">${pct(aptos(o), o.cant)}</td><td class="muted">${esc([...new Set(o.rech.map(x => x.causa))].join(", ") || "—")}</td></tr>`))}</div></div>`;
  },
};
ACC.registrarControl = el => { const m = S.medicion.find(x => x.id === el.dataset.id); m.ult = HOY; registrar("Control de equipo de medición", m.id, m.tipo); toast(`${m.id}: control registrado`); pintar(); };

// ---------------------------------------------------------------- etiquetado
const estampilla = n => "F-" + String(80000 + (n % 100000)).padStart(6, "0");
const etiqueta = (n, o) => `<div class="etq"><div>${qr(D.url + ser(n))}</div><div><b>FLAMA · ${esc(o.modelo)}</b><div class="n">${ser(n)}</div><small>fabricado ${MES_TXT[o.mes - 1]} ${D.anio}<br>estampilla DPS ${estampilla(n)}</small></div></div>`;
VISTAS.etiquetado = {
  titulo: "Etiquetado",
  sub: () => "Puesto 24 (manuales) · C-15 (carros) · una lectura del grabado por equipo",
  html() {
    const lotes = S.ordenes.filter(o => o.etapa === E["Para etiquetar"]);
    if (!lotes.length) return `<div class="panel"><div class="cuerpo"><p class="muted" style="margin:0">No hay lotes cerrados esperando etiqueta.</p></div></div>`;
    const o = lotes.find(x => x.op === UI.f.etqOp) || lotes[0]; UI.f.etqOp = o.op;
    const rechSet = new Set(o.rech.map(x => x.n)), aptas = Array.from({ length: o.cant }, (_, i) => o.desde + i).filter(n => !rechSet.has(n));
    const hechas = aptas.slice(0, o.etiquetados), falta = aptas.slice(o.etiquetados), u = UI.f.etqUlt;
    return `<div class="grilla"><div class="panel c8"><header><div class="filtros">${lotes.map(l => `<button aria-pressed="${l.op === o.op}" data-a="etqLote" data-id="${l.op}">${l.op} · ${esc(l.modelo)}</button>`).join("")}</div><span class="muted">${o.etiquetados} de ${aptas.length}</span></header>
      <div class="cuerpo" style="display:flex;flex-direction:column;gap:12px">${barra(o.etiquetados, aptas.length, "var(--green)")}
      <form class="lector" data-f="leer"><input id="lectura" autocomplete="off" placeholder="Leé el grabado · ${falta[0] ? ser(falta[0]) : "lote completo"}" aria-label="Lectura del grabado"><button class="btn pri" type="submit">Leer</button></form>
      <div class="filtros"><button data-a="leerSig" ${falta.length ? "" : "disabled"}>Lectura del siguiente</button>${o.rech.length ? `<button data-a="leerRech">Lectura de un rechazo</button>` : ""}<button data-a="leerTodo" ${falta.length ? "" : "disabled"}>Leer los ${falta.length} restantes</button></div>
      ${u ? `<div class="aviso ${u.ok ? "ok" : "no"}">${u.ok ? `✓ ${ser(u.n)} · etiqueta impresa · estampilla ${estampilla(u.n)}` : `✗ ${esc(u.s)} · ${esc(u.motivo)}`}</div>` : ""}
      ${!falta.length ? `<div class="aviso ok">Lote completo. <button class="btn sm ok" data-a="aDeposito" data-id="${o.op}">Pasar a depósito PT</button></div>` : ""}</div></div>
      <div class="panel c4"><header><h2>Últimas etiquetas</h2></header><div class="cuerpo" style="display:flex;flex-direction:column;gap:8px">${hechas.slice(-3).reverse().map(n => etiqueta(n, o)).join("") || `<p class="muted" style="margin:0">Todavía no se imprimió ninguna.</p>`}</div></div></div>`;
  },
};
function leer(txt) {
  const o = S.ordenes.find(x => x.op === UI.f.etqOp), n = numSerie(String(txt).trim().replace(/^N°\s*/, ""));
  const rechSet = new Set(o.rech.map(x => x.n)), aptas = Array.from({ length: o.cant }, (_, i) => o.desde + i).filter(k => !rechSet.has(k));
  if (n == null || n < o.desde || n > o.hasta) UI.f.etqUlt = { ok: false, s: txt, motivo: "no pertenece al lote abierto" };
  else if (rechSet.has(n)) { UI.f.etqUlt = { ok: false, s: ser(n), motivo: "bloqueado: " + o.rech.find(x => x.n === n).causa }; registrar("Bloqueo en etiquetado", ser(n)); }
  else if (aptas.indexOf(n) < o.etiquetados) UI.f.etqUlt = { ok: false, s: ser(n), motivo: "ya tiene etiqueta; reimpresión solo con supervisor" };
  else { o.etiquetados = Math.max(o.etiquetados, aptas.indexOf(n) + 1); UI.f.etqUlt = { ok: true, n }; registrar("Equipo identificado", ser(n), "estampilla " + estampilla(n)); }
  pintar(); const i = $("#lectura"); if (i) i.focus();
}
FORM.leer = () => { const v = $("#lectura").value; if (v) leer(v); };
ACC.etqLote = el => { UI.f.etqOp = el.dataset.id; UI.f.etqUlt = null; pintar(); };
ACC.leerSig = () => { const o = S.ordenes.find(x => x.op === UI.f.etqOp), rs = new Set(o.rech.map(x => x.n)); const a = Array.from({ length: o.cant }, (_, i) => o.desde + i).filter(k => !rs.has(k)); if (a[o.etiquetados]) leer(ser(a[o.etiquetados])); };
ACC.leerRech = () => { const o = S.ordenes.find(x => x.op === UI.f.etqOp); if (o.rech[0]) leer(ser(o.rech[0].n)); };
ACC.leerTodo = () => { const o = S.ordenes.find(x => x.op === UI.f.etqOp); o.etiquetados = aptos(o); UI.f.etqUlt = null; registrar("Lote identificado", o.op, `${aptos(o)} equipos`); pintar(); };
ACC.aDeposito = el => { const o = S.ordenes.find(x => x.op === el.dataset.id); o.etapa = E["Depósito PT"]; o.cierre = HOY; registrar("Ingreso a depósito PT", o.op, `${aptos(o)} equipos`); toast(`${o.op} en depósito PT`); pintar(); };
