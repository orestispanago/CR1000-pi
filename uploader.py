import os
from ftplib import FTP


def upload_to_ftp(local_files, ftp_ip, ftp_user, ftp_password, ftp_dir):
    with FTP(ftp_ip, ftp_user, ftp_password) as ftp:
        ftp.cwd(ftp_dir)
        for local_file in local_files:
            with open(local_file, "rb") as f:
                ftp.storbinary(f"STOR {local_file}", f)


def archive_uploaded(local_files):
    if len(local_files) > 1:
        for local_file in local_files[:-1]:
            os.rename(local_file, f"uploaded/{local_file}")

