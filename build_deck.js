const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const FIG = (name) => path.resolve("reports/figures", name);

// Lee dimensiones reales del PNG (IHDR) para preservar el aspecto sin estirar.
function pngSize(p) { const b = fs.readFileSync(p); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
// Coloca la imagen centrada dentro de un box, conservando su relacion de aspecto.
function fitImage(slide, file, boxX, boxY, boxW, boxH) {
  const { w, h } = pngSize(FIG(file)); const r = w / h;
  let dw = boxW, dh = boxW / r;
  if (dh > boxH) { dh = boxH; dw = boxH * r; }
  slide.addImage({ path: FIG(file), x: boxX + (boxW - dw) / 2, y: boxY + (boxH - dh) / 2, w: dw, h: dh });
}

// ---- Palette (Ocean / Teal data theme) ----
const DARK = "0E2A38";   // deep slate-teal (title/closing bg)
const DARK2 = "10394B";  // panel on dark
const TEAL = "0E7C86";   // primary
const TEALL = "1AA0AB";  // lighter teal
const ACCENT = "E8833A";  // warm orange = churn / risk
const LIGHT = "F5F8F9";  // content bg
const CARD = "FFFFFF";
const TEXT = "1F2D34";
const MUTED = "6A7A82";
const LINE = "DCE6E9";

const HF = "Trebuchet MS"; // headers
const BF = "Calibri";      // body

const pres = new pptxgen();
pres.defineLayout({ name: "W", width: 13.333, height: 7.5 });
pres.layout = "W";
pres.author = "Grupo 1";
pres.title = "Pipeline de clasificacion de churn";

const W = 13.333, H = 7.5, M = 0.6;
const shadow = () => ({ type: "outer", color: "0E2A38", blur: 9, offset: 3, angle: 90, opacity: 0.13 });

// ---------- helpers ----------
function header(slide, num, kicker, title) {
  slide.background = { color: LIGHT };
  // number badge motif
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 0.5, w: 0.62, h: 0.62, rectRadius: 0.1, fill: { color: TEAL } });
  slide.addText(String(num).padStart(2, "0"), { x: M, y: 0.5, w: 0.62, h: 0.62, align: "center", valign: "middle", fontFace: HF, fontSize: 18, bold: true, color: "FFFFFF", margin: 0 });
  slide.addText(kicker.toUpperCase(), { x: M + 0.8, y: 0.5, w: 10, h: 0.28, fontFace: HF, fontSize: 11.5, bold: true, color: TEAL, charSpacing: 2, margin: 0, valign: "middle" });
  slide.addText(title, { x: M + 0.8, y: 0.76, w: W - M * 2 - 0.8, h: 0.62, fontFace: HF, fontSize: 27, bold: true, color: TEXT, margin: 0, valign: "middle" });
  slide.addText("Pipeline de clasificacion de churn  ·  Grupo 1", { x: M, y: H - 0.42, w: 8, h: 0.3, fontFace: BF, fontSize: 9, color: MUTED, margin: 0 });
  slide.addText(`${num} / 12`, { x: W - M - 1.2, y: H - 0.42, w: 1.2, h: 0.3, fontFace: BF, fontSize: 9, color: MUTED, align: "right", margin: 0 });
}

function card(slide, x, y, w, h, fill) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill || CARD }, line: { color: LINE, width: 1 }, shadow: shadow() });
}

function msg(slide, text, y) {
  // Intencionalmente vacio: los mensajes tecnicos pasan al guion oral.
}

// table style helper
function thead(cells) { return cells.map(t => ({ text: t, options: { fill: { color: TEAL }, color: "FFFFFF", bold: true, fontFace: HF, fontSize: 12, align: "center", valign: "middle" } })); }
function trow(cells, opts) { return cells.map((t, i) => ({ text: String(t), options: Object.assign({ fontFace: BF, fontSize: 12, color: TEXT, align: i === 0 ? "left" : "center", valign: "middle" }, (opts && opts[i]) || {}) })); }

// =====================================================================
// SLIDE 0 — TITLE
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: DARK };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: TEAL } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.22, y: 0, w: 0.08, h: H, fill: { color: ACCENT } });
  s.addText("PRESENTACION TECNICA", { x: 1.1, y: 1.5, w: 11, h: 0.4, fontFace: HF, fontSize: 15, bold: true, color: TEALL, charSpacing: 4, margin: 0 });
  s.addText("Pipeline de clasificacion\nde churn", { x: 1.05, y: 2.0, w: 11, h: 2.0, fontFace: HF, fontSize: 52, bold: true, color: "FFFFFF", lineSpacingMultiple: 0.95, margin: 0 });
  s.addText("Deteccion de clientes en riesgo con validacion agrupada, control de leakage y seleccion reproducible de modelos.",
    { x: 1.1, y: 4.25, w: 9.7, h: 0.8, fontFace: BF, fontSize: 16, color: "C7D7DD", margin: 0 });
  // bottom chips
  const chips = ["5.630 clientes", "16,8% churn", "Validacion agrupada", "Modelo final: Reg. logistica"];
  let cx = 1.1;
  chips.forEach(c => {
    const w = 0.35 + c.length * 0.105;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: 5.55, w, h: 0.5, rectRadius: 0.25, fill: { color: DARK2 }, line: { color: TEAL, width: 1 } });
    s.addText(c, { x: cx, y: 5.55, w, h: 0.5, align: "center", valign: "middle", fontFace: BF, fontSize: 12, color: "DFEDF0", margin: 0 });
    cx += w + 0.25;
  });
  s.addText("ITBA · IA aplicada a negocios · Grupo 1 · 2026", { x: 1.1, y: 6.6, w: 11, h: 0.35, fontFace: BF, fontSize: 12, color: "8AA3AC", margin: 0 });
}

