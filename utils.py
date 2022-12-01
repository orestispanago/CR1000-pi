import io
import logging
import os
import urllib.request

from datalogger import DATA_DIR

logger = logging.getLogger(__name__)


def mkdir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.debug(f"Created local directory {dir_path}")


def get_external_ip():
    external_ip = (
        urllib.request.urlopen("https://ifconfig.me/ip").read().decode("utf-8")
    )
    logger.debug(f"External IP: {external_ip}")
    return external_ip


def str_to_bytes_io(text):
    bio = io.BytesIO()
    bio.write(text.encode())
    bio.seek(0)  # move to beginning of file
    return bio


def archive_past_days(local_files):
    if len(local_files) > 1:
        for local_file in local_files[:-1]:
            base_name = os.path.basename(local_file)
            year = base_name[:4]
            dest_folder = f"{DATA_DIR}/archive/{year}"
            dest_path = f"{dest_folder}/{base_name}"
            mkdir_if_not_exists(dest_folder)
            os.rename(local_file, dest_path)
            logger.info(f"Renamed local file {local_file} to {dest_path}")
