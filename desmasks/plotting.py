"""
load the geom from fits tables
"""

import numpy as np
import colorsys


def get_colors():
    uvals = np.array(
        [32,  64,  96, 128, 160, 192, 224,
         256, 288, 320, 352, 384, 448, 480]
    )

    colors = list(reversed(rainbow(uvals.size)))

    d = {}
    for i, val in enumerate(uvals):
        d[val] = colors[i]

    return d


def plot_by_val(smap, ra, dec, show=False, **kw):
    """
    plot ra, dec values colored by their value

    Parameters
    ----------
    smap: HealSparseMap
        A HealSparseMap or object with that interface
    ra: array
        array of ra values
    dec: array
        array of dec values
    show: bool
        If True, bring up a plot window.  Default Fals
    **kw:
        other keywords for the FramedPlot

    Returns
    -------
    biggles plot object
    """
    import biggles

    vals = smap.getValueRaDec(ra, dec)
    uvals = np.unique(vals)
    print('uvals: %s' % repr(uvals))
    colors = get_colors()

    if 'xrange' not in kw:
        kw['xrange'] = (ra.min(), ra.max())

    if 'yrange' not in kw:
        kw['yrange'] = (dec.min(), dec.max())

    plt = biggles.FramedPlot(
        xlabel='RA',
        ylabel='DEC',
        **kw
    )

    for i, val in enumerate(uvals):
        if val == 0:
            continue
        w, = np.where(vals == val)
        color = colors[val]
        pts = biggles.Points(ra[w], dec[w], type='dot', color=color)
        plt.add(pts)

    if show:
        plt.show()

    return plt


def rainbow(num, type='hex'):
    """
    make rainbow colors

    parameters
    ----------
    num: integer
        number of colors
    type: string, optional
        'hex' or 'rgb', default hex
    """
    # not going to 360
    minh = 0.0
    # 270 would go to pure blue
    maxh = 285.0

    hstep = (maxh-minh)/(num-1)
    colors = []
    for i in range(num):
        h = minh + i*hstep

        # just change the hue
        r, g, b = colorsys.hsv_to_rgb(h/360.0, 1.0, 1.0)
        r *= 255
        g *= 255
        b *= 255
        if type == 'rgb':
            colors.append((r, g, b))
        elif type == 'hex':

            rgb = (int(r), int(g), int(b))
            colors.append(rgb_to_hex(rgb))
        else:
            raise ValueError("color type should be 'rgb' or 'hex'")

    return colors


def heat(num, type='hex'):
    """
    make range from blue to red

    parameters
    ----------
    num: integer
        number of colors
    type: string, optional
        'hex' or 'rgb', default hex
    """
    # not going to 360
    minh = 0.0
    # 270 would go to pure blue
    maxh = 250.0

    hstep = (maxh-minh)/(num-1)
    colors = []
    for i in range(num):
        h = minh + i*hstep

        # just change the hue
        r, g, b = colorsys.hsv_to_rgb(h/360.0, 1.0, 1.0)
        r *= 255
        g *= 255
        b *= 255
        if type == 'rgb':
            colors.append((r, g, b))
        elif type == 'hex':
            colors.append(rgb_to_hex((r, g, b)))
        else:
            raise ValueError("color type should be 'rgb' or 'hex'")

    return list(reversed(colors))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb
