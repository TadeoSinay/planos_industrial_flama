// ================================================================ base: utilidades, marca, estado y registro con hash
const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const n0 = x => Math.round(x).toLocaleString("es-AR");
const nf = (x, d = 2) => Number(x).toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
const DEMO = D.demo, SERIES = DEMO.series, REJ = SERIES[16];   // el equipo 17 del lote falla la prueba hidráulica
const OTRO = SERIES[30];                                         // el que se usa para la inutilización (años después)
const CLI = SERIES[2];                                           // el que se sigue hasta el cliente
const AA = String(D.anio).slice(2);
const MES = D.mesNombre.toLowerCase();
const hoy = () => new Date().toLocaleDateString("es-AR");

// generador pseudoaleatorio con semilla fija: los datos simulados son siempre los mismos
function semilla(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function normal(r, m, s) { let u = 0, v = 0; while (!u) u = r(); while (!v) v = r(); return m + s * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

// marca: si build.py encontró app/logo.svg o app/logo.png se usa ese; si no, la marca provisoria
function logo(h = 34, cls = "logo") {
  if (LOGO) return `<img class="${cls}" src="${LOGO}" alt="FLAMA" style="height:${h}px">`;
  return `<svg class="${cls}" viewBox="0 0 40 40" style="height:${h}px;width:${h}px" role="img" aria-label="FLAMA"><rect width="40" height="40" rx="8" fill="#C8241A"/>
    <path d="M20 4.5c2.2 6.4 10.5 10.4 10.5 19.6 0 6.8-4.7 11.4-10.5 11.4S9.5 30.9 9.5 24.1c0-5 2.8-8.3 5.2-11.3.5 4 2.3 6.3 4.3 7.4-1-5.2-.9-10.6 1-15.7z" fill="#fff"/>
    <path d="M20 21.5c1.7 3.2 5.1 4.4 5.1 8 0 3-2.3 5-5.1 5s-5.1-2-5.1-5c0-2.7 2.1-4.3 5.1-8z" fill="#C8241A"/></svg>`;
}
const foto = k => IMG && IMG[k] ? IMG[k] : "";

function qr(key, size = 96) {
  const q = D.qr[key]; if (!q) return "";
  return `<svg viewBox="-2 -2 ${q.n + 4} ${q.n + 4}" width="${size}" height="${size}" role="img" aria-label="QR ${esc(key)}"><rect x="-2" y="-2" width="${q.n + 4}" height="${q.n + 4}" fill="#fff"/><path d="${q.d}" fill="#000"/></svg>`;
}
function dm(texto, size = 64) {           // DataMatrix ilustrativo (patrón con borde en L), solo para mostrar
  let h = 0; for (const c of texto) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  let r = ""; const n = 18;
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
    h = (h * 1103515245 + 12345) >>> 0;
    const on = j === 0 || i === n - 1 || (i === 0 && j % 2 === 0) || (j === n - 1 && i % 2 === 1) || (i > 0 && j > 0 && i < n - 1 && j < n - 1 && (h >> 16) % 2);
    if (on) r += `<rect x="${j}" y="${i}" width=".9" height=".9"/>`;
  }
  return `<svg viewBox="0 0 18 18" width="${size}" height="${size}" aria-hidden="true"><g fill="currentColor">${r}</g></svg>`;
}

// ---------------------------------------------------------------- estado y registro con hash
const S = { vista: "inicio", paso: 0, opOk: false, grabados: 0, tildes: {}, foto: null, cerrado: false, impresos: [], ultimo: null,
  cajas: 0, pallet: false, despachado: false, cot: "", salida: false, recibido: false, danio: false,
  instalado: null, recarga: null, inutil: false, tab: "com", eventos: [],
  cli: { tab: "equipo", reclamos: [], tipo: "seguridad", texto: "El manómetro marca en la zona roja y el precinto está roto.", servicio: false, baja: false, datos: null },
  manual: { q: "" }, desv: { sev: "todas", abierto: null } };
SERIES.forEach(s => S.tildes[s] = { esp: true, ph: s !== REJ, carga: s !== REJ, perd: s !== REJ });

async function sha(t) {
  try { const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t));
    return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, "0")).join(""); }
  catch (e) { let h = 0; for (const c of t) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h.toString(16).padStart(8, "0") + "…"; }
}
async function evento(tipo, ref, quien, datos = {}) {
  const prev = S.eventos.length ? S.eventos[S.eventos.length - 1].hash : "0".repeat(64);
  const hora = new Date().toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const e = { n: S.eventos.length + 1, hora, tipo, ref, quien, datos };
  e.hash = await sha(prev + JSON.stringify(e));
  S.eventos.push(e); pintarRegistro(); if ($("#barra")) pintarBarra();
}
function pintarRegistro() {
  $("#registro tbody").innerHTML = S.eventos.slice().reverse().map(e => `<tr class="nuevo-in"><td class="mono">${e.n}</td><td class="mono">${e.hora}</td><td>${esc(e.tipo)}</td><td class="mono">${esc(e.ref)}</td><td>${esc(e.quien)}</td><td class="mono hash">${e.hash.slice(0, 16)}…</td></tr>`).join("")
    || `<tr><td colspan="6" style="color:var(--ink-3)">Todavía no hay eventos. Entrá al Recorrido y confirmá la orden del paso 1: cada acción queda acá.</td></tr>`;
}