// =====================================================================
// SLIDE 1 — ARQUITECTURA
// =====================================================================
{
  const s = { addShape(){}, addText(){}, addTable(){}, addImage(){}, background: null };
  header(s, 1, "Arquitectura del experimento", "Flujo completo del pipeline");
  const steps = [
    "Dataset raw", "Auditoria de calidad y duplicados", "Split estratificado por grupos",
    "Feature engineering", "Preprocesamiento dentro del pipeline", "Validacion cruzada agrupada",
    "Comparacion y seleccion de modelos", "Ajuste de umbral con predicciones OOF",
    "Evaluacion final en test", "Interpretabilidad"
  ];
  const colX = [M, 6.95];
  const top = 1.95, ch = 0.46, gap = 0.06;
  steps.forEach((st, i) => {
    const col = i < 5 ? 0 : 1;
    const row = i % 5;
    const x = colX[col], y = top + row * (ch + gap);
    card(s, x, y, 5.78, ch, CARD);
    s.addShape(pres.shapes.OVAL, { x: x + 0.13, y: y + 0.08, w: 0.3, h: 0.3, fill: { color: i === 9 ? ACCENT : TEAL } });
    s.addText(String(i + 1), { x: x + 0.13, y: y + 0.08, w: 0.3, h: 0.3, align: "center", valign: "middle", fontFace: HF, fontSize: 12, bold: true, color: "FFFFFF", margin: 0 });
    s.addText(st, { x: x + 0.55, y, w: 5.1, h: ch, valign: "middle", fontFace: BF, fontSize: 13, color: TEXT, margin: 0 });
  });
  // connector arrow between columns
  s.addText("➜", { x: 6.45, y: top + 2 * (ch + gap), w: 0.5, h: ch, align: "center", valign: "middle", fontSize: 18, color: TEAL, margin: 0 });
  msg(s, "Separar preparacion, seleccion y evaluacion final reduce el leakage y el sobreajuste al conjunto de test.");
}

// =====================================================================
// SLIDE 2 — DATASET Y TARGET
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 1, "Dataset y variable objetivo", "5.630 clientes, target Churn binario");
  // stat callouts
  const stats = [["5.630", "observaciones"], ["20", "columnas (18 predictoras)"], ["16,8%", "clientes con churn"]];
  let sx = M;
  stats.forEach(([n, l]) => {
    card(s, sx, 1.95, 3.0, 1.35);
    s.addText(n, { x: sx, y: 2.05, w: 3.0, h: 0.8, align: "center", fontFace: HF, fontSize: 38, bold: true, color: TEAL, margin: 0 });
    s.addText(l, { x: sx, y: 2.85, w: 3.0, h: 0.4, align: "center", fontFace: BF, fontSize: 12, color: MUTED, margin: 0 });
    sx += 3.2;
  });
  // donut
  s.addChart(pres.charts.DOUGHNUT, [{ name: "Target", labels: ["Churn = 0 (4.682)", "Churn = 1 (948)"], values: [83.2, 16.8] }],
    { x: 9.7, y: 1.8, w: 3.2, h: 3.1, holeSize: 60, chartColors: ["1AA0AB", "E8833A"], showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: TEXT, showValue: false, dataLabelColor: "FFFFFF", showTitle: false });
  // variable types
  card(s, M, 3.5, 9.2, 1.95);
  s.addText("Tipos de variables", { x: M + 0.25, y: 3.62, w: 8, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: TEXT, margin: 0 });
  const types = [["Numericas continuas", "p. ej. CashbackAmount, Tenure"], ["Numericas discretas / ordinales", "OrderCount, SatisfactionScore"], ["Categoricas nominales", "PreferedOrderCat, MaritalStatus"], ["Binarias", "Complain, Gender"]];
  types.forEach((t, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + 0.3 + col * 4.5, y = 4.05 + row * 0.62;
    s.addShape(pres.shapes.RECTANGLE, { x, y: y + 0.05, w: 0.12, h: 0.4, fill: { color: TEAL } });
    s.addText([{ text: t[0] + "  ", options: { bold: true, color: TEXT } }, { text: t[1], options: { color: MUTED, fontSize: 10.5 } }], { x: x + 0.25, y, w: 4.0, h: 0.55, valign: "middle", fontFace: BF, fontSize: 12, margin: 0 });
  });
  msg(s, "El desbalance obliga a usar metricas sensibles a la clase positiva y estrategias de balanceo en los modelos.");
}

