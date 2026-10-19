# 0001 — Paquete propio de WOK

Estado: aceptada — octubre 2026

## Contexto

WOK es un restaurante cantonés. Su sitio necesita tokens de color,
tipografía y escalas en un paquete propio, como todo cliente del estudio:
`@wok/ui`, consumido por tag desde el sitio. No hay kit de pipeline todavía,
así que el runbook "cliente nuevo" (paso 1) arma la estructura copiando
**archivos** de paquetes existentes, nunca su historia ni sus datos.

Tampoco hay Figma de WOK con variables. Lo que hay es una propuesta de color
aprobada para arrancar (primitivos por rol, semánticos claro/oscuro, notas y
contraste) y las fuentes que entregó el cliente.

## Decisión

### Qué es y de dónde sale

- Paquete de tokens de WOK: `build/tokens.css` (`:root`),
  `build/tokens-dark.css` (`.dark`), `build/theme-bridge.css` (Tailwind v4 +
  shadcn) y `build/tokens.js`.
- La estructura sale de **divergentes-ui v0.2.0**, el paquete más nuevo del
  estudio, también para los archivos que el runbook toma de hablemos-ui
  (`figma-to-sd.py`, `style-dictionary-dark.config.js`,
  `theme-bridge.template.css`, `check-ramps.mjs`). Se copiaron archivos, no
  la historia.
- **No se hereda nada de datos**: ni familias, ni semánticos de otra marca,
  ni `ALLOW`, ni fuentes, ni textos. Las listas de `figma-to-sd.py`
  (`REQUIRED_TOKENS`, `EXPECTED_DARK_CROSS_COLLECTION`), de `sistema.py`
  (`FAMILIES`, `BRAND`, `TYPE`) y del bridge (`--primary`, familias, pesos)
  son de WOK. Componentes propios de un sitio ajeno (portada, filtros,
  pie, banda de proceso) no se trajeron.
- Escalas que no son de marca (espaciado, radios, sombras, motion,
  z-index, opacidad, breakpoints y la escala tipográfica) parten de los
  valores genéricos de ese paquete, con descripciones neutras.

### La fuente: semilla de una sola vez, después Figma

El flujo es Figma → `source/raw/*.json` → `figma-to-sd.py` →
`source/*.json` → Style Dictionary → `build/`. Como el Figma no existe,
`herramientas/semilla-figma.py` genera `source/raw/` con **el mismo formato
del export de variables** (12 colecciones, alias como `VARIABLE_ALIAS` con
`aliasName` y `resolvedValue`), a partir de `herramientas/semilla/`
(copias sin tocar de `propuesta.json` y `semanticos.json`). Ricardo los
importa en Figma y desde ahí se exporta. El script no se vuelve a correr: se
niega a pisar `source/raw/` sin `--forzar`. Los cambios posteriores a la
propuesta no se editan en la copia: van en `AJUSTES` del script, por tema y
con motivo. Cada semántico lleva una línea de uso como descripción, y los
FLOAT y las familias llevan scopes acotados (`OPACITY`, `CORNER_RADIUS`,
`STROKE_FLOAT`, `GAP`/`WIDTH_HEIGHT`, `FONT_*`, `LINE_HEIGHT`,
`LETTER_SPACING`, `FONT_FAMILY`); ratios, motion y z-index quedan sin scope
porque solo los usa el CSS.

### Colores

Familias por rol, 50–950 en OKLCH: `neutral`, `paper`, `brand`, `accent`,
`support`, `success`, `info`, `warning`, `danger`, más `white` y `black`.
Las cuatro anclas del manual quedan **exactas** en un stop:

| Manual | Stop | Hex |
|---|---|---|
| Verde Bosque Profundo | `color/brand/900` | #1A3129 |
| Verde Lima Suave | `color/support/400` | #A7CC73 |
| Naranja Intenso | `color/accent/500` | #FF5100 |
| Marfil Cálido | `color/paper/50` | #F4EFE6 |

