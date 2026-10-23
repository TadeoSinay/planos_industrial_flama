// ================================================================ servicio: recargas, reclamos y clientes
const planRecargas = () => [...D.recargas.comercial, ...D.recargas.industrial].reduce((a, t) => a + t.cant, 0);
const tiposRecarga = () => [...new Set([...D.recargas.comercial, ...D.recargas.industrial].filter(t => t.cant > 0).map(t => t.tipo))];

VISTAS.recargas = {
  titulo: "Recargas",
  sub: () => `Plantas comercial e industrial · plan de ${MES_TXT[D.mes - 1]}: ${n0(planRecargas())} recipientes (Aprovechamiento_Recargas)`,
  acciones: () => `<button class="btn pri" data-a="nuevaOS">Nueva recepción</button>`,
  html() {
    const pl = fil("rpla", "Todas"), lista = S.recargas.filter(r => pl === "Todas" || r.planta === pl);
    const hab = habiles(D.anio, D.mes), trans = hab.filter(d => d <= HOY).length;
    const hechas = Math.round(planRecargas() * trans / hab.length) + S.recargas.filter(r => r.etapa === 5).length;
    const col = (i, t) => { const xs = lista.filter(r => r.etapa === i && !r.inutil);
      return `<div class="col-k"><h3>${esc(t)}<span class="muted">${xs.length}</span></h3>${xs.map(r => `<button class="tarjeta" data-det="recarga" data-id="${r.os}"><b>${r.os}</b><span>${esc(r.tipo)} · ${esc(r.marca)}</span><span class="muted">${esc(cliente(r.cliente).nombre)} · ${dias(r.fecha)} d</span>${r.ph ? pill("con PH", "vi") : ""}${r.polvoBajo ? pill("polvo bajo de peso", "av") : ""}</button>`).join("")}</div>`; };
    const inut = lista.filter(r => r.inutil);
    return `<div class="kpis"><div class="kpi in"><span>Hechas en el mes</span><b>${n0(hechas)}</b><small>de ${n0(planRecargas())} del plan</small></div>
      <div class="kpi av"><span>En taller</span><b>${S.recargas.filter(r => r.etapa >= 2 && r.etapa < 4 && !r.inutil).length}</b><small>incluye control final</small></div>
      <div class="kpi ok"><span>Listas para entregar</span><b>${S.recargas.filter(r => r.etapa === 4).length}</b></div>
      <div class="kpi in"><span>Sustitutos prestados</span><b>${S.recargas.filter(r => r.sustituto && r.etapa < 5).length}</b></div>
      <div class="kpi ${inut.length ? "no" : "ok"}"><span>Para inutilizar</span><b>${inut.length}</b><small>acta y 30 días a disposición</small></div></div>
      ${UI.f.nuevaOS ? formOS() : ""}
      <div class="panel"><header><h2>Órdenes de servicio</h2>${chips("rpla", [["Todas", "Todas"], ["Comercial", "Planta comercial"], ["Industrial", "Planta industrial"]], "Todas")}</header><div class="cuerpo"><div class="kanban">${ETAPAS_OS.slice(0, 5).map((t, i) => col(i, t)).join("")}
        <div class="col-k"><h3>Inutilizar<span class="muted">${inut.length}</span></h3>${inut.map(r => `<button class="tarjeta" data-det="recarga" data-id="${r.os}" style="border-color:var(--red)"><b>${r.os}</b><span>${esc(r.tipo)}</span><span class="muted">${esc(r.inutil)}</span></button>`).join("")}</div></div></div></div>`;
  },
};
function formOS() {
  return `<div class="panel"><header><h2>Recepción</h2><button class="btn sm" data-a="cancelarOS">Cancelar</button></header><div class="cuerpo"><form class="form" data-f="crearOS">
    <label class="campo">Cliente<select id="osCli">${S.clientes.map(c => `<option value="${c.id}">${esc(c.nombre)}</option>`).join("")}</select></label>
    <label class="campo">Tipo de equipo<select id="osTipo">${tiposRecarga().map(t => `<option>${esc(t)}</option>`).join("")}</select></label>
    <label class="campo">Marca<select id="osMarca"><option>Otra marca</option><option ${UI.f.osSerie ? "selected" : ""}>FLAMA</option></select></label>
    <label class="campo">Serie o n° grabado<input id="osNro" value="${esc(UI.f.osSerie || "")}" placeholder="si es FLAMA, la serie ${AA}-000000"></label>
    <label class="campo">Año de fabricación<input id="osFab" type="number" value="${UI.f.osSerie ? D.anio : D.anio - 4}"></label>
    <label class="campo">Planta<select id="osPlanta"><option>Comercial</option><option>Industrial</option></select></label>
    <label class="campo">Sustituto<select id="osSus"><option value="">No</option><option>Sí, entregar sustituto habilitado</option></select></label>
    <label class="campo ancho">Observaciones de la recepción<input id="osObs" placeholder="estado visual, precinto, manómetro"></label>
    <div class="ancho"><button class="btn pri" type="submit">Registrar y enviar presupuesto</button></div></form></div></div>`;
}
ACC.nuevaOS = () => { UI.f.nuevaOS = true; pintar(); };
ACC.cancelarOS = () => { UI.f.nuevaOS = false; UI.f.osSerie = null; pintar(); };
FORM.crearOS = () => {
  const tipo = $("#osTipo").value, t = [...D.recargas.comercial, ...D.recargas.industrial].find(x => x.tipo === tipo);
  const r = { os: `OS-${AA}-${String(++S.nOs).padStart(5, "0")}`, fecha: HOY, planta: $("#osPlanta").value, tipo, agente: t ? t.agente : "", cliente: $("#osCli").value, marca: $("#osMarca").value,
    nro: $("#osNro").value, fab: +$("#osFab").value, tecnico: OPER[S.nOs % OPER.length], etiqueta: `S-${AA}-${String(30000 + S.nOs).padStart(6, "0")}`, etapa: 1, sustituto: $("#osSus").value ? `SUS-${(S.nOs % 120) + 1}` : null, ph: false, polvoBajo: false,
    presupuesto: Math.round((t && t.agente === "CO₂" ? 18000 : 14000) / 100) * 100, inutil: null, obs: $("#osObs").value };
  S.recargas.unshift(r); UI.f.nuevaOS = false; UI.f.osSerie = null; if (numSerie(r.nro)) registrar("Recibido para servicio", r.nro, r.os); registrar("Recepción de recarga", r.os, `${r.tipo} · ${cliente(r.cliente).nombre}`); toast(`${r.os} registrada · presupuesto enviado`); pintar(); abrirDetalle("recarga", r.os);
};
DETALLES.recarga = id => {
  const r = S.recargas.find(x => x.os === id); if (!r) return null;
  const c = cliente(r.cliente), pie = r.inutil ? `<button class="btn pri" data-a="osActa" data-id="${r.os}">Labrar acta e inutilizar</button>`
    : r.etapa < 5 ? `${r.etapa >= 2 && r.etapa < 4 ? `<button class="btn" data-a="osInutil" data-id="${r.os}">Mandar a inutilizar</button>` : ""}<button class="btn pri" data-a="osAvanzar" data-id="${r.os}">${r.etapa === 1 ? "Presupuesto aprobado: a taller" : "Pasar a " + ETAPAS_OS[r.etapa + 1]}</button>` : "";
  const pasos = r.agente === "ABC" ? ["Descarga y control del polvo (puffer)", r.polvoBajo ? "Polvo bajo de peso: cambio total por polvo nuevo" : "Reposición de polvo", "Desarme y limpieza", r.ph ? "Prueba hidráulica · oblea nueva" : "Prueba hidráulica no corresponde este año", "Fecha grabada en el tubo de pesca", "Carga, presurización con N₂ y control de pérdidas", "Marbete del año, precinto y etiqueta de servicio con QR"]
    : ["Descarga y control del agente", "Desarme, limpieza e inspección", r.ph ? "Prueba hidráulica" : "Prueba hidráulica no corresponde este año", "Carga y control de pérdidas", "Marbete, precinto y etiqueta de servicio con QR"];
  return { titulo: r.os, sub: `${esc(r.tipo)} · ${esc(r.marca)} · planta ${r.planta.toLowerCase()}`, pie,
    cuerpo: `<div class="etapas">${ETAPAS_OS.map((e, i) => `<span class="${i < r.etapa ? "hecha" : i === r.etapa ? "actual" : ""}">${esc(e)}</span>`).join("")}</div>
      ${r.inutil ? `<div class="aviso no">Inutilizar: ${esc(r.inutil)}. Agente a disposición final, 2 orificios Ø10 mm, manguera cortada${cliente(r.cliente).jur === "PBA" ? " y corte de la rosca (PBA)" : ""}; 30 días a disposición del propietario.</div>` : ""}
      <div class="qrgrid" style="display:grid;grid-template-columns:110px 1fr;gap:14px;align-items:start"><div class="qr">${qr(D.url + r.etiqueta)}</div>
      <dl class="dl"><dt>Cliente</dt><dd><a href="#" data-det="cliente" data-id="${c.id}">${esc(c.nombre)}</a> · ${c.jur}</dd><dt>Recibido</dt><dd>${fecha(r.fecha)} · hace ${dias(r.fecha)} d</dd><dt>Etiqueta de servicio</dt><dd class="mono"><a href="#" data-a="verEtiqueta" data-id="${r.etiqueta}">${r.etiqueta}</a></dd>
      ${r.nro ? `<dt>N° del equipo</dt><dd class="mono">${numSerie(r.nro) ? `<a href="#" data-det="equipo" data-id="${numSerie(r.nro)}">${esc(r.nro)}</a>` : esc(r.nro)} · fabricado ${r.fab || "—"}</dd>` : ""}<dt>Técnico</dt><dd>${esc(r.tecnico || "—")}</dd><dt>Presupuesto</dt><dd>$ ${n0(r.presupuesto)} · ${r.etapa >= 2 ? "aprobado" : "enviado"}</dd><dt>Sustituto</dt><dd>${r.sustituto ? esc(r.sustituto) + " (tarjeta «sustituto habilitado»)" : "no"}</dd>
      <dt>Garantía</dt><dd>${r.etapa === 5 ? "30 días desde la entrega" : "—"}</dd><dt>Tarjeta oficial</dt><dd>${c.jur === "CABA" ? "SGM de la AGC" : "tarjeta DPS + estampilla de control"}</dd></dl></div>
      <div><h3>Trabajo</h3><ul class="tl">${pasos.map((p, i) => `<li class="${r.etapa > 3 || (r.etapa >= 2 && i < 2) ? "" : "p"}"><time></time><i></i><span>${esc(p)}</span></li>`).join("")}</ul></div>` };
};
ACC.osAvanzar = el => { const r = S.recargas.find(x => x.os === el.dataset.id); r.etapa = r.etapa === 1 ? 2 : r.etapa + 1; registrar("Recarga: " + ETAPAS_OS[r.etapa], r.os); toast(`${r.os}: ${ETAPAS_OS[r.etapa]}`); pintar(); };
ACC.osInutil = el => { const r = S.recargas.find(x => x.os === el.dataset.id); r.inutil = "Condición de inutilización en la revisión (IRAM 3517-2 anexo F)"; registrar("Recarga: a inutilizar", r.os); pintar(); };
ACC.osActa = el => { const r = S.recargas.find(x => x.os === el.dataset.id); S.recargas.splice(S.recargas.indexOf(r), 1); registrar("Acta de inutilización", r.os, r.inutil); toast(`${r.os}: acta labrada · aviso al propietario`); ACC.cerrarDetalle(); pintar(); };

