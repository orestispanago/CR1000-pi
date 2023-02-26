import glob
import json
import logging
import os

from datalogger import save_as_daily_files, save_multiple_files
from uploaders import ftp_upload_files, sftp_upload_files
from utils import archive_past_days, archive_uploaded

logger = logging.getLogger(__name__)


class Task:
    # Converts dict to object so that attributes are accessed with "." notation
    def __init__(self, dict):
        self.__dict__.update(dict)

    def save(self, data):
        save_as_daily_files(data, folder=self.local_folder, prefix=self.prefix)

    def upload(self):
        local_files = sorted(glob.glob(f"{self.local_folder}/*.csv"))
        ftp_upload_files(
            local_files,
            ip=self.ip,
            user=self.user,
            passwd=self.passwd,
            dir=self.dir,
            annual_folders=self.annual_folders,
        )

    def archive(self):
        archive_past_days(src_folder=self.local_folder)

    def run(self, data=None):
        logger.debug(f"{'-' * 10} Running {self.__class__.__name__} {'-' * 10}")
        self.save(data=data)
        self.upload()
        self.archive()

    def __repr__(self):
        return f"{self.__dict__}"


class NasTask(Task):
    def __init__(self, dict):
        super(NasTask, self).__init__(dict)


class MymeasurementsTask(Task):
    def __init__(self, dict):
        super(MymeasurementsTask, self).__init__(dict)

    def save(self, data):
        save_multiple_files(
            data,
            folder=self.local_folder,
            records_per_file=5,
            prefix=self.prefix,
        )

    def archive(self):
        archive_uploaded(src_folder=self.local_folder)


class PyranocamTask(Task):
    def __init__(self, dict):
        super(PyranocamTask, self).__init__(dict)

    def upload(self):
        local_files = sorted(glob.glob(f"{self.local_folder}/*.csv"))
        sftp_upload_files(
            local_files,
            host=None,
            user=None,
            passwd=None,
            known_hosts_file=None,
            dir=None,
            subdir=None,
        )


dname = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(dname, "tasks_config.json")

with open(config_file, "r") as f:
    configs = json.load(f)

nas_task = NasTask(configs["nas"])
mymeasurements_task = MymeasurementsTask(configs["mymeasurements"])
pyranocam_task = PyranocamTask(configs["pyranocam"])
