// Capturas del sistema de gestión para el Word (trazabilidad/capturas/*.png). Sirve index.html con las rutas de
// vercel.json. Si la librería de QR no carga (sin internet), dibuja los QR con segno (Python) para que la captura sea real.
// Uso: NODE_PATH=$(npm root -g) node capturas.js
const http = require("http"), fs = require("fs"), path = require("path"), { execFileSync } = require("child_process");
const { chromium } = require("playwright");
const AQUI = __dirname, OUT = path.join(AQUI, "..", "capturas");
const html = fs.readFileSync(path.join(AQUI, "index.html"));
const srv = http.createServer((q, r) => { r.writeHead(200, { "content-type": "text/html; charset=utf-8" }); r.end(html); }).listen(0);
const URL = `http://127.0.0.1:${srv.address().port}`;
const PY = "import segno,sys,json\nprint(json.dumps([segno.make(t, error='m').svg_inline(scale=3, border=2, omitsize=True) for t in json.loads(sys.stdin.read())]))";
async function rellenarQR(p) {
  const textos = await p.evaluate(() => [...document.querySelectorAll('div[title^="http"]')].map(d => d.title));
  if (!textos.length) return;
  const svgs = JSON.parse(execFileSync("python3", ["-c", PY], { input: JSON.stringify(textos) }).toString());
  await p.evaluate(s => document.querySelectorAll('div[title^="http"]').forEach((d, i) => { d.outerHTML = s[i].replace("<svg ", '<svg style="width:100%;height:auto;display:block" '); }), svgs);
}
(async () => {
  fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const foto = async (n, sel) => { await p.waitForTimeout(250); await rellenarQR(p); sel ? await p.locator(sel).screenshot({ path: path.join(OUT, n + ".png") }) : await p.screenshot({ path: path.join(OUT, n + ".png") }); };
  const c = async s => { await p.click(s); await p.waitForTimeout(150); };
  for (const v of ["tablero", "ordenes", "calidad", "expedicion", "recargas", "reclamos", "insumos", "reportes"]) { await p.goto(`${URL}/#${v}`); await foto("cap_" + v); }
  await p.goto(`${URL}/#ordenes`); await c("[data-a=filtro][data-v=cerrar]"); await c("tr.click"); await foto("cap_orden");
  await p.goto(`${URL}/#etiquetado`); await c("[data-a=leerSig]"); await c("[data-a=leerSig]"); await c("[data-a=leerRech]"); await foto("cap_etiquetado");
  await p.goto(`${URL}/#equipos`); await p.fill("#q", "005480"); await p.waitForTimeout(200); await p.keyboard.press("Enter"); await foto("cap_equipo");
  await p.goto(`${URL}/#recargas`); await c(".col-k:nth-child(3) .tarjeta"); await foto("cap_recarga");
  await p.goto(`${URL}/#tablero`); await p.fill("#q", "PO-2610"); await p.waitForTimeout(200); await p.keyboard.press("Enter"); await foto("cap_lote");
  const m = await b.newPage({ viewport: { width: 400, height: 760 }, deviceScaleFactor: 2 });
  await m.goto(`${URL}/m/26-005480`); await m.waitForTimeout(300); await rellenarQR(m); await m.screenshot({ path: path.join(OUT, "cap_qr.png") });
  await b.close(); srv.close(); console.log("ok", fs.readdirSync(OUT).length, "capturas");
})();
