import pandas as pd
import os
from typing import List
from .swipe import Backing_File, Swipe
from pathlib import Path
import matplotlib.pyplot as plt

THRESHOLD = 30


def plot_deltas(list_delta):
    plt.plot(list_delta, color="magenta", marker="o", mfc="pink")  # plot the data

    plt.xticks(range(0, len(list_delta) + 1, 1))  # set the tick frequency on x-axis

    plt.ylabel("data")  # set the label for y axis
    plt.xlabel("index")  # set the label for x-axis
    plt.title("Time Deltas")  # set the title of the graph
    plt.show()  # display the graph


def grab_first():
    path = os.path.join(os.getcwd(), "data")
    first = os.listdir(path)[0]
    print(first)
    pd.options.display.max_columns = None
    df = pd.read_csv(os.path.join(path, first))
    return df


def unique_words(df: pd.DataFrame):
    data = df.iloc[:, :1].values.tolist()
    store = set()
    for row in data:
        # Since the log file is not actually a csv we can't do a simple column name/index lookup
        string = row[10]
        sep = " "
        # Use a regex of the space character to split out the sentence column from the string
        sentence = string.split(sep, 1)[0]
        store.add(sentence)
    return store


def unique_words_from_file(path: str):
    file = open(path, "r")
    lines = file.readlines()
    search_space = lines[1:]
    found = set()
    for line in search_space:
        word = list(line.split(" "))[10]
        if (
            word != "me"
            and word != "vanke"
            and word != "told"
            and word != "mary"
            and word != "pembina"
            and word != "interactions"
            and word != "haciendo"
        ):
            found.add(word)
    return found


def unique_sentences(df: pd.DataFrame):
    data = df.iloc[:, :1].values.tolist()
    store = set()
    for row in data:
        # Since the log file is not actually a csv we can;t do a simple column name/index lookup
        string = row[0]
        sep = " "
        # Use a regex of the space character to split out the sentence column from the string
        sentence = string.split(sep, 1)[0]
        store.append(sentence)
    return store


def extract_trajectories(path: str, key: str):
    # TODO: Reading the file should be its own method.... we should only operate on the DataFrame (take the df as a parameter)
    df = pd.read_csv(
        path,
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
    found = df.loc[df["word"] == key].values.tolist()
    return (found, key)


def write_to_file(data, key):
    # data_file = Path(os.path.join(os.getcwd(), "src", "py", "temp", key + ".log"))
    data_file = Path(os.path.join(os.getcwd(), "src", "core", "temp", key + ".log"))
    data_file.touch(exist_ok=True)
    f = open(data_file, "w+")
    for line in data:
        word = list(line.split(" "))[10]
        if key == word:
            f.write(line)


def extract_timestamps_from_file(path: str, header_present=False):
    file = open(path, "r")
    lines = file.readlines()
    timestamps = []
    for line in lines:
        res = list(line.split(" "))[1]
        word = list(line.split(" "))[10]
        timestamps.append((res))
    if header_present == True:
        return (timestamps[1:], word)
    elif header_present == False:
        return (timestamps, word)


def extract_timestamps_from_lines(lines: List[str]):
    timestamps = []
    for line in lines:
        res = list(line.split(" "))[1]
        word = list(line.split(" "))[10]
        timestamps.append((res))
    return (timestamps, word)


def compute_timestamp_deltas(timestamps: List[int]):
    try:
        # print(timestamps)
        curr = int(timestamps[0])
        # print("curr", curr)
        deltas = []
        for i in range(1, len(timestamps)):
            delta = int(timestamps[i]) - curr
            if delta > 0:
                deltas.append(delta)
            curr = int(timestamps[i])
        return deltas
    except ValueError:
        # print(timestamps)
        curr = int(timestamps[1])
        print("curr", curr)
        deltas = []
        for i in range(2, len(timestamps)):
            delta = int(timestamps[i]) - curr
            deltas.append(delta)
            curr = int(timestamps[i])
        return deltas


def precheck_deltas(deltas: List[int]):
    for delta in deltas:
        if delta < THRESHOLD:
            continue
        if delta > THRESHOLD:
            return False
    return True


def extract_swipes_indices(deltas: List[int]):
    # print("deltas: ", (deltas))
    if precheck_deltas(deltas) == True:
        return None
    above = []
    for i in range(0, len(deltas)):
        if deltas[i] >= THRESHOLD:
            above.append(i)
    return above


def into_intervals(indices: List[int]):
    intervals = []
    # print("Length of indices: ", len(indices))
    if len(indices) == 0:
        raise ValueError("No indices provided")
    elif len(indices) == 1:
        if indices[0] == 0:
            interval = [0, indices[0] + len(indices) + 1]
        else:
            interval = [0, indices[0] + 1]
        intervals.append(interval)
        return intervals
    try:
        for i in range(0, len(indices)):
            # FIXME: So let's say our indices are: [0, 22, 44], the code currently returns [0, 22], [22, 44]] when instead it should return [0, 22], [23, 44]]
            s = [indices[i], indices[i + 1] + 1]
            intervals.append(s)
        return intervals
    except IndexError:
        return intervals


def create_swipes(timestamps: List[str], word: str, intervals, path: str):
    # print(intervals)
    ranges = []
    for interval in intervals:
        ranges.append(list(range(interval[0], interval[1] + 1)))
    # print(ranges)
    swipe_list = []
    times = []
    for index_range in ranges:
        for element in index_range:
            time = timestamps[element - 1]
            times.append(time)
        swipe = Swipe(word, Backing_File(path), times)
        # print(len(times))
        # print(swipe)
        swipe_list.append(swipe)
        # print(len(swipe_list))
        # Clear the existing times before iterating again
        times = []
    return swipe_list
