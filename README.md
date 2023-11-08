PyADIF-File
===========

[![Python test & lint](https://github.com/gitandy/PyADIF-File/actions/workflows/python-test.yml/badge.svg)](https://github.com/gitandy/PyADIF-File/actions/workflows/python-test.yml)

Convert ADIF ADI content (ham radio QSO logs) to dictionary and vice versa

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

You have to care about reading/writing the content from/to the file.

Installation
------------
The package is available via [PyPI](https://pypi.org/project/PyADIF-File/)

    pip install pyadif-file

Exporting ADI
-------------
If an empty header is provided, the fields are generated with suiting defaults.
Missing header fields are inserted.

Empty record fields and records are not exported at all.

*_INTL fields are not exported (see ADIF specification).
If non ASCII characters are used the API raises an Exception.

Source Code
-----------
The source code is available at [GitHub](https://github.com/gitandy/PyADIF-File)

Copyright
---------
DragonLog &copy; 2023 by Andreas Schawo is licensed under [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/) 
