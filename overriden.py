import datetime
from pycampbellcr1000.utils import ListDict, Dict

# Override pycampbellcr1000.ListDict method to avoid b'' in table fields
def get_data_generator(self, tablename, start_date=None, stop_date=None):
    """Get all data from `tablename` from `start_date` to `stop_date` as
    generator. The data can be fragmented into multiple packets, this
    generator can return parsed data from each packet before receiving
    the next one.
    :param tablename: Table name that contains the data.
    :param start_date: The beginning datetime record.
    :param stop_date: The stopping datetime record.
    """
    self.ping_node()
    start_date = start_date or datetime(1990, 1, 1, 0, 0, 1)
    stop_date = stop_date or datetime.now()
    more = True
    while more:
        records = ListDict()
        data, more = self._collect_data(tablename, start_date, stop_date)
        for i, rec in enumerate(data):
            if not rec["NbrOfRecs"]:
                more = False
                break
            for j, item in enumerate(rec["RecFrag"]):
                if start_date <= item["TimeOfRec"] <= stop_date:
                    start_date = item["TimeOfRec"]
                    # for no duplicate record
                    if more and (
                        (j == (len(rec["RecFrag"]) - 1)) and (i == (len(data) - 1))
                    ):
                        break
                    new_rec = Dict()
                    new_rec["Datetime"] = item["TimeOfRec"]
                    new_rec["RecNbr"] = item["RecNbr"]
                    for key in item["Fields"]:
                        # overriden part
                        new_rec[key.decode("utf-8")] = item["Fields"][key]
                    records.append(new_rec)

        if records:
            records = records.sorted_by("Datetime")
            yield records.sorted_by("Datetime")
        else:
            more = False
