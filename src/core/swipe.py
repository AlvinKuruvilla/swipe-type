import pandas as pd


def string_to_list(string: str):
    # FIXME: Improve this regex so it only looks at spaces and does not accidentally think a quote, or anything else, is
    # part of the expression string
    res = list(string.split(" "))
    return res


class Backing_File:
    def __init__(self, path: str):
        self.path = path

    def get_path(self):
        return self.path

    def lookup_row_by_timestamp(self, timestamp: str):
        df = pd.read_csv(
            self.get_path(),
            sep=" ",
            usecols=[
                "sentence",
                "timestamp",
                "keyb_width",
                "keyb_height",
                "event",
                "x_pos",
                "y_pos",
                "x_radius",
                "y_radius",
                "angle",
                "word",
            ],
        )

        return df.loc[df["timestamp"] == timestamp].values.tolist()


class Swipe:
    def __init__(self, key: str, backing_file: Backing_File, swipe_data):
        self.key = key
        self.backing_file = backing_file
        self.swipe_data = swipe_data

    def get_key(self):
        return self.key

    def x_pos(self, timestamp: str):
        row = self.get_backing_file().lookup_row_by_timestamp(timestamp)
        row = row.split(" ")
        # FIX: I dont know if this is a bug with
        # how we are sending the swipe data to the swipe object or if we accidentally
        # shave off a row somewhere but i looks like when printing out the rows in the file
        # the last row is missing, or at least it is for delay.log
        # print("Found row:", row)
        return row[5]

    def y_pos(self, timestamp: str):
        row = self.get_backing_file().lookup_row_by_timestamp(timestamp)
        row = row.split(" ")
        # print("Found row:", row)
        return row[6]

    def sentence(self, timestamp: str):
        row = self.get_backing_file().lookup_row_by_timestamp(timestamp)
        row = row.split(" ")
        return row[0]

    def first_and_last_timestamp(self):
        return [self.swipe_data[0], self.swipe_data[-1]]

    def last_timestamp(self):
        return self.swipe_data[-1]

    def first_timestamp(self):
        return self.swipe_data[0]

    def event(self, timestamp: str):
        row = self.get_backing_file().lookup_row_by_timestamp(timestamp)
        row = row.split(" ")
        return row[4]

    def x_radius(self, timestamp: str):
        row = self.get_backing_file().lookup_row_by_timestamp(timestamp)
        row = row.split(" ")
        return row[7]

    def y_radius(self, timestamp: str):
        row = self.get_backing_file().lookup_row_by_timestamp(timestamp)
        row = row.split(" ")
        return row[8]

    def get_word(self, timestamp: str):
        row = self.get_backing_file().lookup_row_by_timestamp(timestamp)
        row = row.split(" ")
        return row[10]

    def swipe_timestamps(self):
        # print(self.swipe_data)
        # print("Found", len(self.swipe_data), "timestamps")
        return self.swipe_data

    def timestamp_at(self, index: int):
        return self.swipe_timestamps[index]

    def stringify(self):
        return f"Word: {self.key} Timestamps {self.swipe_data}"

    def get_backing_file(self) -> Backing_File:
        return self.backing_file
