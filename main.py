import glob
import logging
import logging.config
import os
import traceback

from datalogger import DATA_DIR, get_data_since_last_readout, save_as_daily_files
from uploader import upload_files_list, upload_ip_file
from utils import archive_past_days

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("pycampbellcr1000").setLevel(logging.CRITICAL + 1)
logging.getLogger("pylink").setLevel(logging.CRITICAL + 1)

logger = logging.getLogger(__name__)


def main():
    upload_ip_file()
    data = get_data_since_last_readout()
    save_as_daily_files(data)
    local_files = sorted(glob.glob(f"{DATA_DIR}/*.csv"))
    upload_files_list(local_files)
    archive_past_days(local_files)
    logger.debug(f"{'-' * 15} SUCCESS {'-' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
