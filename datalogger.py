import glob
import datetime
import logging
import serial
from pycampbellcr1000 import CR1000
import overriden

logger = logging.getLogger(__name__)

CR1000.get_data_generator = overriden.get_data_generator


def get_last_record():
    local_files = sorted(glob.glob("*.csv"))
    if len(local_files) > 0:
        with open(local_files[-1], "r") as f:
            last_line = f.readlines()[-1]
            last_record = last_line.split(",")[0]
            return datetime.datetime.strptime(last_record, "%Y-%m-%d %H:%M:%S")
    return datetime.datetime(1990, 1, 1, 0, 0, 1)


def serial_port():
    # Faster than CR1000.from_url() on raspberry
    # use port=None to create a serial port object without opening the underlying port
    # Found here: https://github.com/LionelDarras/PyCampbellCR1000/issues/21
    ser = serial.Serial(
        port=None,
        baudrate=115200,
        timeout=2,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=1,
    )
    ser.port = "/dev/ttyUSB0"
    return ser


def get_data_since_last_readout():
    start = get_last_record() + datetime.timedelta(milliseconds=1)
    stop = datetime.datetime.utcnow()

    logger.debug("Connecting to device...")
    device = CR1000(serial_port())
    logger.debug("Connection successfull. Retrieving data...")

    data = device.get_data("Table1", start, stop)
    logger.info(f"Retrieved {len(data)} records.")
    return data
