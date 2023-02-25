## CR1000-pi

Gets measurements from Campbell Scientific CR1000 or CR800 datalogger

Saves data to daily csv files

Uploads csv files to FTP or SFTP server

## Requirements: 

[PyCampbellCR1000 library](https://github.com/LionelDarras/PyCampbellCR1000)

Install using:

```pip install pycampbellcr1000```

pysftp:

```pip install pysftp```

## Instructions

Edit the FTP parameters in ```uploader.py``` and ```TABLE_NAME``` in ```datalogger.py```. 

To avoid overlapping cron job execution, use ```flock``` in crontab:

```
*/5 * * * * /usr/bin/flock -w 0 ~/flock_file.lock python3 ~/CR1000-pi/main.py
```

To check if your cron job is running:

```
grep CRON /var/log/syslog
```

To make sure that ```flock``` works:

```
flock -n -x ~/flock_file.lock true || echo "LOCKED"
```