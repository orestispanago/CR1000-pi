import os
import itertools
import glob
import datetime
import logging
import serial
from pycampbellcr1000 import CR1000
from pycampbellcr1000.utils import ListDict

logger = logging.getLogger(__name__)


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
                        (j == (len(rec["RecFrag"]) - 1)) and (i == (len(data) - 1))
                    ):
                        break
                    new_rec = {"Datetime": item["TimeOfRec"], "RecNbr": item["RecNbr"]}
                    for key in item["Fields"]:
                        # overriden part
                        new_rec[key.decode("utf-8")] = item["Fields"][key]
                    records.append(new_rec)

        if records:
            records = records.sorted_by("Datetime")
            yield records.sorted_by("Datetime")
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
    date_func = lambda x: x["Datetime"].date()
    for key, group in itertools.groupby(records, date_func):
        dates.append(ListDict(group))
    return dates


def save_as_daily_files(records):
    dates = group_by_date(records)
    for d in dates:
        output_file = f'{d[0]["Datetime"].strftime("%Y%m%d")}.csv'
        records_to_csv(d, output_file)


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
    print(data)
    logger.info(f"Retrieved {len(data)} records.")
    return data


CR1000.get_data_generator = get_data_generator
