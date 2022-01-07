import glob
from setuptools import setup, find_packages

scripts = glob.glob('bin/*')
scripts = [s for s in scripts if '~' not in s]

# data_files copies the ups/esutil.table into prefix/ups
setup(
    name='desmasks',
    version='0.2.0',
    description='Code for working with DES masks in healsparse format',
    packages=find_packages(),
    scripts=scripts,
)
