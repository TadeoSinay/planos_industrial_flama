// ================================================================ estructura: menú, vistas, panel de detalle y búsqueda
const IC = {
  tablero: '<path d="M3 13h8V3H3zM13 21h8V11h-8zM3 21h8v-6H3zM13 3v6h8V3z"/>',
  ordenes: '<path d="M9 5h11M9 12h11M9 19h11M4 5h.01M4 12h.01M4 19h.01"/>',
  calidad: '<path d="m9 12 2 2 4-4"/><path d="M12 3 4 6v6c0 5 3.4 8.3 8 9 4.6-.7 8-4 8-9V6z"/>',
  etiquetado: '<path d="M3 5v14M7 5v14M11 5v14M15 5v14M19 5v14"/>',
  expedicion: '<path d="M3 7h11v9H3zM14 10h4l3 3v3h-7z"/><circle cx="7" cy="18" r="1.6"/><circle cx="17" cy="18" r="1.6"/>',
  equipos: '<rect x="8" y="6" width="8" height="15" rx="3"/><path d="M11 3h2v3h-2zM13 4h4"/>',
  recargas: '<path d="M20 12a8 8 0 1 1-2.3-5.7M20 4v5h-5"/>',
  reclamos: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  clientes: '<circle cx="9" cy="8" r="3.5"/><path d="M2 20c0-3.5 3-6 7-6s7 2.5 7 6M16 4a3.5 3.5 0 0 1 0 7M18 14c2.4.7 4 2.8 4 6"/>',
  desvios: '<path d="M12 3 2 20h20zM12 10v4M12 17h.01"/>',
  insumos: '<path d="M21 8 12 3 3 8v8l9 5 9-5zM3 8l9 5 9-5M12 13v8"/>',
  reportes: '<path d="M6 3h9l5 5v13H6zM14 3v6h6M9 13h8M9 17h8"/>',
  config: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-2.7-1.1l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0-1.1-2.7H3a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.1-2.7l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 2.7-1.1V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 2.7 1.1l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0 1.1 2.7H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1.1z"/>',
};
const MENU = [
  ["", [["tablero", "Tablero"]]],
  ["Producción", [["ordenes", "Órdenes"], ["calidad", "Calidad"], ["etiquetado", "Etiquetado"]]],
  ["Logística", [["expedicion", "Expedición"], ["equipos", "Equipos"]]],
  ["Servicio", [["recargas", "Recargas"], ["reclamos", "Reclamos"], ["clientes", "Clientes"]]],
  ["Gestión", [["desvios", "Desvíos"], ["insumos", "Insumos"], ["reportes", "Reportes"], ["config", "Configuración"]]],
];
const VISTAS = {};               // id → { titulo, sub(), acciones(), html() } (las agrega cada módulo)
const UI = { vista: "tablero", f: {}, pag: {}, det: null };
const ACC = {}, FORM = {};

function contadores() {
  const ord = S.ordenes.filter(o => o.mes === D.mes && o.etapa < E["Despachada"]).length;
  const etq = S.ordenes.filter(o => o.etapa === E["Para etiquetar"]).length;
  const rc = S.reclamos.filter(x => x.etapa < 3).length, rcv = S.reclamos.filter(vencido).length;
  const os = S.recargas.filter(x => x.etapa < 5 && !x.inutil).length;
  const rd = S.desvios.filter(x => x.estado !== "Cerrado").length;
  const ins = D.insumos.filter(m => estadoInsumo(m).k === "no").length;
  return { ordenes: [ord], etiquetado: [etq], reclamos: [rc, rcv], recargas: [os], desvios: [rd], insumos: [ins, ins] };
}
function pintarMenu() {
  const c = contadores();
  $("#lateral").innerHTML = `<div class="marca">${logo(30)}<div><b>FLAMA</b><small>Sistema de gestión</small></div></div>` +
    MENU.map(([g, items]) => `<nav class="grupo-nav" aria-label="${esc(g || "Inicio")}">${g ? `<h6>${esc(g)}</h6>` : ""}${items.map(([id, t]) => {
      const k = c[id]; return `<a href="#${id}" data-v="${id}" ${UI.vista === id ? 'aria-current="page"' : ""}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${IC[id]}</svg>${esc(t)}${k && k[0] ? `<span class="cnt ${k[1] ? "alerta" : ""}">${k[0]}</span>` : ""}</a>`; }).join("")}</nav>`).join("");
}
function pintar() {
  const v = VISTAS[UI.vista];
  $("#vista").innerHTML = `<div class="cab"><div><h1>${esc(v.titulo)}</h1>${v.sub ? `<div class="sub">${v.sub()}</div>` : ""}</div>${v.acciones ? `<div class="acciones">${v.acciones()}</div>` : ""}</div>${v.html()}`;
  pintarMenu();
  if (UI.det) abrirDetalle(UI.det.tipo, UI.det.id, true);
}
function ir(v) { UI.vista = VISTAS[v] ? v : "tablero"; UI.det = null; $("#capa").innerHTML = ""; try { history.replaceState(null, "", "#" + UI.vista); } catch (e) {} pintar(); window.scrollTo(0, 0); }

