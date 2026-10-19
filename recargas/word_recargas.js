// Word «Justificación de recargas»: arma el .docx con los bloques que deja generar_word_recargas.py.
// Uso: node word_recargas.js <bloques.json> <salida.docx>   (necesita el paquete npm docx)
// Bloques: titulo, sub, h1, h2, h3, p, b (viñeta), nota, tabla, salto. En el texto, **x** va en negrita.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, HeadingLevel,
  AlignmentType, Footer, PageNumber, LevelFormat, BorderStyle, PageBreak, ExternalHyperlink,
} = require("docx");

const B = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const OUT = process.argv[3];

const W = 9906;          // A4 con márgenes de 1000 DXA
const FONT = "Arial";
const NEGRO = "000000", GRIS_O = "595959", GRIS_M = "BFBFBF", GRIS_C = "EDEDED";
const fino = { style: BorderStyle.SINGLE, size: 4, color: GRIS_M };
const bordes = { top: fino, bottom: fino, left: fino, right: fino };

// texto con **negrita** y enlaces [texto](url)
function runs(x, o = {}) {
  const out = [];
  const re = /\*\*(.+?)\*\*|\[([^\]]+)\]\((https?:[^)\s]+)\)/g;
  let i = 0, m;
  const tr = (s, b) => new TextRun({ text: s, font: FONT, size: o.size || 19, bold: b || o.bold, italics: o.italics,
    color: o.color || NEGRO });
  while ((m = re.exec(x)) !== null) {
    if (m.index > i) out.push(tr(x.slice(i, m.index)));
    if (m[1] !== undefined) out.push(tr(m[1], true));
    else out.push(new ExternalHyperlink({ link: m[3], children: [new TextRun({ text: m[2], font: FONT,
      size: o.size || 19, color: "1F1F1F", underline: {} })] }));
    i = m.index + m[0].length;
  }
  if (i < x.length) out.push(tr(x.slice(i)));
  return out;
}

const par = (x, o = {}) => new Paragraph({ children: runs(x, o), spacing: { after: o.after ?? 100, before: o.before ?? 0,
  line: 276 }, alignment: o.align, heading: o.heading, keepNext: o.keepNext,
  numbering: o.bullet ? { reference: "vinetas", level: 0 } : undefined });

function celda(c, ancho, o = {}) {
  return new TableCell({ width: { size: ancho, type: WidthType.DXA }, borders: bordes,
    shading: o.fill ? { type: ShadingType.CLEAR, color: "auto", fill: o.fill } : undefined,
    margins: { top: 30, bottom: 30, left: 70, right: 70 },
    children: [new Paragraph({ alignment: o.align, spacing: { after: 0 },
      children: runs(c === null || c === undefined ? "—" : String(c), { size: 16, bold: o.bold, color: o.color }) })] });
}

function tabla(b) {
  const k = W / b.cols.reduce((a, x) => a + x, 0);
  const cw = b.cols.map((x) => Math.round(x * k));
  cw[cw.length - 1] += W - cw.reduce((a, x) => a + x, 0);
  const num = new Set(b.num || []);
  const neg = new Set(b.negrita || []);
  const head = new TableRow({ tableHeader: true, cantSplit: true,
    children: b.cab.map((h, i) => celda(h, cw[i], { bold: true, color: "FFFFFF", fill: NEGRO, align: AlignmentType.CENTER })) });
  const rows = b.filas.map((f, j) => new TableRow({ cantSplit: true, children: f.map((c, i) => celda(c, cw[i], {
    align: num.has(i) ? AlignmentType.RIGHT : undefined, bold: neg.has(j), fill: neg.has(j) ? GRIS_C : undefined })) }));
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: cw, rows: [head, ...rows] });
}

const hijos = [];
for (const b of B) {
  switch (b.t) {
    case "titulo": hijos.push(par(b.x, { size: 36, bold: true, after: 120 })); break;
    case "sub": hijos.push(par(b.x, { size: 20, color: GRIS_O, after: 60 })); break;
    case "h1": hijos.push(par(b.x, { heading: HeadingLevel.HEADING_1, keepNext: true, before: 240, after: 120 })); break;
    case "h2": hijos.push(par(b.x, { heading: HeadingLevel.HEADING_2, keepNext: true, before: 180, after: 80 })); break;
    case "h3": hijos.push(par(b.x, { heading: HeadingLevel.HEADING_3, keepNext: true, before: 140, after: 60 })); break;
    case "p": hijos.push(par(b.x, { keepNext: b.keep })); break;
    case "b": hijos.push(par(b.x, { bullet: true, after: 40 })); break;
    case "nota": hijos.push(par(b.x, { size: 16, color: GRIS_O, after: 120 })); break;
    case "tabla":
      hijos.push(tabla(b));
      hijos.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      break;
    case "salto": hijos.push(new Paragraph({ children: [new PageBreak()] })); break;
    default: throw new Error("bloque desconocido: " + b.t);
  }
}

const doc = new Document({
  creator: "FLAMA", title: "Justificación de recargas",
  styles: {
    default: { document: { run: { font: FONT, size: 19 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: NEGRO }, paragraph: { outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: NEGRO, space: 2 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, font: FONT, color: NEGRO }, paragraph: { outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 20, bold: true, font: FONT, color: GRIS_O }, paragraph: { outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "vinetas", levels: [{ level: 0, format: LevelFormat.BULLET, text: "–",
    alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1000, bottom: 1000, left: 1000, right: 1000 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      new TextRun({ text: "Justificación de recargas · ", font: FONT, size: 15, color: GRIS_O }),
      new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 15, color: GRIS_O })] })] }) },
    children: hijos,
  }],
});

Packer.toBuffer(doc).then((buf) => fs.writeFileSync(OUT, buf));
