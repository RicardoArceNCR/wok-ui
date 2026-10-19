# @wok/ui

Tokens de WOK (restaurante cantonés). La fuente que se edita es el Figma de WOK; `source/raw/` es su export de variables (plugin Export/Import Variables de Jan Toman). El CSS de `build/` se genera y se versiona para que el sitio no corra Python ni Style Dictionary.

```bash
npm ci
npm run verify                       # figma-to-sd + Style Dictionary + chequeos
npm run sistema                      # regenera sistema/sistema.html
```

> **Hoy `source/raw/` es una semilla, no un export.** El Figma de WOK todavía no existe: `herramientas/semilla-figma.py` generó `source/raw/` desde la propuesta de color aprobada (`herramientas/semilla/`). Es de una sola vez: se importa en Figma y desde ahí manda Figma (ADR 0001). El script se niega a pisar `source/raw/` sin `--forzar`.

## En el sitio

El sitio fija un tag, nunca una rama:

```json
"@wok/ui": "github:RicardoArceNCR/wok-ui#v0.1.0"
```

El repo es **público**: los tokens ya viajan en el CSS público del sitio, así que se instala por HTTPS sin token. Si pnpm intenta clonar por SSH (en Vercel y CI falla sin llave), reescribí SSH→HTTPS antes del install: `git config --global url."https://github.com/".insteadOf "git@github.com:"`.

El paquete no tiene script `prepare`: instalarlo es bajar `build/` tal cual.

Un solo grafo de `@import`, todo dentro de `globals.css`:

```css
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

@import "@wok/ui/tokens.css";       /* :root, claro         */
@import "@wok/ui/tokens-dark.css";  /* .dark                */
@import "@wok/ui/theme-bridge.css"; /* Tailwind v4 + shadcn */
```

El oscuro va por la clase `.dark`, no por `prefers-color-scheme`. El sitio no redefine la paleta: si falta un color, se agrega como semántico en Figma y sale en una versión nueva.

### Variables que usa el sitio

| Para | Variable |
|---|---|
| Fondo de página | `--background-page` (marfil en claro, bosque en oscuro) |
| Texto | `--text-primary`, `--text-secondary`, `--text-tertiary` |
| Acción (botón primario, `bg-primary`) | `--brand-action` (+ `-hover`, `-press`) con `--text-on-brand` |
| Superficie de marca | `--surface-ink` (bosque en los dos temas) con `--text-on-ink`; franja lima `--surface-support` con `--text-on-support` |
| Naranja de manual | `--brand-accent` y `--surface-highlight-bg`: solo display ≥24px o ilustración |
| Fuentes | `--brand-font-display`, `--brand-font-body`, `--brand-font-mono` (Tailwind: `font-display`, `font-sans`, `font-mono`) |

### Fuentes

Las fuentes **no** están en este paquete: las sirve el sitio con `next/font/local`. Los tokens `--brand-font-*` son pilas CSS que empiezan por las variables de `next/font`:

```css
--brand-font-display: var(--font-display, "Gang of Three", "WokDisplayFallback", Arial, Helvetica, sans-serif);
--brand-font-body: var(--font-body, Lato, system-ui, …, sans-serif);
--brand-font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
```

El contrato es el nombre de la variable: el sitio carga `next/font` con `variable: "--font-display"` (Gang of Three) y `variable: "--font-body"` (Lato, renombrada "WOK Sans" por la OFL), puestas en `<html>`. Gang of Three es provisoria y su licencia está pendiente (ADR 0001).

## Qué publica

`exports`: `tokens.css`, `tokens-dark.css`, `theme-bridge.css`, `tokens.js` y `build/*` (incluye `theme-bridge-typography.generated.css`). `files` deja afuera `source/`, el pipeline, la semilla y los chequeos: al sitio le llegan `build/`, este README y `package.json`.

Rampas (`color/<familia>/<stop>`, 50–950): `neutral`, `paper` (marfil), `brand` (bosque), `accent` (naranja), `support` (lima), `success`, `info`, `warning`, `danger`, más `white` y `black`.

`build/` no se edita a mano. El único archivo del bridge que se toca es `theme-bridge.template.css`.

## Controles

`npm test`, dentro de `verify`:

- `check-units`: ningún token sale con un número pelado ni queda pelado en oscuro.
- `check-ramps`: monotonía, matiz, croma y `neutral` acromático.
- `check-contrast`: los pares de `scripts/contrast-pairs.json`, WCAG 2 en claro y oscuro.

Cada chequeo tiene una lista `ALLOW`, la única vía para que algo en falla pase, con motivo escrito. En rampas y contraste arranca vacía.

CI (`.github/workflows/verify.yml`): `npm run verify`, `build/` y `source/*.json` al día con `source/raw`, y tag igual a la versión. Decisiones en `docs/decisions/`, estado frente al estándar en `docs/checklist-n1.md`, cambios por versión en `CHANGELOG.md`.

## Publicar una versión

1. Exportá desde Figma las colecciones que cambiaron a `source/raw/`.
2. `npm run verify` y `npm run sistema`.
3. Anotá el cambio en `CHANGELOG.md` y subí `version` en `package.json`.
4. Commit, `git tag -a vX.Y.Z`, push con tags. CI valida que el tag coincida.
5. En el sitio, subí el pin de `@wok/ui` a ese tag.
