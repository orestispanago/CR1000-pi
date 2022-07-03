import os
from ftplib import FTP
import logging
from threading import local

logger = logging.getLogger(__name__)


def upload_to_ftp(local_files, ftp_ip, ftp_user, ftp_password, ftp_dir):
    logger.info("Uploading to FTP server...")
    with FTP(ftp_ip, ftp_user, ftp_password) as ftp:
        ftp.cwd(ftp_dir)
        for local_file in local_files:
            with open(local_file, "rb") as f:
                ftp.storbinary(f"STOR {local_file}", f)
    logger.info(f"Uploaded {len(local_files)} files.")


def mkdir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def archive_past_days(local_files, dest_folder):
    mkdir_if_not_exists(dest_folder)
    if len(local_files) > 1:
        for local_file in local_files[:-1]:
            new_fname = f"{dest_folder}/{local_file}"
            os.rename(local_file, new_fname)
            logger.info(f"Renamed file {local_file} to {new_fname}")
