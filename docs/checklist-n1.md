# Checklist Paquete N1 — @wok/ui v0.1.0

Las 15 fichas de Paquete N1 del estándar del estudio, revisadas el
2026-10-18 sobre el tag local `v0.1.0`, antes del primer push.
`sin-datos-de-otro-cliente` va al final, como pide el runbook.

| Ficha | Estado | Evidencia o lo que falta |
|---|---|---|
| `ci-verify` | ⏳ después del push | `.github/workflows/verify.yml` idéntico al de referencia (PR, push a `main`, tags `v*`, `npm ci`, Node de `.nvmrc`, Python 3.12, `npm run verify`). Corre recién cuando el repo exista en GitHub. |
| `build-al-dia-en-ci` | ✅ local · ⏳ CI | Paso `git diff --quiet -- build source` en el workflow. En local, `npm ci && npm run verify` sobre el árbol commiteado deja `build/` y `source/` sin cambios. |
| `tag-igual-version` | ✅ local · ⏳ CI | Tag anotado `v0.1.0` y `"version": "0.1.0"`. El paso "Tag igual a la versión" corre cuando se suba el tag. |
| `check-unidades` | ✅ | `scripts/check-units.mjs` en `npm test`. Se sacaron dos excepciones que no aplican a WOK (breakpoints, que ahora salen con `px`, y una escala tipográfica que este paquete no tiene); quedan z-index, opacity, pesos y leading. |
| `check-rampas` | ✅ | `scripts/check-ramps.mjs` con `ALLOW` vacía: las 9 familias pasan las cuatro reglas. |
| `check-contraste` | ✅ | `scripts/check-contrast.mjs` + `scripts/contrast-pairs.json`: 76 pares, 152 mediciones, ninguno informativo (mínimo 0). 1 en `ALLOW` con motivo (contorno del botón primario sobre `surface/base` en oscuro). Que el contraste bloquea el build está en el ADR 0001. |
| `changelog-semver` | ✅ | `CHANGELOG.md` con la cabecera de reglas semver, `[Sin publicar]` y `[0.1.0]`. |
| `nvmrc-y-engines` | ✅ | `.nvmrc` = 22, `engines.node` = `>=22`, CI con `node-version-file`. npm con `package-lock.json`, sin pnpm. |
| `lamina-sistema` | ✅ | `npm run sistema` → `sistema/sistema.html` (152 mediciones, 1 en ALLOW, 0 fallas), versionada y al día con `build/`. |
| `adrs-paquete` | ✅ | `docs/decisions/0001-paquete-propio-de-wok.md`. |
| `sin-prepare` | ✅ | `scripts`: `tokens`, `build`, `test`, `verify`, `sistema`. Ningún script de ciclo de vida. |
| `files-limita-publicacion` | ✅ | `files: ["build", "README.md"]`; `npm pack --dry-run` lista solo `build/`, README y `package.json`. `exports` suma `./tokens.js`. |
| `gitignore-pycache` | ✅ | `.gitignore` con `__pycache__/`, `node_modules` y los archivos de pnpm; `git ls-files` no lista nada de eso. |
| `repo-publico` | ⏳ después del push | Crear `RicardoArceNCR/wok-ui` **público**. `private: true` y `UNLICENSED` se quedan (impiden un `npm publish`, no la lectura). El README ya dice que se instala sin token. |
| `sin-datos-de-otro-cliente` | ✅ | Ver abajo. |

## `sin-datos-de-otro-cliente`

Se corrió el grep de "Antes del primer deploy" del runbook "cliente nuevo"
(los nombres de los otros clientes del estudio y el prefijo de temas de un medio) sobre todo el
repo, sin `node_modules`, `.git` ni el lockfile. Solo aparecen
`CHANGELOG.md` y el ADR 0001, que dicen de qué paquete salió la estructura:
son las dos citas de origen que permite la ficha.

`build/`, `source/`, `scripts/`, `herramientas/` y `sistema/` no nombran a
otro cliente. Revisados a ojo los nombres de familias y semánticos de
`build/tokens.css`: son de WOK (`paper`, `brand`, `accent`, `support`,
`surface/ink`, `surface/support`, `focus/ring-on-*`), sin tokens de temas
de un medio ni familias de otra marca. La copia de la propuesta en
`herramientas/semilla/semanticos.json` perdió su nota de origen y el mapeo
de renombres, que nombraban otra paleta.

## Fuera de N1 (objetivo)

- `allow-fuera-del-codigo`: las `ALLOW` siguen dentro de los scripts, como
  en el resto de los paquetes, hasta que exista el kit.
- `kit-tokens-al-dia`: no aplica todavía; no hay `kits/tokens-pipeline`.
