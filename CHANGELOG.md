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
- Acción: `brand/action` = `accent/600` #D44304 con texto blanco (4,56:1).
- `surface/ink` es el Verde Bosque en los dos temas, con `text/on-ink` marfil. La franja lima es `surface/support`, con `text/on-support`.

### Tipografía

- `brand/font-display`, `brand/font-body` y `brand/font-mono` son pilas CSS sobre las variables de `next/font` del sitio (`--font-display`, `--font-body`); mono es la del sistema. Las fuentes no van en el paquete.
- Display Gang of Three **provisoria, licencia pendiente**. Cuerpo Lato (OFL).
- Pesos: `regular` 400, `bold` 700, `black` 900 (los cortes que carga el sitio).

### Controles

- `check-units` tal cual; `check-ramps` y `check-contrast` con `ALLOW` vacía.
- 57 pares de contraste en claro y oscuro (114 mediciones): todos pasan AA.
- CI: verify, `build/` al día y tag igual a la versión (corre al primer push).
- `sistema/sistema.html`, generado por `herramientas/sistema.py` desde `build/`.

### Para el sitio

- Instalar `github:RicardoArceNCR/wok-ui#v0.1.0` e importar los tres CSS en `globals.css` (README).
- Cargar `next/font` con `variable: "--font-display"` y `"--font-body"` en `<html>`.