// =====================================================================
// SLIDE 3 — AUDITORIA DE CALIDAD
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 2, "Auditoria de calidad", "Nulos, duplicados y categorias equivalentes");
  const stats = [["1.856", "filas con algun nulo", "exactamente 1 faltante c/u"], ["556", "filas con features identicas", "perfiles duplicados"], ["0", "duplicados de CustomerID", "identificador integro"]];
  let sx = M;
  stats.forEach(([n, l, sub]) => {
    card(s, sx, 1.95, 3.0, 1.6);
    s.addText(n, { x: sx, y: 2.02, w: 3.0, h: 0.7, align: "center", fontFace: HF, fontSize: 34, bold: true, color: ACCENT, margin: 0 });
    s.addText(l, { x: sx, y: 2.72, w: 3.0, h: 0.35, align: "center", fontFace: BF, fontSize: 12, bold: true, color: TEXT, margin: 0 });
    s.addText(sub, { x: sx, y: 3.05, w: 3.0, h: 0.35, align: "center", fontFace: BF, fontSize: 10, color: MUTED, margin: 0 });
    sx += 3.2;
  });
  // 7 vars con nulos badge
  card(s, 9.7, 1.95, 3.03, 1.6, DARK);
  s.addText("7", { x: 9.7, y: 2.02, w: 3.03, h: 0.7, align: "center", fontFace: HF, fontSize: 34, bold: true, color: TEALL, margin: 0 });
  s.addText("variables numericas\ncon valores faltantes", { x: 9.7, y: 2.72, w: 3.03, h: 0.7, align: "center", fontFace: BF, fontSize: 12, color: "DFEDF0", margin: 0 });
  // equivalences
  card(s, M, 3.75, 12.13, 1.55);
  s.addText("Categorias semanticamente equivalentes detectadas", { x: M + 0.25, y: 3.85, w: 10, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: TEXT, margin: 0 });
  const eq = [["Phone", "Mobile Phone"], ["COD", "Cash on Delivery"], ["CC", "Credit Card"], ["Mobile", "Mobile Phone"]];
  eq.forEach((e, i) => {
    const x = M + 0.3 + i * 2.95, y = 4.35;
    s.addText([{ text: e[0], options: { bold: true, color: ACCENT } }, { text: "  ≡  ", options: { color: MUTED } }, { text: e[1], options: { bold: true, color: TEAL } }], { x, y, w: 2.85, h: 0.6, valign: "middle", fontFace: BF, fontSize: 12.5, margin: 0 });
  });
  msg(s, "Los perfiles repetidos deben tratarse como grupos para impedir que una copia quede en train y otra en test.");
}

// =====================================================================
// SLIDE 4 — IMPUTACION
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 3, "Estrategia de imputacion", "Metodo por variable, siempre dentro del fold");
  s.addTable([
    thead(["Variables", "Metodo"]),
    trow(["WarehouseToHome, CouponUsed", "Mediana"]),
    trow(["Tenure, HourSpendOnApp, OrderAmountHike,\nOrderCount, DaySinceLastOrder", "KNN Imputer"]),
    trow(["Categoricas", "Moda"]),
  ], { x: M, y: 1.95, w: 7.0, colW: [5.0, 2.0], rowH: [0.45, 0.5, 0.75, 0.5], border: { pt: 1, color: LINE }, fill: { color: CARD }, valign: "middle" });

  card(s, 7.9, 1.95, 4.83, 2.2, CARD);
  s.addText("Configuracion", { x: 8.1, y: 2.05, w: 4.4, h: 0.3, fontFace: HF, fontSize: 14, bold: true, color: TEAL, margin: 0 });
  s.addText([
    { text: "KNNImputer(n_neighbors=5, weights=\"distance\")", options: { bullet: true, breakLine: true } },
    { text: "Estandarizacion previa para modelos sensibles a escala", options: { bullet: true, breakLine: true } },
    { text: "KNN vs. imputacion iterativa comparados por MAE simulado", options: { bullet: true, breakLine: true } },
    { text: "KNN obtuvo menor MAE en las 5 variables evaluadas", options: { bullet: true } },
  ], { x: 8.1, y: 2.4, w: 4.45, h: 1.7, fontFace: BF, fontSize: 12, color: TEXT, paraSpaceAfter: 6, margin: 0 });

  card(s, M, 4.4, 12.13, 1.1, DARK);
  s.addText([{ text: "Detalle metodologico   ", options: { bold: true, color: TEALL } }, { text: "La imputacion se ajusta dentro de cada fold: los datos de validacion nunca participan del calculo de medianas, vecinos, moda o escalado.", options: { color: "EAF2F4" } }],
    { x: M + 0.3, y: 4.4, w: 11.5, h: 1.1, valign: "middle", fontFace: BF, fontSize: 13, margin: 0 });
  msg(s, "Imputar antes de dividir o fuera del pipeline produciria leakage de preprocesamiento.");
}

