#!/usr/bin/env python

import argparse
import os
import shutil
from datetime import timedelta, date, datetime
from os.path import isdir
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from matplotlib import pyplot as plt

from app.lib.templates import datetime_format


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

    p = everyone_data.loc[:, 'P'].copy()
    t = everyone_data.loc[:, 'T'].copy()
    r: pd.DataFrame = 100 * p / t
    everyone_data.loc[:, 'Ratio'] = r.round(decimals=1)
    everyone_data.loc[:, 'P'] = (p / 1000).round(decimals=1)
    everyone_data.loc[:, 'T'] = (t / 1000).round(decimals=1)
    rolling_mean = (
            p.rolling(min_periods=1, window=7).mean() / 1000
    ).round(decimals=1).astype(int)
    everyone_data.loc[:, 'Mean'] = rolling_mean

    rolling_rate = (
        r.rolling(min_periods=1, window=7).mean().round(decimals=1)
    )
    everyone_data.loc[:, 'RollingRate'] = rolling_rate

    latest_data = everyone_data.loc[start_date:end_date].copy()
    latest_data = latest_data.drop(['cl_age90'], axis=1)
    latest_data = latest_data.drop(['pop'], axis=1)
    latest_data = latest_data.rename_axis(
        "Date",
        axis='rows'
    )

    return latest_data.reindex(index=latest_data.index[::-1])


def format_data(df: pd.DataFrame, format_: str) -> str:
    func = df.to_csv
    return func(columns=['P', 'T', 'Mean', 'Ratio', 'RollingRate'])


def build_data_cmd(args) -> None:
    start = datetime.strptime(args.start, '%Y-%m-%d')
    data = get_latest_data(start_date=start)
    formatted_data = format_data(data, format_=args.format)
    if args.path is not None:
        with open(args.path, 'w') as f:
            f.write(formatted_data)
    else:
        print(formatted_data)


def build_mean_plot(data: pd.DataFrame, path: Path):
    plt.figure(figsize=(12, 5))
    plt.bar(data.index, data['Mean'].values)
    plt.xlabel('Date of tests')
    plt.ylabel('New cases (k), rolling average)')
    plt.savefig(path)
    plt.clf()


def build_rate_plot(data: pd.DataFrame, path: Path):
    plt.figure(figsize=(12, 5))
    plt.bar(data.index, data['RollingRate'].values)
    plt.xlabel('Date of tests')
    plt.ylabel('Positive rate, rolling average (%)')
    plt.savefig(path)
    plt.clf()


def build_website_cmd(args) -> None:
    start = datetime.strptime(args.start, '%Y-%m-%d')
    data = get_latest_data(start)

    if isdir(args.dest):
        shutil.rmtree(args.dest)
    os.mkdir(args.dest)
    shutil.copytree('website/static', args.dest / 'static')

    plot_path = args.dest / 'static' / 'rolling_mean.png'
    build_mean_plot(data=data, path=plot_path)

    rate_plot_path = args.dest / 'static' / 'rate_plot.png'
    build_rate_plot(data=data, path=rate_plot_path)

    # Jinja2 setup
    env = Environment(loader=FileSystemLoader('website'))
    env.filters['datetime_format'] = datetime_format
    template = env.get_template('index.html')

    with open(args.dest / 'index.html', 'w') as f:
        html = template.render(
            title='Covid Mux',
            data=data,
            run_datetime=datetime.now(),
            plots=['rolling_mean', 'rate_plot'],
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
    build_website_parser.add_argument('--start', required=False, default=last_week)

    build_website_parser.set_defaults(func=build_website_cmd)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
