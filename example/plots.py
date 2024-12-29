#!/usr/bin/env python3

import argparse
import csv
import sys

from contextlib import ExitStack
from datetime import datetime as dt
from typing import TextIO

import plotly.express as px


def load_data(file: TextIO):
    '''
    Loads data from a CSV file
    '''
    data = list(csv.DictReader(file))

    for x in data:
        yield {'date': dt.strptime(x['date'], '%Y-%m-%d').date()} | \
            {k: float(x[k]) for k in ['days', 'rate', 'pred', 'offset',
                                      'upper', 'lower', 'center', 'simil']}


def load_values(file: TextIO) -> dict:
    '''
    Loads values from a text file
    '''
    result = {}

    for line in file:
        k, v = line.strip().split('=', 1)

        v = dt.strptime(v, '%Y-%m-%d').date() if k.startswith('date_') \
            else float(v)

        result[k] = v

    return result


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Generate plots based on data computed with smartchg'
    )

    parser.add_argument('file_in_data', metavar='FILE_IN_DATA', type=str,
                        nargs='?', default='-',
                        help='Input file with the CSV data. If set '
                        'to "-" then stdin is used (default: -)')
    parser.add_argument('file_in_values', metavar='FILE_IN_VALUES', type=str,
                        nargs='?', default='-',
                        help='Input file with the computed values. If set '
                        'to "-" then stdin is used (default: -)')

    parser.add_argument('-r', '--plot-rate', action='store_true',
                        help='Generate plot based on rate values')
    parser.add_argument('-o', '--plot-offset', action='store_true',
                        help='Generate plot based on offset values')
    parser.add_argument('-s', '--plot-simil', action='store_true',
                        help='Generate plot based on simil values')

    args = parser.parse_args(argv[1:])

    ############################################################################

    with ExitStack() as stack:
        file_in_data = (sys.stdin if args.file_in_data == '-'
                        else stack.enter_context(
                            open(args.file_in_data, 'r')))
        file_in_values = (sys.stdin if args.file_in_values == '-'
                          else stack.enter_context(
                              open(args.file_in_values, 'r')))
        data = list(load_data(file_in_data))
        values = load_values(file_in_values)

    if args.plot_rate:
        fig = px.line(
            data,
            x='date',
            y=['rate', 'pred', 'upper', 'lower', 'center'],
            template='plotly_dark',
            title='Rate values',
        )
        fig.add_vline(
            annotation_text='today',
            x=dt.combine(data[-1]['date'], dt.min.time()).timestamp() * 1000,
            line_color='#0cc',
        )
        fig.show()

    if args.plot_offset:
        pass  # TODO
        fig.show()

    if args.plot_simil:
        pass  # TODO
        fig.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