// =====================================================================
// SLIDE 5 — EDA
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 4, "Analisis exploratorio para modelar", "Hallazgos que influyeron en decisiones tecnicas");
  // left findings
  const finds = [
    ["Tenure", "mayor diferencia entre clases"],
    ["Complain", "fuerte asociacion, temporalidad no confirmada"],
    ["DaySinceLastOrder", "relacion contraintuitiva, riesgo temporal"],
    ["CashbackAmount", "asociacion relevante"],
    ["Categoricas", "diferencias entre segmentos"],
  ];
  card(s, M, 1.78, 4.25, 3.85);
  finds.forEach((f, i) => {
    const y = 2.08 + i * 0.58;
    s.addShape(pres.shapes.OVAL, { x: M + 0.3, y: y + 0.08, w: 0.11, h: 0.11, fill: { color: i < 3 ? ACCENT : TEAL } });
    s.addText([{ text: f[0] + "  ", options: { bold: true, color: TEXT } }, { text: f[1], options: { color: MUTED, fontSize: 7.3 } }], { x: M + 0.58, y, w: 3.65, h: 0.22, valign: "middle", fontFace: BF, fontSize: 10.2, margin: 0 });
  });
  // methods chips
  s.addText("Metodos: Mann-Whitney U · Chi-cuadrado · Rank-biserial · Cramer's V", { x: M, y: 5.55, w: 5.5, h: 0.4, fontFace: BF, fontSize: 10.5, italic: true, color: TEAL, margin: 0 });
  // right figures
  fitImage(s, "h1_tenure.png", 5.1, 1.65, 7.65, 2.22);
  fitImage(s, "h2_complain.png", 5.1, 4.12, 7.65, 2.22);
  msg(s, "El EDA sirvio para formular variables y detectar riesgos metodologicos, no para seleccionar predictores por p-valor.");
}

// =====================================================================
// SLIDE 6 — SPLIT AGRUPADO
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 5, "Split agrupado", "StratifiedGroupKFold sin perfiles compartidos");
  card(s, M, 1.95, 6.0, 1.9, DARK);
  s.addText("StratifiedGroupKFold(\n    n_splits=5,\n    shuffle=True,\n    random_state=42\n)", { x: M + 0.3, y: 2.05, w: 5.5, h: 1.7, fontFace: "Consolas", fontSize: 14, color: "9FE4EA", valign: "middle", margin: 0 });
  card(s, M, 4.05, 6.0, 1.45);
  s.addText("Definicion del grupo", { x: M + 0.25, y: 4.13, w: 5.5, h: 0.3, fontFace: HF, fontSize: 13, bold: true, color: TEAL, margin: 0 });
  s.addText([
    { text: "Hash de todas las variables explicativas", options: { bullet: true, breakLine: true } },
    { text: "No incluye CustomerID ni Churn", options: { bullet: true } },
  ], { x: M + 0.25, y: 4.5, w: 5.5, h: 0.9, fontFace: BF, fontSize: 12.5, color: TEXT, paraSpaceAfter: 5, margin: 0 });

  s.addTable([
    thead(["Conjunto", "Filas", "Churn"]),
    trow(["Train", "4.514", "764"]),
    trow(["Test", "1.116", "184"]),
  ], { x: 7.0, y: 1.95, w: 5.73, colW: [2.4, 1.66, 1.67], rowH: 0.5, border: { pt: 1, color: LINE }, fill: { color: CARD }, valign: "middle" });
  // big 0 callout
  card(s, 7.0, 3.6, 5.73, 1.9, CARD);
  s.addText("0", { x: 7.0, y: 3.6, w: 5.73, h: 1.1, align: "center", fontFace: HF, fontSize: 60, bold: true, color: TEAL, margin: 0 });
  s.addText("perfiles compartidos entre train y test", { x: 7.0, y: 4.7, w: 5.73, h: 0.35, align: "center", fontFace: BF, fontSize: 13, bold: true, color: TEXT, margin: 0 });
  s.addText("El test no se usa para elegir modelo, features ni umbral", { x: 7.0, y: 5.02, w: 5.73, h: 0.35, align: "center", fontFace: BF, fontSize: 10.5, color: MUTED, margin: 0 });
  msg(s, "La estratificacion mantiene la clase; el agrupamiento evita evaluar sobre perfiles equivalentes a los entrenados.");
}

// =====================================================================
// SLIDE 7 — FEATURE ENGINEERING
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 6, "Feature engineering", "Tres variables de intensidad, deterministas");
  const feats = [
    ["OrdersPerTenure", "OrderCount / (Tenure + 1)"],
    ["CashbackPerOrder", "CashbackAmount / (OrderCount + 1)"],
    ["CouponsPerOrder", "CouponUsed / (OrderCount + 1)"],
  ];
  feats.forEach((f, i) => {
    const x = M + i * 4.07;
    card(s, x, 1.95, 3.82, 1.5, DARK);
    s.addText(f[0], { x: x + 0.25, y: 2.1, w: 3.4, h: 0.4, fontFace: HF, fontSize: 16, bold: true, color: TEALL, margin: 0 });
    s.addText(f[1], { x: x + 0.25, y: 2.6, w: 3.4, h: 0.7, fontFace: "Consolas", fontSize: 12, color: "EAF2F4", valign: "top", margin: 0 });
  });
  card(s, M, 3.7, 12.13, 1.75);
  s.addText("Justificacion tecnica", { x: M + 0.25, y: 3.8, w: 8, h: 0.32, fontFace: HF, fontSize: 14, bold: true, color: TEAL, margin: 0 });
  const just = [
    "Capturan intensidad, no solo magnitud absoluta", "El +1 evita divisiones por cero",
    "Transformaciones deterministas, no usan el target", "Se generan por separado en train y test",
    "Se incluyen antes del ColumnTransformer", "OrdersPerTenure conserva importancia en el modelo final",
  ];
  just.forEach((j, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    s.addText(j, { x: M + 0.3 + col * 6.0, y: 4.18 + row * 0.42, w: 5.8, h: 0.4, fontFace: BF, fontSize: 12, color: TEXT, bullet: { code: "2022", indent: 14 }, margin: 0 });
  });
  msg(s, "OrdersPerTenure conserva importancia en el modelo final segun permutacion y SHAP.");
}

