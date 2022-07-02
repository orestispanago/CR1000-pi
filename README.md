## CR1000-pi

Gets measurements from Campbell Scientific CR1000 datalogger

Saves data to daily csv files

Uploads csv files to FTP server

Using [PyCampbellCR1000 library](https://github.com/LionelDarras/PyCampbellCR1000)

Crontab:

```
*/5 * * * * python3 ~/CR1000-pi/main.py
```