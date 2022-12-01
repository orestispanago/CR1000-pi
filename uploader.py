import logging
import os
from ftplib import FTP, error_perm

import utils

logger = logging.getLogger(__name__)

IP = ""
USER = ""
PASSWORD = ""
DIR = "/dataloggers/test"

IP_FILE = "dataloggers/IP-addresses/test.txt"


def upload_file_from_memory(remote_fname, bytes_io_object):
    with FTP(IP, USER, PASSWORD) as ftp:
        ftp.storbinary(f"STOR {remote_fname}", bytes_io_object)
    logger.info(f"Created file {remote_fname} at FTP")


def upload_ip_file():
    external_ip = utils.get_external_ip()
    ip_bytes_io = utils.str_to_bytes_io(external_ip)
    upload_file_from_memory(IP_FILE, ip_bytes_io)


def mkdir_and_enter(ftp_session, dir_name):
    if dir_name not in ftp_session.nlst():
        ftp_session.mkd(dir_name)
        logger.debug(f"Created FTP directory {dir_name}")
    ftp_session.cwd(dir_name)


def make_dirs(ftp_session, folder_path):
    for f in folder_path.split("/"):
        mkdir_and_enter(ftp_session, f)


def upload_file(ftp_session, local_path, remote_path):
    with open(local_path, "rb") as f:
        ftp_session.storbinary(f"STOR {remote_path}", f)
    logger.info(f"Uploaded {local_path} to {remote_path}")


def upload_files_list(local_files):
    with FTP(IP, USER, PASSWORD) as ftp:
        ftp.cwd(DIR)
        for local_file in local_files:
            base_name = os.path.basename(local_file)
            year = base_name[:4]
            remote_path = f"{year}/{base_name}"
            try:
                upload_file(ftp, local_file, remote_path)
            except error_perm as e:
                if "55" in str(e):
                    make_dirs(ftp, os.path.dirname(remote_path))
                    ftp.cwd(DIR)
                    upload_file(ftp, local_file, remote_path)
