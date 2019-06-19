"""
load the geom from fits tables
"""

import numpy as np
import fitsio
import healsparse as hs


def read_stars(fname, ext='satstars'):
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


def read_bleeds(fname, ext='bleedtrail'):
    """
    read bleed masks from a file

    Parameters
    ----------
    fname: string
        File to read
    ext: string, optional
        Extension to read, default 'bleedtrail'
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


def load_circles(data, expand=1.0):
    """
    load a set of circle objects from the input data

    Parameters
    ----------
    data: array with fields
        Must have ra, dec, radius, badpix fields
    expand: number, optional
        Factor by which to expand star masks, default 1
    """

    circles = []
    for i in range(data.size):

        idata = data[i]

        radius = idata['radius']/3600.0
        radius *= expand
        if 'badpix' not in idata:
            value = 32
        else:
            value = idata['badpix']

        circle = hs.Circle(
            ra=idata['ra'],
            dec=idata['dec'],
            radius=radius,
            value=value,
        )
        circles.append(circle)

    return circles


def load_polygons(data):
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

    EDGEBLEED = 128

    polygons = []
    for i in range(data.size):

        idata = data[i]

        band = idata['band'].strip()

        if band in ['u', 'Y'] and idata['badpix'] == EDGEBLEED:
            print('skipping %s EDGEBLEED' % band)
            continue

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

        polygon = hs.Polygon(
            ra=ra,
            dec=dec,
            value=idata['badpix'],
        )
        polygons.append(polygon)

    return polygons
