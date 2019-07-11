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


def read_imgdata(*, fname, ext='imgdata', bands=None, trim=True):
    """
    read from the imgdata extension, which holds the polygons
    representing all ccds that went into coadds

    Parameters
    ----------
    fname: string
        File to read
    ext: string, optional
        Extension to read, default 'imgdata'
    trim: bool
        If True, trim to intersection of all circles
    """

    with fitsio.FITS(fname) as fobj:
        data = fobj[ext].read(lower=True)

    if bands is not None:
        dbands = np.char.rstrip(data['band'])
        for i in range(len(bands)):
            tlogic = dbands == bands[i]
            if i == 0:
                logic = tlogic
            else:
                logic = logic | tlogic
        w, = np.where(logic)
        if w.size == 0:
            raise ValueError('none matched bands %s' % str(bands))

        data = data[w]

    if trim:
        minra = max(data['rac1'].max(), data['rac2'].max())
        maxra = min(data['rac3'].min(), data['rac4'].min())

        mindec = max(data['decc2'].max(), data['decc3'].max())
        maxdec = min(data['decc1'].min(), data['decc4'].min())

        data = data[0:0+1]
        data['rac1'] = minra
        data['rac2'] = minra
        data['rac3'] = maxra
        data['rac4'] = maxra

        data['decc1'] = maxdec
        data['decc2'] = mindec
        data['decc3'] = mindec
        data['decc4'] = maxdec

    return data


def get_trimmed_tile_geom(indata, trim_pixels=100):
    """
    add extra boundary mask, used for COSMOS

    Parameters
    ----------
    trim_pixels: int
        Number of pixels to trim, default 100
    """

    data = indata.copy()

    fac = 0.263/3600.0
    off = trim_pixels*fac

    data['rac1'] -= off
    data['rac2'] += off
    data['rac3'] += off
    data['rac4'] -= off

    data['decc1'] += off
    data['decc2'] += off
    data['decc3'] -= off
    data['decc4'] -= off

    return data


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

    values = _extract_values(values, data.size)

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

    values = _extract_values(values, data.size)

    has_bands = 'band' in data.dtype.names
    has_badpix = 'badpix' in data.dtype.names
    if bands is not None and not has_bands:
        raise ValueError('bands= sent but no bands present in input data')

    EDGEBLEED = 128

    polygons = []
    for i in range(data.size):

        idata = data[i]

        if has_bands and bands is not None:
            band = idata['band'].strip()
            if band not in bands:
                continue

        if (has_bands and
                has_badpix and
                band in ['u', 'Y'] and
                idata['badpix'] == EDGEBLEED):

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


def _extract_values(values, n):
    try:
        nv = len(values)
        if nv != n:
            raise ValueError('values must be scalar or length '
                             'of data, got %d instead of %d' % (nv, n))
    except TypeError:
        values = [values]*n

    return values
