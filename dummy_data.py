import datetime
import urllib.request

external_ip = urllib.request.urlopen("https://ident.me").read().decode("utf8")


def save_dummy_daily_file():
    utc_now = datetime.datetime.utcnow()
    output_file = f'{utc_now.strftime("%Y%m%d")}.csv'
    num_rows = 30
    num_cols = 10
    dummy_cols = "\t9999.99" * num_cols
    with open(output_file, "a") as f:
        for i in range(num_rows):
            utc_now = datetime.datetime.utcnow()
            date_str = utc_now.strftime("%Y-%m-%d %H:%M:%S.%f")
            f.write(f"{i+1}\t{date_str}\t{external_ip}{dummy_cols}\n")
