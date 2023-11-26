PyADIF-File
===========

[![PyPI Package](https://img.shields.io/pypi/v/pyadif_file?color=%2334D058&label=PyPI%20Package)](https://pypi.org/project/pyadif_file)
[![Test & Lint](https://github.com/gitandy/PyADIF-File/actions/workflows/python-test.yml/badge.svg)](https://github.com/gitandy/PyADIF-File/actions/workflows/python-test.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/pyadif_file.svg?color=%2334D058&label=Python)](https://pypi.org/project/pyadif_file)


Convert [ADIF](https://adif.org/) ADI content (ham radio QSO logs) to dictionary and vice versa

The required/resulting dictionary format is

    {
        'HEADER': 
            {Header param: Value,
             'USERDEFS': [list of user definitions]},
        'RECORDS': [list of records]
    }

The header or each record is/must be a dictionary in the format
    
    {
        ADIF parameter name: Text value,
    }

A user definition is a dictionary of
    
    {
        'dtype': one char representing the type,
        'userdef': the field definition text
    }

Installation
------------
The package is available via [PyPI](https://pypi.org/project/PyADIF-File/)

    pip install pyadif-file

Usage
-----

For reading and writing files you can use load_adi or dump_adi.
There is a corresponding variant for handling string: loads_adi and dumps_adi.

Here is an example for reading an ADI file:

    import adif_file as af

    adi = af.load_adi('qsos.adi')
    for rec in adi['RECORDS']:
        if "CALL" in rec:
            print(f'QSO on {rec["QSO_DATE"]} at {rec["TIME_ON"]} with {rec["CALL"]}')

    ====
    QSO on 20231008 at 1145 with DL4BDF
    QSO on 20231008 at 1146 with DL5HJK
    QSO on 20231009 at 1147 with M3KJH
    QSO on 20231010 at 1148 with HB4FDS


### Exporting ADI

If an empty header is provided, the fields are generated with suiting defaults.
Missing header fields are inserted.

Empty record fields and empty records are not exported at all.

*_INTL fields are not exported (see ADIF specification).
If non ASCII characters are used the API raises an Exception.

Source Code
-----------
The source code is available at [GitHub](https://github.com/gitandy/PyADIF-File)

Copyright
---------
DragonLog &copy; 2023 by Andreas Schawo is licensed under [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/) 
