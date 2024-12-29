# smartchg

[![GitHub main workflow](https://img.shields.io/github/actions/workflow/status/dmotte/smartchg/main.yml?branch=main&logo=github&label=main&style=flat-square)](https://github.com/dmotte/smartchg/actions)
[![PyPI](https://img.shields.io/pypi/v/smartchg?logo=python&style=flat-square)](https://pypi.org/project/smartchg/)

:snake: DCA-based **asset exchange algorithm**.

Inspired by **PAC** (_Pre-Authorized Contribution_ plan) and [Smart PAC](https://www.youtube.com/watch?v=kSThDk39pjU).

## Installation

This utility is available as a Python package on **PyPI**:

```bash
pip3 install smartchg
```

## Usage

There are some files in the [`example`](example) directory of this repo that can be useful to demonstrate how this tool works, so let's change directory first:

```bash
cd example/
```

We need a Python **virtual environment** ("venv") with some packages to do the demonstration:

```bash
python3 -mvenv venv
venv/bin/python3 -mpip install -r requirements.txt
```

> **Note**: we refer to the **source asset** with the **generic ticker symbol** `SRC`, and to the **destination asset** with `DST`.

Now we need to **fetch data** related to some asset. To do that, we can use https://github.com/dmotte/misc/blob/main/python-scripts/ohlcv-fetchers/yahoo-finance.py.

> **Note**: in the following commands, replace the local path of the `invoke.sh` script with the correct one.

```bash
~/git/misc/python-scripts/ohlcv-fetchers/invoke.sh yahoo-finance '^GSPC' -i1d -d2020-01-01T00Z -f'{:.6f}' > ohlcv-SPX500.csv
```

Now that we have the data, we can **compute the output data and values**:

```bash
rate=$(tail -1 ohlcv-SPX500.csv | cut -d, -f6)
python3 -msmartchg -a.15 -r"$rate" -t1000 --fmt-src='{:.2f}' --fmt-dst='{:.4f}' --fmt-{rate,simil}='{:.6f}' {ohlcv,smartchg,values}-SPX500.csv
grep '^sugg_' values-SPX500.csv
```

> **Note**: each **output value** and **entry field** is described with a comment in the `compute_stuff` function's code. You can search for the strings `# - entry` and `# - values` in the [`smartchg/cli.py`](smartchg/cli.py) file to get an overview.

And finally display some nice **plots** using the [`plots.py`](example/plots.py) script (which uses the [_Plotly_](https://github.com/plotly/plotly.py) Python library):

```bash
venv/bin/python3 plots.py -ros {smartchg,values}-SPX500.csv
```

For more details on how to use this command, you can also refer to its help message (`--help`).

## Algorithm

The algorithm is based on the assumption that one **need to exchange** some amount of one asset (e.g. `EUR`) for another asset (e.g. `SPX500`) **regularly** (e.g. once a month, every month). Also, they cannot decide **when** to make the exchange (e.g. always on the same day of the month). Therefore, the only controllable variable is "**how much**" to exchange, that is, the quantity of assets to be exchanged.

This algorithm tries to **optimize the quantity** of assets to be exchanged based on the **trend** of the historical **exchange rate** values, in order to determine whether the current exchange rate is **convenient** (and therefore we should exchange **more**) or **unconvenient** (and therefore we should exchange **less**). In one simple sentence, the motto is: [_"Buy more when low!"_](https://www.investopedia.com/ask/answers/04/052704.asp)

> **Note**: the following explanation is for illustration purposes only. Please refer to the [Python code](smartchg/cli.py) for any details.

| Symbol     | Variable          |
| ---------- | ----------------- |
| $a$        | `apy`             |
| $m$        | `multiplier`      |
| $t$        | `target`          |
| $n$        | `len(data)`       |
| $d_i$      | `entry['days']`   |
| $r_i$      | `entry['rate']`   |
| $p_i$      | `entry['pred']`   |
| $\delta_i$ | `entry['offset']` |
| $s_i$      | `entry['simil']`  |
| $S$        | `sugg_src`        |

First of all, we need to calculate the exchange rate **prediction** and **offset**:

$$
    p_i = r_1 (1 + a)^{d_i/365}
    \quad \quad
    \delta_i = r_i - p_i
$$

Then we need the **mean** and **standard deviation** of the offset values:

$$
    \mu_\delta = \frac{1}{n} \sum_{i=1}^{n} \delta_i
    \quad \quad
    \sigma_\delta = \sqrt{\frac{1}{n-1} \sum_{i=1}^{n} \left( \delta_i - \mu_\delta \right) ^ 2}
$$

The **similarity** values are calculated using the following formula:

$$
    s_i = \frac{\delta_i - \mu_\delta}{2 \sigma_\delta}
$$

Finally, we need to compute the **suggested `SRC` amount**, taking the **multiplier** value into account:

$$ S = t (1 - s_n m) $$

For example, if $t=500$, $s_n=-1$, and $m=0.10$, we have:

$$ S = 500 \cdot (1 - (-1) \cdot 0.10) = 500 \cdot 1.1 = 550 $$

## Development

If you want to contribute to this project, you can install the package in **editable** mode:

```bash
pip3 install -e . --user
```

This will just link the package to the original location, basically meaning any changes to the original package would reflect directly in your environment ([source](https://stackoverflow.com/a/35064498)).

If you want to run the tests, you'll have to install the `pytest` package and then run:

```bash
pytest test
```
