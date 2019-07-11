import os


def _extract_mask_tilename(tilename_full):
    """
    mask files don't have reqnum/attnum
    """
    if '_r' in tilename_full:
        tilename = '_'.join(tilename_full.split('_')[0:2])
    else:
        tilename = tilename_full

    return tilename


def get_mask_dir():
    """
    get the collated file name
    """
    bdir = os.environ['MEDS_DIR']
    return os.path.join(
        bdir,
        'masks',
        'healsparse',
    )


def get_mask_file(tilename_full):
    """
    get the mask file name.

    Parameters
    ----------
    tilename: string
        Either the basic tilename such as SN-C3_C10
        or with reqnum/attnum SN-C3_C10_r3688p01
    """
    d = get_mask_dir()

    # without reqnum etc.
    mask_tilename = _extract_mask_tilename(tilename_full)

    return os.path.join(d, '%s-griz-healsparse.fits' % mask_tilename)


def get_bounds_file(tilename_full):
    """
    get the healsparse bounds map file name.

    Parameters
    ----------
    tilename: string
        Either the basic tilename such as SN-C3_C10
        or with reqnum/attnum SN-C3_C10_r3688p01
    """
    d = get_mask_dir()

    # without reqnum etc.
    mask_tilename = _extract_mask_tilename(tilename_full)

    return os.path.join(d, '%s-griz-bounds-healsparse.fits' % mask_tilename)
