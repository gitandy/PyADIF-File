#!/usr/bin/env python

import sys
import csv

from adif_file import adi

CSV_SEPARATOR = ';'


def csv2adi(csv_file: str, adi_file: str, header=True):
    doc = {'RECORDS': []}
    if header:
        doc['HEADER'] = {}

    with open(csv_file) as csv_f:
        for row in csv.DictReader(csv_f, delimiter=CSV_SEPARATOR):
            doc['RECORDS'].append(row)

    adi.dump(adi_file, doc)


def adi2csv(adi_file: str, csv_file: str):
    with open(adi_file) as adi_f:
        adi_str = adi_f.read()

    fieldnames = ['QSO_DATE', 'TIME_ON', 'CALL', 'BAND', 'MODE', 'RST_SENT', 'RST_RCVD']
    for i, rec in enumerate(adi.loadi(adi_str)):
        if i == 0:
            continue
        for k in rec.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    with open(csv_file, 'w', newline='') as csv_f:
        csv_w = csv.DictWriter(csv_f, fieldnames, delimiter=CSV_SEPARATOR)
        csv_w.writeheader()

        for i, rec in enumerate(adi.loadi(adi_str)):
            if i == 0:
                continue
            csv_w.writerow(rec)


if __name__ == '__main__':
    import os

    if len(sys.argv) > 2:
        fin = sys.argv.pop(1)
        fout = sys.argv.pop(1)
        ftype = os.path.splitext(fin)[1]
        if not os.path.isfile(fin):
            sys.exit(f'Unable to read file "{fin}"')

        if ftype == '.csv':
            csv2adi(fin, fout, not (len(sys.argv) > 1 and sys.argv[1] == '-n'))
        elif ftype == '.adi':
            adi2csv(fin, fout)
        else:
            sys.exit(f'Unable to determin filetype from extension "{ftype}".\nUse .adi or .csv files only.')
    else:
        sys.exit(f'Requires an .adi or .csv file as parameter\nUsage: {sys.argv[0]} INPUT OUTPUT [-n]')
