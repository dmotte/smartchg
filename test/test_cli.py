#!/usr/bin/env python3

import io
import textwrap

import pytest

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
    data = [
        {'date': date(2020, 8, 13), 'rate': 116.08,
         'days': 0, 'pred': 116.08, 'offset': 0,
         'upper': 119.61203664986661, 'lower': 115.32909946584198,
         'center': 117.4705680578543, 'simil': -0.649352534536865},
        {'date': date(2020, 9, 13), 'rate': 118.45,
         'days': 31, 'pred': 117.02346213527241, 'offset': 1.4265378647275924,
         'upper': 120.55549878513902, 'lower': 116.27256160111439,
         'center': 118.4140301931267, 'simil': 0.016796794035397015},
        {'date': date(2020, 10, 13), 'rate': 118.62,
         'days': 61, 'pred': 117.94379048751321, 'offset': 0.6762095124867926,
         'upper': 121.47582713737982, 'lower': 117.19288995335519,
         'center': 119.33435854536751, 'simil': -0.3335834800622602},
        {'date': date(2020, 11, 13), 'rate': 121.34,
         'days': 92, 'pred': 118.90240093216751, 'offset': 2.437599067832494,
         'upper': 122.43443758203412, 'lower': 118.15150039800949,
         'center': 120.2929689900218, 'simil': 0.48893129410519126},
        {'date': date(2020, 12, 13), 'rate': 122.25,
         'days': 122, 'pred': 119.83750615577543, 'offset': 2.4124938442245707,
         'upper': 123.36954280564204, 'lower': 119.08660562161741,
         'center': 121.22807421362972, 'simil': 0.4772079264585371},
        {'date': date(2021, 1, 5), 'rate': 125,
         'days': 145, 'pred': 120.55939749074545, 'offset': 4.440602509254546,
         'upper': 124.09143414061207, 'lower': 119.80849695658743,
         'center': 121.94996554859975, 'simil': 1.4242723254391365},
    ]

    headers_line = 'date,days,rate,pred,offset,upper,lower,center,simil'

    csv = '\n'.join([
        headers_line,
        '2020-08-13,0,116.08,116.08,0,119.61203664986661,115.32909946584198,'
        '117.4705680578543,-0.649352534536865',
        '2020-09-13,31,118.45,117.02346213527241,1.4265378647275924,'
        '120.55549878513902,116.27256160111439,118.4140301931267,'
        '0.016796794035397015',
        '2020-10-13,61,118.62,117.94379048751321,0.6762095124867926,'
        '121.47582713737982,117.19288995335519,119.33435854536751,'
        '-0.3335834800622602',
        '2020-11-13,92,121.34,118.90240093216751,2.437599067832494,'
        '122.43443758203412,118.15150039800949,120.2929689900218,'
        '0.48893129410519126',
        '2020-12-13,122,122.25,119.83750615577543,2.4124938442245707,'
        '123.36954280564204,119.08660562161741,121.22807421362972,'
        '0.4772079264585371',
        '2021-01-05,145,125,120.55939749074545,4.440602509254546,'
        '124.09143414061207,119.80849695658743,121.94996554859975,'
        '1.4242723254391365',
    ]) + '\n'

    buf = io.StringIO()
    save_data(data, buf)
    buf.seek(0)

    assert buf.read() == csv

    csv = '\n'.join([
        headers_line,
        '2020-08-13,0.00,116.080,116.080,0.000,119.612,115.329,117.471,-0.6494',
        '2020-09-13,31.00,118.450,117.023,1.427,120.555,116.273,118.414,0.0168',
        '2020-10-13,61.00,118.620,117.944,0.676,121.476,117.193,119.334,-0.3336',
        '2020-11-13,92.00,121.340,118.902,2.438,122.434,118.152,120.293,0.4889',
        '2020-12-13,122.00,122.250,119.838,2.412,123.370,119.087,121.228,0.4772',
        '2021-01-05,145.00,125.000,120.559,4.441,124.091,119.808,121.950,1.4243',
    ]) + '\n'

    buf = io.StringIO()
    save_data(data, buf, '{:.2f}', '{:.3f}', '{:.4f}')
    buf.seek(0)

    assert buf.read() == csv