// =====================================================================
// SLIDE 8 — PIPELINE PREPROCESAMIENTO
// =====================================================================
{
  const s = { addShape(){}, addText(){}, addTable(){}, addImage(){}, background: null };
  header(s, 8, "Pipeline de preprocesamiento", "Tres ramas integradas con ColumnTransformer");
  const branches = [
    ["Numericas KNN", ["KNNImputer", "StandardScaler (solo regresion)"]],
    ["Numericas mediana", ["SimpleImputer(median)", "StandardScaler (solo regresion)"]],
    ["Categoricas", ["SimpleImputer(most_frequent)", "OneHotEncoder(handle_unknown=ignore)"]],
  ];
  branches.forEach((b, i) => {
    const x = M + i * 4.07;
    card(s, x, 1.95, 3.82, 2.4, CARD);
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.95, w: 3.82, h: 0.5, fill: { color: TEAL } });
    s.addText(b[0], { x: x + 0.2, y: 1.95, w: 3.5, h: 0.5, valign: "middle", fontFace: HF, fontSize: 13.5, bold: true, color: "FFFFFF", margin: 0 });
    b[1].forEach((step, j) => {
      const y = 2.7 + j * 0.75;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.25, y, w: 3.3, h: 0.55, rectRadius: 0.06, fill: { color: LIGHT }, line: { color: LINE, width: 1 } });
      s.addText(step, { x: x + 0.35, y, w: 3.1, h: 0.55, valign: "middle", fontFace: "Consolas", fontSize: 10.5, color: TEXT, margin: 0 });
      if (j < b[1].length - 1) s.addText("↓", { x: x + 0.25, y: y + 0.52, w: 3.3, h: 0.22, align: "center", fontSize: 12, color: TEAL, margin: 0 });
    });
  });
  card(s, M, 4.6, 12.13, 0.9, DARK);
  s.addText([{ text: "Diferencias por modelo   ", options: { bold: true, color: TEALL } }, { text: "Regresion logistica: numericas escaladas. Arbol y Random Forest: sin escalado. Todos: imputacion y one-hot dentro del fold.", options: { color: "EAF2F4" } }],
    { x: M + 0.3, y: 4.6, w: 11.5, h: 0.9, valign: "middle", fontFace: BF, fontSize: 12.5, margin: 0 });
  msg(s, "El pipeline garantiza que cada fold aprenda sus propios parametros de transformacion.");
}

// =====================================================================
// SLIDE 9 — MODELOS E HIPERPARAMETROS
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 7, "Modelos e hiperparametros", "Del piso Dummy al ensamble Random Forest");
  const models = [
    ["Dummy", "strategy = most_frequent", TEAL],
    ["Regresion logistica", "class_weight = balanced\nmax_iter = 2000\nrandom_state = 42", TEAL],
    ["Arbol de decision", "class_weight = balanced\nmax_depth = 5\nmin_samples_leaf = 20", TEAL],
    ["Random Forest", "n_estimators = 476\nmax_depth = 16 · max_features = 0.5\nmax_samples = 0.7\nclass_weight = {0:1, 1:5}", ACCENT],
  ];
  models.forEach((m, i) => {
    const x = M + i * 3.07;
    card(s, x, 1.95, 2.85, 2.55, CARD);
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.95, w: 0.1, h: 2.55, fill: { color: m[2] } });
    s.addText(m[0], { x: x + 0.25, y: 2.05, w: 2.5, h: 0.6, fontFace: HF, fontSize: 14, bold: true, color: TEXT, valign: "middle", margin: 0 });
    s.addText(m[1], { x: x + 0.25, y: 2.65, w: 2.5, h: 1.75, fontFace: "Consolas", fontSize: 10, color: MUTED, valign: "top", margin: 0 });
  });
  card(s, M, 4.65, 12.13, 0.85, DARK);
  s.addText([{ text: "Ajuste   ", options: { bold: true, color: TEALL } }, { text: "Random Forest se ajusto con RandomizedSearchCV sobre los mismos folds agrupados optimizando F2 (de ahi valores como n_estimators=476).", options: { color: "EAF2F4" } }],
    { x: M + 0.3, y: 4.65, w: 11.5, h: 0.85, valign: "middle", fontFace: BF, fontSize: 12.5, margin: 0 });
  msg(s, "Dummy fija el piso; la regresion aporta interpretabilidad; el arbol capta no linealidad; Random Forest reduce varianza por ensamble.");
}

