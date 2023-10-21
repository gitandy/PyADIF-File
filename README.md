PyADIF-File
===========
Convert ADIF ADI content to dictionary and vice versa

The required/resulting dictionary format is

    {
        'HEADER': None,
        'RECORDS': [list of records]
    }

The header or each record is/must be a dictionary in the format
    
    {
        ADIF parameter name: Text value,
    }

You have to care about reading/writing the content from/to the file.

Installation
------------
The package is available via PyPI

    pip install adif-file

Exporting ADI
-------------
If an empty header is provided, the fields are generated with suiting defaults.
Missing header fields are inserted.

Empty record fields and records are not exported at all.

*_INTL fields are not exported (see ADIF specification).
If non ASCII characters are used the API raises an Exception.

Copyright
---------
DragonLog &copy; 2023 by Andreas Schawo is licensed under [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/) 