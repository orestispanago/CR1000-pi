import os
import itertools
from pycampbellcr1000.utils import ListDict


def records_to_csv(records, fname):
    if os.path.exists(fname):
        output = records.to_csv(header=False)
    else:
        output = records.to_csv()
    with open(fname, "a") as f:
        f.write(output)


def group_by_date(records):
    dates = []
    date_func = lambda x: x["Datetime"].date()
    for key, group in itertools.groupby(records, date_func):
        dates.append(ListDict(group))
    return dates


def save_as_daily_files(records):
    dates = group_by_date(records)
    for d in dates:
        output_file = f'{d[0]["Datetime"].strftime("%Y%m%d")}.csv'
        records_to_csv(d, output_file)
