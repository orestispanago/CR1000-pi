from ftplib import FTP
import logging

logger = logging.getLogger(__name__)


def upload_to_ftp(local_files, ftp_ip, ftp_user, ftp_password, ftp_dir):
    logger.debug("Uploading to FTP server...")
    with FTP(ftp_ip, ftp_user, ftp_password) as ftp:
        ftp.cwd(ftp_dir)
        for local_file in local_files:
            with open(local_file, "rb") as f:
                ftp.storbinary(f"STOR {local_file}", f)
    logger.info(f"Uploaded {len(local_files)} files.")

