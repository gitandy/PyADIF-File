from pprint import pp
from adif_file import adi

if __name__ == '__main__':
    adi_data = adi.load('example.adi')

    print('---Print QSO data for QSO with callsign---')
    for rec in adi_data['RECORDS']:
        if 'CALL' in rec:
            print(f'QSO on {rec["QSO_DATE"]} {rec["TIME_ON"]} with {rec["CALL"]}')

    print('\n---PPrint whole content---')

    pp(adi_data)
