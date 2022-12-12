import datetime
import logging

import requests
import serial
from pycampbellcr1000 import CR1000
from pycampbellcr1000.utils import ListDict, nsec_to_time

logger = logging.getLogger(__name__)


class Datalogger:
    def __init__(self, serial_port=None):
        self.device = CR1000(serial_connection(serial_port))
        self.last_record = None
        self.records = None

    def get_last_record(self, url):
        get_resp = requests.get(url)
        data = get_resp.json(url)
        last_record = datetime.datetime.strptime(
            data["Datetime_UTC"], "%a, %d %b %Y %H:%M:%S GMT"
        )
        self.last_record = last_record
        return last_record

    def get_records_since_last_readout(self, table=None):
        start = self.last_record + datetime.timedelta(milliseconds=1)
        stop = datetime.datetime.utcnow()
        records = self.device.get_data(table, start, stop)
        logger.info(f"Retrieved {len(records)} records.")
        self.records = records

    def post_records(self, url):
        resp = requests.post(url, json=self.records)
        logger.debug(f"POST status: {resp.status_code}")
        logger.debug(resp.text)


def serial_connection(port=None):
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
    ser.port = port
    return ser


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


CR1000.get_data_generator = get_data_generator
CR1000.set_time_utc = set_time_utc
