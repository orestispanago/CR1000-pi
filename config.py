import json


class Config:
    # Converts dict to object so that attributes are accessed with "." notation
    def __init__(self, dict):
        self.__dict__.update(dict)

    def __repr__(self):
        return f"{self.__dict__}"


with open("ftp_config.json", "r") as f:
    contents = json.load(f)

nas = Config(contents["nas"])
mymeasurements = Config(contents["mymeasurements"])
pyranocam = Config(contents["pyranocam"])