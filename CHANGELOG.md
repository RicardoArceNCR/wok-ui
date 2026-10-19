# Changelog

Cada tag dice qué cambió en la paleta y qué tiene que revisar el sitio.
Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Versiones: semver. Un token renombrado o borrado es **mayor**; un valor
nuevo o un token nuevo es **menor**; una descripción o un ajuste que no
cambia el CSS es **parche**.

## [Sin publicar]

## [0.1.0] — 2026-10-18

Primera versión de `@wok/ui` (ADR 0001).

### Origen

- Estructura copiada archivo por archivo (sin historia) de divergentes-ui v0.2.0, según el runbook "cliente nuevo" del estudio. Ningún token, excepción ni texto de otro cliente.
- `source/raw/` es una **semilla**: la generó `herramientas/semilla-figma.py` desde la propuesta de color aprobada, con el formato del export de Figma. Se importa en Figma y desde ahí manda Figma.

### Paleta

- Nueve familias por rol, 50–950: `neutral`, `paper`, `brand`, `accent`, `support`, `success`, `info`, `warning`, `danger`, más `white` y `black`.
- Anclas exactas del manual: Verde Bosque Profundo `brand/900` #1A3129, Verde Lima Suave `support/400` #A7CC73, Naranja Intenso `accent/500` #FF5100, Marfil Cálido `paper/50` #F4EFE6.
- Acción: `brand/action` = `accent/600` #D44304 con texto blanco (4,56:1). El naranja de manual (`brand/accent`) es para ilustración y display sobre bosque (4,24:1), no para texto sobre marfil (2,85:1).
- `surface/ink` es el Verde Bosque en los dos temas, con `text/on-ink` marfil. La franja lima es `surface/support`, con `text/on-support`.
- Texto en claro un stop más oscuro que la propuesta: `text/secondary` = `neutral/800`, `text/tertiary` = `neutral/700` (el 600 daba 4,26:1 sobre `surface/container`).
- Foco: `focus/ring-color` (`info/700` en claro, `info/300` en oscuro) y un anillo por superficie especial: `focus/ring-on-ink`, `-on-support`, `-on-inverse`, `-on-highlight`. `input/border-focus` usa `focus/ring-color`. Todos ≥3:1 donde se dibujan.

### Tipografía

- `brand/font-display` = `Gang of Three` y `brand/font-body` = `Lato`: nombres de familia, los mismos que en Figma. `brand/font-mono` es la pila mono del sistema.
- `theme-bridge.css` arma `font-display`, `font-sans` y `font-mono` desde las variables de `next/font` del sitio (`--font-wok-display`, `--font-wok-body`, `--font-wok-mono`), con el token y un respaldo genérico detrás. Las fuentes no van en el paquete.
- Display Gang of Three **provisoria, licencia pendiente**. Cuerpo Lato (OFL), servida por el sitio como "WOK Sans".
- Pesos: `regular` 400, `bold` 700, `black` 900 (los cortes que carga el sitio).

### Figma

- Semánticos con una línea de uso como descripción. Scopes acotados en los FLOAT y en las familias (`OPACITY`, `CORNER_RADIUS`, `STROKE_FLOAT`, `GAP`, `WIDTH_HEIGHT`, `FONT_SIZE`, `FONT_WEIGHT`, `LINE_HEIGHT`, `LETTER_SPACING`, `FONT_FAMILY`); ratios, motion y z-index sin scope.

### Controles

- `check-units` sin excepciones de otro paquete: los breakpoints salen con `px` y no hay escala tipográfica vieja.
- `check-ramps` con `ALLOW` vacía.
- `check-contrast`: 76 pares en claro y oscuro (152 mediciones), sin pares informativos. Una entrada en `ALLOW`, con motivo: el contorno del botón primario sobre `surface/base` en oscuro (2,39:1).
- CI: verify, `build/` al día y tag igual a la versión (corre al primer push).
- `sistema/sistema.html`, generado por `herramientas/sistema.py` desde `build/`.

### Para el sitio

- Instalar `github:RicardoArceNCR/wok-ui#v0.1.0` e importar los tres CSS en `globals.css` (README).
- Cargar `next/font` con `variable: "--font-wok-display"` y `"--font-wok-body"` en `<html>`.
- Sobre `surface/ink`, la navegación, `surface/support`, `surface/inverse` o `surface/highlight-bg`, usar el anillo de foco de esa superficie.
