import logging
import os
from ftplib import FTP, error_perm

import pysftp

import utils

logger = logging.getLogger(__name__)


def upload_file_from_memory(ip, user, password, remote_path, bytes_io_object):
    with FTP(ip, user, password) as ftp:
        ftp.storbinary(f"STOR {remote_path}", bytes_io_object)
    logger.info(f"Created file {remote_path} at FTP")


def upload_ip_file(ip, user, password, remote_path):
    external_ip = utils.get_external_ip()
    ip_bytes_io = utils.str_to_bytes_io(external_ip)
    upload_file_from_memory(ip, user, password, remote_path, ip_bytes_io)


def ftp_mkdir_and_enter(ftp_session, dir_name):
    if dir_name not in ftp_session.nlst():
        ftp_session.mkd(dir_name)
        logger.debug(f"Created FTP directory {dir_name}")
    ftp_session.cwd(dir_name)


def ftp_make_dirs(ftp_session, folder_path):
    for f in folder_path.split("/"):
        ftp_mkdir_and_enter(ftp_session, f)


def ftp_upload_file(ftp_session, local_path, remote_path):
    with open(local_path, "rb") as f:
        ftp_session.storbinary(f"STOR {remote_path}", f)
    logger.info(f"Uploaded {local_path} to {remote_path}")


def ftp_upload_files(
    local_files, ip=None, user=None, passwd=None, dir=None, annual_folders=False
):
    with FTP(ip, user, passwd) as ftp:
        ftp.cwd(dir)
        for local_file in local_files:
            base_name = os.path.basename(local_file)
            if annual_folders:
                year = base_name.split("_")[1][:4]
                remote_path = f"{year}/{base_name}"
            else:
                remote_path = base_name
            try:
                ftp_upload_file(ftp, local_file, remote_path)
            except error_perm as e:
                if "55" in str(e):
                    ftp_make_dirs(ftp, os.path.dirname(remote_path))
                    ftp.cwd(dir)
                    ftp_upload_file(ftp, local_file, remote_path)


def sftp_upload_files(
    local_files,
    host=None,
    user=None,
    passwd=None,
    known_hosts_file=None,
    dir=None,
    subdir=None,
):
    cnopts = pysftp.CnOpts(knownhosts=known_hosts_file)
    logger.debug("Uploading to SFTP server...")
    with pysftp.Connection(
        host, username=user, password=passwd, cnopts=cnopts
    ) as sftp:
        sftp.cwd(dir)
        if subdir not in sftp.listdir():
            sftp.mkdir(subdir)
        sftp.chdir(subdir)
        for local_file in local_files:
            sftp.put(local_file)
            logger.debug(f"Uploaded {local_file} to SFTP")
    logger.info(f"Uploaded {len(local_files)} files to SFTP.")