- **Acción = `accent/600` (#D44304)** con texto blanco: 4,56:1. El naranja
  de manual con blanco da 3,27 y con bosque 4,24: ninguno alcanza AA en texto
  normal. #FF5100 (`brand/accent`) queda para ilustración y display ≥24px
  **sobre bosque** (4,24:1), y como fondo de `surface/highlight` con texto
  bosque (5,06:1). Sobre marfil da 2,85:1: no sirve ni como texto grande;
  ahí los titulares van en `brand/action` (accent-600, 3,98:1, ≥24px) o en
  `text/brand` (accent-700, cualquier tamaño).
- **El marfil va en `paper`, no en `neutral`.** Su croma (0,013) supera el
  0,010 que `check-ramps` tolera en `neutral` (regla 4). En vez de abrir una
  entrada de `ALLOW` (que es backlog de bugs, no permisos), el marfil y sus
  arenas forman `paper`, el papel de marca. `neutral` usa el mismo matiz
  (82°) con croma ≤0,008: cálido, pero gris.
- **`surface/ink` es el material de marca: Verde Bosque (`brand/900`) en los
  dos temas**, con `text/on-ink` marfil (12,10:1). En la propuesta ese nombre
  lo tenía la franja lima; acá la lima es `surface/support` con
  `text/on-support` bosque (7,61:1). En oscuro `surface/ink` coincide con la
  página: es a propósito, el material no cambia con el tema.
- **Texto en claro, un stop más oscuro que la propuesta**: `text/tertiary`
  en `neutral/600` daba 4,26:1 sobre `surface/container` y
  `background/subtle` (paper-100). Queda `text/secondary` = `neutral/800` y
  `text/tertiary` = `neutral/700` (≥5,13:1 sobre cualquier fondo claro).
- `feedback/error` usa `danger` (carmín a 15°), no el naranja. El botón
  peligroso es `danger/700`, más oscuro que la acción.

### Foco: un anillo por superficie

Un solo color de foco no llega a 3:1 en todas las superficies de WOK (el
azul de foco claro da 2,96 sobre bosque y 2,57 sobre lima; el naranja de
acción, 2,39 sobre un campo oscuro). Hay un token por tipo de superficie y
el sitio usa el de la superficie donde se dibuja el anillo:

| Token | Claro | Oscuro | Sobre |
|---|---|---|---|
| `focus/ring-color` | info-700 | info-300 | página, `background/*`, `surface/base`, `raised`, `container`, `subtle`, campos, tarjetas |
| `focus/ring-on-ink` | info-300 | info-300 | `surface/ink`, navegación, `surface/accent-bg` |
| `focus/ring-on-support` | brand-950 | brand-950 | `surface/support` |
| `focus/ring-on-inverse` | info-300 | info-700 | `surface/inverse`, tooltip |
| `focus/ring-on-highlight` | brand-950 | brand-950 | `surface/highlight-bg` |

El borde de foco de los campos (`input/border-focus`) es `focus/ring-color`.
Cada combinación está en `scripts/contrast-pairs.json` con mínimo 3: la
más justa es 4,37:1 (`focus/ring-color` sobre `background/strong` en
claro).

### Dudas abiertas sobre el manual

- **Declarado vs muestra.** El PDF muestra el naranja como #EC5E2A y el
  bosque como #203029, distintos de los hex declarados. Se usan los
  **declarados**: coinciden con el RGB y el CMYK impresos (255/81/0) y la
  muestra parece una conversión de perfil. Pregunta para el cliente: ¿el
  naranja en pantalla es #FF5100 o #EC5E2A? Si es el segundo, se cambia el
  ancla en Figma y se regenera la rampa.
- **Lima: RGB vs hex.** El manual imprime RGB 157/204/115 (= #9DCC73) junto
  a "# A7CC73". Se usó el hex declarado; hay que confirmarlo.

### Tipografía y licencias

- Las fuentes **no** van en el paquete: las sirve el sitio con
  `next/font/local`.
- `brand/font-display` = `Gang of Three` y `brand/font-body` = `Lato` son
  **nombres de familia**, los mismos que en Figma (sirven para enlazar
  estilos de texto). `brand/font-mono` es la pila mono del sistema: WOK no
  tiene mono de marca.
- El puente a `next/font` está en `theme-bridge.css`. El sitio define en
  `<html>` sus propias variables, `--font-wok-display` y `--font-wok-body`
  (y opcionalmente `--font-wok-mono`), y el bridge arma
  `--font-display: var(--font-wok-display, var(--brand-font-display),
  "WokDisplayFallback", Arial, Helvetica, sans-serif)` y lo mismo para
  `--font-sans` y `--font-mono`. Las claves de Tailwind no coinciden con las
  variables de `next/font`, así que no hay ciclo, y si falta la variable del
  sitio la pila cae al nombre del token y al respaldo: nunca queda vacía.
- **Gang of Three (display): provisoria, licencia pendiente.** El archivo
  no trae licencia; `fsType` 8 es un permiso técnico, no una licencia web.
  Además el texto del manual nombra a Meditative, mientras la muestra es Gang
  of Three: el cliente tiene que confirmar cuál y conseguir la licencia
  (también pendiente para Meditative).
- **Lato (cuerpo): OFL 1.1.** El sitio sirve un subset renombrado "WOK Sans"
  por el Reserved Font Name; la copia de la OFL viaja con las fuentes del
  sitio.
- Pesos publicados: 400, 700 y 900, los cortes que carga el sitio.

### Componentes

Conjunto genérico (botón, campo, tarjeta, navegación, modal, etiqueta,
toast, tooltip, avatar), todo con alias a semánticos o escalas, en claro y
oscuro. Los botones primario, secundario y peligroso siguen la propuesta.
Decisiones propias, a revisar en Figma: el borde de campo es
`border/strong` (3,79:1, alcanza el 3:1 de un límite de control), el foco de
campo es `focus/ring-color` y la navegación va sobre `surface/ink` con
`focus/ring-on-ink`.

### El contraste bloquea el build

`check-contrast` mide 76 pares en claro y oscuro (texto sobre fondo,
botones, feedback, bordes de campo, el anillo de foco sobre cada superficie
y componentes) y falla debajo del mínimo: 4,5 para texto, 3 para no texto y
foco. **No hay pares informativos** (mínimo 0): un par que no cumple está en
`ALLOW`, con motivo y ratio, y la corrida lo cuenta.

`ALLOW` de contraste tiene una entrada: `brand/action` sobre `surface/base`
en oscuro (2,39:1), el contorno del botón primario sobre una superficie
bosque-800. WCAG 1.4.11 no exige el contorno cuando la etiqueta identifica
el control (blanco sobre accent-600, 4,56:1), y cambiar la acción en oscuro
rompería ese texto. Sobre la página oscura da 3,04 y pasa. `ALLOW` de rampas
está vacía.

## Consecuencias

- El sitio fija `#v0.1.0` e importa los tres CSS en `globals.css`; carga
  `next/font` con `variable: "--font-wok-display"` y `"--font-wok-body"` en
  `<html>`, y usa el anillo de foco de cada superficie.
- Cuando exista el Figma, el primer export reemplaza la semilla. Si Figma
  cambia un valor o un nombre, es una versión nueva con su línea en el
  CHANGELOG (un renombre es mayor).
- Antes de publicar el sitio: licencia de la display y respuesta del
  cliente sobre el naranja y la lima.
