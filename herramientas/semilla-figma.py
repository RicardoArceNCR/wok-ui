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
# La copia de la propuesta no se edita: todo cambio posterior va acá, por tema,
# con su motivo. Cada entrada nombre → ref reemplaza o agrega el semántico.
#
# 1. surface/ink es la superficie del material de marca: Verde Bosque
#    (brand-900) en los dos temas, con texto marfil (12.10:1). La franja lima
#    que en la propuesta se llamaba surface/ink pasa a surface/support, con
#    texto bosque (7.61:1). Ver RENOMBRES.
# 2. Foco: un anillo por tipo de superficie, todos >=3:1 contra la superficie
#    donde se dibujan (scripts/contrast-pairs.json los mide). ring-color en
#    claro baja a info-700: info-600 daba 3.09 sobre background/strong.
# 3. Texto en claro un stop más oscuro: text/tertiary (neutral-600) daba 4.26
#    sobre surface/container y background/subtle (paper-100). Queda
#    secondary = neutral-800 y tertiary = neutral-700.
RENOMBRES = {'surface/ink': 'surface/support', 'text/on-ink': 'text/on-support'}
COMUNES = {
    'surface/ink': 'color/brand/900',
    'text/on-ink': 'color/paper/50',
    'focus/ring-on-ink': 'color/info/300',
    'focus/ring-on-support': 'color/brand/950',
    'focus/ring-on-highlight': 'color/brand/950',
}
AJUSTES = {
    'claro': {**COMUNES,
              'text/secondary': 'color/neutral/800',
              'text/tertiary': 'color/neutral/700',
              'focus/ring-color': 'color/info/700',
              'focus/ring-on-inverse': 'color/info/300'},
    'oscuro': {**COMUNES,
               'focus/ring-on-inverse': 'color/info/700'},
}
# Dónde van los semánticos nuevos (después de cuál).
INSERTAR_DESPUES = {
    'focus/ring-offset': ['focus/ring-on-ink', 'focus/ring-on-support', 'focus/ring-on-inverse', 'focus/ring-on-highlight'],
}

# ── Una línea de uso por semántico (Figma la muestra como descripción) ────────
DESCRIPCIONES = {
    'background/page': 'Fondo de página',
    'background/base': 'Fondo de secciones a sangre',
    'background/subtle': 'Fondo de bandas suaves y hover de botones',
    'background/strong': 'Fondo marcado: botón deshabilitado, press',
    'surface/base': 'Superficie de controles: campos y botón secundario',
    'surface/raised': 'Superficie elevada: tarjetas, modales, toasts',
    'surface/container': 'Contenedor agrupador sobre la página',
    'surface/subtle': 'Hover de tarjeta',
    'surface/inverse': 'Superficie invertida: tooltip, bloque de contraste',
    'surface/inverse-subtle': 'Velo sobre surface/inverse',
    'surface/accent-bg': 'Bloque destacado oscuro',
    'surface/accent-text': 'Texto sobre surface/accent-bg',
    'surface/accent-border': 'Borde sobre surface/accent-bg y surface/ink',
    'surface/ink': 'Material de marca: Verde Bosque en los dos temas',
    'surface/support': 'Franja de apoyo lima',
    'surface/highlight-bg': 'Fondo naranja de bandas promocionales; texto solo display ≥24px',
    'surface/highlight-text': 'Texto sobre surface/highlight-bg',
    'text/primary': 'Texto principal y titulares',
    'text/secondary': 'Texto secundario y etiquetas',
    'text/tertiary': 'Texto terciario, ayudas y placeholder',
    'text/disabled': 'Texto deshabilitado (sin requisito de contraste)',
    'text/inverse': 'Texto sobre surface/inverse',
    'text/inverse-secondary': 'Texto secundario sobre surface/inverse',
    'text/brand': 'Texto de marca en naranja apto para cuerpo',
    'text/brand-accent': 'Texto de apoyo verde: antetítulos',
    'text/on-brand': 'Texto sobre brand/action y botón peligroso',
    'text/on-ink': 'Texto sobre surface/ink',
    'text/on-support': 'Texto sobre surface/support',
    'border/default': 'Borde de tarjetas y separación suave',
    'border/subtle': 'Borde muy suave, deshabilitado',
    'border/strong': 'Borde de campos y controles (≥3:1)',
    'border/brand': 'Borde de marca, hover de campo',
    'border/inverse': 'Borde sobre surface/inverse',
    'border/inverse-subtle': 'Borde suave sobre surface/inverse',
    'brand/main': 'Color principal de marca: Verde Bosque',
    'brand/subtle': 'Fondo suave de marca: etiqueta y avatar',
    'brand/strong': 'Texto sobre brand/subtle',
    'brand/action': 'Acción principal: botón primario (accent-600)',
    'brand/action-hover': 'Hover de la acción principal',
    'brand/action-press': 'Press de la acción principal',
    'brand/accent': 'Naranja de manual: ilustración y display sobre bosque, nunca texto sobre marfil',
    'brand/support': 'Lima de marca: detalles sobre bosque',
    'focus/ring-color': 'Anillo de foco sobre página y superficies del tema',
    'focus/ring-offset': 'Separación entre el control y el anillo',
    'focus/ring-on-ink': 'Anillo de foco sobre surface/ink, nav y surface/accent-bg',
    'focus/ring-on-support': 'Anillo de foco sobre surface/support',
    'focus/ring-on-inverse': 'Anillo de foco sobre surface/inverse',
    'focus/ring-on-highlight': 'Anillo de foco sobre surface/highlight-bg',
    'interaction/hover-overlay': 'Velo de hover (con opacity/*)',
    'interaction/active-overlay': 'Velo de press (con opacity/*)',
    'interaction/link/default': 'Enlace',
    'interaction/link/hover': 'Enlace en hover',
    'interaction/link/visited': 'Enlace visitado',
    'overlay/modal': 'Velo detrás de un modal',
    'overlay/card': 'Velo sobre imagen de tarjeta',
    'overlay/hero': 'Velo sobre imagen de portada para texto encima',
    'divider/default': 'Separador',
    'divider/strong': 'Separador marcado',
}
for _tipo, _uso in (('success', 'éxito'), ('warning', 'aviso'), ('error', 'error'), ('info', 'información')):
    DESCRIPCIONES[f'feedback/{_tipo}/bg'] = f'Fondo de mensaje de {_uso}'
    DESCRIPCIONES[f'feedback/{_tipo}/border'] = f'Borde de mensaje de {_uso}'
    DESCRIPCIONES[f'feedback/{_tipo}/text'] = f'Texto de mensaje de {_uso}'
    DESCRIPCIONES[f'feedback/{_tipo}/icon'] = f'Ícono de {_uso} (siempre con texto)'

