// ================================================================ utilidades
const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const n0 = x => Math.round(x).toLocaleString("es-AR");
const nf = (x, d = 1) => Number(x).toLocaleString("es-AR", { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (a, b) => b ? nf(100 * a / b, 1) + " %" : "—";
const AA = String(D.anio).slice(2);
const ser = n => `${AA}-${String(n).padStart(6, "0")}`;
const numSerie = s => { const m = String(s).match(/^(\d{2})-?(\d{6})$/); return m && m[1] === AA ? +m[2] : null; };

// fecha de trabajo: hoy si cae en el mes del plan; si no, el día 23 del mes del plan
const HOY = (() => { const h = new Date(); return h.getFullYear() === D.anio && h.getMonth() + 1 === D.mes ? new Date(D.anio, D.mes - 1, h.getDate()) : new Date(D.anio, D.mes - 1, 23); })();
const fecha = d => d ? new Date(d).toLocaleDateString("es-AR", { day: "2-digit", month: "2-digit", year: "2-digit" }) : "—";
const dias = (a, b = HOY) => Math.round((new Date(b) - new Date(a)) / 864e5);
const sumar = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
function habiles(anio, mes) { const out = []; for (let d = 1; d <= 31; d++) { const x = new Date(anio, mes - 1, d); if (x.getMonth() !== mes - 1) break; if (x.getDay() % 6) out.push(x); } return out; }
const MES_TXT = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];

// generador con semilla fija: los datos de prueba son siempre los mismos
function semilla(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const hashN = s => { let h = 2166136261; for (const c of String(s)) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; };
const elegir = (r, arr) => arr[Math.floor(r() * arr.length)];

function logo(h = 30) {
  return `<svg viewBox="0 0 40 40" style="height:${h}px;width:${h}px;flex:none" role="img" aria-label="FLAMA"><rect width="40" height="40" rx="8" fill="#C8241A"/>
    <path d="M20 4.5c2.2 6.4 10.5 10.4 10.5 19.6 0 6.8-4.7 11.4-10.5 11.4S9.5 30.9 9.5 24.1c0-5 2.8-8.3 5.2-11.3.5 4 2.3 6.3 4.3 7.4-1-5.2-.9-10.6 1-15.7z" fill="#fff"/>
    <path d="M20 21.5c1.7 3.2 5.1 4.4 5.1 8 0 3-2.3 5-5.1 5s-5.1-2-5.1-5c0-2.7 2.1-4.3 5.1-8z" fill="#C8241A"/></svg>`;
}
function qr(texto) {
  try { const q = qrcode(0, "M"); q.addData(texto); q.make(); return q.createSvgTag({ cellSize: 3, margin: 2, scalable: true }); }
  catch (e) { return `<div title="${esc(texto)}" style="aspect-ratio:1;border:1.5px dashed var(--line);border-radius:6px;display:grid;place-items:center;font:600 11px/1 var(--f-body);color:var(--ink-3)">QR</div>`; }
}
function toast(t) {
  const el = document.createElement("div"); el.className = "toast"; el.textContent = t; el.setAttribute("role", "status");
  document.body.appendChild(el); setTimeout(() => el.remove(), 2600);
}
async function copiar(texto) {
  try { await navigator.clipboard.writeText(texto); toast("Copiado al portapapeles"); }
  catch (e) { toast("No se pudo copiar: seleccioná el texto y copialo a mano"); }
}
const pill = (t, c) => `<span class="pill ${c}">${esc(t)}</span>`;
const barra = (v, max, col = "var(--blue)") => `<div class="barra" title="${n0(v)} de ${n0(max)}"><i style="width:${Math.min(100, max ? 100 * v / max : 0)}%;background:${col}"></i></div>`;
const tabla = (cab, filas, opt = {}) => `<div class="tscroll"><table class="t"><thead><tr>${cab.map(c => `<th class="${/^(Cant|u\b|%|Stock|Días|Plan|Hechos|Aptos|Rech|Equipos|Consumo|Cobertura|Punto)/.test(c) ? "num" : ""}">${esc(c)}</th>`).join("")}</tr></thead><tbody>${filas.join("") || `<tr><td colspan="${cab.length}" class="muted">${esc(opt.vacio || "Sin registros")}</td></tr>`}</tbody></table></div>`;

// SHA-256 (Web Crypto) para la cadena de eventos; las celdas [data-hash] se completan después de pintar
async function sha256(t) {
  try { const x = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)); return [...new Uint8Array(x)].map(v => v.toString(16).padStart(2, "0")).join(""); }
  catch (e) { return hashN(t).toString(16).padStart(8, "0").repeat(8); }
}
async function hashear() {
  const els = [...document.querySelectorAll("[data-hash]")]; let prev = "0".repeat(64);
  for (const el of els) { prev = await sha256(prev + el.dataset.hash); el.textContent = prev.slice(0, 16) + "…"; el.title = prev; }
}
