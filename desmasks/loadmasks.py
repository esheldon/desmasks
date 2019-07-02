"""
load the geom from fits tables
"""

import numpy as np
import fitsio
import healsparse as hs


def read_stars(*, fname, ext='satstars'):
    """
    read star masks from a file

    Parameters
    ----------
    fname: string
        File to read
    ext: string, optional
        Extension to read, default 'satstars'
    """
    with fitsio.FITS(fname) as fobj:
        data = fobj[ext].read(lower=True)

    w, = np.where(
        (data['ccdnum'] != 31)
        &
        (data['ccdnum'] != 2)
    )
    data = data[w]
    return data


def read_bleeds(*, fname, ext='bleedtrail', skipmask=0):
    """
    read bleed masks from a file

    Parameters
    ----------
    fname: string
        File to read
    ext: string, optional
        Extension to read, default 'bleedtrail'
    skipmask: integer
        Entries that have these bits set will not be returned
    """

    with fitsio.FITS(fname) as fobj:
        data = fobj[ext].read(lower=True)

    w, = np.where(
        (data['ccdnum'] != 31)
        &
        (data['ccdnum'] != 2)
        &
        ((data['badpix'] & skipmask) == 0)
    )

    data = data[w]
    return data


def read_tile_geom(*, fname, ext='tilegeom'):
    """
    read in the basic tile geometry into an integer map
    with values 1

    Parameters
    ----------
    fname: string
        File to read
    ext: string, optional
        Extension to read, default 'bleedtrail'
    """

    with fitsio.FITS(fname) as fobj:
        data = fobj[ext].read(lower=True)

    return data


def get_sn_edge_mask(indata, trim_pixels=100):
    """
    add extra boundary mask, used for SN fields

    Parameters
    ----------
    trim_pixels: int
        Number of pixels to trim
    """

    data = indata[0]

    # ra4, dec4       ra3, dec3
    #
    #
    # ra1, dec1       ra2, dec2
    fac = 0.263/3600.0
    off = trim_pixels*fac

    value = 256
    polys = []

    allra = np.array([
        data['rac1'],
        data['rac2'],
        data['rac3'],
        data['rac4'],
    ])
    alldec = np.array([
        data['decc1'],
        data['decc2'],
        data['decc3'],
        data['decc4'],
    ])

    ramin = allra.min()
    decmin = alldec.min()
    ramax = allra.max()
    decmax = alldec.max()

    # left side
    ra = [
        ramin,
        ramin + off,
        ramin + off,
        ramin,
    ]
    dec = [
        decmin,
        decmin,
        decmax,
        decmax,
    ]
    ply = hs.Polygon(ra=ra, dec=dec, value=value)
    polys.append(ply)

    # right side
    ra = [
        ramax - off,
        ramax,
        ramax,
        ramax - off,
    ]
    dec = [
        decmin,
        decmin,
        decmax,
        decmax,
    ]
    ply = hs.Polygon(ra=ra, dec=dec, value=value)
    polys.append(ply)

    # bottom
    ra = [
        ramin,
        ramax,
        ramax,
        ramin,
    ]
    dec = [
        decmin,
        decmin,
        decmin + off,
        decmin + off,
    ]
    ply = hs.Polygon(ra=ra, dec=dec, value=value)
    polys.append(ply)

    # top
    ra = [
        ramin,
        ramax,
        ramax,
        ramin,
    ]
    dec = [
        decmax,
        decmax,
        decmax - off,
        decmax - off,
    ]
    ply = hs.Polygon(ra=ra, dec=dec, value=value)
    polys.append(ply)

    return polys


def load_circles(*, data, values, bands=None, expand=1.0):
    """
    load a set of circle objects from the input data

    Parameters
    ----------
    data: array with fields
        Must have ra, dec, radius, badpix fields
    expand: number, optional
        Factor by which to expand star masks, default 1
    """

    has_bands = 'band' in data.dtype.names
    if bands is not None and not has_bands:
        raise ValueError('bands= sent but no bands present in input data')

    try:
        nv = len(values)
    except TypeError:
        values = [values]*data.size

    circles = []
    for i in range(data.size):

        idata = data[i]

        if bands is not None:
            band = idata['band'].strip()
            if band not in bands:
                continue

        radius = idata['radius']/3600.0
        radius *= expand

        circle = hs.Circle(
            ra=idata['ra'],
            dec=idata['dec'],
            radius=radius,
            value=values[i],
        )
        circles.append(circle)

    return circles


def load_polygons(*, data, values, bands=None):
    """
    load a set of polygons (rectangles) from the input
    data.  EDGEBLEED is skipped for 'u' and 'Y' bands

    Parameters
    ----------
    data: array with fields
        Must have
        ra_1, dec_1
        ra_2, dec_2
        ra_3, dec_3
        ra_4, dec_4
        badpix
    """

    has_bands = 'band' in data.dtype.names
    if bands is not None and not has_bands:
        raise ValueError('bands= sent but no bands present in input data')

    EDGEBLEED = 128

    polygons = []
    for i in range(data.size):

        idata = data[i]

        if bands is not None:
            band = idata['band'].strip()
            if band not in bands:
                continue

        if has_bands and band in ['u', 'Y'] and idata['badpix'] == EDGEBLEED:
            print('skipping %s EDGEBLEED' % band)
            continue

        ra, dec = _extract_vert(idata)

        polygon = hs.Polygon(
            ra=ra,
            dec=dec,
            value=values[i],
        )
        polygons.append(polygon)

    return polygons


def _extract_vert(idata):
    if 'ra_1' in idata.dtype.names:
        ra = [
            idata['ra_1'],
            idata['ra_2'],
            idata['ra_3'],
            idata['ra_4'],
        ]
        dec = [
            idata['dec_1'],
            idata['dec_2'],
            idata['dec_3'],
            idata['dec_4'],
        ]
    else:
        ra = [
            idata['rac1'],
            idata['rac2'],
            idata['rac3'],
            idata['rac4'],
        ]
        dec = [
            idata['decc1'],
            idata['decc2'],
            idata['decc3'],
            idata['decc4'],
        ]

    return ra, dec