# ── Familias tipográficas ─────────────────────────────────────────────────────
# NOMBRES de familia, como se llaman en Figma (sirven para enlazar estilos de
# texto). El puente a next/font va en theme-bridge.template.css. Mono es una
# pila: WOK no tiene mono de marca y no se usa en Figma.
FUENTES = {
    'brand/font-display': ('Gang of Three',
                           'Display: Gang of Three (provisoria, licencia pendiente). Unicase: titulares en mayúsculas'),
    'brand/font-body':    ('Lato',
                           'Cuerpo: Lato (OFL). El sitio la sirve renombrada "WOK Sans"'),
    'brand/font-mono':    ('ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace',
                           'Mono: la del sistema (WOK no tiene mono de marca)'),
}

# ── Scopes de Figma ───────────────────────────────────────────────────────────
# Acotan en qué campos ofrece Figma cada variable. [] = no se ofrece en ningún
# campo (ratios y valores que solo usa el CSS). Colores: ALL_SCOPES.
def scopes(nombre, tipo):
    p = nombre.split('/')
    if tipo == 'COLOR':
        return ['ALL_SCOPES']
    if tipo == 'STRING':
        return ['FONT_FAMILY'] if nombre in ('brand/font-display', 'brand/font-body') else []
    hoja = p[-1]
    if p[0] == 'opacity':
        return ['OPACITY']
    if p[0] == 'radius' or hoja == 'radius':
        return ['CORNER_RADIUS']
    if p[0] == 'border':
        return ['STROKE_FLOAT']
    if p[0] == 'spacing':
        return ['GAP', 'WIDTH_HEIGHT']
    if p[0] == 'breakpoint' or hoja == 'height' or (len(p) > 1 and p[-2] == 'size' and p[0] != 'typography'):
        return ['WIDTH_HEIGHT']
    if hoja in ('padding-x', 'padding-y', 'padding'):
        return ['GAP']
    if p[:2] == ['typography', 'size'] or hoja == 'size':
        return ['FONT_SIZE']
    if p[:2] == ['typography', 'weight'] or hoja == 'font-weight':
        return ['FONT_WEIGHT']
    if hoja == 'line-height':
        return ['LINE_HEIGHT']
    if hoja == 'letter-spacing' and p[0] == 'typography':
        return ['LETTER_SPACING']
    # typography/leading y tracking (ratios), button/letter-spacing (alias a un
    # ratio), motion, z-index: los usa el CSS, no un campo de Figma.
    return []

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
    ('input/border-focus', 'focus/ring-color'),
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
            'scopes': scopes(nombre, tipo), 'hiddenFromPublishing': False, 'codeSyntax': {},
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
        datos = {RENOMBRES.get(k, k): dict(v) for k, v in semanticos[tema].items()}
        orden = []
        for nombre in semanticos[tema]:
            orden.append(nombre)
            if nombre in RENOMBRES:
                orden.append(RENOMBRES[nombre])
            orden += INSERTAR_DESPUES.get(nombre, [])
        for nombre, ref in AJUSTES[tema].items():
            datos[nombre] = {'ref': ref}
            if nombre not in orden:
                sys.exit(f'✗ AJUSTES: {nombre} no tiene lugar en el orden (INSERTAR_DESPUES)')
        for nombre in orden:
            d = datos[nombre]
            _, destino = buscar(d['ref'], [prim])
            if nombre not in DESCRIPCIONES:
                sys.exit(f'✗ {nombre} sin descripción en DESCRIPCIONES')
            desc = DESCRIPCIONES[nombre]
            if 'alpha' in d:
                rgba = dict(prim.valor(destino), a=d['alpha'])
                c.agregar(nombre, 'COLOR', rgba, f'{desc} ({d["ref"]} al {round(d["alpha"] * 100)}%)')
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
