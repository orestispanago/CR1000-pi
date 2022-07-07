import os
import logging


logger = logging.getLogger(__name__)


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
