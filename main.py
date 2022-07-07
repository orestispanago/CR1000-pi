import os
import glob
import logging
import logging.config
import traceback
from uploader import upload_to_ftp
from file_utils import archive_past_days
from config import FTP_IP, FTP_USER, FTP_PASS, FTP_DIR
from record_functions import save_as_daily_files
import datalogger

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("pycampbellcr1000").setLevel(logging.CRITICAL + 1)
logging.getLogger("pylink").setLevel(logging.CRITICAL + 1)

logger = logging.getLogger(__name__)


def main():
    data = datalogger.get_data_since_last_readout()
    save_as_daily_files(data)
    local_files = sorted(glob.glob("*.csv"))
    upload_to_ftp(local_files, FTP_IP, FTP_USER, FTP_PASS, FTP_DIR)
    archive_past_days(local_files, "archive")
    logger.debug(f"{'-' * 15} SUCCESS {'-' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
