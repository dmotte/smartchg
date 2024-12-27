#!/usr/bin/env python3

import argparse
import csv
import statistics
import sys

from contextlib import ExitStack
from datetime import date
from datetime import datetime as dt
from datetime import timedelta
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
        'date_thresh': str,

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
                  apy: float, multiplier: float, rate: float,
                  target: float) -> tuple[list[dict], dict]:
    '''
    Computes the output data with statistics and the output values
    '''
    # - values['date_thresh']: minimum date at which the data can start

    date_thresh = today - timedelta(days=lookbehind)
    data = [x.copy() for x in data
            if x['date'] >= date_thresh and x['date'] < today]

    first = data[0]

    current = {'date': today, 'rate': rate}
    data.append(current)

    for entry in data:
        # - entry['days']: days passed since the first entry
        # - entry['pred']: rate prediction calculated using the expected APY
        # - entry['offset']: difference between the actual rate and pred

        entry['days'] = (entry['date'] - first['date']
                         ).total_seconds() / 60 / 60 / 24
        entry['pred'] = first['rate'] * (1 + apy) ** (entry['days'] / 365)
        entry['offset'] = entry['rate'] - entry['pred']

    # - values['offset_mean']: mean of all the past (data[:-1]) offsets
    # - values['offset_stdev']: Standard Deviation of all the past (data[:-1])
    #   offsets (which also equals to the stdev of all the past rate values)

    offset_mean = statistics.mean(x['offset'] for x in data[:-1])
    offset_stdev = statistics.stdev(x['offset'] for x in data[:-1])

    # - values['offset_upper']: upper "pseudo-bollinger" of the offset values
    # - values['offset_lower']: lower "pseudo-bollinger" of the offset values

    # Inspired by this article:
    # https://www.learnpythonwithrune.org/pandas-calculate-and-plot-the-bollinger-bands-for-a-stock/

    offset_upper = offset_mean + 2 * offset_stdev
    offset_lower = offset_mean - 2 * offset_stdev

    for entry in data:
        # - entry['upper']: upper "pseudo-bollinger" for the rate value
        # - entry['lower']: lower "pseudo-bollinger" for the rate value
        # - entry['center']: center between the two "pseudo-bollinger" values
        # - entry['simil']: how much entry['offset'] and offset_mean are
        #   similar. For example:
        #   - if entry['offset'] == offset_mean then --> simil = 0
        #   - if entry['offset'] == offset_upper then --> simil = 1
        #   - if entry['offset'] == offset_lower then --> simil = -1

        entry['upper'] = entry['pred'] + offset_upper
        entry['lower'] = entry['pred'] + offset_lower
        entry['center'] = entry['pred'] + offset_mean
        entry['simil'] = (entry['offset'] - offset_mean) / (2 * offset_stdev)

    # - values['sugg_src']: suggested amount of SRC to be exchanged for DST
    # - values['sugg_dst']: suggested amount of DST to be bought with SRC

    # These values are higher when DST/SRC is low

    sugg_src = target * (1 - current['simil'] * multiplier)
    sugg_dst = sugg_src / rate

    values = {
        'date_thresh': date_thresh,

        'offset_mean': offset_mean,
        'offset_stdev': offset_stdev,
        'offset_upper': offset_upper,
        'offset_lower': offset_lower,

        'sugg_src': sugg_src,
        'sugg_dst': sugg_dst,
    }

    return data, values


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