// ---------------------------------------------------------------- reclamos
const PLAZO_RC = { "Seguridad": 1, "Garantía": 2, "Servicio de recarga": 2, "Atención o entrega": 2, "Datos personales": 10 };   // días (criterio; datos: Ley 25.326 art. 14)
const vencido = x => x.etapa < 2 && dias(x.fecha) > PLAZO_RC[x.tipo];
VISTAS.reclamos = {
  titulo: "Reclamos",
  sub: () => "Entran por el QR del equipo, mail o teléfono · plazos: seguridad 24 h, resto 2 días hábiles, datos personales 10 días",
  acciones: () => `<button class="btn pri" data-a="nuevoRC">Nuevo reclamo</button>`,
  html() {
    const f = fil("rcest", "abiertos"), xs = S.reclamos.filter(x => f === "todos" || x.etapa < 3);
    return `<div class="kpis"><div class="kpi in"><span>Abiertos</span><b>${S.reclamos.filter(x => x.etapa < 3).length}</b></div><div class="kpi ${S.reclamos.some(vencido) ? "no" : "ok"}"><span>Fuera de plazo</span><b>${S.reclamos.filter(vencido).length}</b></div>
      <div class="kpi av"><span>De seguridad abiertos</span><b>${S.reclamos.filter(x => x.tipo === "Seguridad" && x.etapa < 3).length}</b><small>sustituto en 48 h</small></div></div>
      ${UI.f.nuevoRC ? `<div class="panel"><header><h2>Nuevo reclamo</h2><button class="btn sm" data-a="cancelarRC">Cancelar</button></header><div class="cuerpo"><form class="form" data-f="crearRC">
        <label class="campo">Cliente<select id="rcCli">${S.clientes.map(c => `<option value="${c.id}">${esc(c.nombre)}</option>`).join("")}</select></label>
        <label class="campo">Tipo<select id="rcTipo">${Object.keys(PLAZO_RC).map(t => `<option>${t}</option>`).join("")}</select></label>
        <label class="campo">Serie del equipo<input id="rcSerie" placeholder="${ser(5012)}"></label><label class="campo">Entró por<select id="rcCanal"><option>QR del equipo</option><option>Mail</option><option>Teléfono</option></select></label>
        <label class="campo ancho">Qué pasa<textarea id="rcTexto" rows="2"></textarea></label><div class="ancho"><button class="btn pri" type="submit">Registrar y dar número</button></div></form></div></div>` : ""}
      <div class="panel"><header><h2>Bandeja</h2>${chips("rcest", [["abiertos", "Abiertos"], ["todos", "Todos"]], "abiertos")}</header>${tabla(["Reclamo", "Fecha", "Cliente", "Serie", "Tipo", "Etapa", "Plazo"], xs.map(x => `<tr class="click" data-det="reclamo" data-id="${x.id}"><td class="mono nw">${x.id}</td><td class="nw">${fecha(x.fecha)}</td><td>${esc(cliente(x.cliente).nombre)}</td><td class="mono nw">${esc(x.serie)}</td><td>${esc(x.tipo)}</td><td>${pill(ETAPAS_RC[x.etapa], x.etapa === 3 ? "ok" : "in")}</td><td>${x.etapa >= 2 ? pill("respondido", "ok") : vencido(x) ? pill("vencido", "no") : pill(`${PLAZO_RC[x.tipo] - dias(x.fecha)} d`, "av")}</td></tr>`), { vacio: "Sin reclamos abiertos" })}</div>`;
  },
};
ACC.nuevoRC = () => { UI.f.nuevoRC = true; pintar(); };
ACC.cancelarRC = () => { UI.f.nuevoRC = false; pintar(); };
FORM.crearRC = () => {
  const x = { id: `RC-${AA}-${String(S.nRc++).padStart(6, "0")}`, fecha: HOY, cliente: $("#rcCli").value, serie: $("#rcSerie").value || "—", tipo: $("#rcTipo").value, texto: $("#rcTexto").value || "(sin texto)", etapa: 0, canal: $("#rcCanal").value };
  S.reclamos.unshift(x); UI.f.nuevoRC = false; registrar("Reclamo recibido", x.id, x.tipo); toast(`${x.id} registrado`); pintar(); abrirDetalle("reclamo", x.id);
};
DETALLES.reclamo = id => {
  const x = S.reclamos.find(r => r.id === id); if (!x) return null;
  const n = numSerie(x.serie), e = n ? equipo(n) : null;
  return { titulo: x.id, sub: `${esc(x.tipo)} · ${esc(cliente(x.cliente).nombre)}`,
    pie: x.etapa < 3 ? `${x.etapa < 2 ? `<button class="btn" data-a="rcDesvio" data-id="${x.id}">Abrir desvío</button>` : ""}<button class="btn pri" data-a="rcAvanzar" data-id="${x.id}">Pasar a ${ETAPAS_RC[x.etapa + 1]}</button>` : "",
    cuerpo: `<div class="etapas">${ETAPAS_RC.map((t, i) => `<span class="${i < x.etapa ? "hecha" : i === x.etapa ? "actual" : ""}">${t}</span>`).join("")}</div>
      ${vencido(x) ? `<div class="aviso no">Fuera de plazo (${PLAZO_RC[x.tipo]} d).</div>` : ""}
      <dl class="dl"><dt>Recibido</dt><dd>${fecha(x.fecha)}${x.canal ? " · " + esc(x.canal) : ""}</dd><dt>Plazo</dt><dd>${PLAZO_RC[x.tipo]} día${PLAZO_RC[x.tipo] > 1 ? "s" : ""}</dd><dt>Dice</dt><dd>«${esc(x.texto)}»</dd>
      <dt>Equipo</dt><dd>${e ? `<a href="#" data-det="equipo" data-id="${n}" class="mono">${x.serie}</a> · ${esc(e.o.modelo)} · ${e.o.op}` : esc(x.serie)}</dd>
      ${e ? `<dt>Lote</dt><dd>${e.o.rech.length} rechazos en fábrica · polvo ${e.o.insumos.polvo} · ${S.reclamos.filter(r => numSerie(r.serie) && ordenDe(numSerie(r.serie)) === e.o).length} reclamos del mismo lote</dd>` : ""}</dl>
      <div class="aviso in">La respuesta informa la vía de conciliación (Ventanilla Federal / COPREC) si el cliente no queda conforme.</div>` };
};
ACC.rcAvanzar = el => { const x = S.reclamos.find(r => r.id === el.dataset.id); x.etapa++; registrar("Reclamo: " + ETAPAS_RC[x.etapa], x.id); toast(`${x.id}: ${ETAPAS_RC[x.etapa]}`); pintar(); };
ACC.rcDesvio = el => { const x = S.reclamos.find(r => r.id === el.dataset.id); const d = { id: `RD-${AA}-${String(S.nRd++).padStart(3, "0")}`, fecha: HOY, origen: "Cliente", que: x.texto, ref: x.id, sev: x.tipo === "Seguridad" ? "Mayor" : "Menor", resp: "Calidad", estado: "Abierto", causa: "", accion: "" };
  S.desvios.unshift(d); registrar("Desvío abierto", d.id, x.id); toast(`${d.id} abierto`); pintar(); };