// =====================================================================
// SLIDE 10 — METRICAS
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 8, "Metricas de evaluacion", "F2 prioriza recall sobre precision");
  const f = [["Recall", "TP / (TP + FN)"], ["Precision", "TP / (TP + FP)"], ["F-beta (β=2)", "(1+β²)·P·R / (β²·P + R)"]];
  f.forEach((it, i) => {
    const y = 1.95 + i * 0.92;
    card(s, M, y, 6.0, 0.78, CARD);
    s.addText(it[0], { x: M + 0.25, y, w: 2.2, h: 0.78, valign: "middle", fontFace: HF, fontSize: 15, bold: true, color: TEAL, margin: 0 });
    s.addText(it[1], { x: M + 2.4, y, w: 3.5, h: 0.78, valign: "middle", fontFace: "Consolas", fontSize: 13, color: TEXT, margin: 0 });
  });
  s.addText("Con β=2, recall pesa 4× la precision dentro de la formula.", { x: M, y: 4.78, w: 6.0, h: 0.4, fontFace: BF, fontSize: 11.5, italic: true, color: ACCENT, margin: 0 });
  // confusion mini
  card(s, 7.0, 1.95, 5.73, 3.55, CARD);
  s.addText("Matriz de confusion", { x: 7.2, y: 2.05, w: 5.3, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: TEXT, margin: 0 });
  const cm = [[{ t: "TP", c: TEAL }, { t: "FN", c: ACCENT }], [{ t: "FP", c: ACCENT }, { t: "TN", c: "9FB3BB" }]];
  cm.forEach((rw, r) => rw.forEach((cell, c) => {
    const x = 7.7 + c * 2.4, y = 2.55 + r * 1.25;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.2, h: 1.1, fill: { color: cell.c } });
    s.addText(cell.t, { x, y, w: 2.2, h: 1.1, align: "center", valign: "middle", fontFace: HF, fontSize: 22, bold: true, color: "FFFFFF", margin: 0 });
  }));
  s.addText("Complementarias: F1 · PR-AUC · ROC-AUC · cantidad de alertas", { x: 7.2, y: 5.0, w: 5.4, h: 0.4, fontFace: BF, fontSize: 11, color: MUTED, margin: 0 });
  msg(s, "PR-AUC es especialmente informativa con 16,8% de positivos; ROC-AUC se reporta como capacidad global de ranking.");
}

// =====================================================================
// SLIDE 11 — SENSIBILIDAD TEMPORAL
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 9, "Sensibilidad temporal", "Random Forest con y sin variables de riesgo");
  s.addTable([
    thead(["Escenario", "F2", "Recall", "Precision", "PR-AUC", "ROC-AUC"]),
    trow(["Completo", "0,754", "0,753", "0,760", "0,831", "0,957"]),
    trow(["Sin Complain", "0,700", "0,698", "0,711", "0,787", "0,944"]),
    trow(["Sin DaySinceLastOrder", "0,742", "0,738", "0,758", "0,816", "0,953"]),
    trow(["Sin ambas (final)", "0,674", "0,670", "0,689", "0,776", "0,938"], { 0: { bold: true, color: ACCENT } }),
  ], { x: M, y: 2.0, w: 6.0, colW: [1.95, 0.82, 0.82, 0.92, 0.78, 0.71], rowH: 0.52, border: { pt: 1, color: LINE }, fill: { color: CARD }, valign: "middle", fontSize: 11 });

  fitImage(s, "temporal_sensitivity_f2.png", 6.95, 1.9, 5.78, 3.6);

  card(s, M, 4.75, 6.0, 1.0, DARK);
  s.addText([{ text: "Decision   ", options: { bold: true, color: ACCENT } }, { text: "Excluir Complain y DaySinceLastOrder por temporalidad no garantizada. Medido sobre RF por ser el modelo mas reactivo a ambas.", options: { color: "EAF2F4" } }],
    { x: M + 0.3, y: 4.75, w: 5.55, h: 1.0, valign: "middle", fontFace: BF, fontSize: 11.5, margin: 0 });
  msg(s, "Se acepta una caida de performance para evitar leakage temporal y mantener validez en produccion.");
}

// =====================================================================
// SLIDE 12 — COMPARACION DE MODELOS
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 10, "Comparacion de modelos", "Fuera de fold, umbral 0,50, escenario conservador");
  s.addTable([
    thead(["Modelo", "F2", "Recall", "Precision", "PR-AUC", "ROC-AUC"]),
    trow(["Dummy", "0,000", "0,000", "0,000", "0,169", "0,500"], { 0: { color: MUTED } }),
    trow(["Regresion logistica", "0,689", "0,802", "0,441", "0,636", "0,873"], { 0: { bold: true, color: TEAL }, 1: { bold: true, color: TEAL }, 2: { bold: true, color: TEAL } }),
    trow(["Arbol de decision", "0,658", "0,775", "0,411", "0,569", "0,854"]),
    trow(["Random Forest", "0,674", "0,670", "0,689", "0,776", "0,938"], { 3: { bold: true }, 4: { bold: true }, 5: { bold: true } }),
  ], { x: M, y: 2.0, w: 6.0, colW: [1.95, 0.82, 0.82, 0.92, 0.78, 0.71], rowH: 0.52, border: { pt: 1, color: LINE }, fill: { color: CARD }, valign: "middle", fontSize: 11 });

  fitImage(s, "final_model_comparison_cv.png", 6.95, 1.9, 5.78, 3.6);

  card(s, M, 4.75, 6.0, 1.0, CARD);
  s.addText([
    { text: "Seleccion   ", options: { bold: true, color: TEAL } },
    { text: "Regresion logistica balanceada. Criterio primario F2, secundario recall. RF gana en precision y ranking, pero detecta menos churns.", options: { color: TEXT } },
  ], { x: M + 0.3, y: 4.75, w: 5.55, h: 1.0, valign: "middle", fontFace: BF, fontSize: 11.5, margin: 0 });
  msg(s, "La seleccion responde al criterio definido antes de observar el conjunto de test.");
}

