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
from tqdm import tqdm

if __name__ == "__main__":
    words = unique_words_from_file(
        os.path.join(os.getcwd(), "data", "n6ml9p7egar03rp99p8neh89if.log")
    )
    print(words)
    # print(words)
    # for unique_word in words:
    #     # At this current moment we can reasonably assume that all the files have been generated
    #     # print(file)
    #     trajectories, word = extract_trajectories(
    #         os.path.join(os.getcwd(), "data", "n6ml9p7egar03rp99p8neh89if.log"),
    #         unique_word,
    #     )
    #     print(trajectories)
