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
| Naranja de manual #FF5100 | `--brand-accent`: ilustración y display (≥24px) **sobre bosque** (`--surface-ink`, 4,24:1). Nunca texto sobre marfil (2,85:1): ahí los titulares van en `--brand-action` (≥24px, 3,98:1) o `--text-brand` (cualquier tamaño). `--surface-highlight-bg` es el naranja como fondo, con `--surface-highlight-text` bosque (5,06:1). |
| Foco | Un anillo por superficie, todos ≥3:1: `--focus-ring-color` (página y superficies del tema), `--focus-ring-on-ink` (`--surface-ink`, navegación, `--surface-accent-bg`), `--focus-ring-on-support`, `--focus-ring-on-inverse` (tooltip y `--surface-inverse`), `--focus-ring-on-highlight`. `--ring` de shadcn es `--focus-ring-color`. |
| Fuentes | Tailwind `font-display`, `font-sans`, `font-mono` (ver abajo) |

Dentro de un contenedor con `--surface-ink` (o la navegación), el sitio redefine el anillo localmente: `--ring: var(--focus-ring-on-ink)` o `outline-color: var(--focus-ring-on-ink)`. Lo mismo con las otras superficies.

### Fuentes

Las fuentes **no** están en este paquete: las sirve el sitio con `next/font/local`. Los tokens `--brand-font-display` (`Gang of Three`) y `--brand-font-body` (`Lato`) son **nombres de familia**, los mismos que usa Figma; `--brand-font-mono` es la pila mono del sistema (WOK no tiene mono de marca).

El sitio tiene que definir en `<html>` estas variables con el `variable` de `next/font`:

| Variable del sitio | Fuente |
|---|---|
| `--font-wok-display` | Gang of Three (`variable: "--font-wok-display"`) |
| `--font-wok-body` | Lato servida como "WOK Sans" (`variable: "--font-wok-body"`) |
| `--font-wok-mono` | opcional; sin ella, la mono del sistema |

y, si quiere el respaldo con métricas ajustadas del display, el `@font-face` `WokDisplayFallback`. El bridge arma la pila:

```css
--font-display: var(--font-wok-display, var(--brand-font-display), "WokDisplayFallback", Arial, Helvetica, sans-serif);
--font-sans: var(--font-wok-body, var(--brand-font-body), system-ui, …, sans-serif);
--font-mono: var(--font-wok-mono, var(--brand-font-mono));
```

Si falta una variable del sitio, cae al nombre del token y después al respaldo: nunca queda vacía. Gang of Three es provisoria y su licencia está pendiente (ADR 0001).

## Qué publica

`exports`: `tokens.css`, `tokens-dark.css`, `theme-bridge.css`, `tokens.js` y `build/*` (incluye `theme-bridge-typography.generated.css`). `files` deja afuera `source/`, el pipeline, la semilla y los chequeos: al sitio le llegan `build/`, este README y `package.json`.

Rampas (`color/<familia>/<stop>`, 50–950): `neutral`, `paper` (marfil), `brand` (bosque), `accent` (naranja), `support` (lima), `success`, `info`, `warning`, `danger`, más `white` y `black`.

`build/` no se edita a mano. El único archivo del bridge que se toca es `theme-bridge.template.css`.

## Controles

`npm test`, dentro de `verify`:

- `check-units`: ningún token sale con un número pelado ni queda pelado en oscuro.
- `check-ramps`: monotonía, matiz, croma y `neutral` acromático.
- `check-contrast`: los pares de `scripts/contrast-pairs.json`, WCAG 2 en claro y oscuro.

Cada chequeo tiene una lista `ALLOW`, la única vía para que algo en falla pase, con motivo escrito. Rampas: vacía. Contraste: una entrada (el contorno del botón primario sobre `--surface-base` en oscuro, 2,39:1; la etiqueta identifica el botón). No hay pares informativos: todo par se mide y lo que falla se cuenta.

CI (`.github/workflows/verify.yml`): `npm run verify`, `build/` y `source/*.json` al día con `source/raw`, y tag igual a la versión. Decisiones en `docs/decisions/`, estado frente al estándar en `docs/checklist-n1.md`, cambios por versión en `CHANGELOG.md`.

## Publicar una versión

1. Exportá desde Figma las colecciones que cambiaron a `source/raw/`.
2. `npm run verify` y `npm run sistema`.
3. Anotá el cambio en `CHANGELOG.md` y subí `version` en `package.json`.
4. Commit, `git tag -a vX.Y.Z`, push con tags. CI valida que el tag coincida.
5. En el sitio, subí el pin de `@wok/ui` a ese tag.
