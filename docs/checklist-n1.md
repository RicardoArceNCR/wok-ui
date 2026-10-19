# Checklist Paquete N1 — @wok/ui v0.1.0

Las 15 fichas de Paquete N1 del estándar del estudio, revisadas el
2026-10-18 sobre el tag local `v0.1.0`, antes del primer push.
`sin-datos-de-otro-cliente` va al final, como pide el runbook.

| Ficha | Estado | Evidencia o lo que falta |
|---|---|---|
| `ci-verify` | ⏳ después del push | `.github/workflows/verify.yml` idéntico al de referencia (PR, push a `main`, tags `v*`, `npm ci`, Node de `.nvmrc`, Python 3.12, `npm run verify`). Corre recién cuando el repo exista en GitHub. |
| `build-al-dia-en-ci` | ✅ local · ⏳ CI | Paso `git diff --quiet -- build source` en el workflow. En local, `npm run verify` sobre el árbol commiteado deja `build/` y `source/` sin cambios. |
| `tag-igual-version` | ✅ local · ⏳ CI | Tag anotado `v0.1.0` y `"version": "0.1.0"`. El paso "Tag igual a la versión" corre cuando se suba el tag. |
| `check-unidades` | ✅ | `scripts/check-units.mjs` tal cual (md5 `c860aeff`), en `npm test`. Sin valores pelados, claro y oscuro en paridad. |
| `check-rampas` | ✅ | `scripts/check-ramps.mjs` con `ALLOW` vacía: las 9 familias pasan las cuatro reglas. |
| `check-contraste` | ✅ | `scripts/check-contrast.mjs` + `scripts/contrast-pairs.json`: 57 pares, 114 mediciones, 0 en `ALLOW`. Que el contraste bloquea el build está en el ADR 0001. |
| `changelog-semver` | ✅ | `CHANGELOG.md` con la cabecera de reglas semver, `[Sin publicar]` y `[0.1.0]`. |
| `nvmrc-y-engines` | ✅ | `.nvmrc` = 22, `engines.node` = `>=22`, CI con `node-version-file`. npm con `package-lock.json`, sin pnpm. |
| `lamina-sistema` | ✅ | `npm run sistema` → `sistema/sistema.html` (110 pares mostrados, 0 fallas), versionada. |
| `adrs-paquete` | ✅ | `docs/decisions/0001-paquete-propio-de-wok.md`. |
| `sin-prepare` | ✅ | `scripts`: `tokens`, `build`, `test`, `verify`, `sistema`. Ningún script de ciclo de vida. |
| `files-limita-publicacion` | ✅ | `files: ["build", "README.md"]`; `npm pack --dry-run` lista solo `build/`, README y `package.json`. `exports` suma `./tokens.js`. |
| `gitignore-pycache` | ✅ | `.gitignore` con `__pycache__/`, `node_modules` y los archivos de pnpm; `git ls-files` no lista nada de eso. |
| `repo-publico` | ⏳ después del push | Crear `RicardoArceNCR/wok-ui` **público**. `private: true` y `UNLICENSED` se quedan (impiden un `npm publish`, no la lectura). El README ya dice que se instala sin token. La historia no trae datos de otro cliente. |
| `sin-datos-de-otro-cliente` | ✅ | Ver abajo. |

## `sin-datos-de-otro-cliente`

Grep del runbook (más `topic`) sobre todo el repo, sin `node_modules`,
`.git` ni el lockfile:

```bash
grep -rn -i "contracorriente\|hablemos\|divergentes\|vper\|bluezone\|misitio\|topic" . \
  --exclude-dir=node_modules --exclude-dir=.git --exclude=package-lock.json
```

Lo que aparece son citas deliberadas de origen:

- `CHANGELOG.md` y el ADR 0001: de qué paquete salió la estructura.
- Este archivo: el comando de arriba.
- `herramientas/semilla/semanticos.json` (`_doc`): copia sin tocar de la
  propuesta de color, que dice que los nombres de semánticos siguen la
  convención de ese paquete. Se deja igual para que la copia sea verificable
  contra el original.

`build/`, `source/`, `scripts/` y `sistema/` no tienen ningún nombre de otro
cliente. Revisados a ojo los nombres de familias y semánticos de
`build/tokens.css`: son de WOK (`paper`, `brand`, `accent`, `support`,
`surface/ink`, `surface/support`; sin `topic`, sin colores con nombre de
medio, sin familia editorial).

## Fuera de N1 (objetivo)

- `allow-fuera-del-codigo`: las `ALLOW` siguen dentro de los scripts, como
  en el resto de los paquetes, hasta que exista el kit.
- `kit-tokens-al-dia`: no aplica todavía; no hay `kits/tokens-pipeline`.
