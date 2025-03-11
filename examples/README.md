PyADIF-File Examples
====================
For all examples it is expected that PyADIF-File is installed properly in the system wide site-packages 
and you run Python >= 3.10 as well

    # pip install pyadif-file

**Have fun!**


gen_big_adi
-----------
This tool generates huge ADIF files in ADI or ADX format.
This files can be used for performance testing your code.

    gen_big_adi.py [NUMBER_QSOS] [-x]

Per default it generates a 1000 QSO sized ADI file 

    # gen_big_adi.py -x 10000

This will generate a 10000 QSO ADX file.


csv2adi
-------
This tool converts an ADI file to CSV or vice versa.
As CSV field seperator `;` is used.

    csv2adi.py [INPUT] [OUTPUT] [-n]

Generate ADI from CSV (use `-n` to omit a header)

    # csv2adi.py file.csv file.adi

Generate CSV from ADI

    # csv2adi.py file.adi file.csv


nu_plugin_adi
-------------
This one provides a plugin to use ADI format inside [Nushell](https://www.nushell.sh/) easily.

The plugin provides `to adi` and `from adi`.

It's just the start of development so do not be afraid of some misbehaviour.
I learned Nushell just two weeks ago and couldn't resist.

Register plugin in running Nushell

    # plugin add ./nu_plugin_adi.py
    # plugin use adi

Show the first 10 QSOs from ADI file as table (`from adi` is automatically run from `open` on .adi files)
    
    # open file.adi | first 10

Once information is represented as a table, all Nushell doors are wide open...

Find all QSO with a portable station in ADI, select some columns only 
and store them to CSV (using non default separator `;`)

    # open file.adi | where CALL =~ "/P" | select QSO_DATE TIME_ON CALL BAND MODE | to csv -s ";" | save file.csv

Convert CSV to ADI (using non default separator `;`)

    # open file.csv --raw | from csv -s ";" | to adi | save file.adi

You get it? Be amazed! I am! Totally!