def test_save_values():
    values = {
        'date_thresh': date(2020, 8, 8),

        'offset_mean': 1.3905680578542898,
        'offset_stdev': 1.0707342960061585,
        'offset_upper': 3.532036649866607,
        'offset_lower': -0.7509005341580273,

        'sugg_src': 857.5727674560864,
        'sugg_dst': 6.860582139648691,
    }

    txt = textwrap.dedent('''\
        date_thresh=2020-08-08
        offset_mean=1.3905680578542898
        offset_stdev=1.0707342960061585
        offset_upper=3.532036649866607
        offset_lower=-0.7509005341580273
        sugg_src=857.5727674560864
        sugg_dst=6.860582139648691
    ''')

    buf = io.StringIO()
    save_values(values, buf)
    buf.seek(0)

    assert buf.read() == txt

    txt = textwrap.dedent('''\
        date_thresh=2020-08-08
        offset_mean=1.39
        offset_stdev=1.07
        offset_upper=3.53
        offset_lower=-0.75
        sugg_src=857.573
        sugg_dst=6.8606
    ''')

    buf = io.StringIO()
    save_values(values, buf, '{:.2f}', '{:.3f}', '{:.4f}')
    buf.seek(0)

    assert buf.read() == txt


def test_compute_stuff():
    data_in_orig = [
        {'date': date(2020, 1, 13), 'rate': 104.04},
        {'date': date(2020, 2, 13), 'rate': 103.50},
        {'date': date(2020, 3, 13), 'rate': 105.77},
        {'date': date(2020, 4, 13), 'rate': 106.71},
        {'date': date(2020, 5, 13), 'rate': 108.48},
        {'date': date(2020, 6, 13), 'rate': 111.59},
        {'date': date(2020, 7, 13), 'rate': 116.04},
        {'date': date(2020, 8, 13), 'rate': 116.08},
        {'date': date(2020, 9, 13), 'rate': 118.45},
        {'date': date(2020, 10, 13), 'rate': 118.62},
        {'date': date(2020, 11, 13), 'rate': 121.34},
        {'date': date(2020, 12, 13), 'rate': 122.25},
    ]

    data_out_expected = [
        {'date': date(2020, 8, 13), 'rate': 116.08,
         'days': 0, 'pred': 116.08, 'offset': 0,
         'upper': 119.61203664986661, 'lower': 115.32909946584198,
         'center': 117.4705680578543, 'simil': -0.649352534536865},
        {'date': date(2020, 9, 13), 'rate': 118.45,
         'days': 31, 'pred': 117.02346213527241, 'offset': 1.4265378647275924,
         'upper': 120.55549878513902, 'lower': 116.27256160111439,
         'center': 118.4140301931267, 'simil': 0.016796794035397015},
        {'date': date(2020, 10, 13), 'rate': 118.62,
         'days': 61, 'pred': 117.94379048751321, 'offset': 0.6762095124867926,
         'upper': 121.47582713737982, 'lower': 117.19288995335519,
         'center': 119.33435854536751, 'simil': -0.3335834800622602},
        {'date': date(2020, 11, 13), 'rate': 121.34,
         'days': 92, 'pred': 118.90240093216751, 'offset': 2.437599067832494,
         'upper': 122.43443758203412, 'lower': 118.15150039800949,
         'center': 120.2929689900218, 'simil': 0.48893129410519126},
        {'date': date(2020, 12, 13), 'rate': 122.25,
         'days': 122, 'pred': 119.83750615577543, 'offset': 2.4124938442245707,
         'upper': 123.36954280564204, 'lower': 119.08660562161741,
         'center': 121.22807421362972, 'simil': 0.4772079264585371},
        {'date': date(2021, 1, 5), 'rate': 125,
         'days': 145, 'pred': 120.55939749074545, 'offset': 4.440602509254546,
         'upper': 124.09143414061207, 'lower': 119.80849695658743,
         'center': 121.94996554859975, 'simil': 1.4242723254391365},
    ]
    values_out_expected = {
        'date_thresh': date(2020, 8, 8),

        'offset_mean': 1.3905680578542898,
        'offset_stdev': 1.0707342960061585,
        'offset_upper': 3.532036649866607,
        'offset_lower': -0.7509005341580273,

        'sugg_src': 857.5727674560864,
        'sugg_dst': 6.860582139648691,
    }

    data_in = [x.copy() for x in data_in_orig]
    data_in_copy = [x.copy() for x in data_in]
    data_out, values_out = compute_stuff(data_in, date(2021, 1, 5), 30 * 5,
                                         0.10, 0.10, 125, 1000)
    assert data_in == data_in_copy
    assert data_out == data_out_expected
    assert values_out == values_out_expected

    with pytest.raises(ValueError) as exc_info:
        compute_stuff([], date(2020, 1, 1), 365, 0, 0.10, 0, 1000)
    assert exc_info.value.args == ('The rate value must be > 0',)
