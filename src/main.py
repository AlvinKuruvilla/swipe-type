from rich.traceback import install
from core.features import Feature_Extractor
from core.swipe_extractor import (
    compute_timestamp_deltas,
    extract_timestamps_from_file,
    extract_swipes_indices,
    into_intervals,
    create_swipes,
    unique_words_from_file,
    extract_trajectories,
    write_to_file,
)
import os
import pickle
import warnings

if __name__ == "__main__":
    install()
    words = unique_words_from_file()
    # print(words)
    for unique_word in words:
        timestamps = extract_timestamps_from_file(
            os.path.join(os.getcwd(), "src", "core", "temp", unique_word + ".log")
        )
        print(timestamps)