// =====================================================================
// SLIDE 13 — UMBRAL Y TEST FINAL
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 11, "Ajuste de umbral y test final", "Umbral elegido OOF, congelado antes de test");
  // threshold table
  s.addText("Ajuste fuera de fold", { x: M, y: 1.85, w: 5, h: 0.3, fontFace: HF, fontSize: 13, bold: true, color: TEAL, margin: 0 });
  s.addTable([
    thead(["Umbral", "F2", "Recall", "Precision", "Contactos"]),
    trow(["0,41 (final)", "0,696", "0,861", "0,394", "1.668"], { 0: { bold: true, color: ACCENT } }),
    trow(["0,50", "0,689", "0,802", "0,441", "1.391"]),
  ], { x: M, y: 2.2, w: 5.9, colW: [1.7, 0.95, 1.05, 1.2, 1.0], rowH: 0.48, border: { pt: 1, color: LINE }, fill: { color: CARD }, valign: "middle", fontSize: 11 });

  // test results table
  s.addText("Resultado final en test", { x: M, y: 3.65, w: 5, h: 0.3, fontFace: HF, fontSize: 13, bold: true, color: TEAL, margin: 0 });
  s.addTable([
    thead(["Metrica", "Valor", "Metrica", "Valor"]),
    trow(["F2", "0,665", "PR-AUC", "0,577"], { 1: { bold: true, color: TEAL } }),
    trow(["Recall", "0,837", "ROC-AUC", "0,857"], { 1: { bold: true, color: TEAL } }),
    trow(["Precision", "0,365", "Accuracy", "0,733"]),
    trow(["F1", "0,508", "", ""]),
  ], { x: M, y: 4.0, w: 5.9, colW: [1.7, 1.25, 1.7, 1.25], rowH: 0.42, border: { pt: 1, color: LINE }, fill: { color: CARD }, valign: "middle", fontSize: 11 });

  // confusion image + callout
  s.addImage({ path: FIG("final_test_confusion_matrix.png"), x: 7.1, y: 1.85, w: 3.4, sizing: { type: "contain", w: 3.4, h: 3.0 } });
  card(s, 10.6, 1.95, 2.13, 3.0, DARK);
  s.addText("83,7%", { x: 10.6, y: 2.4, w: 2.13, h: 0.8, align: "center", fontFace: HF, fontSize: 30, bold: true, color: ACCENT, margin: 0 });
  s.addText("recall en test", { x: 10.6, y: 3.15, w: 2.13, h: 0.35, align: "center", fontFace: BF, fontSize: 12, color: "DFEDF0", margin: 0 });
  s.addText("154 TP · 30 FN\n268 FP · 664 TN", { x: 10.6, y: 3.6, w: 2.13, h: 1.0, align: "center", fontFace: BF, fontSize: 12, color: "9FE4EA", margin: 0 });
  msg(s, "La diferencia entre validacion y test no cambia la seleccion: el modelo mantiene recall superior al 80%.");
}

// =====================================================================
// SLIDE 14 — INTERPRETABILIDAD
// =====================================================================
{
  const s = pres.addSlide();
  header(s, 12, "Interpretabilidad y limitaciones", "Drivers consistentes, sin lectura causal");
  s.addImage({ path: FIG("final_feature_importance.png"), x: M, y: 1.9, w: 4.0, sizing: { type: "contain", w: 4.0, h: 2.5 } });
  s.addImage({ path: FIG("final_shap_global.png"), x: 4.8, y: 1.9, w: 4.0, sizing: { type: "contain", w: 4.0, h: 2.5 } });
  // top vars + limitations
  card(s, 9.0, 1.9, 3.73, 2.5, CARD);
  s.addText("Top variables", { x: 9.2, y: 2.0, w: 3.4, h: 0.3, fontFace: HF, fontSize: 13, bold: true, color: TEAL, margin: 0 });
  s.addText([
    { text: "Tenure", options: { bullet: { type: "number" }, breakLine: true } },
    { text: "CashbackAmount", options: { bullet: { type: "number" }, breakLine: true } },
    { text: "PreferedOrderCat", options: { bullet: { type: "number" }, breakLine: true } },
    { text: "OrdersPerTenure", options: { bullet: { type: "number" }, breakLine: true } },
    { text: "SatisfactionScore", options: { bullet: { type: "number" } } },
  ], { x: 9.25, y: 2.35, w: 3.4, h: 1.95, fontFace: BF, fontSize: 12.5, color: TEXT, paraSpaceAfter: 4, margin: 0 });

  card(s, M, 4.55, 12.13, 1.0);
  s.addText("Limitaciones tecnicas", { x: M + 0.25, y: 4.62, w: 6, h: 0.3, fontFace: HF, fontSize: 13, bold: true, color: ACCENT, margin: 0 });
  const lims = ["Dataset observacional", "Temporalidad incompleta", "Perfiles duplicados en la fuente", "Precision final 36,5%", "Requiere monitoreo ante drift", "SHAP/importancia ≠ causalidad"];
  lims.forEach((l, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    s.addText(l, { x: M + 0.3 + col * 4.0, y: 4.95 + row * 0.32, w: 3.9, h: 0.3, fontFace: BF, fontSize: 11, color: TEXT, bullet: { code: "2022", indent: 12 }, margin: 0 });
  });
  s.addShape(pres.shapes.RECTANGLE, { x: M - 0.02, y: 1.55, w: 12.17, h: 5.2, fill: { color: LIGHT }, line: { color: LIGHT } });
  fitImage(s, "final_interpretability_combo.png", M, 1.65, 8.25, 4.85);

  card(s, 9.15, 1.75, 3.58, 2.05, CARD);
  s.addText("Lectura tecnica", { x: 9.38, y: 1.92, w: 3.1, h: 0.3, fontFace: HF, fontSize: 13.5, bold: true, color: TEAL, margin: 0 });
  const reads = [
    "Tenure aparece en ambos metodos.",
    "Cashback y categoria preferida sostienen poder explicativo.",
    "OrdersPerTenure valida el feature engineering.",
  ];
  reads.forEach((t, i) => {
    s.addText(t, { x: 9.43, y: 2.35 + i * 0.43, w: 3.0, h: 0.34, fontFace: BF, fontSize: 11.2, color: TEXT, bullet: { code: "2022", indent: 12 }, margin: 0 });
  });

  card(s, 9.15, 4.05, 3.58, 2.1, CARD);
  s.addText("Limites", { x: 9.38, y: 4.22, w: 3.1, h: 0.3, fontFace: HF, fontSize: 13.5, bold: true, color: ACCENT, margin: 0 });
  const cleanLims = ["Dataset observacional", "Temporalidad incompleta", "Precision final 36,5%", "Importancia no implica causalidad"];
  cleanLims.forEach((l, i) => {
    s.addText(l, { x: 9.43, y: 4.65 + i * 0.34, w: 3.0, h: 0.3, fontFace: BF, fontSize: 10.8, color: TEXT, bullet: { code: "2022", indent: 12 }, margin: 0 });
  });
  msg(s, "El modelo final es reproducible y conservador, pero debe monitorearse y recalibrarse en produccion.", H - 1.0);
}

