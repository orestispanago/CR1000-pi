## CR1000-pi

Gets measurements from Campbell Scientific CR1000 or CR800 datalogger

Saves data to daily csv files

Uploads csv files to FTP and SFTP server

Based on [PyCampbellCR1000 library](https://github.com/LionelDarras/PyCampbellCR1000)

## Instructions

Install requirements using 

```pip install -r requirements.txt```

Edit the tasks configuration parameters in ```tasks_config.json```. 

To remove a task, edit ```main()``` function in ```main.py```.

To avoid overlapping cron job execution, use ```flock``` in crontab:

```
*/5 * * * * /usr/bin/flock -w 0 ~/cr1000_pi.lock python3 ~/CR1000-pi/main.py
```

To check if your cron job is running:

```
grep CRON /var/log/syslog
```

To make sure that ```flock``` works:

```
flock -n -x ~/cr1000_pi.lock true || echo "LOCKED"
```