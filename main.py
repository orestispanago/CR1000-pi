import os
import glob
import logging
import traceback
from pycampbellcr1000 import CR1000
from uploader import upload_to_ftp, archive_past_days
from config import *
from record_functions import store_last_record, store_to_daily_files, get_start_stop
import overriden
import usb

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.basicConfig(
    filename="logfile.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
)
logging.getLogger("pycampbellcr1000").setLevel(logging.CRITICAL + 1)
logging.getLogger("pylink").setLevel(logging.CRITICAL + 1)

logger = logging.getLogger(__name__)

CR1000.get_data_generator = overriden.get_data_generator


def main():
    start, stop = get_start_stop(LAST_REC_FILE, DT_FORMAT)

    logger.info("Connecting to device...")
    device = CR1000(usb.serial_port())
    logger.info("Connection successfull. Retrieving data...")

    data = device.get_data("Table1", start, stop)
    logger.info(f"Retrieved {len(data)} records.")

    store_to_daily_files(data)
    store_last_record(data, LAST_REC_FILE, DT_FORMAT)

    local_files = sorted(glob.glob("*.csv"))
    upload_to_ftp(local_files, FTP_IP, FTP_USER, FTP_PASS, FTP_DIR)
    archive_past_days(local_files, "archive")

    logger.info("SUCCESS! Bye...\n")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
