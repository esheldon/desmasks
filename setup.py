from distutils.core import setup


# data_files copies the ups/esutil.table into prefix/ups
setup(
    name='desmasks',
    version='0.1.0',
    description='Code for working with DES masks in healsparse format',
    packages=['desmasks'],
)
