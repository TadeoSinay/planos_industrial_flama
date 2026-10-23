// ================================================================ producción: órdenes, calidad y etiquetado
const aptos = o => o.cant - o.rech.length;
const fil = (k, def) => UI.f[k] ?? def;
const chips = (k, ops, def) => `<div class="filtros" role="group">${ops.map(([v, t]) => `<button aria-pressed="${fil(k, def) === v}" data-a="filtro" data-k="${k}" data-v="${v}">${esc(t)}</button>`).join("")}</div>`;
ACC.filtro = el => { UI.f[el.dataset.k] = el.dataset.v; UI.pag[UI.vista] = 0; pintar(); };
const medicionPH = o => S.medicion.find(m => m.id === (o.carro ? "PH-M2" : "PH-M1"));
const vencida = m => sinControl(m);

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

// liberar la orden; después, cada etapa se registra con las firmas y lotes de insumo de la hoja de ruta
const puestosDe = (o, e) => hojaRuta(o).filter(p => p.etapa === e);
ACC.avanzarOrden = el => {
  const o = S.ordenes.find(x => x.op === el.dataset.id);
  if (o.etapa === 0) { cambiarEtapa(o, 1); registrar("Orden liberada", o.op, `${o.cant} series ${ser(o.desde)} a ${ser(o.hasta)} · ${o.partida}`); toast(`${o.op} liberada`); pintar(); return; }
  abrirDetalle("etapa", o.op);
};
DETALLES.etapa = op => {
  const o = S.ordenes.find(x => x.op === op), ps = puestosDe(o, o.etapa);
  return { titulo: `${o.op} · ${ETAPAS[o.etapa]}`, sub: "Lo que dice la hoja de ruta firmada: quién hizo cada puesto y qué lote de insumo usó",
    cuerpo: `<form class="form" data-f="regEtapa"><input type="hidden" id="reOp" value="${esc(o.op)}">${ps.map((p, i) => `<div class="ancho"><b class="mono">${esc(p.puesto)}</b> ${esc(p.op)} <span class="muted">· ${esc(p.equipo)}</span></div>
      <label class="campo">Firma<input id="reF${i}" required value="${esc(USUARIO)}"></label>${p.lleva ? `<label class="campo">Lote de ${esc(p.lleva)} (etiqueta del proveedor)<input id="reL${i}" required placeholder="como figura en la etiqueta"></label>` : "<span></span>"}`).join("")}
      <div class="ancho"><button class="btn pri" type="submit">Registrar y pasar a ${esc(ETAPAS[o.etapa + 1])}</button></div></form>` };
};
FORM.regEtapa = () => {
  const o = S.ordenes.find(x => x.op === $("#reOp").value), ps = puestosDe(o, o.etapa), t = ahoraISO();
  ps.forEach((p, i) => { const lote = p.lleva ? $("#reL" + i).value.trim() : null; o.reg[p.puesto] = { t, quien: $("#reF" + i).value.trim(), lote }; if (lote) o.insumos[p.lleva] = lote; });
  let e = o.etapa + 1; while (e < E["Para cerrar"] && !puestosDe(o, e).length) e++;   // los cilindros no tienen carga ni presurización
  cambiarEtapa(o, e); registrar("Etapa registrada", o.op, ps.map(p => p.puesto).join(", ") + " → " + ETAPAS[e]); ACC.cerrarDetalle(); toast(`${o.op}: ${ETAPAS[e]}`); pintar();
};
// cierre: rechazos y pesadas de la hoja, ensayos de lote L1-L5 y pintura; lo visa el responsable técnico
ACC.cerrarOrden = el => abrirDetalle("cierre", el.dataset.id);
DETALLES.cierre = op => {
  const o = S.ordenes.find(x => x.op === op), kg = kgDe(o.modelo), c = CATALOGO[kg], med = medicionPH(o);
  return { titulo: `Cierre de ${o.op}`, sub: `${esc(o.modelo)} · ${o.cant} series ${ser(o.desde)} a ${ser(o.hasta)} · partida ${o.partida}`,
    cuerpo: `${sinControl(med) ? `<div class="aviso no">${med.id} sin contraste vigente: registralo en Calidad antes de cerrar (Res. 349/07 art. 20).</div>` : ""}
    <form class="form" data-f="cierreLote"><input type="hidden" id="ciOp" value="${esc(o.op)}">
      <label class="campo ancho">Rechazos de la hoja (uno por renglón: serie y ensayo PH, Pérd., Esp., Visual o Carga)<textarea id="ciRech" rows="3" placeholder="serie y ensayo"></textarea></label>
      ${o.cilindro ? "" : `<label class="campo ancho">Pesadas (kg) de las series aptas, en orden, o «serie kg» por renglón · banda del BOM<textarea id="ciPes" rows="3" placeholder="archivo de la balanza o valores anotados"></textarea></label>`}
      <label class="campo">L1 · presión de rotura (MPa) · ≥ ${nf(2 * (o.carro ? PH.car : PH.man), 1)}<input id="ciL1" type="number" step="0.01" required></label>
      <label class="campo">L2 · expansión permanente (%) · ≤ 10<input id="ciL2" type="number" step="0.1" required></label>
      ${o.cilindro ? "" : `<label class="campo">L3 · tiempo de descarga (s) · ≥ ${descargaMin(o)}<input id="ciL3s" type="number" step="0.1" required></label>
      <label class="campo">L3 · descargado (%) · ≥ 85<input id="ciL3p" type="number" step="0.1" required></label>
      <label class="campo">L3 · alcance (m) · catálogo ${c ? c[2] + "/" + c[3] : "—"}<input id="ciL3a" type="number" step="0.1" required></label>
      <label class="campo">L4 · certificado IRAM 3569 del polvo (n°)<input id="ciL4" required value="${esc(o.insumos.polvo || "")}"></label>
      <label class="campo">L5 · certificado IRAM 3533 de válvulas (n°)<input id="ciL5" required value="${esc(o.insumos.valvula || "")}"></label>`}
      <label class="campo">Pintura · 5 lecturas (µm) · 60 a 100<input id="ciPin" required placeholder="5 valores separados por coma"></label>
      <label class="campo">Adherencia ISO 2409 (clase 0 a 5)<input id="ciAdh" type="number" min="0" max="5" required></label>
      <label class="campo">Curado: frote MEK<select id="ciMek"><option value="1">sin ablandamiento</option><option value="0">con ablandamiento</option></select></label>
      <label class="campo">Visa (responsable técnico)<input id="ciRT" required value="${esc(USUARIO)}"></label>
      <div class="ancho"><button class="btn ok" type="submit" ${sinControl(med) ? "disabled" : ""}>Registrar y visar</button></div></form>` };
};
FORM.cierreLote = () => {
  const o = S.ordenes.find(x => x.op === $("#ciOp").value), num = id => { const el = $(id); return el ? parseFloat(String(el.value).replace(",", ".")) : null; }, err = [];
  const rech = $("#ciRech").value.split(/\n/).map(l => l.trim()).filter(Boolean).map(l => { const [s_, en] = l.split(/\s+/), n = numSerie(s_), c = CAUSAS.find(x => x[1].toLowerCase() === String(en || "").toLowerCase());
    if (n == null || n < o.desde || n > o.hasta) err.push(`${s_}: no es del lote`); if (!c) err.push(`${s_}: ensayo «${en || ""}» no válido`); return c ? { n, causa: c[0], ensayo: c[1] } : null; }).filter(Boolean);
  const aptas = Array.from({ length: o.cant }, (_, i) => o.desde + i).filter(n => !rech.some(x => x.n === n)), pes = {};
  if ($("#ciPes")) $("#ciPes").value.split(/\n/).map(l => l.trim()).filter(Boolean).forEach((l, i) => { const p = l.split(/\s+/); const n = p.length > 1 ? numSerie(p[0]) : aptas[i], v = parseFloat(p[p.length - 1].replace(",", "."));
    if (n == null || !aptas.includes(n) || !(v > 0)) err.push(`pesada «${l}» no válida`); else pes[n] = v; });
  const lect = $("#ciPin").value.split(/[,;\s]+/).map(x => parseFloat(x.replace(",", "."))).filter(x => x > 0);
  if (lect.length < 5) err.push("pintura: faltan lecturas (son 5)");
  if (err.length) { toast(err.slice(0, 2).join(" · ")); return; }
  const pe = o.carro ? PH.car : PH.man, lab = { t: ahoraISO(), quien: $("#ciRT").value.trim(),
    rotura: { p: num("#ciL1"), min: 2 * pe }, expansion: { pct: num("#ciL2"), max: 10 },
    descarga: o.cilindro ? null : { s: num("#ciL3s"), min: descargaMin(o), pct: num("#ciL3p"), alc: num("#ciL3a"), cat: CATALOGO[kgDe(o.modelo)] },
    polvo: o.cilindro ? null : $("#ciL4").value.trim(), valvula: o.cilindro ? null : $("#ciL5").value.trim(), pintura: { lect, adh: num("#ciAdh"), mek: $("#ciMek").value === "1" } };
  const mal = labFallas(lab);
  o.rech = rech; o.pesadas = pes; o.lab = lab;
  if (mal.length) { registrar("Lote retenido en el cierre", o.op, mal.join(", ")); ACC.cerrarDetalle(); toast(`${o.op} retenido: ${mal.join(", ")}`); pintar(); return; }
  o.visado = { t: lab.t, quien: lab.quien }; cambiarEtapa(o, E["Para etiquetar"]); o.etiquetados = 0;
  registrar("Lote cerrado y visado", o.op, `${rech.length} rechazos · ${Object.keys(pes).length} pesadas · L1-L5 aprobados`); ACC.cerrarDetalle(); toast(`${o.op} cerrado · ${rech.length} rechazo${rech.length === 1 ? "" : "s"}`); pintar();
};
// qué ensayos de lote no cumplen (DOC-02 3.2 y DOC-01 4)
function labFallas(x) {
  const f = [], mn = Math.min(...x.pintura.lect), med = x.pintura.lect.reduce((a, v) => a + v, 0) / x.pintura.lect.length;
  if (!(x.rotura.p >= x.rotura.min)) f.push("L1"); if (!(x.expansion.pct <= x.expansion.max)) f.push("L2");
  if (x.descarga && !(x.descarga.s >= x.descarga.min && x.descarga.pct >= 85)) f.push("L3");
  if (!(med >= 60 && med <= 100 && mn >= 48)) f.push("espesor de pintura"); if (!(x.pintura.adh <= 1)) f.push("adherencia"); if (!x.pintura.mek) f.push("curado");
  return f;
}
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
    return `<div class="kpis"><div class="kpi ${tot ? "ok" : ""}"><span>Rendimiento a la primera</span><b>${tot ? pct(tot - rech, tot) : "—"}</b><small>${tot ? `${rech} rechazos en ${n0(tot)} equipos cerrados` : "sin lotes cerrados registrados"}</small></div>
      <div class="kpi ${cerrar.length ? "av" : "ok"}"><span>Lotes para cerrar</span><b>${cerrar.length}</b><small>sin cierre no se etiqueta</small></div>
      <div class="kpi ${S.medicion.some(m => estadoMed(m)[1] !== "ok") ? "no" : "ok"}"><span>Medición sin control vigente</span><b>${S.medicion.filter(m => estadoMed(m)[1] !== "ok").length}</b><small>de ${S.medicion.length} equipos</small></div>
      <div class="kpi in"><span>Desvíos abiertos</span><b>${S.desvios.filter(d => d.estado !== "Cerrado").length}</b><small>ver Desvíos</small></div></div>
      <div class="grilla"><div class="panel c7"><header><h2>Lotes para cerrar</h2></header>${tabla(["Orden", "Modelo", "Cant", "Manómetro", ""], cerrar.map(o => { const m = medicionPH(o);
        return `<tr><td class="mono"><a href="#" data-det="orden" data-id="${o.op}">${o.op}</a></td><td>${esc(o.modelo)}</td><td class="num">${o.cant}</td><td>${m.id} ${pill(...estadoMed(m))}</td><td class="num"><button class="btn sm ok" data-a="cerrarOrden" data-id="${o.op}">Cerrar lote</button></td></tr>`; }), { vacio: "No hay lotes esperando cierre" })}</div>
      <div class="panel c5"><header><h2>Rechazos por causa</h2><span class="muted">${MES_TXT[D.mes - 1]}</span></header><div class="cuerpo">${causas.map(([c, v]) => `<div style="display:grid;grid-template-columns:170px 1fr 28px;gap:8px;align-items:center;margin:6px 0;font-size:13px"><span>${esc(c)}</span>${barra(v, max, "var(--red)")}<b class="num">${v}</b></div>`).join("")}</div></div>
      <div class="panel c12"><header><h2>Equipos de medición</h2><span class="muted">equipos del proyecto · la prueba hidráulica se bloquea si el manómetro no tiene contraste de los últimos 15 días</span></header>${tabla(["Equipo", "Descripción", "Control", "Último", "Próximo", "Estado", ""], S.medicion.map(m => {
        const [txt, cl] = estadoMed(m);
        return `<tr><td class="mono">${m.id}</td><td>${esc(m.desc)}</td><td>${esc(m.tipo)}</td><td class="nw">${fecha(m.ult)}</td><td class="nw">${m.ult && m.cada ? fecha(sumar(m.ult, m.cada)) : "—"}</td><td>${pill(txt, cl)}</td><td class="num"><button class="btn sm" data-a="registrarControl" data-id="${m.id}">Registrar control</button></td></tr>`; }))}</div>
      <div class="panel c12"><header><h2>Ensayos por orden</h2></header>${tabla(["Orden", "Modelo", "Cant", "Aptos", "Rech", "%", "Causas"], mes.map(o => `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td>${esc(o.modelo)}</td><td class="num">${o.cant}</td><td class="num">${aptos(o)}</td><td class="num">${o.rech.length}</td><td class="num">${pct(aptos(o), o.cant)}</td><td class="muted">${esc([...new Set(o.rech.map(x => x.causa))].join(", ") || "—")}</td></tr>`))}</div></div>`;
  },
};
ACC.registrarControl = el => abrirDetalle("control", el.dataset.id);
DETALLES.control = id => { const m = S.medicion.find(x => x.id === id);
  return { titulo: `Control de ${m.id}`, sub: esc(m.desc), cuerpo: `<form class="form" data-f="regControl"><input type="hidden" id="coId" value="${m.id}">
    <label class="campo">Fecha<input id="coF" type="date" required value="${new Date(HOY).toISOString().slice(0, 10)}"></label><label class="campo">Resultado<select id="coR"><option>conforme</option><option>no conforme</option></select></label>
    <label class="campo ancho">Patrón o certificado (n°)<input id="coC" required></label><div class="ancho"><button class="btn pri" type="submit">Registrar</button></div></form>` }; };
