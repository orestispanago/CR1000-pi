import os
import datetime
import itertools
from pycampbellcr1000.utils import ListDict


def records_to_csv(records, fname):
    if os.path.exists(fname):
        output = records.to_csv(header=False)
    else:
        output = records.to_csv()
    with open(fname, "a") as f:
        f.write(output)


def store_last_record(records, fname, dt_format):
    last_record_str = records[-1]["Datetime"].strftime(dt_format)
    with open(fname, "w") as f:
        f.write(last_record_str)


def group_by_date(records):
    dates = []
    date_func = lambda x: x["Datetime"].date()
    for key, group in itertools.groupby(records, date_func):
        dates.append(ListDict(group))
    return dates


def store_to_daily_files(records):
    dates = group_by_date(records)
    for d in dates:
        output_file = f'{d[0]["Datetime"].strftime("%Y%m%d")}.csv'
        records_to_csv(d, output_file)


def get_last_stored_record(last_rec_file, dt_format):
    if os.path.exists(last_rec_file) and os.path.getsize(last_rec_file) > 0:
        with open(last_rec_file, "r") as f:
            return datetime.datetime.strptime(f.read(), dt_format)
    return datetime.datetime(1990, 1, 1, 0, 0, 1)


def get_start_stop(last_rec_file, dt_format):
    last_stored_rec = get_last_stored_record(last_rec_file, dt_format)
    start = last_stored_rec + datetime.timedelta(milliseconds=1)
    stop = datetime.datetime.utcnow()
    return start, stop