// ---------------------------------------------------------------- piezas de pantalla
const pc = (url, html, rol = "Planta") => `<div class="pc"><div class="pc-bar"><i></i><i></i><i></i><span class="url">trazabilidad-flama.vercel.app/${url}</span></div><div class="pc-head">${logo(20)}<b>FLAMA · Trazabilidad</b><span>${esc(rol)}</span></div><div class="pc-in">${html}</div></div>`;
const tel = (html, marca = "trazabilidad-flama.vercel.app") => `<div class="tel"><div class="tel-in"><div class="tel-top"><i></i></div><div class="tel-brand">${logo(18)}<b>FLAMA</b><span>${esc(marca)}</span></div><div class="tel-body">${html}</div></div></div>`;
const etiqueta = (s, tit = DEMO.modelo, l2 = "fabricado " + MES + " " + D.anio, l3 = "escaneá para ver su historia") =>
  `<div class="etq nuevo-in"><div class="qr">${qr(s)}</div><div><b>${logo(13, "lg")} FLAMA · ${esc(tit)}</b><div class="num">${esc(s)}</div><small>${esc(l2)}<br>${esc(l3)}</small></div></div>`;
function sheet(fuente, archivo, hoja, cols, filas, tabs, nuevas = []) {
  const ic = { db: `<span class="ic db">DB</span>`, gov: `<span class="ic gov">GOB</span>` }[fuente] || `<span class="ic">S</span>`;
  return `<div class="sheet"><div class="sheet-head">${ic}<span><b>${esc(archivo)}</b> › ${esc(hoja)}</span></div>
  <div class="tscroll"><table><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>
  ${filas.map((f, i) => `<tr class="${nuevas.includes(i) ? "nuevo" : ""}">${f.map(c => `<td>${esc(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
  ${tabs ? `<div class="tabs">${tabs.map(t => `<span class="${t === hoja ? "on" : ""}">${esc(t)}</span>`).join("")}</div>` : ""}</div>`;
}
const TABS_DB = ["OP", "SERIES", "EVENTOS", "LOTES_INSUMO", "AGREGACION", "CUSTODIA", "FICHAS", "RECLAMOS", "DESVIOS"];
const lotesMes = () => D.lotes.filter(l => !l.modelo.startsWith("Carro"));
const ACC = {}, INPUT = {}, FORM = {};   // acciones por data-a, inputs por data-i y formularios por data-f; cada vista agrega los suyos
const sumarDias = (n, habiles = false) => { const d = new Date(); let k = 0; while (k < n) { d.setDate(d.getDate() + 1); if (!habiles || (d.getDay() % 6)) k++; } return d.toLocaleDateString("es-AR"); };
const norm = arr =>`<div class="normref">${arr.map(n => `<span>${esc(n)}</span>`).join("")}</div>`;
