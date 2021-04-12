"""
load the geom from ds9 region files converted to sky coords
"""

import os
import numpy as np
import healsparse as hs

STAR = 32
TRAIL = 64


def load_regions(fname, doplot=False, verbose=False, **kw):
    """
    load circles and polygons from a converted ds9 region file

    The file must have been converted to sky coords

    Parameters
    ----------
    fname: string
        File to read
    doplot: bool
        If set, make a plot
    **kw keywords for the plotting
    """
    print('reading geom from:', fname)
    with open(fname) as fobj:

        circles = []
        polygons = []

        for line in fobj:
            line = line.strip()

            if line[:6] == 'circle':
                circles.append(extract_circle(line))
            elif line[:7] == 'polygon':
                polygons.append(extract_polygon(line))
            else:
                continue

    if verbose:
        for circle in circles:
            print('circle:', circle)

        for polygon in polygons:
            print('polygon:', polygon)

    allgeom = circles + polygons

    if doplot:
        from .plotting import plotrand

        nside = 2**17
        smap = hs.HealSparseMap.make_empty(
            nside_coverage=32,
            nside_sparse=nside,
            dtype=np.int16,
            sentinel=0,
        )
        hs.realize_geom(allgeom, smap)

        nrand = 100000
        plt = plotrand(
            smap,
            nrand,
            randpix=False,
            by_val=True,
            show=False,
            title=os.path.basename(fname),
        )
        return plt

    return allgeom


class ExtractorBase(object):
    """
    base class for extractor
    """
    def __init__(self, *, line, value):
        self.value = value
        lb = line.find('(')
        rb = line.find(')')

        data = line[lb+1:rb].split(',')
        self.data = np.array([float(v) for v in data])
        self._extract()

    def get_geom(self):
        """
        get the geometric primitive, either a healsparse Circle or Polygon
        """
        return self._geom


class CircleExtractor(ExtractorBase):
    """
    class to extract a circle
    """
    def _extract(self):
        ra = self.data[0]
        dec = self.data[1]
        radius = self.data[2]

        self._geom = hs.Circle(
            ra=ra,
            dec=dec,
            radius=radius,
            value=self.value,
        )


class PolygonExtractor(ExtractorBase):
    """
    class to extract a polygon
    """
    def _extract(self):

        ra = []
        dec = []

        npair = len(self.data)//2

        ra = np.zeros(npair)
        dec = np.zeros(npair)

        for i in range(npair):
            ira = i*2
            idec = i*2 + 1

            ra[i] = self.data[ira]
            dec[i] = self.data[idec]

        self._geom = hs.Polygon(
            ra=ra,
            dec=dec,
            value=self.value,
        )


def extract_circle(line):
    ce = CircleExtractor(line=line, value=STAR)
    return ce.get_geom()


def extract_polygon(line):
    pe = PolygonExtractor(line=line, value=TRAIL)
    return pe.get_geom()
