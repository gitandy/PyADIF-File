#!/usr/bin/env python
# Copyright 2025 by Andreas Schawo <df1asc@darc.de>, licensed under CC BY-SA 4.0

import os
import sys
import json

from adif_file import adi

NUSHELL_VERSION = 0, 102
PLUGIN_VERSION = '0.1.1'

__call_command__ = ''
__call_id__ = None
__call_span__ = None
__adi_table__ = []
__adi_doc__ = ''


def signatures():
    """
    Format the plugin signature
    """
    return {
        'Signature': [
            {
                'sig': {
                    'name': 'to adi',
                    'description': 'Convert table to ADIF format',
                    'extra_description': '',
                    'required_positional': [],
                    'optional_positional': [],
                    'named': [
                        {
                            'long': 'help',
                            'short': 'h',
                            'arg': None,
                            'required': False,
                            'desc': 'Display the help message for this command',
                        },
                        {
                            'long': 'noheader',
                            'short': 'n',
                            'arg': None,
                            'required': False,
                            'desc': 'Do not output a header',
                        },
                    ],
                    'input_output_types': [['Any', 'String']],
                    'allow_variants_without_examples': True,
                    'search_terms': ['Python', 'ADIF'],
                    'is_filter': False,
                    'creates_scope': False,
                    'allows_unknown_args': False,
                    'category': 'Experimental',
                },
                'examples': [],
            },
            {
                'sig': {
                    'name': 'from adi',
                    'description': 'Convert ADIF format to table',
                    'extra_description': '',
                    'required_positional': [],
                    'optional_positional': [],
                    'named': [
                        {
                            'long': 'help',
                            'short': 'h',
                            'arg': None,
                            'required': False,
                            'desc': 'Display the help message for this command',
                        },
                    ],
                    'input_output_types': [['String', 'Any']],
                    'allow_variants_without_examples': True,
                    'search_terms': ['Python', 'ADIF'],
                    'is_filter': False,
                    'creates_scope': False,
                    'allows_unknown_args': False,
                    'category': 'Experimental',
                },
                'examples': [],
            }
        ]
    }


def adif_date2iso(date: str) -> str:
    """Convert ADIF date to iso format"""
    if not date or len(date) != 8:
        return date
    return date[:4] + '-' + date[4:6] + '-' + date[6:8]


def adif_time2iso(time: str) -> str:
    if not time or len(time) not in (4, 6):
        return time
    return time[:2] + ':' + time[2:4] + (':' + time[4:6] if len(time) == 6 else '')


def process_to_adi(data):
    """Convert table data to ADIF string"""
    global __adi_doc__

    try:
        rec_data = data['val']
        record = {}
        for f in rec_data:
            for t in rec_data[f]:
                val = str(rec_data[f][t]['val'])
                if 'DATE' in f.upper():
                    val = val.replace('-', '')
                elif f.upper().startswith('TIME'):
                    val = val.replace(':', '')
                elif 'CALL' in f.upper():
                    val = val.upper()
                record[f] = val

        __adi_doc__ += adi.dumps({'RECORDS': [record]}, linebreaks=False) + '\n'
    except KeyError:
        write_error(__call_id__, 'only table input data is supported', __call_span__)
        sys.exit(1)


def process_from_adi():
    """Convert ADIF formated data to table"""
    global __adi_table__

    try:
        fieldnames = ['QSO_DATE', 'TIME_ON', 'CALL', 'BAND', 'MODE', 'RST_SENT', 'RST_RCVD']
        for i, rec in enumerate(adi.loadi(__adi_doc__)):
            if i == 0:
                continue
            for k in rec.keys():
                if k not in fieldnames:
                    fieldnames.append(k)

        for i, rec in enumerate(adi.loadi(__adi_doc__)):
            if i == 0:
                continue
            val = {}
            for f in fieldnames:
                rec_val: str = rec[f] if f in rec else ''
                if 'DATE' in f:
                    rec_val = adif_date2iso(rec_val)
                elif f.startswith('TIME'):
                    rec_val = adif_time2iso(rec_val)
                elif 'CALL' in f:
                    rec_val = rec_val.upper()

                val[f] = {'String': {'val': rec_val, 'span': __call_span__}}

            __adi_table__.append({'Record':
                {
                    'val': val,
                    'span': __call_span__,
                }
            })
    except IndexError as exc:
        write_error(__call_id__, f'malformed ADIF format: {exc}', __call_span__)
        sys.exit(1)


def tell_nushell_encoding():
    sys.stdout.write(chr(4))
    for ch in 'json':
        sys.stdout.write(chr(ord(ch)))
    sys.stdout.flush()


