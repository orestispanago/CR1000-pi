import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

FTP_IP = ""
FTP_USER = ""
FTP_PASS = ""
FTP_DIR = ""


LAST_REC_FILE = os.path.join(os.getcwd(), "last_record.log")
DT_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
ARCHIVE_DIR = os.path.join(os.getcwd(), "archive")
