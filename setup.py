from setuptools import setup

import adif_file

setup(
    name=adif_file.__proj_name__,
    packages=['adif_file'],
    version=adif_file.__version__,
    description=adif_file.__description__,
    url='https://github.com/gitandy/PyADIF-File',
    author=adif_file.__author_name__,
    author_email=adif_file.__author_email__,
    license=adif_file.__copyright__,
    requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Other Audience',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications :: Ham Radio',
        'Topic :: File Formats'
    ]
)