def tell_nushell_hello(nu_version=''):
    """
    A `Hello` message is required at startup to inform nushell of the protocol capabilities and
    compatibility of the plugin. The version specified should be the version of nushell that this
    plugin was tested and developed against.
    """
    hello = {
        'Hello': {
            'protocol': 'nu-plugin',  # always this value
            'version': nu_version,
            'features': [],
        }
    }
    sys.stdout.write(json.dumps(hello))
    sys.stdout.write('\n')
    sys.stdout.flush()


def write_response(call_id, response):
    """
    Format a response to a plugin call.
    """
    wrapped_response = {
        'CallResponse': [
            call_id,
            response,
        ]
    }
    sys.stdout.write(json.dumps(wrapped_response))
    sys.stdout.write('\n')
    sys.stdout.flush()


def write_error(call_id, text, span=None):
    """
    Format error response to nushell.
    """
    error = (
        {
            'Error': {
                'msg': 'ADI plugin error',
                'labels': [
                    {
                        'text': text,
                        'span': span,
                    }
                ],
            }
        }
        if span is not None
        else {
            'Error': {
                'msg': 'ADI plugin error',
                'help': text,
            }
        }
    )
    write_response(call_id, error)


def handle_input(input_data):
    global __call_command__, __call_id__, __call_span__, __adi_doc__, __adi_table__

    if 'Hello' in input_data:
        match input_data:
            case {'Hello': {'version': nu_ver}}:
                major, minor, patch = [int(part) for part in nu_ver.split('.')]
                if major == NUSHELL_VERSION[0] and minor >= NUSHELL_VERSION[1]:
                    return
                else:
                    write_error(__call_id__,
                                f'Nushell version {nu_ver} does not match. Required Nushell >= {NUSHELL_VERSION}')

    elif input_data == 'Goodbye':
        exit(0)
    elif 'Call' in input_data:
        [call_id, plugin_call] = input_data['Call']
        if plugin_call == 'Metadata':
            write_response(
                call_id,
                {
                    'Metadata': {
                        'version': PLUGIN_VERSION,
                    }
                },
            )
        elif plugin_call == 'Signature':
            write_response(call_id, signatures())
        elif 'Run' in plugin_call:
            __call_command__ = plugin_call['Run']['name']
            __call_id__ = call_id
            __call_span__ = plugin_call['Run']['call']['head']

            if __call_command__ == 'to adi':
                header = True
                for p in plugin_call['Run']['call']['named']:
                    if p[0]['item'] == 'noheader':
                        header = False

                if header:
                    __adi_doc__ = adi.dumpi(
                        {'HEADER': {
                            'PROGRAMID': 'ADIF Nushell-Plugin',
                            'PROGRAMVERSION': PLUGIN_VERSION,
                        }},
                        comment='Exported by ADIF Nushell-Plugin',
                        linebreaks=False).__next__() + '\n'
        else:
            write_error(call_id, 'Operation not supported: ' + str(plugin_call))
    elif 'Data' in input_data:
        if __call_command__ == 'to adi':
            match input_data['Data']:
                case [_, {'List': {'Record': data}}]:
                    process_to_adi(data)
        elif __call_command__ == 'from adi':
            match input_data['Data']:
                case [_, {'Raw': {'Ok': data}}]:
                    __adi_doc__ += bytes(data).decode('utf8')
                case [_, {'Raw': {'Err': text}}]:
                    write_error(__call_id__, text, __call_span__)
        else:
            sys.stderr.write(f'Data for unknown call name: "{__call_command__}"')
            sys.stderr.write('Data: ' + str(input_data['Data']) + '\n')
    elif 'End' in input_data:
        if __call_command__ == 'to adi':
            val = {
                'String': {
                    'val': __adi_doc__,
                    'span': __call_span__,
                },
            }
        elif __call_command__ == 'from adi':
            process_from_adi()
            val = {
                'List': {
                    'vals': __adi_table__,
                    'span': __call_span__,
                },
            }
        else:
            sys.stderr.write(f'End for unknown call name: "{__call_command__}"')
            exit(1)

        p_data = {
            'PipelineData': {
                'Value': [
                    val,
                    None,
                ]
            }
        }
        write_response(__call_id__, p_data)
    elif 'Signal' in input_data:
        if input_data['Signal'] == 'Reset':
            __call_command__ = ''
            __call_id__ = None
            __call_span__ = None
            __adi_table__ = []
            __adi_doc__ = ''
        elif input_data['Signal'] == 'Interrupt':
            exit(1)
    else:
        sys.stderr.write('Unknown message: ' + str(input_data) + '\n')
        exit(1)


def plugin(nu_version=''):
    tell_nushell_encoding()
    tell_nushell_hello(nu_version)
    for line in sys.stdin:
        handle_input(json.loads(line))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--stdio':
        plugin(os.environ.get('NU_VERSION', ''))
    else:
        print('Run me from inside nushell to unlock the magic!')
