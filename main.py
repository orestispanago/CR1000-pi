import os
import glob
import datetime
import itertools
from pycampbellcr1000 import CR1000
from pycampbellcr1000.utils import ListDict
from uploader import upload_to_ftp, archive_uploaded
from config import *


def records_to_csv(data, fname):
    if os.path.exists(fname):
        output = data.to_csv(header=False)
    else:
        output = data.to_csv()
    with open(fname, "a") as f:
        f.write(output)


def store_last_record(last_record, fname, dt_format):
    last_record_str = last_record.strftime(dt_format)
    with open(fname, "w") as f:
        f.write(last_record_str)


def get_last_stored_record(last_rec_file, dt_format):
    if os.path.exists(last_rec_file) and os.path.getsize(last_rec_file) > 0:
        with open(last_rec_file, "r") as f:
            return datetime.datetime.strptime(f.read(), dt_format)
    return datetime.datetime(2022, 7, 1, 13, 0, 0)


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


def get_start_stop():
    last_stored_rec = get_last_stored_record(LAST_REC_FILE, DT_FORMAT)
    start = last_stored_rec + datetime.timedelta(milliseconds=1)
    stop = datetime.datetime.utcnow()
    return start, stop

start, stop = get_start_stop()
device = CR1000.from_url("serial:/dev/ttyUSB0:115200")
data = device.get_data("Table1", start, stop)

last_record = data[-1]["Datetime"]

store_to_daily_files(data)
store_last_record(last_record, LAST_REC_FILE, DT_FORMAT)


local_files = sorted(glob.glob("*.csv"))
upload_to_ftp(local_files, FTP_IP, FTP_USER, FTP_PASS, FTP_DIR)
archive_uploaded(local_files, ARCHIVE_DIR)
