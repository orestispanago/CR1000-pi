import glob
import logging
import logging.config
import os
import traceback

from config import mymeasurements, nas
from datalogger import connect, get_data_since_last_readout, save_as_daily_files
from uploader import ftp_upload_files_list
from utils import archive_past_days

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("pycampbellcr1000").setLevel(logging.CRITICAL + 1)
logging.getLogger("pylink").setLevel(logging.CRITICAL + 1)

logger = logging.getLogger(__name__)


def main():
    device = connect(port="/dev/ttyUSB0")
    device.set_time_utc()
    data = get_data_since_last_readout(
        device=device, folder="data", table="MinAvg_final"
    )
    save_as_daily_files(data, folder="data")
    local_files = sorted(glob.glob(f"data/*.csv"))
    ftp_upload_files_list(local_files, config=nas)
    archive_past_days(local_files, folder="data/archive")
    logger.debug(f"{'-' * 15} SUCCESS {'-' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
