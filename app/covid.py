#!/usr/bin/env python

import argparse
import os
import shutil
from datetime import timedelta, date, datetime
from os.path import isdir
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader


def get_latest_data(start_date: date) -> pd.DataFrame:
    sidep_data: pd.DataFrame = pd.read_csv(
        'https://www.data.gouv.fr/fr/datasets/r/dd0de5d9-b5a5-4503-930a-7b08dc0adc7c',
        parse_dates=True,
        index_col="jour",
        usecols=["jour", "P", "cl_age90", 'T', 'pop'],
        sep=';'
    )
    end_date = date.today()

    everyone_data = sidep_data.loc[sidep_data.loc[:, 'cl_age90'] == 0].copy()
    latest_data: pd.DataFrame = everyone_data.loc[start_date:end_date].copy()

    p = latest_data.loc[:, 'P'].copy()
    t = latest_data.loc[:, 'T'].copy()
    latest_data.loc[:, 'Ratio'] = (100*p/t).round(decimals=1)
    latest_data.loc[:, 'P'] = (p/1000).round(decimals=1)
    latest_data.loc[:, 'T'] = (t/1000).round(decimals=1)
    rolling_mean = (
        p.rolling(min_periods=1, window=7).mean()/1000
    ).round(decimals=1).astype(int)
    latest_data.loc[:, 'Mean'] = rolling_mean

    latest_data = latest_data.drop(['cl_age90'], axis=1)
    latest_data = latest_data.drop(['pop'], axis=1)
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
    start = datetime.strptime(args.start, '%Y-%m-%d')
    data = get_latest_data(start_date=start)
    formatted_data = format_data(data, format_=args.format)
    if args.path is not None:
        with open(args.path, 'w') as f:
            f.write(formatted_data)
    else:
        print(formatted_data)


def build_website_cmd(args) -> None:
    last_week = date.today() - timedelta(10) - timedelta(3)
    data = get_latest_data(last_week)

    # Jinja2 setup
    env = Environment(loader=FileSystemLoader('website'))
    template = env.get_template('index.html')

    if isdir(args.dest):
        shutil.rmtree(args.dest)
    os.mkdir(args.dest)
    shutil.copytree('website/static', args.dest / 'static')

    with open(args.dest / 'index.html', 'w') as f:
        html = template.render(
            title='Covid Mux',
            data=data,
            run_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
        f.write(html)

def main():
    last_week = (date.today() - timedelta(10) - timedelta(3)).strftime('%Y-%m-%d')

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
    build_website_parser.add_argument('--dest', required=False, default='public', type=Path)
    build_website_parser.set_defaults(func=build_website_cmd)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
