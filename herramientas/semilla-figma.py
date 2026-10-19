#!/usr/bin/env python3
"""
semilla-figma.py — SEMILLA DE UNA SOLA VEZ: después manda Figma.

WOK todavía no tiene Figma con variables. Este script arma source/raw/*.json
con el MISMO formato que exporta el plugin Export/Import Variables de Figma
(el que lee figma-to-sd.py: { id, name, modes, variableIds, variables }),
para que Ricardo los IMPORTE en un Figma nuevo de WOK. A partir de ese
momento la fuente es Figma: se exporta a source/raw/ y se corre
`npm run verify`. Este script no se vuelve a correr.

Lee:
  herramientas/semilla/propuesta.json   primitivos de color por rol (50-950),
                                         copia de la propuesta aprobada
  herramientas/semilla/semanticos.json  semánticos claro/oscuro, misma copia
y las escalas genéricas de abajo (espaciado, radios, tipografía, motion,
opacidad, breakpoints, sombras, z-index), que no son de marca.

Escribe: source/raw/{colección}.json (12 colecciones, ver COLECCIONES).

Uso (desde la raíz del paquete):
  python3 herramientas/semilla-figma.py            # falla si source/raw ya existe
  python3 herramientas/semilla-figma.py --forzar   # pisa source/raw (¡pisa lo que vino de Figma!)

Los IDs (VariableID:N:M) son inventados y estables. Al importar, Figma asigna
los suyos; figma-to-sd.py solo usa los IDs para resolver alias dentro del
mismo export, así que el próximo export de Figma funciona igual.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMILLA = ROOT / 'herramientas' / 'semilla'
RAW = ROOT / 'source' / 'raw'

# Colección → (número para los IDs, nombre del modo). El número solo hace
# legibles los IDs; los nombres de modo siguen al export de Figma.
COLECCIONES = {
    'primitivos':       (1, 'Mode 1'),
    'semanticos':       (2, 'Light'),
    'componentes':      (3, 'Mode 1'),
    'spacing':          (4, 'Mode 1'),
    'tipografia':       (5, 'Mode 1'),
    'motion':           (6, 'Mode 1'),
    'opacity':          (7, 'Mode 1'),
    'breakpoints':      (8, 'Mode 1'),
    'semanticos-dark':  (9, 'Dark'),
    'componentes-dark': (10, 'Mode 1'),
    'shadow':           (11, 'Mode 1'),
    'z-index':          (12, 'Mode 1'),
}

FAMILIAS = ['neutral', 'paper', 'brand', 'accent', 'support', 'success', 'info', 'warning', 'danger']
STOPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]

# ── Ajustes sobre semanticos.json (decididos después de la propuesta) ─────────
# surface/ink es la superficie del material de marca: Verde Bosque (brand-900)
# en los dos temas. La franja lima que en la propuesta se llamaba surface/ink
# pasa a surface/support, y su texto (text/on-ink) a text/on-support. Sobre la
# nueva surface/ink el texto es marfil (paper-50, 12.10:1).
AJUSTES = {
    'surface/ink':      ('color/brand/900', 'Superficie del material de marca: Verde Bosque (brand-900) en los dos temas'),
    'text/on-ink':      ('color/paper/50', 'Texto sobre surface/ink: marfil sobre bosque'),
    'surface/support':  ('color/support/400', 'Franja de apoyo: Verde Lima Suave (support-400)'),
    'text/on-support':  ('color/brand/900', 'Texto sobre surface/support: bosque sobre lima'),
}

# ── Familias tipográficas ─────────────────────────────────────────────────────
# El valor es la pila CSS. La primera opción es la variable que publica
# next/font en el sitio (fonts.ts: variable "--font-display" y "--font-body");
# lo que sigue dentro del var() es el respaldo si la variable no existe (la
# lámina, un Storybook). Las fuentes las sirve el sitio, no este paquete.
FUENTES = {
    'brand/font-display': ('var(--font-display, "Gang of Three", "WokDisplayFallback", Arial, Helvetica, sans-serif)',
                           'Display: Gang of Three (provisoria, licencia pendiente). Unicase: titulares en mayúsculas'),
    'brand/font-body':    ('var(--font-body, Lato, system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif)',
                           'Cuerpo: Lato (OFL), servida por el sitio como "WOK Sans"'),
    'brand/font-mono':    ('ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace',
                           'Mono: la del sistema (WOK no tiene mono de marca)'),
}

# ── Escalas genéricas (no son de marca) ───────────────────────────────────────
TIPO_SIZE = [('2xs', 10), ('xs', 12), ('sm', 14), ('md', 16), ('lg', 18), ('xl', 20), ('2xl', 24),
             ('3xl', 28), ('4xl', 32), ('5xl', 40), ('6xl', 48), ('7xl', 64), ('8xl', 104)]
# Solo los cortes que carga el sitio: Lato 400, 700 y 900 (Gang of Three, 400).
TIPO_WEIGHT = [('regular', 400), ('bold', 700), ('black', 900)]
TIPO_LEADING = [('tight', 1.05), ('snug', 1.25), ('normal', 1.5), ('relaxed', 1.7), ('loose', 1.8)]
TIPO_TRACKING = [('tight', -0.03), ('normal', 0), ('wide', 0.06), ('wider', 0.1), ('caps', 0.12)]
RADIUS = [('none', 0), ('xs', 2), ('sm', 4), ('md', 8), ('lg', 12), ('xl', 16), ('2xl', 24), ('full', 9999)]
BORDER = [('none', 0), ('sm', 0.5), ('md', 1), ('lg', 1.5), ('xl', 2)]
SPACING = [(0, 0), (1, 4), (2, 8), (3, 12), (4, 16), (5, 20), (6, 24), (8, 32), (10, 40), (12, 48),
           (16, 64), (20, 80), (24, 96)]
BREAKPOINTS = [('sm', 640), ('md', 768), ('lg', 1024), ('xl', 1280), ('2xl', 1536)]
OPACITY = [('ghost', 0.04), ('hairline', 0.08), ('subtle', 0.16), ('mid', 0.42), ('soft', 0.5),
           ('medium', 0.6), ('strong', 0.72), ('high', 0.8), ('full', 1)]
MOTION = [
    ('motion/duration/instant', 50, 'Feedback inmediato'),
    ('motion/duration/fast', 100, 'Microinteracciones'),
    ('motion/duration/normal', 150, 'Transiciones de interfaz'),
    ('motion/duration/slow', 250, 'Modales y paneles'),
    ('motion/duration/slower', 400, 'Entradas grandes'),
    ('motion/easing/standard', 'cubic-bezier(0.4, 0, 0.2, 1)', 'Movimiento general'),
    ('motion/easing/enter', 'cubic-bezier(0, 0, 0.2, 1)', 'Elementos que entran'),
    ('motion/easing/exit', 'cubic-bezier(0.4, 0, 1, 1)', 'Elementos que salen'),
    ('motion/easing/spring', 'cubic-bezier(0.34, 1.56, 0.64, 1)', 'Rebote sutil'),
]
SHADOW = [
    ('sm', '0px 1px 2px rgba(0, 0, 0, 0.06), 0px 1px 3px rgba(0, 0, 0, 0.10)'),
    ('md', '0px 4px 6px -1px rgba(0, 0, 0, 0.10), 0px 2px 4px -2px rgba(0, 0, 0, 0.10)'),
    ('lg', '0px 10px 15px -3px rgba(0, 0, 0, 0.10), 0px 4px 6px -4px rgba(0, 0, 0, 0.10)'),
    ('sm-dark', '0px 1px 2px rgba(0, 0, 0, 0.30), 0px 1px 3px rgba(0, 0, 0, 0.40)'),
    ('md-dark', '0px 4px 6px -1px rgba(0, 0, 0, 0.40), 0px 2px 4px -2px rgba(0, 0, 0, 0.40)'),
    ('lg-dark', '0px 10px 15px -3px rgba(0, 0, 0, 0.45), 0px 4px 6px -4px rgba(0, 0, 0, 0.45)'),
]
Z_INDEX = [('dropdown', 1000), ('sticky', 1020), ('overlay', 1030), ('modal', 1040), ('toast', 1050), ('tooltip', 1060)]
# Estilos de texto: (estilo, size, line-height, letter-spacing o None). Valores
# en px, ya multiplicados, como los guarda Figma. Punto de partida genérico: se
# calibran en Figma con Gang of Three y Lato.
TIPO_STYLES = [
    ('display/hero', 104, 109.2, -3.12), ('display/xl', 64, 67.2, -1.92), ('display/lg', 48, 50.4, -0.96),
    ('display/md', 40, 50, -0.8), ('display/sm', 32, 40, -0.32),
    ('heading/h1', 28, 35, -0.28), ('heading/h2', 24, 30, None), ('heading/h3', 20, 25, None),
    ('heading/h4', 18, 27, None), ('heading/h5', 16, 24, None),
    ('body/lg', 18, 30.6, None), ('body/md', 16, 27.2, None), ('body/sm', 14, 21, None), ('body/xs', 12, 18, None),
    ('body/lg-bold', 18, 30.6, None), ('body/md-bold', 16, 27.2, None), ('body/sm-bold', 14, 21, None),
    ('label/lg', 16, 20, 0.96), ('label/md', 14, 17.5, 0.84), ('label/sm', 12, 15, 0.72), ('label/xs', 10, 12.5, 0.8),
    ('overline/lg', 14, 17.5, 1.68), ('overline/sm', 12, 15, 1.44),
    ('code/md', 14, 23.8, None), ('code/sm', 12, 18, None),
]

# ── Componentes ───────────────────────────────────────────────────────────────
# Conjunto genérico de interfaz. Cada valor es un alias: (claro, oscuro). Un
# string solo vale para los dos. Los nombres de semánticos se resuelven en
# semanticos (claro) o semanticos-dark (oscuro); los de primitivos, spacing y
# shadow, en su colección. None = transparente.
COMPONENTES = [
    ('button/primary/bg', 'brand/action'),
    ('button/primary/bg-hover', 'brand/action-hover'),
    ('button/primary/bg-press', 'brand/action-press'),
    ('button/primary/text', 'text/on-brand'),
    ('button/primary/border', 'brand/action'),
    ('button/secondary/bg', 'surface/base'),
    ('button/secondary/bg-hover', 'background/subtle'),
    ('button/secondary/bg-press', 'background/strong'),
    ('button/secondary/text', 'text/primary'),
    ('button/secondary/border', 'text/primary'),
    ('button/ghost/bg', None),
    ('button/ghost/bg-hover', 'background/subtle'),
    ('button/ghost/bg-press', 'background/strong'),
    ('button/ghost/text', 'text/primary'),
    ('button/ghost/border', None),
    ('button/danger/bg', 'color/danger/700'),
    ('button/danger/bg-hover', 'color/danger/800'),
    ('button/danger/bg-press', 'color/danger/900'),
    ('button/danger/text', 'text/on-brand'),
    ('button/danger/border', 'color/danger/700'),
    ('button/disabled/bg', 'background/strong'),
    ('button/disabled/text', 'text/disabled'),
    ('button/disabled/border', 'border/subtle'),
    ('button/size/sm/height', 'spacing/8'),
    ('button/size/md/height', 'spacing/10'),
    ('button/size/lg/height', 'spacing/12'),
    ('button/size/sm/padding-x', 'spacing/3'),
    ('button/size/md/padding-x', 'spacing/4'),
    ('button/size/lg/padding-x', 'spacing/6'),
    ('button/radius', 'radius/full'),
    ('button/font-weight', 'typography/weight/bold'),
    ('button/letter-spacing', 'typography/tracking/caps'),
    ('input/bg', 'surface/base'),
    ('input/bg-focus', 'surface/base'),
    ('input/bg-disabled', 'background/subtle'),
    ('input/border', 'border/strong'),
    ('input/border-hover', 'border/brand'),
    ('input/border-focus', 'brand/action'),
    ('input/border-error', 'feedback/error/icon'),
    ('input/border-success', 'feedback/success/icon'),
    ('input/border-disabled', 'border/subtle'),
    ('input/text', 'text/primary'),
    ('input/text-disabled', 'text/disabled'),
    ('input/placeholder', 'text/tertiary'),
    ('input/label', 'text/secondary'),
    ('input/radius', 'radius/md'),
    ('input/padding-x', 'spacing/4'),
    ('input/padding-y', 'spacing/3'),
    ('card/bg', 'surface/raised'),
    ('card/bg-hover', 'surface/subtle'),
    ('card/border', 'border/default'),
    ('card/border-hover', 'border/strong'),
    ('card/text', 'text/primary'),
    ('card/radius', 'radius/lg'),
    ('card/padding', 'spacing/6'),
    ('card/shadow', ('sm', 'sm-dark')),
    ('nav/bg', 'surface/ink'),
    ('nav/border', 'surface/accent-border'),
    ('nav/item/default', 'text/on-ink'),
    ('nav/item/hover', 'brand/support'),
    ('nav/item/active', 'brand/support'),
    ('nav/height', 'spacing/16'),
    ('modal/bg', 'surface/raised'),
    ('modal/border', 'border/default'),
    ('modal/text', 'text/primary'),
    ('modal/overlay', 'overlay/modal'),
    ('modal/radius', 'radius/xl'),
    ('modal/shadow', ('lg', 'lg-dark')),
    ('pill/base/bg', 'background/subtle'),
    ('pill/base/text', 'text/secondary'),
    ('pill/base/border', 'border/default'),
    ('pill/brand/bg', 'brand/subtle'),
    ('pill/brand/text', 'brand/strong'),
    ('pill/success/bg', 'feedback/success/bg'),
    ('pill/success/text', 'feedback/success/text'),
    ('pill/warning/bg', 'feedback/warning/bg'),
    ('pill/warning/text', 'feedback/warning/text'),
    ('pill/error/bg', 'feedback/error/bg'),
    ('pill/error/text', 'feedback/error/text'),
    ('pill/radius', 'radius/full'),
    ('pill/sm/padding-x', 'spacing/2'),
    ('pill/md/padding-x', 'spacing/3'),
    ('toast/bg', 'surface/raised'),
    ('toast/border', 'border/default'),
    ('toast/text', 'text/primary'),
    ('toast/radius', 'radius/lg'),
    ('toast/shadow', ('md', 'md-dark')),
    ('tooltip/bg', 'surface/inverse'),
    ('tooltip/text', 'text/inverse'),
    ('tooltip/radius', 'radius/sm'),
    ('tooltip/shadow', ('sm', 'sm-dark')),
    ('avatar/bg', 'brand/subtle'),
    ('avatar/text', 'brand/strong'),
    ('avatar/border', 'border/default'),
    ('avatar/size/sm', 'spacing/8'),
    ('avatar/size/md', 'spacing/10'),
    ('avatar/size/lg', 'spacing/12'),
]


# ── Utilidades de formato Figma ───────────────────────────────────────────────

def hex_a_rgba(hx, a=1):
    h = hx.lstrip('#')
    return {'r': int(h[0:2], 16) / 255, 'g': int(h[2:4], 16) / 255, 'b': int(h[4:6], 16) / 255, 'a': a}


class Coleccion:
    def __init__(self, nombre):
        self.nombre = nombre
        self.n, self.modo_nombre = COLECCIONES[nombre]
        self.modo = f'{self.n}:0'
        self.vars = []
        self.por_nombre = {}

    def agregar(self, nombre, tipo, valor, descripcion='', alias=None):
        """valor: el resolvedValue. alias: variable destino (dict) o None."""
        vid = f'VariableID:{self.n}:{len(self.vars) + 1}'
        if alias is None:
            vbm = valor
            res = {'resolvedValue': valor, 'alias': None}
        else:
            vbm = {'type': 'VARIABLE_ALIAS', 'id': alias['id']}
            res = {'resolvedValue': valor, 'alias': alias['id'], 'aliasName': alias['name']}
        var = {
            'id': vid, 'name': nombre, 'description': descripcion, 'type': tipo,
            'valuesByMode': {self.modo: vbm},
            'resolvedValuesByMode': {self.modo: res},
            'scopes': ['ALL_SCOPES'], 'hiddenFromPublishing': False, 'codeSyntax': {},
        }
        self.vars.append(var)
        self.por_nombre[nombre] = var
        return var

    def valor(self, var):
        return var['resolvedValuesByMode'][self.modo]['resolvedValue']

    def json(self):
        return {
            'id': f'VariableCollectionId:{self.n}:0',
            'name': self.nombre,
            'modes': {self.modo: self.modo_nombre},
            'variableIds': [v['id'] for v in self.vars],
            'variables': self.vars,
        }


def buscar(nombre, colecciones):
    for c in colecciones:
        if nombre in c.por_nombre:
            return c, c.por_nombre[nombre]
    sys.exit(f'✗ alias sin destino: {nombre}')


# ── Armado ────────────────────────────────────────────────────────────────────

def main():
    if RAW.exists() and any(RAW.glob('*.json')) and '--forzar' not in sys.argv:
        sys.exit(f'✗ {RAW.relative_to(ROOT)} ya tiene JSON. La fuente ahora es Figma: exportá desde ahí.\n'
                 '  Si de verdad querés volver a la semilla, corré con --forzar.')

    propuesta = json.loads((SEMILLA / 'propuesta.json').read_text(encoding='utf-8'))
    semanticos = json.loads((SEMILLA / 'semanticos.json').read_text(encoding='utf-8'))
    anclas = {v['parada']: (nombre, v['declarado']) for nombre, v in propuesta['manual'].items()}

    # primitivos
    prim = Coleccion('primitivos')
    for fam in FAMILIAS:
        rampa = propuesta['color'][fam]
        for stop in STOPS:
            hx = rampa[str(stop)]
            desc = hx.lower()
            if f'{fam}-{stop}' in anclas:
                nombre, declarado = anclas[f'{fam}-{stop}']
                assert hx.upper() == declarado.upper(), f'{fam}-{stop} no es el ancla declarada'
                desc += f' · {nombre} (ancla del manual)'
            prim.agregar(f'color/{fam}/{stop}', 'COLOR', hex_a_rgba(hx), desc)
    prim.agregar('color/white', 'COLOR', hex_a_rgba(propuesta['color']['white']), '#ffffff')
    prim.agregar('color/black', 'COLOR', hex_a_rgba(propuesta['color']['black']), '#000000')
    for k, v in TIPO_SIZE:
        prim.agregar(f'typography/size/{k}', 'FLOAT', v, f'{v}px')
    for k, v in TIPO_WEIGHT:
        prim.agregar(f'typography/weight/{k}', 'FLOAT', v, str(v))
    for k, v in TIPO_LEADING:
        prim.agregar(f'typography/leading/{k}', 'FLOAT', v, str(v))
    for k, v in TIPO_TRACKING:
        prim.agregar(f'typography/tracking/{k}', 'FLOAT', v, f'{v}em')
    for k, v in RADIUS:
        prim.agregar(f'radius/{k}', 'FLOAT', v, f'{v}px')
    for k, v in BORDER:
        prim.agregar(f'border/{k}', 'FLOAT', v, f'{v}px')

    # escalas sueltas
    spacing = Coleccion('spacing')
    for k, v in SPACING:
        spacing.agregar(f'spacing/{k}', 'FLOAT', v, f'{v}px')
    tipo = Coleccion('tipografia')
    for estilo, size, lh, ls in TIPO_STYLES:
        tipo.agregar(f'typography/styles/{estilo}/size', 'FLOAT', size, f'{size}px')
        tipo.agregar(f'typography/styles/{estilo}/line-height', 'FLOAT', lh, f'{lh}px')
        if ls is not None:
            tipo.agregar(f'typography/styles/{estilo}/letter-spacing', 'FLOAT', ls, f'{ls}px')
    motion = Coleccion('motion')
    for k, v, d in MOTION:
        motion.agregar(k, 'FLOAT' if isinstance(v, (int, float)) else 'STRING', v, d)
    opacity = Coleccion('opacity')
    for k, v in OPACITY:
        opacity.agregar(f'opacity/{k}', 'FLOAT', v, f'{round(v * 100)}%')
    bps = Coleccion('breakpoints')
    for k, v in BREAKPOINTS:
        bps.agregar(f'breakpoint/{k}', 'FLOAT', v, f'{v}px')
    shadow = Coleccion('shadow')
    for k, v in SHADOW:
        shadow.agregar(k, 'STRING', v)
    zi = Coleccion('z-index')
    for k, v in Z_INDEX:
        zi.agregar(k, 'FLOAT', v)

    # semánticos claro y oscuro
    sem = {}
    for coleccion, tema in (('semanticos', 'claro'), ('semanticos-dark', 'oscuro')):
        c = Coleccion(coleccion)
        datos = {k: dict(v) for k, v in semanticos[tema].items()}
        # surface/ink (lima) y text/on-ink pasan a support; surface/ink y
        # text/on-ink se redefinen. Se reemplazan en su lugar para mantener
        # el orden del archivo.
        datos['surface/support'] = datos.pop('surface/ink')
        datos['text/on-support'] = datos.pop('text/on-ink')
        for nombre, (ref, _) in AJUSTES.items():
            datos[nombre] = {'ref': ref}
        orden = []
        for nombre in semanticos[tema]:
            if nombre == 'surface/ink':
                orden += ['surface/ink', 'surface/support']
            elif nombre == 'text/on-ink':
                orden += ['text/on-ink', 'text/on-support']
            else:
                orden.append(nombre)
        for nombre in orden:
            d = datos[nombre]
            _, destino = buscar(d['ref'], [prim])
            desc = AJUSTES.get(nombre, (None, ''))[1]
            if 'alpha' in d:
                rgba = dict(prim.valor(destino), a=d['alpha'])
                c.agregar(nombre, 'COLOR', rgba, desc or f'{d["ref"]} al {round(d["alpha"] * 100)}%')
            else:
                c.agregar(nombre, 'COLOR', prim.valor(destino), desc, alias=destino)
        if tema == 'claro':
            for nombre, (valor, desc) in FUENTES.items():
                c.agregar(nombre, 'STRING', valor, desc)
        sem[tema] = c

    # componentes claro y oscuro
    comps = {}
    for coleccion, tema, idx in (('componentes', 'claro', 0), ('componentes-dark', 'oscuro', 1)):
        c = Coleccion(coleccion)
        fuentes = [sem[tema], prim, spacing, shadow]
        for nombre, alias in COMPONENTES:
            if isinstance(alias, tuple):
                alias = alias[idx]
            if alias is None:
                c.agregar(nombre, 'COLOR', {'r': 0, 'g': 0, 'b': 0, 'a': 0}, 'Transparente')
                continue
            origen, destino = buscar(alias, fuentes)
            c.agregar(nombre, destino['type'], origen.valor(destino), '', alias=destino)
        comps[tema] = c

    RAW.mkdir(parents=True, exist_ok=True)
    todas = [prim, sem['claro'], comps['claro'], spacing, tipo, motion, opacity, bps,
             sem['oscuro'], comps['oscuro'], shadow, zi]
    for c in todas:
        (RAW / f'{c.nombre}.json').write_text(json.dumps(c.json(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'✓ source/raw/{c.nombre}.json ({len(c.vars)} variables)')
    print('\nSemilla escrita. Importala en Figma y desde ahí exportá: este script no se vuelve a correr.')


if __name__ == '__main__':
    main()
