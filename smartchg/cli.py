#!/usr/bin/env python3

import argparse
import csv
import sys

from contextlib import ExitStack
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
    # - fmt-...

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
