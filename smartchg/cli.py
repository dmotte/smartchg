#!/usr/bin/env python3

import argparse
import csv
import sys

from contextlib import ExitStack
from datetime import date
from datetime import datetime as dt
from typing import TextIO


def load_data(file: TextIO, krate: str = 'Open'):
    '''
    Loads data from a CSV file.

    Compatible with Yahoo Finance OHLCV CSV files, in particular
    https://github.com/dmotte/misc/blob/main/python-scripts/ohlcv-fetchers/yahoo-finance.py
    '''
    data = list(csv.DictReader(file))

    for x in data:
        yield {
            'date': dt.strptime(x['Date'], '%Y-%m-%d').date(),
            'rate': float(x[krate]),
        }


def save_data(data: list[dict], file: TextIO, fmt_days: str = '',
              fmt_rate: str = '', fmt_simil: str = ''):
    '''
    Saves data into a CSV file
    '''
    func_days = str if fmt_days == '' else lambda x: fmt_days.format(x)
    func_rate = str if fmt_rate == '' else lambda x: fmt_rate.format(x)
    func_simil = str if fmt_simil == '' else lambda x: fmt_simil.format(x)

    fields = {
        'date': str,
        'days': func_days,

        'rate': func_rate,
        'pred': func_rate,
        'offset': func_rate,

        'upper': func_rate,
        'lower': func_rate,
        'center': func_rate,

        'simil': func_simil,
    }

    print(','.join(fields.keys()), file=file)
    for x in data:
        print(','.join(f(x[k]) for k, f in fields.items()), file=file)


def save_values(data: dict, file: TextIO, fmt_rate: str = '',
                fmt_src: str = '', fmt_dst: str = ''):
    '''
    Saves values into a text file
    '''
    func_rate = str if fmt_rate == '' else lambda x: fmt_rate.format(x)
    func_src = str if fmt_src == '' else lambda x: fmt_src.format(x)
    func_dst = str if fmt_dst == '' else lambda x: fmt_dst.format(x)

    fields = {
        'date_start': str,
        'date_end': str,

        'offset_mean': func_rate,
        'offset_stdev': func_rate,
        'offset_upper': func_rate,
        'offset_lower': func_rate,

        'sugg_src': func_src,
        'sugg_dst': func_dst,
    }

    for k, f in fields.items():
        print(f'{k}={f(data[k])}', file=file)


def compute_stuff(data: list[dict], today: date, lookbehind: int,
                  apy: float, multiplier: float, rate: float, target: float):
    '''
    Computes the output data with statistics and the output values
    '''
    pass  # TODO


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='DCA-based asset exchange algorithm'
    )

    parser.add_argument('file_in', metavar='FILE_IN', type=str,
                        nargs='?', default='-',
                        help='Input file. If set to "-" then stdin is used '
                        '(default: -)')
    parser.add_argument('file_out_data', metavar='FILE_OUT_DATA', type=str,
                        nargs='?', default='-',
                        help='Output file for the CSV data. If set '
                        'to "-" then stdout is used (default: -)')
    parser.add_argument('file_out_values', metavar='FILE_OUT_VALUES', type=str,
                        nargs='?', default='-',
                        help='Output file for the computed values. If set '
                        'to "-" then stdout is used (default: -)')

    # TODO flags
    # - krate
    #
    # - today
    # - lookbehind
    #
    # - apy
    # - multiplier
    # - rate
    # - target
    #
    # - fmt-days
    # - fmt-rate
    # - fmt-simil
    # - fmt-src
    # - fmt-dst

    args = parser.parse_args(argv[1:])

    ############################################################################

    with ExitStack() as stack:
        file_in = (sys.stdin if args.file_in == '-'
                   else stack.enter_context(open(args.file_in, 'r')))
        file_out_data = (sys.stdout if args.file_out_data == '-'
                         else stack.enter_context(
                             open(args.file_out_data, 'w')))
        file_out_values = (sys.stdout if args.file_out_values == '-'
                           else stack.enter_context(
                               open(args.file_out_values, 'w')))

        # TODO

    return 0