FORM.regControl = () => { const m = S.medicion.find(x => x.id === $("#coId").value), ok = $("#coR").value === "conforme", f = $("#coF").value;
  if (ok) m.ult = new Date(f + "T12:00:00").toISOString(); (m.hist = m.hist || []).push({ f, ok, cert: $("#coC").value.trim() });
  registrar("Control de equipo de medición", m.id, `${$("#coR").value} · ${$("#coC").value.trim()}`); ACC.cerrarDetalle(); toast(`${m.id}: ${ok ? "control vigente" : "no conforme: sigue bloqueado"}`); pintar(); };

// ---------------------------------------------------------------- etiquetado
const etiqueta = (n, o) => `<div class="etq"><div>${qr(D.url + ser(n))}</div><div><b>FLAMA · ${esc(o.modelo)}</b><div class="n">${ser(n)}</div><small>${esc(o.partida)} · ${S.ident[n] ? fecha(S.ident[n]) : ""}<br>IRAM ${o.carro ? "3550" : "3523"}</small></div></div>`;
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
      ${u ? `<div class="aviso ${u.ok ? "ok" : "no"}">${u.ok ? `✓ ${ser(u.n)} · etiqueta impresa` : `✗ ${esc(u.s)} · ${esc(u.motivo)}`}</div>` : ""}
      ${!falta.length ? `<div class="aviso ok">Lote completo. <button class="btn sm ok" data-a="aDeposito" data-id="${o.op}">Pasar a depósito PT</button></div>` : ""}</div></div>
      <div class="panel c4"><header><h2>Últimas etiquetas</h2></header><div class="cuerpo" style="display:flex;flex-direction:column;gap:8px">${hechas.slice(-3).reverse().map(n => etiqueta(n, o)).join("") || `<p class="muted" style="margin:0">Todavía no se imprimió ninguna.</p>`}</div></div></div>`;
  },
};
function leer(txt) {
  const o = S.ordenes.find(x => x.op === UI.f.etqOp), n = numSerie(String(txt).trim().replace(/^N°\s*/, ""));
  const rechSet = new Set(o.rech.map(x => x.n)), aptas = Array.from({ length: o.cant }, (_, i) => o.desde + i).filter(k => !rechSet.has(k));
  if (n == null || n < o.desde || n > o.hasta) UI.f.etqUlt = { ok: false, s: txt, motivo: "no pertenece al lote abierto" };
  else if (rechSet.has(n)) { UI.f.etqUlt = { ok: false, s: ser(n), motivo: "bloqueado: " + o.rech.find(x => x.n === n).causa }; registrar("Bloqueo en etiquetado", ser(n)); }
  else if (S.ident[n]) UI.f.etqUlt = { ok: false, s: ser(n), motivo: "ya tiene etiqueta; reimpresión solo con supervisor" };
  else { S.ident[n] = ahoraISO(); o.etiquetados = Math.max(o.etiquetados, aptas.indexOf(n) + 1); UI.f.etqUlt = { ok: true, n }; registrar("Equipo identificado", ser(n), "lectura del grabado"); }
  pintar(); const i = $("#lectura"); if (i) i.focus();
}
FORM.leer = () => { const v = $("#lectura").value; if (v) leer(v); };
ACC.etqLote = el => { UI.f.etqOp = el.dataset.id; UI.f.etqUlt = null; pintar(); };
ACC.leerSig = () => { const o = S.ordenes.find(x => x.op === UI.f.etqOp), rs = new Set(o.rech.map(x => x.n)); const a = Array.from({ length: o.cant }, (_, i) => o.desde + i).filter(k => !rs.has(k)); if (a[o.etiquetados]) leer(ser(a[o.etiquetados])); };
ACC.leerRech = () => { const o = S.ordenes.find(x => x.op === UI.f.etqOp); if (o.rech[0]) leer(ser(o.rech[0].n)); };
ACC.leerTodo = () => { const o = S.ordenes.find(x => x.op === UI.f.etqOp), rs = new Set(o.rech.map(x => x.n)), t = ahoraISO();
  for (let n = o.desde; n <= o.hasta; n++) if (!rs.has(n) && !S.ident[n]) S.ident[n] = t;
  o.etiquetados = aptos(o); UI.f.etqUlt = null; registrar("Lote identificado", o.op, `${aptos(o)} equipos · lectura manual`); pintar(); };
ACC.aDeposito = el => { const o = S.ordenes.find(x => x.op === el.dataset.id), t = ahoraISO(), p24 = o.carro ? "C-15" : "24", p25 = o.carro ? "C-16" : "25";
  o.reg[p24] = o.reg[p24] || { t, quien: USUARIO, lote: null }; o.reg[p25] = { t, quien: USUARIO, lote: null }; o.pallet = `PAL ${o.op.slice(3)}`;
  cambiarEtapa(o, E["Depósito PT"]); registrar("Ingreso a depósito PT", o.op, `${aptos(o)} equipos · ${o.pallet}`); toast(`${o.op} en depósito PT`); pintar(); };

// ---------------------------------------------------------------- historial de lotes
const ciclo = o => o.emision && o.cierre ? Math.max(1, dias(o.emision, o.cierre)) : null;
function stats(v) { const n = v.length; if (!n) return null; const m = v.reduce((a, x) => a + x, 0) / n; const sd = Math.sqrt(v.reduce((a, x) => a + (x - m) ** 2, 0) / Math.max(1, n - 1)); return { n, m, sd }; }
const cpk = (st, lie, lse) => st && st.sd ? Math.min(lse - st.m, st.m - lie) / (3 * st.sd) : null;
function distribucion(o) {
  const c = {}; for (let n = o.desde; n <= o.hasta; n++) { const e = equipo(n); c[e.estado] = (c[e.estado] || 0) + 1; } return c;
}
VISTAS.lotes = {
  titulo: "Historial de lotes",
  sub: () => `${S.ordenes.length} órdenes de ${D.anio} · matafuegos y cilindros · cada una con su hoja de ruta, ensayos por serie, insumos y destino`,
  acciones: () => `<button class="btn" data-a="csvLotes">Copiar para Sheets</button>`,
  html() {
    const mes = fil("lmes", "todos"), lin = fil("llin", "Todas"), tip = fil("ltip", "Todos"), q = (UI.f.lq || "").toUpperCase();
    const xs = S.ordenes.filter(o => (mes === "todos" || o.mes === +mes) && (lin === "Todas" || o.linea === lin) && (tip === "Todos" || tipoEq(o) === tip) && (!q || (o.op + o.modelo + o.partida + Object.values(o.insumos).join(" ")).toUpperCase().includes(q))).slice().reverse();
    const p = UI.pag.lotes || 0, pag = xs.slice(p * 40, p * 40 + 40);
    return `<div class="panel"><header><div class="filtros"><input id="lq" type="search" placeholder="Orden, partida o lote de insumo" value="${esc(UI.f.lq || "")}" data-in="lq" aria-label="Buscar lote">
      <select aria-label="Mes" data-k="lmes" data-cambio="filtroSel"><option value="todos">Todo el año</option>${Array.from({ length: D.mes }, (_, i) => `<option value="${i + 1}" ${+mes === i + 1 ? "selected" : ""}>${MES_TXT[i]}</option>`).reverse().join("")}</select>
      ${chips("llin", [["Todas", "Todas"], ["Manuales", "Manuales"], ["Carros", "Carros"]], "Todas")}${chips("ltip", [["Todos", "Todos"], ["Matafuego", "Matafuegos"], ["Cilindro", "Cilindros"]], "Todos")}</div><span class="muted">${xs.length} lotes</span></header>
      ${tabla(["Orden", "Modelo", "Tipo", "Cant", "Aptos", "Rech", "%", "Partida DPS", "Emisión", "Cierre", "Ciclo", "Etapa", "Remito"], pag.map(o => `<tr class="click" data-det="orden" data-id="${o.op}"><td class="mono">${o.op}</td><td class="nw">${esc(o.modelo)}</td><td>${tipoEq(o)}</td><td class="num">${o.cant}</td>
        <td class="num">${o.etapa >= E["Para etiquetar"] ? aptos(o) : "—"}</td><td class="num">${o.etapa >= E["Para etiquetar"] ? o.rech.length : "—"}</td><td class="num">${o.etapa >= E["Para etiquetar"] ? pct(aptos(o), o.cant) : "—"}</td><td class="mono">${o.partida}</td>
        <td class="nw">${fecha(o.emision)}</td><td class="nw">${fecha(o.cierre)}</td><td class="num">${ciclo(o) ? ciclo(o) + " d" : "—"}</td><td>${pill(ETAPAS[o.etapa], etapaPill(o.etapa))}</td><td class="mono">${o.remito || "—"}</td></tr>`))}
      <div class="paginas">página ${p + 1} de ${Math.max(1, Math.ceil(xs.length / 40))} <button class="btn sm" data-a="pag" data-d="-1" ${p ? "" : "disabled"}>‹</button><button class="btn sm" data-a="pag" data-d="1" ${(p + 1) * 40 < xs.length ? "" : "disabled"}>›</button></div></div>`;
  },
};
ACC.csvLotes = () => copiar(["orden\tmodelo\ttipo\tcant\taptos\trechazos\tpartida\temision\tcierre\tetapa\tremito", ...S.ordenes.map(o => [o.op, o.modelo, tipoEq(o), o.cant, aptos(o), o.rech.length, o.partida, fecha(o.emision), fecha(o.cierre), ETAPAS[o.etapa], o.remito || ""].join("\t"))].join("\n"));

const mpDe = (k, o) => { const esp = ESPESOR[kgDe(o.modelo)];
  const f = { chapa: m => m.mat.includes(`LAF ${String(esp).replace(".", ",")} `), cupulas: m => /Fleje|Casquete/.test(m.mat) && m.mat.includes(kgDe(o.modelo).replace(" kg", "")), alambre: m => m.mat.startsWith("Alambre MAG"), pintura: m => /[Pp]intura en polvo/.test(m.mat), polvo: m => /^Polvo ABC/.test(m.mat), valvula: m => /^Válvula/.test(m.mat) && m.mat.includes(kgDe(o.modelo)) }[k];
  return f ? D.insumos.find(f) : null; };
VISTAS.lote = {
  titulo: () => esc(UI.param),
  sub: () => { const o = S.ordenes.find(x => x.op === UI.param); return o ? `${esc(o.modelo)} · ${tipoEq(o).toLowerCase()} · ${o.cant} u · línea ${o.linea.toLowerCase()} · partida ${o.partida} · ${pill(ETAPAS[o.etapa], etapaPill(o.etapa))}` : ""; },
  acciones: () => { const o = S.ordenes.find(x => x.op === UI.param); if (!o) return "";
    const sig = o.etapa < E["Para cerrar"] ? ETAPAS[o.etapa + 1] : null;
    return `<a href="#lotes" data-v="lotes" class="btn">← Lotes</a>` + (o.etapa === 0 ? `<button class="btn pri" data-a="avanzarOrden" data-id="${o.op}">Liberar a producción</button>`
      : o.etapa < E["Para cerrar"] ? `<button class="btn pri" data-a="avanzarOrden" data-id="${o.op}">Registrar ${esc(ETAPAS[o.etapa])}</button>`
      : o.etapa === E["Para cerrar"] ? `<button class="btn ok" data-a="cerrarOrden" data-id="${o.op}">Cerrar lote y visar</button>`
      : o.etapa === E["Para etiquetar"] ? `<button class="btn pri" data-a="aEtiquetado" data-id="${o.op}">Ir a etiquetado</button>`
      : o.etapa === E["Depósito PT"] ? `<button class="btn pri" data-a="nuevoRemito" data-id="${o.op}">Armar remito</button>` : ""); },
  html() {
    const o = S.ordenes.find(x => x.op === UI.param); if (!o) return `<div class="aviso av">No existe la orden ${esc(UI.param)}.</div>`;
    const tab = fil("ltab", "res"), cerr = o.etapa >= E["Para etiquetar"], m = modeloBOM(o.modelo), med = medicionPH(o), rem = o.remito && remito(o.remito);
    const ser_ = Array.from({ length: o.cant }, (_, i) => o.desde + i), masas = cerr ? ser_.filter(n => !o.rech.some(x => x.n === n)).map(n => masaCarga(n, o)).filter(x => x != null) : [];
    const st = stats(masas), dist = cerr ? distribucion(o) : {};
    const kpis = `<div class="kpis"><div class="kpi in"><span>Series</span><b class="mono" style="font-size:20px">${ser(o.desde)}</b><small>a ${ser(o.hasta)} · ${o.cant} u</small></div>
      <div class="kpi ${cerr ? (o.rech.length / o.cant < 0.02 ? "ok" : "av") : ""}"><span>Aptos / rechazos</span><b>${cerr ? `${aptos(o)} / ${o.rech.length}` : "—"}</b><small>${cerr ? pct(aptos(o), o.cant) + " a la primera" : "se cargan al cerrar"}</small></div>
      <div class="kpi in"><span>Ciclo de la orden</span><b>${ciclo(o) ? ciclo(o) + " d" : "—"}</b><small>${fecha(o.emision)} → ${fecha(o.cierre)}</small></div>
      ${o.cilindro ? `<div class="kpi in"><span>Producto</span><b style="font-size:20px">Cilindro</b><small>se vende vacío, sin carga ni válvula</small></div>` : `<div class="kpi ${st ? "ok" : ""}"><span>Carga · Cpk</span><b>${st ? nf(cpk(st, m.min, m.max), 2) : "—"}</b><small>${st ? `x̄ ${nf(st.m, 3)} kg · σ ${nf(st.sd * 1000, 0)} g` : "sin datos"}</small></div>`}
      <div class="kpi in"><span>Identificados</span><b>${cerr ? `${o.etiquetados} / ${aptos(o)}` : "—"}</b><small>lecturas del grabado en ${o.carro ? "C-15" : "puesto 24"}</small></div>
      <div class="kpi ${dist.Instalado ? "ok" : "in"}"><span>Destino</span><b>${cerr ? n0(dist.Instalado || 0) : "—"}</b><small>instalados · ${n0(dist["En distribuidor"] || 0)} en distribuidor</small></div></div>`;
    const tabs = [["res", "Resumen"], ["est", "Estadios"], ["hoja", "Hoja de ruta"], ["ens", "Ensayos por serie"], ["lot", "Ensayos de lote"], ["ins", "Insumos y medición"], ["dist", "Distribución"], ["ev", "Eventos"]];
    let cuerpo = "";
    if (tab === "res") cuerpo = `<div class="grilla"><div class="panel c7"><header><h2>Etapas</h2></header><div class="cuerpo"><div class="etapas">${ETAPAS.map((e, i) => `<span class="${i < o.etapa ? "hecha" : i === o.etapa ? "actual" : ""}">${esc(e)}</span>`).join("")}</div>
        ${retenido(o).length ? `<div class="aviso no" style="margin-top:10px">Lote retenido: ${esc(retenido(o).join(" · "))}. Registrá el contraste en Calidad para poder cerrar.</div>` : ""}
        <dl class="dl" style="margin-top:12px"><dt>Plan</dt><dd>${esc(o.modelo)} · ${MES_TXT[o.mes - 1]} ${D.anio} (Plan mensual)</dd><dt>Partida DPS</dt><dd class="mono">${o.partida} · certificado de fabricación por partida de 100 u o más</dd>
        <dt>Prueba hidráulica</dt><dd>${nf(o.carro ? PH.car : PH.man, 1)} MPa · 60 s · manómetro ${med.id}</dd>${o.cilindro ? "" : `<dt>Carga</dt><dd>${m ? `${nf(m.carga, 1)} kg nominal · banda ${nf(m.min, 2)} a ${nf(m.max, 2)} kg (BOM) · N₂ ${nf(N2, 1)} MPa` : "—"}</dd>`}
        <dt>Cierre</dt><dd>${o.visado ? `${fecha(o.visado.t)} · visado ${esc(o.visado.quien)}` : "pendiente"}</dd>
        <dt>Pallet</dt><dd class="mono">${esc(o.pallet || "—")}</dd><dt>Remito</dt><dd>${rem ? `<a href="#" data-det="remito" data-id="${rem.id}">${rem.id}</a> · ${esc(cliente(rem.cliente).nombre)} · ${esc(rem.transp)} ${rem.patente}` : "—"}</dd></dl></div></div>
        <div class="panel c5"><header><h2>Normas que aplica</h2></header><div class="cuerpo"><ul class="lista-alertas">${[["IRAM 3517-2 · anexo F", "serie grabada: sin número no hay trazabilidad"], ["Res. 349/07 art. 21-23 · anexo IV", "partida, estampilla de fabricación y cuño DPS"], ["Res. 349/07 art. 9 · anexo I C", "planilla de ensayos por partida, visada por el RT"], ["Res. 349/07 art. 20", "contraste del manómetro de PH cada 15 días"], ["DOC-02 FLAMA", "presión de PH, banda de carga y N₂"]].map(([a, b]) => `<li class="in"><span><b class="mono" style="font-size:12px">${a}</b><br>${b}</span><span></span></li>`).join("")}</ul></div></div></div>`;
    if (tab === "est") cuerpo = tabEstadios(o);
    if (tab === "lot") cuerpo = tabEnsayosLote(o);
    if (tab === "hoja") cuerpo = `<div class="panel"><header><h2>Hoja de ruta</h2><span class="muted">papel firmado en el carro · foto al cierre · se carga en la base</span></header>${tabla(["Puesto", "Operación", "Equipo", "Lote anotado", "Fecha y hora", "Firma", "Estado"], hojaRuta(o).map(h => `<tr><td class="mono">${h.puesto}</td><td>${esc(h.op)}</td><td class="muted">${esc(h.equipo)}</td><td class="mono">${esc(h.insumo || "—")}</td><td class="nw">${h.fecha ? new Date(h.fecha).toLocaleString("es-AR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) : "—"}</td><td>${esc(h.firma || "—")}</td><td>${pill(h.estado, h.estado === "hecho" ? "ok" : h.estado === "en curso" ? "av" : "gr")}</td></tr>`))}</div>`;
    if (tab === "ens") cuerpo = !cerr ? `<div class="aviso in">Los ensayos por serie se cargan al cerrar el lote (tildes de la hoja de ruta y planilla de la partida).</div>` :
      `${st ? `<div class="panel"><header><h2>Masa de carga · carta de valores individuales</h2><span class="muted">n ${st.n} · x̄ ${nf(st.m, 3)} · σ ${nf(st.sd * 1000, 0)} g · Cpk ${nf(cpk(st, m.min, m.max), 2)}</span></header><div class="cuerpo">${cartaI(masas, m.min, m.max, ser_.filter(n => !o.rech.some(x => x.n === n)).map(ser))}</div></div>` : ""}
      <div class="panel"><header><h2>Ensayos por serie</h2><span class="muted">DOC-02 · ✓ / ✗ de la hoja de ruta y pesadas registradas al cerrar</span></header>${tabla(["Serie", "Espesor", "PH", "Carga (kg)", "N₂", "Pérdidas", "Visual", "Resultado"], ser_.map(n => { const x = ensayos(n, o), ok = v => v ? "✓" : `<b style="color:var(--red)">✗</b>`;
        return `<tr class="click" data-det="equipo" data-id="${n}"><td class="mono">${ser(n)}</td><td>${ok(x.esp)}</td><td class="nw">${nf(x.ph.p, 1)} MPa · ${x.ph.t} s ${ok(x.ph.ok)}</td><td class="num">${x.carga ? `${x.carga.kg ? nf(x.carga.kg, 3) : "—"} ${ok(x.carga.ok)}` : "—"}</td><td class="num">${x.n2 ? nf(x.n2, 1) + " MPa" : "—"}</td><td>${x.perd == null ? "—" : ok(x.perd)}</td><td>${ok(x.visual)}</td><td>${x.rech ? pill(x.rech.causa, "no") : pill("apto", "ok")}</td></tr>`; }))}</div>`;
    if (tab === "ins") cuerpo = `<div class="grilla"><div class="panel c7"><header><h2>Lotes de insumo</h2><span class="muted">anotados en la hoja de ruta</span></header>${tabla(["Insumo", "Lote", "Material (MRP)", "Proveedor"], Object.entries(o.insumos).map(([k, v]) => { const mp = mpDe(k, o);
        return `<tr><td>${k[0].toUpperCase() + k.slice(1)}</td><td class="mono"><a href="#" data-a="trazaLote" data-q="${esc(v.split(" · ")[0])}">${esc(v)}</a></td><td>${mp ? `<a href="#" data-det="insumo" data-id="${esc(mp.cod)}">${esc(mp.cod)}</a> · ${esc(mp.mat)}` : "—"}</td><td>${mp ? esc(mp.prov) : "—"}</td></tr>`; }))}</div>
        <div class="panel c5"><header><h2>Equipos de medición</h2></header>${tabla(["Equipo", "Uso", "Control vigente"], [[med.id, "prueba hidráulica"], [o.carro ? "B-2" : "B-1", "masa de carga"], ["MP-PAT", "patrón de contraste"]].map(([id, u]) => { const x = S.medicion.find(z => z.id === id); return `<tr><td class="mono">${id}</td><td>${u}</td><td>${fecha(x.ult)} ${pill(...estadoMed(x))}</td></tr>`; }))}</div></div>`;
    if (tab === "dist") { const grupos = {}; if (cerr) for (const n of ser_) { const e = equipo(n); const k = e.estado + "|" + e.custodia; grupos[k] = (grupos[k] || 0) + 1; }
      cuerpo = !cerr ? `<div class="aviso in">El lote todavía está en planta.</div>` : `<div class="kpis">${Object.entries(dist).map(([k, v]) => `<div class="kpi ${estadoPill[k] === "ok" ? "ok" : estadoPill[k] === "no" ? "no" : "in"}"><span>${k}</span><b>${v}</b></div>`).join("")}</div>
        <div class="panel"><header><h2>Dónde está cada equipo</h2></header>${tabla(["Estado", "Custodia", "Equipos"], Object.entries(grupos).sort((a, b) => b[1] - a[1]).map(([k, v]) => { const [e, c] = k.split("|"); return `<tr><td>${pill(e, estadoPill[e])}</td><td>${esc(c)}</td><td class="num">${v}</td></tr>`; }))}</div>`; }
    if (tab === "ev") { const ev = S.eventos.filter(x => x.ref === o.op || (o.remito && x.ref === o.remito)).slice().reverse();
      cuerpo = `<div class="panel"><header><h2>Eventos del lote</h2><span class="muted">registros con su hash SHA-256 encadenado</span></header>${tabla(["Fecha", "Evento", "Detalle", "Quién", "Hash"], ev.map(x => `<tr><td class="nw">${new Date(x.t).toLocaleString("es-AR", { day: "2-digit", month: "2-digit", year: "2-digit", hour: "2-digit", minute: "2-digit" })}</td><td>${esc(x.tipo)}</td><td class="muted">${esc(x.detalle)}</td><td>${esc(x.quien)}</td><td class="mono muted" title="${esc(x.hash || "")}">${esc((x.hash || "…").slice(0, 16))}…</td></tr>`), { vacio: "Todavía no hay registros de este lote" })}</div>`; }
    return kpis + `<div class="filtros" role="tablist">${tabs.map(([k, t]) => `<button role="tab" aria-pressed="${tab === k}" data-a="filtro" data-k="ltab" data-v="${k}">${t}</button>`).join("")}</div>` + cuerpo;
  },
};
ACC.trazaLote = el => { UI.f.trq = el.dataset.q; ir("traza"); };
