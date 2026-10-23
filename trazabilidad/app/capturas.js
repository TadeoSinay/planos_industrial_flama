// Capturas de la app para el Word (trazabilidad/capturas/*.png) y contenido.json con las tablas de la app
// (plazos, matriz normativa, procedimientos, reglas y desvíos), para que el Word use exactamente lo mismo.
// Sirve index.html con las mismas rutas que vercel.json. Uso: NODE_PATH=$(npm root -g) node capturas.js
const http = require("http"), fs = require("fs"), path = require("path");
const { chromium } = require("playwright");
const AQUI = __dirname, OUT = path.join(AQUI, "..", "capturas");
const html = fs.readFileSync(path.join(AQUI, "index.html"));
const srv = http.createServer((q, r) => { r.writeHead(200, { "content-type": "text/html; charset=utf-8" }); r.end(html); }).listen(0);
const URL = `http://127.0.0.1:${srv.address().port}`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const click = async s => { await p.click(s); await p.waitForTimeout(120); };
  const foto = (n, opt = {}) => p.screenshot(Object.assign({ path: path.join(OUT, n + ".png") }, opt));
  await p.goto(URL + "/#inicio"); await p.waitForTimeout(400); await foto("cap_inicio");
  await p.goto(URL + "/#orden"); await p.waitForTimeout(300);
  await click("[data-a=confirmar]"); await foto("cap_orden");
  await click("#sig"); await click("#sig"); await click("[data-a=grabarTodo]"); await click("#sig");
  await p.screenshot({ path: path.join(OUT, "cap_hoja.png"), clip: { x: 0, y: 60, width: 1440, height: 840 } });
  await click("#sig"); await click("[data-a=cerrar]"); await click("#sig");
  for (let i = 0; i < 3; i++) await click("[data-a=leerSig]");
  await click("[data-a=leerRech]"); await foto("cap_etiquetado");
  await click("[data-a=leerTodo]"); await click("#sig"); await click("[data-a=pallet]"); await click("#sig"); await click("[data-a=despachar]");
  await click("#sig"); await click("[data-a=salida]"); await click("#sig"); await click("[data-a=recibir]"); await click("#sig");
  await p.selectOption("#jur", "CABA"); await p.waitForTimeout(150); await foto("cap_instalacion");
  await click("[data-a=firmar]"); await click("#sig"); await click("#sig"); await foto("cap_reclamo");
  await click("[data-a=resolverReclamo]"); await click("#sig"); await click("[data-a=rBajo]"); await foto("cap_recarga");
  await click("[data-a=servicio]"); await click("#sig"); await click("[data-a=inutilizar]");
  await p.goto(URL + "/#clientes"); await p.waitForTimeout(300);
  await click("[data-k=reclamo]"); await click("[data-a=otroReclamo]"); await click("[data-a=enviarReclamo]"); await foto("cap_clientes");
  await p.goto(URL + "/#manual"); await p.waitForTimeout(300); await click('[data-q="PO-2603"]');
  await p.locator("#m-buscar").screenshot({ path: path.join(OUT, "cap_buscar.png") });
  await p.goto(URL + "/#desvios"); await p.waitForTimeout(300);
  const bl = p.locator(".bloque");
  await bl.nth(0).screenshot({ path: path.join(OUT, "cap_pareto.png") });
  await bl.nth(1).screenshot({ path: path.join(OUT, "cap_cartap.png") });
  await bl.nth(2).screenshot({ path: path.join(OUT, "cap_carga.png") });
  const datos = await p.evaluate(() => ({ PLAZOS, MATRIZ, PROCS, RACI, REGLAS, RDS: RDS.map(r => Object.assign({ cod: "RD-" + AA + "-" + r.id }, r)),
    DV: { N: DV.N, rech: DV.rech, causas: DV.causas, media: DV.media, lcs: DV.lcs, lci: DV.lci, pb: DV.pb, nLotes: DV.ph.length },
    PASOS: PASOS.map(x => ({ id: x.id, g: x.g, t: x.t, r: x.r, quien: x.quien, equipo: x.equipo, tiempo: x.tiempo, normas: x.normas, falla: x.falla })),
    PARTIDA: { id: PARTIDA.id, u: PARTIDA.u, ops: PARTIDA.ops.map(l => l.op) }, DEMO: { op: DEMO.op, modelo: DEMO.modelo, desde: SERIES[0], hasta: SERIES[SERIES.length - 1], rej: REJ, cli: CLI } }));
  fs.writeFileSync(path.join(AQUI, "contenido.json"), JSON.stringify(datos, null, 1));
  const m = await b.newPage({ viewport: { width: 400, height: 860 }, deviceScaleFactor: 2 });
  await m.goto(URL + "/m/" + datos.DEMO.cli); await m.waitForTimeout(400); await m.screenshot({ path: path.join(OUT, "cap_qr.png") });
  await b.close(); srv.close(); console.log("ok", fs.readdirSync(OUT).length, "capturas");
})();
