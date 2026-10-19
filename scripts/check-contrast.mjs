#!/usr/bin/env node
/**
 * Contraste WCAG 2 de los pares semánticos, sobre el CSS ya compilado.
 * Mismo criterio que check-ramps: se valida la salida, no la fuente. Un
 * hex nuevo en Figma que rompa AA no llega a un tag.
 *
 * Lee build/tokens.css (:root) y build/tokens-dark.css (.dark, que se
 * superpone a :root), resuelve las cadenas var() y mide cada par de
 * scripts/contrast-pairs.json en los dos temas.
 *
 * ALLOW: única vía para que un par en falla pase. Cada entrada con motivo.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const { pairs } = JSON.parse(readFileSync(path.join(root, "scripts/contrast-pairs.json"), "utf8"));

// Única vía para que un par en falla pase: motivo escrito y el ratio medido
// en un comentario. Se borra la línea cuando el arreglo llega desde Figma.
// contrast-pairs.json no tiene pares con mínimo 0: todo par se mide y, si
// falla, está acá a la vista (y se cuenta en cada corrida).
const ALLOW = [
  {
    theme: "oscuro", fg: "brand-action", bg: "surface-base",
    why: "Contorno del botón primario sobre una superficie bosque-800. WCAG 1.4.11 no exige el contorno cuando la etiqueta identifica el control (blanco sobre accent-600, 4.56:1), y la acción es el mismo naranja en los dos temas. Sobre la página oscura da 3.04 y pasa.",
  }, // 2.39:1, mínimo 3
];

function decls(file) {
  const css = readFileSync(path.join(root, file), "utf8");
  const map = new Map();
  for (const [, name, value] of css.matchAll(/--([a-z0-9-]+)\s*:\s*([^;]+);/g)) map.set(name, value.trim());
  return map;
}

const light = decls("build/tokens.css");
const dark = new Map([...light, ...decls("build/tokens-dark.css")]);

function resolve(map, name, depth = 0) {
  const v = map.get(name);
  if (v == null || depth > 20) return null;
  const ref = v.match(/^var\(--([a-z0-9-]+)\)$/);
  return ref ? resolve(map, ref[1], depth + 1) : v;
}

function rgb(value) {
  if (!value) return null;
  const hex = value.match(/^#([0-9a-f]{6})$/i);
  if (hex) return [0, 2, 4].map((i) => parseInt(hex[1].slice(i, i + 2), 16));
  const m = value.match(/^rgba?\(\s*(\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)$/);
  if (m && (m[4] === undefined || Number(m[4]) === 1)) return [m[1], m[2], m[3]].map(Number);
  return null; // con alfa: depende del fondo, fuera de alcance
}

const lin = (c) => ((c /= 255) <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const lum = ([r, g, b]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
const ratio = (a, b) => {
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};

const errors = [];
let measured = 0;
let allowed = 0;
for (const [theme, map] of [
  ["claro", light],
  ["oscuro", dark],
]) {
  for (const [fg, bg, min, use] of pairs) {
    const a = rgb(resolve(map, fg));
    const b = rgb(resolve(map, bg));
    if (!a || !b) {
      errors.push(`${theme}: --${fg} sobre --${bg}: no se pudo resolver (¿token renombrado?)`);
      continue;
    }
    measured++;
    const r = ratio(a, b);
    if (min > 0 && r < min) {
      if (ALLOW.some((x) => x.theme === theme && x.fg === fg && x.bg === bg)) {
        allowed++;
        continue;
      }
      errors.push(`${theme}: --${fg} sobre --${bg} = ${r.toFixed(2)}:1, mínimo ${min} (${use})`);
    }
  }
}

if (errors.length) {
  console.error(`\ncheck-contrast: ${errors.length} problema(s)\n`);
  for (const e of errors) console.error("  - " + e);
  console.error("\nSe arregla en Figma (stop o alias), no acá. Si es intencional, ALLOW con motivo.\n");
  process.exit(1);
}
console.log(`check-contrast: OK — ${measured} pares en claro y oscuro, ${allowed} en ALLOW`);
