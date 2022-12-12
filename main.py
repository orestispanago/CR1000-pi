import logging
import logging.config
import os
import traceback

from datalogger import Datalogger

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("pycampbellcr1000").setLevel(logging.CRITICAL + 1)
logging.getLogger("pylink").setLevel(logging.CRITICAL + 1)

logger = logging.getLogger(__name__)


def main():
    base_url = ""
    dataloger_to_db = {"datalogger_table": "db_table"}

    datalogger = Datalogger(serial_port="/dev/ttyUSB0")
    datalogger.device.set_time_utc()
    for datalogger_table, db_table in dataloger_to_db.items():
        last_record_url = f"{base_url}/{db_table}/last"
        post_url = f"{base_url}/{db_table}/store"

        datalogger.get_last_record(last_record_url)
        datalogger.get_records_since_last_readout(table=datalogger_table)
        datalogger.post_records(post_url)

    logger.debug(f"{'-' * 15} SUCCESS {'-' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
