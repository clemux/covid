#!/usr/bin/env python

import argparse
from datetime import timedelta, date
from pathlib import Path
from typing import Optional

import pandas as pd


def get_latest_data(start_date: date) -> pd.DataFrame:
    sidep_data: pd.DataFrame = pd.read_csv(
        'https://www.data.gouv.fr/fr/datasets/r/dd0de5d9-b5a5-4503-930a-7b08dc0adc7c',
        parse_dates=True,
        index_col="jour",
        usecols=["jour", "P", "cl_age90", 'T'],
        sep=';'
    )
    end_date = date.today()

    everyone_data = sidep_data.loc[sidep_data.loc[:, 'cl_age90'] == 0]
    latest_data: pd.DataFrame = everyone_data[start_date:end_date]
    latest_data = latest_data.drop(['cl_age90'], axis=1)

    rolling_mean = latest_data['P'].rolling(min_periods=1, window=7).mean().round(decimals=0).astype(int)
    latest_data['Mean'] = rolling_mean

    # Improve output
    latest_data = latest_data.rename(
        columns={
            'P': 'New positive cases',
            'Mean': 'Rolling average (7d)',
            'T': 'Number of tests',
        },
    )
    latest_data = latest_data.rename_axis(
        "Date",
        axis='rows'
    )

    return latest_data


def write_file(data: pd.DataFrame, path: Optional[Path] = None, format_: Optional[str] = 'html') -> None:
    func = data.to_html
    match format_:
        case 'html':
            pass
        case 'csv':
            func = data.to_csv
        case 'json':
            func = data.to_json
    with open(path, 'w') as f:
        func(f)


if __name__ == '__main__':
    last_week = date.today() - timedelta(7) - timedelta(3)

    parser = argparse.ArgumentParser()
    parser.add_argument('--start', required=False, default=last_week)
    parser.add_argument('--path', required=False, default=None, dest='path')
    parser.add_argument('--format', required=False, default='csv')
    args = parser.parse_args()

    output_data = get_latest_data(start_date=args.start)

    if args.path is not None:
        write_file(data=output_data, path=args.path, format_=args.format)
    else:
        print(output_data)
