#!/usr/bin/env python

import argparse
import subprocess
from datetime import timedelta, date

import pandas as pd


def get_latest_data(start_date: date) -> pd.DataFrame:
    sidep_data: pd.DataFrame = pd.read_csv(
        'https://www.data.gouv.fr/fr/datasets/r/dd0de5d9-b5a5-4503-930a-7b08dc0adc7c',
        parse_dates=True,
        index_col="jour",
        usecols=["jour", "P", "cl_age90", 'T', 'pop'],
        sep=';'
    )
    end_date = date.today()

    everyone_data = sidep_data.loc[sidep_data.loc[:, 'cl_age90'] == 0]
    latest_data: pd.DataFrame = everyone_data[start_date:end_date]

    latest_data['Ratio'] = (100*latest_data['P']/latest_data['T']).round(decimals=1)
    latest_data['P'] = (latest_data['P']/1000).round(decimals=1)
    latest_data['T'] = (latest_data['T']/1000).round(decimals=1)
    rolling_mean = (
        latest_data['P'].rolling(min_periods=1, window=7).mean()
    ).round(decimals=1).astype(int)
    latest_data['Mean'] = rolling_mean

    latest_data = latest_data.drop(['cl_age90'], axis=1)
    latest_data = latest_data.drop(['pop'], axis=1)
    # Improve output
    # latest_data = latest_data.rename(
    #     columns={
    #         'P': 'Nouveaux cas positifs (milliers)',
    #         'Mean': 'Moyenne glissante sur 7j (milliers)',
    #         'T': 'Nombre de tests (milliers)',
    #         'Ratio': "Taux de positivité (%)"
    #
    #     },
    # )
    latest_data = latest_data.rename_axis(
        "Date",
        axis='rows'
    )

    return latest_data


def format_data(df: pd.DataFrame, format_: str) -> str:
    func = df.to_csv
    match format_:
        case 'html':
            pass
        case 'json':
            func = df.to_json
    return func(columns=['P', 'T', 'Mean', 'Ratio'])


def build_data_cmd(args) -> None:
    data = get_latest_data(start_date=args.start)
    formatted_data = format_data(data, format_=args.format)
    if args.path is not None:
        with open(args.path, 'w') as f:
            f.write(formatted_data)
    else:
        print(formatted_data)


def build_website_cmd(args) -> None:
    cmd = ['hugo']
    if args.server:
        cmd.append('server')
    cmd.extend(['--destination', args.dest])
    subprocess.run(cmd, cwd=args.dir)


def main():
    last_week = date.today() - timedelta(10) - timedelta(3)

    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(required=True)

    # build data
    build_data_parser = sub_parsers.add_parser('build-data')
    build_data_parser.add_argument('--start', required=False, default=last_week)
    build_data_parser.add_argument('--path', required=False, default=None, dest='path')
    build_data_parser.add_argument('--format', required=False, default='csv')
    build_data_parser.set_defaults(func=build_data_cmd)

    # build website
    build_website_parser = sub_parsers.add_parser('build-website')
    build_website_parser.add_argument('--dir', required=False, default='.')
    build_website_parser.add_argument('--dest', required=False, default='public')
    build_website_parser.add_argument('--server', action='store_true')
    build_website_parser.set_defaults(func=build_website_cmd)

    args = parser.parse_args()
    args.func(args)
