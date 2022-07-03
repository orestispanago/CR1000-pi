import os
import glob
import datetime
import itertools
from pycampbellcr1000 import CR1000
from pycampbellcr1000.utils import ListDict
from uploader import upload_to_ftp, archive_past_days
from config import *
import logging


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.basicConfig(
    filename="logfile.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(name)s %(funcName)s() - %(levelname)s: %(message)s",
)
logging.getLogger("pycampbellcr1000").setLevel(logging.CRITICAL + 1)
logging.getLogger("pylink").setLevel(logging.CRITICAL + 1)

logger = logging.getLogger(__name__)


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


def main():
    start, stop = get_start_stop()

    logger.info("Connecting to device...")
    device = CR1000.from_url("serial:/dev/ttyUSB0:115200")
    logger.info("Connection successfull. Retrieving data...")

    data = device.get_data("Table1", start, stop)
    logger.info(f"Retrieved {len(data)} records.")

    store_to_daily_files(data)
    store_last_record(data[-1]["Datetime"], LAST_REC_FILE, DT_FORMAT)

    local_files = sorted(glob.glob("*.csv"))
    upload_to_ftp(local_files, FTP_IP, FTP_USER, FTP_PASS, FTP_DIR)
    archive_past_days(local_files, "archive")

    logger.info("SUCCESS! Bye...")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