// =====================================================================
// SLIDE 15 — CONCLUSION
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: DARK };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: TEAL } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.22, y: 0, w: 0.08, h: H, fill: { color: ACCENT } });
  s.addText("CONCLUSION", { x: 1.0, y: 0.6, w: 10, h: 0.4, fontFace: HF, fontSize: 14, bold: true, color: TEALL, charSpacing: 4, margin: 0 });
  s.addText("Decisiones tecnicas clave", { x: 1.0, y: 1.0, w: 11, h: 0.7, fontFace: HF, fontSize: 32, bold: true, color: "FFFFFF", margin: 0 });
  const dec = [
    ["Split por grupos", "Neutraliza los 556 perfiles duplicados y evita fuga train/test."],
    ["Todo dentro del fold", "Imputacion y preprocesamiento aprenden solo del train de cada fold."],
    ["Exclusion conservadora", "Complain y DaySinceLastOrder fuera por temporalidad no garantizada."],
    ["Decision antes de test", "Modelo y umbral 0,41 fijados con F2 y recall como prioridad."],
  ];
  dec.forEach((d, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 1.0 + col * 6.0, y = 2.0 + row * 1.15;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 5.6, h: 1.0, fill: { color: DARK2 }, line: { color: "1E4658", width: 1 } });
    s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: y + 0.28, w: 0.45, h: 0.45, fill: { color: TEAL } });
    s.addText(String(i + 1), { x: x + 0.2, y: y + 0.28, w: 0.45, h: 0.45, align: "center", valign: "middle", fontFace: HF, fontSize: 15, bold: true, color: "FFFFFF", margin: 0 });
    s.addText(d[0], { x: x + 0.85, y: y + 0.12, w: 4.6, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: "FFFFFF", margin: 0 });
    s.addText(d[1], { x: x + 0.85, y: y + 0.45, w: 4.6, h: 0.5, fontFace: BF, fontSize: 11, color: "C7D7DD", margin: 0 });
  });
  // result callout
  s.addShape(pres.shapes.RECTANGLE, { x: 1.0, y: 4.5, w: 11.33, h: 1.35, fill: { color: TEAL } });
  s.addText([
    { text: "Resultado final   ", options: { bold: true, color: "C9F2F5", fontSize: 13 } },
    { text: "Regresion logistica balanceada, umbral 0,41: ", options: { color: "FFFFFF", fontSize: 15 } },
    { text: "detecta el 83,7% de los churns (recall) con F2 = 0,665 en test, sosteniendo lo visto en validacion.", options: { bold: true, color: "FFFFFF", fontSize: 15 } },
  ], { x: 1.4, y: 4.5, w: 10.5, h: 1.35, valign: "middle", fontFace: BF, margin: 0 });
  s.addText("Pipeline reproducible y honesto sobre sus limitaciones: prioriza no perder clientes en riesgo y deja la calibracion economica a la presentacion de negocios.",
    { x: 1.0, y: 6.1, w: 11.33, h: 0.7, fontFace: BF, fontSize: 13, italic: true, color: "9FB8C0", margin: 0 });
}

pres.writeFile({ fileName: "presentacion_tecnica_churn.pptx" }).then(f => console.log("WROTE", f));
