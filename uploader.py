import logging
import os
from ftplib import FTP, error_perm

import pysftp

logger = logging.getLogger(__name__)


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


def ftp_upload_files_list(local_files, config=None):
    with FTP(config.ip, config.user, config.passwd) as ftp:
        ftp.cwd(config.dir)
        for local_file in local_files:
            base_name = os.path.basename(local_file)
            if config.annual_folders:
                year = base_name[:4]
                remote_path = f"{year}/{base_name}"
            else:
                remote_path = base_name
            try:
                ftp_upload_file(ftp, local_file, remote_path)
            except error_perm as e:
                if "55" in str(e):
                    ftp_make_dirs(ftp, os.path.dirname(remote_path))
                    ftp.cwd(config.dir)
                    ftp_upload_file(ftp, local_file, remote_path)


def sftp_upload_files_list(local_files, config=None):
    cnopts = pysftp.CnOpts(knownhosts=config.known_hosts_file)
    logger.debug("Uploading to SFTP server...")
    with pysftp.Connection(
        config.host, username=config.user, password=config.passwd, cnopts=cnopts
    ) as sftp:
        sftp.cwd(dir)
        if config.subdir not in sftp.listdir():
            sftp.mkdir(config.subdir)
        sftp.chdir(config.subdir)
        for local_file in local_files:
            sftp.put(local_file)
            logger.debug(f"Uploaded {local_file} to SFTP")
    logger.info(f"Uploaded {len(local_files)} files to SFTP.")
