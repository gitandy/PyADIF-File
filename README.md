PyADIF-File
===========

[![PyPI Package](https://img.shields.io/pypi/v/pyadif_file?color=%2334D058&label=PyPI%20Package)](https://pypi.org/project/pyadif_file)
[![Test & Lint](https://github.com/gitandy/PyADIF-File/actions/workflows/python-test.yml/badge.svg)](https://github.com/gitandy/PyADIF-File/actions/workflows/python-test.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/pyadif_file.svg?color=%2334D058&label=Python)](https://pypi.org/project/pyadif_file)

Author: Andreas Schawo, DF1ASC 
([HamQTH](http://www.hamqth.com/DF1ASC), [eQSL](http://www.eqsl.cc/Member.cfm?DF1ASC))

Convert [ADIF](https://adif.org/) ADI content (ham radio QSO logs) to dictionary and vice versa

The required/resulting dictionary format for ADI is

    {
        'HEADER': 
            {Header param: Value,
             'USERDEFS': [list of user definitions]},
        'RECORDS': [list of records]
    }

For ADI the header or each record is/must be a dictionary in the format
    
    {
        ADIF parameter name: Text value,
    }

For ADI a user definition is a dictionary of
    
    {
        'dtype': one char representing the type,
        'userdef': the field definition text
    }

The library also supports ADX import/export as compatible as possible to the ADI part. 
Though it will differ in handling application and user definitions.
It relys on the [ADX schemas](https://adif.org/314/ADIF_314.htm#ADX_Schemas) from adif.org.
For the ADX import there is no validation by default to be able to read fast.

Installation
------------
The package is available via [PyPI](https://pypi.org/project/PyADIF-File/)

    pip install pyadif-file

Usage
-----

For reading and writing files you can use adi.load or adi.dump.
There is a corresponding variant for handling string: adi.loads and adi.dumps.

Here is an example for reading an ADI file:

    from adif_file import adi

    adi_doc = adi.load('qsos.adi')
    for rec in adi_doc['RECORDS']:
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
PyADIF-File &copy; 2023-2025 by Andreas Schawo is licensed under [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/) 

PyADIF-File uses
* xmlschema Copyright (c), 2016-2022, SISSA (Scuola Internazionale Superiore di Studi Avanzati)
* xmltodict Copyright (c), 2012 Martin Blech and individual contributors

