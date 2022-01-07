def make_hyperleda_map(fname, output, nside, radius_factor):
    """
    make a healsparse map for hyperleda, trimming to the DES area

    Parameters
    ----------
    fname: str
        Path to the catalog
    output: str
        Output file path
    nside: int
        Nside for the map
    radius_factor: float
        factor by which to dilate the radii listed in the hyperleda catalog
    """
    data = _read_hyperleda_catalog(fname)
    hmap = _make_map(data=data, radius_factor=radius_factor)
    print('writing:', output)
    hmap.write(output, clobber=True)


def _make_map(data, radius_factor):
    import healsparse
    import numpy as np
    from tqdm import tqdm
    from esutil.numpy_util import between

    circles = []
    for objdata in tqdm(data):
        if between(objdata['dej2000'], -75, 10) and (
            between(objdata['raj2000'], 0, 120) or
            between(objdata['raj2000'], 295, 360)
        ):
            circle = healsparse.geom.Circle(
                ra=objdata['raj2000'],
                dec=objdata['dej2000'],
                radius=objdata['radius_degrees'] * radius_factor,
                value=1,
            )
            circles.append(circle)

    hmap = healsparse.HealSparseMap.make_empty(
        nside_coverage=32,
        nside_sparse=2**14,
        # nside_sparse=2**16,
        dtype=np.int16,
        sentinel=0,
    )
    # hmap = healsparse.HealSparseMap.make_empty(32, 16384, np.int16, sentinel=0)
    healsparse.realize_geom(circles, hmap)
    return hmap


def _read_hyperleda_catalog(fname):
    import numpy as np
    import fitsio
    import esutil as eu

    data = fitsio.read(fname, lower=True)

    # logd25 is log(radius/0.1 arcmin)

    w, = np.where(np.isfinite(data['logd25']))
    data = data[w]

    diameter_arcmin = 0.1 * 10**data['logd25']
    # diameter_arcmin = 0.1 * np.exp(data['logd25'])

    radius_degrees = (diameter_arcmin / 2) / 60

    dt = [('radius_degrees', 'f8')]
    output = eu.numpy_util.add_fields(data, dt)

    output['radius_degrees'] = radius_degrees

    return output


def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='input hyperleda file')
    parser.add_argument('--output', required=True,
                        help='output healsparse map file')
    parser.add_argument('--nside', type=int, default=16384)
    parser.add_argument('--radius-factor', type=float, default=4)
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    main(
        fname=args.input,
        output=args.output,
        nside=args.nside,
        radius_factor=args.radius_factor,
    )
