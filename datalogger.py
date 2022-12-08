import datetime
import glob
import itertools
import logging
import os

import serial
from pycampbellcr1000 import CR1000
from pycampbellcr1000.utils import ListDict, nsec_to_time

logger = logging.getLogger(__name__)

DATA_DIR = "data"
TABLE_NAME = "MinAvg_final"

# Override pycampbellcr1000.ListDict method to avoid b'' in table fields
def get_data_generator(self, tablename, start_date=None, stop_date=None):
    """Get all data from `tablename` from `start_date` to `stop_date` as
    generator. The data can be fragmented into multiple packets, this
    generator can return parsed data from each packet before receiving
    the next one.
    :param tablename: Table name that contains the data.
    :param start_date: The beginning datetime record.
    :param stop_date: The stopping datetime record.
    """
    self.ping_node()
    start_date = start_date or datetime(1990, 1, 1, 0, 0, 1)
    stop_date = stop_date or datetime.now()
    more = True
    while more:
        records = ListDict()
        data, more = self._collect_data(tablename, start_date, stop_date)
        for i, rec in enumerate(data):
            if not rec["NbrOfRecs"]:
                more = False
                break
            for j, item in enumerate(rec["RecFrag"]):
                if start_date <= item["TimeOfRec"] <= stop_date:
                    start_date = item["TimeOfRec"]
                    # for no duplicate record
                    if more and (
                        (j == (len(rec["RecFrag"]) - 1))
                        and (i == (len(data) - 1))
                    ):
                        break
                    new_rec = {
                        "Datetime_UTC": item["TimeOfRec"],
                        "RecNbr": item["RecNbr"],
                    }
                    for key in item["Fields"]:
                        # overriden part
                        new_rec[key.decode("utf-8")] = item["Fields"][key]
                    records.append(new_rec)

        if records:
            records = records.sorted_by("Datetime_UTC")
            yield records.sorted_by("Datetime_UTC")
        else:
            more = False


def records_to_csv(records, fname):
    if os.path.exists(fname):
        output = records.to_csv(header=False)
    else:
        output = records.to_csv()
    with open(fname, "a") as f:
        f.write(output)


def group_by_date(records):
    dates = []
    date_func = lambda x: x["Datetime_UTC"].date()
    for key, group in itertools.groupby(records, date_func):
        dates.append(ListDict(group))
    return dates


def save_as_daily_files(records):
    dates = group_by_date(records)
    for d in dates:
        fname = f'{d[0].get("Datetime_UTC").strftime("%Y%m%d")}.csv'
        fpath = os.path.join(DATA_DIR, fname)
        records_to_csv(d, fpath)


def remove_last_line(fname):
    with open(fname, "r") as rf:
        lines = rf.readlines()
    with open(fname, "w") as wf:
        wf.writelines(lines[:-2])
    logger.warning(f"Removed last line from {fname}")


def get_last_readout_from_file(fname):
    with open(fname, "r") as f:
        last_line = f.readlines()[-1]
    last_record = last_line.split(",")[0]
    logger.debug(f"Last record: {last_record}")
    return datetime.datetime.strptime(last_record, "%Y-%m-%d %H:%M:%S")


def get_last_record():
    local_files = sorted(glob.glob(f"{DATA_DIR}/*.csv"))
    if len(local_files) > 0:
        last_file = local_files[-1]
        try:
            return get_last_readout_from_file(last_file)
        except ValueError as e:
            logger.error(f"ValueError: {e}")
            logger.warning(f"removing last line from {last_file}")
            remove_last_line(last_file)
            return get_last_readout_from_file(last_file)
    logger.warning("No .csv file found, will read all datalogger memory...")
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


def set_time_utc(self):
    """Sets datalogger time to current UTC"""
    current_time = self.gettime()
    logger.debug(f"Current time: {current_time}")
    utc_now = datetime.datetime.utcnow()
    self.ping_node()
    diff = int((utc_now - current_time).total_seconds())
    logger.debug(f"Setting datalogger time to: {utc_now}")
    # settime (OldTime in response)
    hdr, msg, sdt1 = self.send_wait(self.pakbus.get_clock_cmd((diff, 0)))
    # gettime (NewTime in response)
    hdr, msg, sdt2 = self.send_wait(self.pakbus.get_clock_cmd())
    # remove transmission time
    new_time = nsec_to_time(msg["Time"]) - (sdt1 + sdt2)
    logger.debug(f"New time: {new_time}")
    return new_time


def get_data_since_last_readout():
    start = get_last_record() + datetime.timedelta(milliseconds=1)
    stop = datetime.datetime.utcnow()

    logger.debug("Connecting to device...")
    device = CR1000(serial_port())
    logger.debug("Connection successfull.")

    device.set_time_utc()

    data = device.get_data(TABLE_NAME, start, stop)
    logger.info(f"Retrieved {len(data)} records.")
    return data


CR1000.get_data_generator = get_data_generator
CR1000.set_time_utc = set_time_utc
