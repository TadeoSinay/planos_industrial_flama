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
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1440, height: 1000 } });
  const foto = async (n, sel) => { await p.waitForTimeout(300); await rellenarQR(p); sel ? await p.locator(sel).screenshot({ path: path.join(OUT, n + ".png") }) : await p.screenshot({ path: path.join(OUT, n + ".png") }); };
  const c = async s => { await p.click(s); await p.waitForTimeout(200); };
  const ir = async h => { await p.goto(`${URL}/#${h}`); await p.waitForTimeout(250); };
  // el navegador arranca sin registros: las capturas muestran solo lo real (archivos del proyecto) y los formularios
  for (const v of ["tablero", "ordenes", "lotes", "calidad", "estados", "estadoseq", "amfe", "expedicion", "instalaciones", "recargas", "reclamos", "clientes", "insumos", "eventos", "reportes"]) { await ir(v); await foto("cap_" + v); }
  await ir("tablero"); await c("[data-k=tab][data-v=extra]"); await foto("cap_tablero_extra");
  await ir("amfe"); await c("[data-k=qtab][data-v=campo]"); await foto("cap_amfe_campo");
  await c("[data-k=qtab][data-v=plan]"); await foto("cap_plan");
  await ir("origen"); await c("[data-k=otab][data-v=intra]"); await foto("cap_origen");
  await c("[data-k=otab][data-v=extra]"); await foto("cap_origen_extra");
  await ir("lote-26-10-08"); await foto("cap_orden");
  await c("[data-k=ltab][data-v=hoja]"); await foto("cap_lote_hoja");
  await p.evaluate(() => abrirDetalle("cierre", "OP 26-10-08")); await foto("cap_form_cierre");
  await ir("equipo-26-005480"); await foto("cap_equipo");
  await ir("traza"); await p.fill("#trq", "26-005480"); await c("form[data-f=traza] button[type=submit]"); await foto("cap_lote");
  // tablas de calidad para el Word: las mismas filas que muestra el sistema
  const dat = await p.evaluate(() => ({
    amfeP: amfe(false).map(f => [f.id, f.pto + " · " + f.op, f.modo, f.efecto, f.s, f.O, f.d, f.npr, f.accion ? f.acc : "—", f.base]),
    amfeC: amfe(true).map(f => [f.id, f.etapa, f.modo, f.efecto, f.s, f.O, f.d, f.npr, f.accion ? f.acc : "—", f.base]),
    plan: PLAN.map(x => [x.c, x.pto, x.car, x.esp, x.met + (x.inst.length ? " (" + x.inst.join(", ") + ")" : ""), x.mue, x.reg, x.rea]),
    estLote: ESTADOS_LOTE.map((e, i) => [String(i), ...e, i > 0 && i < 8 ? durTxt(tiempoMedio(i)) : "—"]),
    estEq: ESTADOS_EQ, oriI: ORIGEN_INTRA, oriE: ORIGEN_EXTRA }));
  fs.writeFileSync(path.join(OUT, "datos_calidad.json"), JSON.stringify(dat, null, 1));
  const m = await b.newPage({ viewport: { width: 400, height: 760 }, deviceScaleFactor: 2 });
  await m.goto(`${URL}/m/26-005480`); await m.waitForTimeout(300); await rellenarQR(m); await m.screenshot({ path: path.join(OUT, "cap_qr.png") });
  await b.close(); srv.close(); console.log("ok", fs.readdirSync(OUT).length, "capturas");
})();