// ---------------------------------------------------------------- clientes
VISTAS.clientes = {
  titulo: "Clientes",
  sub: () => "Distribuidores y usuarios finales",
  html() {
    const max = S.ordenes[S.ordenes.length - 1].hasta, cnt = {};
    for (let n = 1; n <= max; n++) { const e = equipo(n); if (e.estado === "Instalado") cnt[e.cliente.id] = (cnt[e.cliente.id] || 0) + 1; else if (e.estado === "En distribuidor") cnt[e.remito.cliente] = (cnt[e.remito.cliente] || 0) + 1; }
    return `<div class="panel">${tabla(["Cliente", "Tipo", "CUIT", "Localidad", "Jurisdicción", "Equipos", "Recargas abiertas", "Reclamos abiertos"], S.clientes.map(c => `<tr class="click" data-det="cliente" data-id="${c.id}"><td>${esc(c.nombre)}</td><td>${esc(c.tipo)}</td><td class="mono">${c.cuit}</td><td>${esc(c.loc)}</td><td>${c.jur}</td><td class="num">${n0(cnt[c.id] || 0)}</td><td class="num">${S.recargas.filter(r => r.cliente === c.id && r.etapa < 5).length}</td><td class="num">${S.reclamos.filter(r => r.cliente === c.id && r.etapa < 3).length}</td></tr>`))}</div>`;
  },
};
DETALLES.cliente = id => {
  const c = cliente(id); if (!c.cuit) return null;
  const max = S.ordenes[S.ordenes.length - 1].hasta, eqs = [];
  for (let n = 1; n <= max && eqs.length < 400; n++) { const e = equipo(n); if ((e.cliente && e.cliente.id === id) || (e.estado === "En distribuidor" && e.remito.cliente === id)) eqs.push(e); }
  return { titulo: esc(c.nombre), sub: `${esc(c.tipo)} · ${c.cuit} · ${esc(c.loc)} (${c.jur})`,
    cuerpo: `<dl class="dl"><dt>Tarjeta oficial</dt><dd>${c.jur === "CABA" ? "SGM de la AGC (Res. 32-AGC/15)" : "Tarjeta DPS (Res. 349/07)"}</dd><dt>Equipos</dt><dd>${eqs.length}</dd><dt>Remitos</dt><dd>${S.remitos.filter(r => r.cliente === id).length}</dd></dl>
      <div><h3>Equipos</h3>${tabla(["Serie", "Modelo", "Estado", "Mantenimiento"], eqs.slice(0, 60).map(e => `<tr class="click" data-det="equipo" data-id="${e.n}"><td class="mono">${e.s}</td><td>${esc(e.o.modelo)}</td><td>${pill(e.estado, estadoPill[e.estado])}</td><td>${fecha(e.mant)}</td></tr>`), { vacio: "Sin equipos" })}${eqs.length > 60 ? `<p class="muted">y ${eqs.length - 60} más</p>` : ""}</div>
      <div><h3>Recargas</h3>${tabla(["Orden", "Tipo", "Etapa"], S.recargas.filter(r => r.cliente === id).map(r => `<tr class="click" data-det="recarga" data-id="${r.os}"><td class="mono">${r.os}</td><td>${esc(r.tipo)}</td><td>${pill(r.inutil ? "Inutilizar" : ETAPAS_OS[r.etapa], r.inutil ? "no" : "in")}</td></tr>`), { vacio: "Sin recargas abiertas" })}</div>` };
};
ACC.verEtiqueta = el => ir("equipo", el.dataset.id);
