#!/usr/bin/env python3

import io
import textwrap

from datetime import date

from smartchg import load_data, save_data, save_values, compute_stuff


def test_load_data():
    csv = textwrap.dedent('''\
        Date,Open,High,Low,Close,Adj Close,Volume
        2000-01-01,10,15,9,12,12,123
        2000-01-08,12,13.5,10.2,13,13,456
        2000-01-15,13,22.1,13,18.5,18,789
    ''')

    data = list(load_data(io.StringIO(csv)))

    assert data == [
        {'date': date(2000, 1, 1), 'rate': 10},
        {'date': date(2000, 1, 8), 'rate': 12},
        {'date': date(2000, 1, 15), 'rate': 13},
    ]

    data = list(load_data(io.StringIO(csv), krate='Close'))

    assert data == [
        {'date': date(2000, 1, 1), 'rate': 12},
        {'date': date(2000, 1, 8), 'rate': 13},
        {'date': date(2000, 1, 15), 'rate': 18.5},
    ]


def test_save_data():
    pass  # TODO


def test_save_values():
    pass  # TODO


def test_compute_stuff():
    pass  # TODO