// ---------------------------------------------------------------- panel de detalle
const DETALLES = {};           // tipo → id → { titulo, sub, cuerpo, pie }
function abrirDetalle(tipo, id, re) {
  const d = DETALLES[tipo](id); if (!d) return;
  UI.det = { tipo, id };
  const scroll = re && $(".detalle .cuerpo") ? $(".detalle .cuerpo").scrollTop : 0;
  $("#capa").innerHTML = `<div class="velo" data-a="cerrarDetalle"></div><section class="detalle" role="dialog" aria-label="${esc(d.titulo)}"><header><div><h2>${d.titulo}</h2>${d.sub ? `<div class="sub">${d.sub}</div>` : ""}</div><button class="cerrar" data-a="cerrarDetalle" aria-label="Cerrar">×</button></header>
    <div class="cuerpo">${d.cuerpo}</div>${d.pie ? `<footer>${d.pie}</footer>` : ""}</section>`;
  if (scroll) $(".detalle .cuerpo").scrollTop = scroll;
}
ACC.cerrarDetalle = () => { UI.det = null; $("#capa").innerHTML = ""; };

// ---------------------------------------------------------------- búsqueda global
function buscar(q) {
  q = q.trim(); if (q.length < 2) return [];
  const Q = q.toUpperCase(), out = [];
  const n = numSerie(Q) ?? (/^\d{3,6}$/.test(Q) ? +Q : null);
  if (n && ordenDe(n)) out.push(["Equipo", ser(n), () => abrirDetalle("equipo", n)]);
  S.ordenes.filter(o => o.op.replace(/\s/g, "").includes(Q.replace(/\s/g, ""))).slice(0, 5).forEach(o => out.push(["Orden", `${o.op} · ${o.modelo}`, () => abrirDetalle("orden", o.op)]));
  S.remitos.filter(r => r.id.replace(/\s/g, "").includes(Q.replace(/\s/g, ""))).slice(0, 4).forEach(r => out.push(["Remito", `${r.id} · ${cliente(r.cliente).nombre}`, () => abrirDetalle("remito", r.id)]));
  S.clientes.filter(c => c.nombre.toUpperCase().includes(Q) || c.cuit.includes(q)).slice(0, 4).forEach(c => out.push(["Cliente", c.nombre, () => abrirDetalle("cliente", c.id)]));
  S.recargas.filter(r => r.os.includes(Q) || r.etiqueta.includes(Q)).slice(0, 4).forEach(r => out.push(["Recarga", `${r.os} · ${r.tipo}`, () => abrirDetalle("recarga", r.os)]));
  D.insumos.filter(m => m.cod.toUpperCase().includes(Q) || m.mat.toUpperCase().includes(Q)).slice(0, 4).forEach(m => out.push(["Insumo", `${m.cod} · ${m.mat}`, () => abrirDetalle("insumo", m.cod)]));
  S.ordenes.filter(o => Object.values(o.insumos).includes(Q)).slice(0, 1).forEach(() => out.push(["Lote MP", `${Q}: órdenes que lo usaron`, () => abrirDetalle("loteMP", Q)]));
  return out.slice(0, 12);
}
let RES = [];
function pintarBusqueda() {
  const q = $("#q").value; RES = buscar(q);
  const el = $("#resq"); el.hidden = !q.trim();
  el.innerHTML = RES.length ? RES.map(([t, txt], i) => `<button data-a="irRes" data-i="${i}"><span class="muted">${esc(t)}</span><span>${esc(txt)}</span></button>`).join("") : `<div style="padding:10px 12px" class="muted">Sin resultados para «${esc(q)}»</div>`;
}
ACC.irRes = el => { const r = RES[+el.dataset.i]; $("#resq").hidden = true; $("#q").value = ""; r && r[2](); };
