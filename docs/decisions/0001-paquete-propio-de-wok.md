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
niega a pisar `source/raw/` sin `--forzar`.

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
  normal. #FF5100 queda para ilustración, display ≥24px y
  `surface/highlight`.
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
- `feedback/error` usa `danger` (carmín a 15°), no el naranja. El botón
  peligroso es `danger/700`, más oscuro que la acción.

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
- `brand/font-display`, `brand/font-body` y `brand/font-mono` son **pilas
  CSS**: empiezan por la variable de `next/font` del sitio
  (`var(--font-display, …)`, `var(--font-body, …)`) y siguen con el respaldo
  para donde no hay `next/font` (la lámina, un Storybook). Mono es la del
  sistema. El bridge mapea `font-display`, `font-sans` y `font-mono` a esos
  tokens. Consecuencia en Figma: estas variables no sirven para enlazar un
  estilo de texto; ahí se elige la fuente directamente.
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
Dos decisiones propias, a revisar en Figma: el borde de campo es
`border/strong` (3,79:1, alcanza el 3:1 de un límite de control) y la
navegación va sobre `surface/ink`.

### El contraste bloquea el build

`check-contrast` mide 57 pares en claro y oscuro (texto sobre fondo,
botones, feedback, foco, bordes de campo y siete de componentes) y falla
debajo de AA. `ALLOW` arranca vacía en contraste y en rampas: un par o una
rampa que falle entra solo con motivo escrito y el ratio medido.

## Consecuencias

- El sitio fija `#v0.1.0` e importa los tres CSS en `globals.css`; carga
  `next/font` con `--font-display` y `--font-body` en `<html>`.
- Cuando exista el Figma, el primer export reemplaza la semilla. Si Figma
  cambia un valor o un nombre, es una versión nueva con su línea en el
  CHANGELOG (un renombre es mayor).
- Antes de publicar el sitio: licencia de la display y respuesta del
  cliente sobre el naranja y la lima.
