"""
load the geom from fits tables
"""

import numpy as np
import healsparse as hs
import healpy as hp
import colorsys


def get_colors():
    uvals = np.array(
        [32,  64,  96, 128, 160, 192, 224,
         256, 288, 320, 352, 384, 416, 448, 480]
    )

    colors = list(reversed(rainbow(uvals.size)))

    d = {}
    for i, val in enumerate(uvals):
        d[val] = colors[i]

    return d


def plot_by_val(smap, ra, dec, use_rainbow=False, show=False, **kw):
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
    use_rainbow: bool
        If set, use a simple rainbow color scheme rather than
        pre-defined colors for each value
    show: bool
        If True, bring up a plot window.  Default Fals
    **kw:
        other keywords for the FramedPlot

    Returns
    -------
    biggles plot object
    """
    import biggles

    size = kw.pop('size', 1)

    vals = smap.get_values_pos(ra, dec)
    uvals = np.unique(vals)
    print('uvals: %s' % repr(uvals))
    if use_rainbow:
        if uvals.size == 1:
            colors = ['orange']
        else:
            colors = rainbow(uvals.size)
    else:
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

        if use_rainbow:
            color = colors[i]
        else:
            color = colors[val]

        pts = biggles.Points(ra[w], dec[w], type='dot', size=size, color=color)
        plt.add(pts)

    if show:
        plt.show()

    return plt


def plotrand(smap,
             nrand,
             randpix=False,
             by_val=False,
             show=False,
             use_rainbow=False,
             rng=None,
             **kw):
    """
    plot random ra, dec from the map


    Parameters
    ----------
    smap: HealSparseMap
        A HealSparseMap or object with that interface
    nrand: int
        number of random points to show
    rng: numpy RandomState
        For generating random points
    by_val: bool
        If set, plot by value in the map; keywords are passed
        on to the plot_by_val function
    show: bool
        If True, bring up a plot window.  Default Fals
    **kw:
        other keywords for the FramedPlot

    Returns
    -------
    biggles plot object
    """
    import biggles

    if randpix:
        if rng is None:
            rng = np.random.RandomState()

        vpix = smap.valid_pixels
        if vpix.size > nrand:
            isub = rng.randint(0, vpix.size, size=nrand)
            sub = vpix[isub]
        else:
            sub = vpix

        ra, dec = hp.pix2ang(smap.nside_sparse, sub, nest=True, lonlat=True)

    else:
        ra, dec = hs.make_uniform_randoms_fast(smap, nrand, rng=rng)

    if 'aspect_ratio' not in kw:
        kw['aspect_ratio'] = (dec.max()-dec.min())/(ra.max()-ra.min())

    if by_val:
        plt = plot_by_val(
            smap, ra, dec,
            show=show, use_rainbow=use_rainbow, **kw
        )
    else:

        size = kw.pop('size', 1)
        if 'xrange' not in kw:
            kw['xrange'] = (ra.min(), ra.max())

        if 'yrange' not in kw:
            kw['yrange'] = (dec.min(), dec.max())

        plt = biggles.FramedPlot(
            xlabel='RA',
            ylabel='DEC',
            **kw
        )

        pts = biggles.Points(ra, dec, type='dot', size=size, color='blue')
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
