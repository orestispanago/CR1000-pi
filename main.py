import logging
import logging.config
import os
import traceback

from datalogger import connect, get_data_since_last_readout
from tasks import mymeasurements_task, nas_task, pyranocam_task

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
    data_1min = get_data_since_last_readout(
        device=device,
        folder=nas_task.local_folder,
        table=nas_task.cr1000_table,
    )
    nas_task.run(data=data_1min)
    mymeasurements_task.run(data=data_1min)

    # data_10sec = get_data_since_last_readout(
    #     device=device,
    #     folder=pyranocam_task.local_folder,
    #     table=pyranocam_task.cr1000_table,
    # )
    # pyranocam_task.run(data=data_10sec)
    logger.debug(f"{'=' * 15} SUCCESS {'=' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
