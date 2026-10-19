#!/usr/bin/env python3
"""
sistema.py — genera la pagina de design system de WOK a partir del CSS
compilado (build/).

  python3 herramientas/sistema.py        (desde la raiz del paquete)

Escribe sistema/sistema.html. La pagina no define colores propios: todo sale de
build/tokens.css y build/tokens-dark.css, incrustados tal cual. Si cambia Figma,
se reexporta, se corre npm run verify y se vuelve a generar esta pagina.

Los hex de marca tampoco estan escritos aca: se leen del CSS. Lo unico propio de
WOK es que familia cumple que rol y los textos de muestra.
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'herramientas'))
from color import wcag, apca  # noqa: E402

# Orden y rotulo de las rampas tal como salen de Figma (color/<familia>/<stop>).
FAMILIES = ['neutral', 'paper', 'brand', 'accent', 'support', 'success', 'info', 'warning', 'danger']
FAM_LABEL = {
    'neutral': 'neutral · grises de interfaz, mismo matiz que el marfil',
    'paper': 'paper · papel de marca; 50 es el Marfil Cálido',
    'brand': 'brand · Verde Bosque Profundo en 900',
    'accent': 'accent · Naranja Intenso en 500; la acción usa 600',
    'support': 'support · Verde Lima Suave en 400',
    'success': 'success · éxito',
    'info': 'info · información y foco',
    'warning': 'warning · aviso',
    'danger': 'danger · error y acciones destructivas',
}
INK = ('brand', 900)  # texto oscuro de referencia en las tarjetas de marca
BRAND = [  # familia/stop, rol en los semanticos
    ('brand', 900, 'Verde Bosque Profundo. text/primary, brand/main, surface/ink y la página en oscuro.'),
    ('accent', 500, 'Naranja Intenso. brand/accent y surface/highlight: ilustración y display ≥24px.'),
    ('accent', 600, 'brand/action: botón primario con texto blanco. El 500 no llega a AA con blanco.'),
    ('support', 400, 'Verde Lima Suave. brand/support y surface/support, con texto bosque.'),
    ('paper', 50, 'Marfil Cálido. background/page en claro y texto sobre bosque.'),
]
TYPE = [  # clase, muestra, familia
    ('display-hero', 'WOK', 'display'),
    ('display-xl', 'Fuego alto', 'display'),
    ('display-lg', 'Cocina cantonesa al wok', 'display'),
    ('display-md', 'Dim sum los fines de semana', 'display'),
    ('display-sm', 'Pato laqueado para compartir', 'display'),
    ('heading-h1', 'Nuestro menú', 'body'),
    ('heading-h2', 'Para empezar', 'body'),
    ('heading-h3', 'Arroces y fideos salteados', 'body'),
    ('heading-h4', 'Bebidas y postres', 'body'),
    ('heading-h5', 'Alérgenos', 'body'),
    ('body-lg', 'Salteamos cada plato al momento, a fuego alto, para que llegue a la mesa con el aroma del wok. Las salsas se preparan en casa.', 'body'),
    ('body-md', 'Fideos de arroz salteados con res, cebollín, brotes de soya y salsa de soya oscura. Se puede pedir sin gluten.', 'body'),
    ('body-sm', 'Precios con impuestos incluidos.', 'body'),
    ('body-xs', 'Contiene soya y sésamo.', 'body'),
    ('label-md', 'Reservar mesa', 'body'),
    ('overline-lg', 'Especial de la casa', 'body'),
    ('code-md', 'npm run verify', 'mono'),
]

# Misma lista que bloquea el build (scripts/check-contrast.mjs), y su ALLOW.
PAIRS = json.load(open(os.path.join(ROOT, 'scripts', 'contrast-pairs.json'), encoding='utf-8'))['pairs']
_cc = open(os.path.join(ROOT, 'scripts', 'check-contrast.mjs'), encoding='utf-8').read()
ALLOW = {({'claro': 'Claro', 'oscuro': 'Oscuro'}[t], fg, bg)
         for t, fg, bg in re.findall(r'theme:\s*"(\w+)",\s*fg:\s*"([^"]+)",\s*bg:\s*"([^"]+)"', _cc)}


def css_colors(*sheets):
    """Resuelve var() sobre las hojas dadas (la última pisa) y devuelve {token: #HEX} opacos."""
    decl = {}
    for css in sheets:
        decl.update(dict(re.findall(r'--([a-z0-9-]+)\s*:\s*([^;]+);', css)))

    def res(n, d=0):
        v = decl.get(n, '').strip()
        m = re.fullmatch(r'var\(--([a-z0-9-]+)\)', v)
        return res(m.group(1), d + 1) if m and d < 20 else v
    return {n: res(n).upper() for n in decl if re.fullmatch(r'#[0-9a-fA-F]{6}', res(n))}


def css_block(css):
    """Devuelve solo las declaraciones dentro del primer bloque { }."""
    m = re.search(r'\{(.*)\}', css, re.S)
    return m.group(1).strip()


def main():
    light_css = open(os.path.join(ROOT, 'build', 'tokens.css'), encoding='utf-8').read()
    dark_css = open(os.path.join(ROOT, 'build', 'tokens-dark.css'), encoding='utf-8').read()
    light, dark = css_block(light_css), css_block(dark_css)
    version = json.load(open(os.path.join(ROOT, 'package.json'), encoding='utf-8'))['version']

    ramps = {}
    for fam, stop, hx in re.findall(r'--color-([a-z]+)-(\d+):\s*(#[0-9a-fA-F]{6})', light_css):
        ramps.setdefault(fam, {})[int(stop)] = hx.upper()
    sem_l = css_colors(light_css)
    sem_d = css_colors(light_css, dark_css)
    anchors = {(f, s) for f, s, _ in BRAND}

    # ── rampas ──
    rows = []
    for fam in FAMILIES + sorted(set(ramps) - set(FAMILIES)):
        cells = []
        for stop in sorted(ramps.get(fam, {})):
            hx = ramps[fam][stop]
            cells.append(
                '<li class="chip%s" style="--c:var(--color-%s-%d)"><span class="sw"></span>'
                '<span class="stop">%d</span><span class="hex">%s</span></li>' % (
                    ' anchor' if (fam, stop) in anchors else '', fam, stop, stop, hx))
        rows.append('<div class="ramp"><h3>%s</h3><ol>%s</ol></div>' % (html.escape(FAM_LABEL.get(fam, fam)), ''.join(cells)))
    ramps_html = '\n'.join(rows)

    # ── marca ──
    white, ink = '#FFFFFF', ramps[INK[0]][INK[1]]
    brand_cards = []
    for fam, stop, role in BRAND:
        hx = ramps[fam][stop]
        rw, rk = wcag(white, hx), wcag(ink, hx)
        fg = white if rw >= rk else ink
        brand_cards.append(
            '<article class="brand" style="--bg:var(--color-%s-%d);--fg:%s"><h3>%s/%d</h3><p>%s</p>'
            '<dl><dt>hex</dt><dd>%s</dd><dt>blanco encima</dt><dd>%.2f:1</dd><dt>%s/%d encima</dt><dd>%.2f:1</dd></dl></article>' % (
                fam, stop, fg, fam, stop, html.escape(role), hx, rw, INK[0], INK[1], rk))

    # ── contraste ──
    crow = []
    for theme, sem in (('Claro', sem_l), ('Oscuro', sem_d)):
        for fg, bg, mn, kind in PAIRS:
            if fg not in sem or bg not in sem or mn == 0:
                continue
            r = wcag(sem[fg], sem[bg])
            ok = r >= mn
            allowed = (theme, fg, bg) in ALLOW
            state = ('ok', 'pasa %g' % mn) if ok else (('warn', 'falla · ALLOW') if allowed else ('bad', 'falla'))
            crow.append('<tr><td>%s</td><td><span class="pair sm" style="--bg:%s;--fg:%s">Aa</span></td>'
                        '<td><code>--%s</code></td><td><code>--%s</code></td><td class="num">%.2f</td>'
                        '<td class="num">%.0f</td><td>%s</td><td><span class="state %s">%s</span></td></tr>' % (
                            theme, sem[bg], sem[fg], fg, bg, r, abs(apca(sem[fg], sem[bg])), kind, state[0], state[1]))
    contrast_html = '\n'.join(crow)
    fails = sum('state bad' in r for r in crow)
    warns = sum('state warn' in r for r in crow)

    # ── tipografia ──
    trows = []
    for cls, sample, fam in TYPE:
        base = '--typography-styles-' + cls
        ls = base + '-letter-spacing' if base + '-letter-spacing:' in light_css else None
        style = 'font-size:var(%s-size);line-height:var(%s-line-height);%s' % (base, base, 'letter-spacing:var(%s);' % ls if ls else '')
        size = re.search(re.escape(base) + r'-size:\s*([\d.]+)px', light_css).group(1)
        lh = re.search(re.escape(base) + r'-line-height:\s*([\d.]+)px', light_css).group(1)
        lsv = re.search(re.escape(base) + r'-letter-spacing:\s*(-?[\d.]+)px', light_css)
        meta = '%s / %s%s · %s' % (size, lh, ' · %s' % lsv.group(1) if lsv else '', fam)
        trows.append('<li class="trow"><div class="tmeta"><code>%s</code><span>%s</span></div>'
                     '<p class="t-%s t-%s" style="%s">%s</p></li>' % (cls, meta, fam, cls.split('-')[0], style, html.escape(sample)))
    type_html = '\n'.join(trows)

    space = ''.join('<li><code>%s</code><span class="bar" style="width:var(--spacing-%s)"></span></li>' % (s, s)
                    for s in ['1', '2', '3', '4', '5', '6', '8', '10', '12', '16', '20', '24'])
    radii = ''.join('<li><span class="rbox" style="border-radius:var(--radius-%s)"></span><code>%s</code></li>' % (r, r)
                    for r in ['none', 'xs', 'sm', 'md', 'lg', 'xl', '2xl', 'full'])
    n_tokens = len(re.findall(r'^\s*--[a-z0-9-]+\s*:', light_css, re.M))

    tpl = open(os.path.join(ROOT, 'herramientas', 'sistema.template.html'), encoding='utf-8').read()
    out = (tpl.replace('/*TOKENS_LIGHT*/', light)
              .replace('/*TOKENS_DARK*/', dark)
              .replace('<!--VERSION-->', version)
              .replace('<!--N_FAMILIES-->', str(len(ramps)))
              .replace('<!--N_TOKENS-->', str(n_tokens))
              .replace('<!--RAMPS-->', ramps_html)
              .replace('<!--BRAND-->', ''.join(brand_cards))
              .replace('<!--CONTRAST-->', contrast_html)
              .replace('<!--CONTRAST_SUMMARY-->', '%d pares medidos en los dos temas: %d fallan y están en ALLOW, %d fallan sin excepción.' % (len(crow), warns, fails))
              .replace('<!--TYPE-->', type_html)
              .replace('<!--SPACE-->', space)
              .replace('<!--RADII-->', radii))
    os.makedirs(os.path.join(ROOT, 'sistema'), exist_ok=True)
    path = os.path.join(ROOT, 'sistema', 'sistema.html')
    open(path, 'w', encoding='utf-8').write(out)
    print('escrito', path, '·', len(out) // 1024, 'KB ·', len(crow), 'pares,', warns, 'en ALLOW,', fails, 'fallas')


if __name__ == '__main__':
    main()
