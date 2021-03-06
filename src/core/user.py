import warnings
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from tqdm import tqdm
import math
import statistics
from algo import score_calc, calc_FRR, calc_FAR, calc_EER, DET_curve
from features import Feature_Extractor
from swipe_extractor import (
    compute_timestamp_deltas,
    create_swipes,
    extract_swipes_indices,
    extract_timestamps_from_file,
    extract_trajectories,
    into_intervals,
    write_to_file,
)
from swipe_extractor import unique_words_from_file
import os
from collections import defaultdict


def make_template(swipes):
    mean_template = [0, 0, 0, 0, 0]

    for feature_set in swipes:
        assert len(feature_set) == 5
        for x in range(0, 5):
            mean_template[x] += feature_set[x]
    for y in range(0, 5):
        mean_template[y] /= 5

    return mean_template


class User:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    def get_path(self):
        return self.path

    def get_name(self):
        return self.name

    def make_all_swipes(self):
        swipeset = defaultdict(list)
        words = unique_words_from_file(self.get_path())
        for unique_word in words:
            # At this current moment we can reasonably assume that all the files have been generated
            trajectories, word = extract_trajectories(self.get_path(), unique_word)
            # write_to_file(trajectories, unique_word)

            timestamps, word = extract_timestamps_from_file(
                os.path.join(os.getcwd(), "src", "core", "temp", unique_word + ".log")
            )

            # print("New:", timestamps)
            # print(unique_word)
            delta = compute_timestamp_deltas(timestamps)
            # print(delta)
            indices = extract_swipes_indices(delta)
            if indices is not None:
                # print(indices)
                intervals = into_intervals(indices)
                # print(intervals)
                # input()
                swipes = create_swipes(
                    timestamps,
                    word,
                    intervals,
                    os.path.join(
                        os.getcwd(), "src", "core", "temp", unique_word + ".log"
                    ),
                )
                for swipe in swipes:
                    swipeset[word].append(swipe)
            elif indices is None:
                warnings.warn(
                    "No indices above the threshold, so swipes cannot be made"
                )
        return swipeset

    def divide_swipes(self, swipes: defaultdict, swipe_count: int):
        template_size = math.floor(swipe_count * 0.7)
        # print("template size:", template_size)
        probe_size = swipe_count - template_size
        # print("probe size:", probe_size)
        counter = 0
        template = []
        probe = []

        for v in swipes.values():
            for i in v:
                if counter < template_size:
                    template.append(i)
                    counter += 1
                elif counter >= template_size:
                    probe.append(i)
                    counter += 1

        # print("counter:", counter)
        # print("length of template list:", len(template))
        # print("length of probe list:", len(probe))

        return (template, probe)


def process_files():
    PIK = "genuine.dat"
    sum = 0
    user = User(
        "2c30a5a6amjsgs1ganoo6kg2lb",
        os.path.join(os.getcwd(), "data", "2c30a5a6amjsgs1ganoo6kg2lb.log"),
    )
    for k, v in user.make_all_swipes().items():
        # print(k)
        sum += len(v)
    # print(sum)
    features = []
    a, b = user.divide_swipes(user.make_all_swipes(), sum)
    for swipe in a:
        features.append(Feature_Extractor.extract_all_features_to_list(swipe))
    # print(features)
    # print(make_template(features))

    # this prints out all the genuine scores
    u = 0
    genuine_scores = []
    template_features = make_template(features)
    for swipe in b:
        genuine_scores.append(score_calc(template_features, swipe))
        u += 1
    genuine_scores.sort()
    with open(PIK, "wb") as f:
        pickle.dump(genuine_scores, f)
    # print(" Genuine scores", genuine_scores)

    # Printing out impostor scores
    impostor_scores = []
    p = os.path.join(os.getcwd(), "data")
    onlyfiles = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))]
    for file in tqdm(onlyfiles):
        user = User(
            file,
            os.path.join(os.getcwd(), "data", file),
        )
        sum = 0
        for k, v in user.make_all_swipes().items():
            # print(k)
            sum += len(v)
        print("Swipe Length:", sum)
        other_file_template, other_file_impostor = user.divide_swipes(
            user.make_all_swipes(), sum
        )
        other_file_total = other_file_impostor + other_file_template
        print("total swipes in Other file", len(other_file_total))
        print(file)
        for swipe in other_file_total:
            impostor_scores.append(score_calc(template_features, swipe))
        imposter_file_path = os.path.join(os.getcwd(), "gen", "imposter_" + file)
        # print(imposter_file_path)

        with open(imposter_file_path, "wb") as f:
            pickle.dump(impostor_scores, f)
        # print("impostor scores:\n", impostor_scores)


def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def stats():
    p = os.path.join(os.getcwd(), "data")
    onlyfiles = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))]
    sum = 0
    genuine_scores = []
    for file in tqdm(onlyfiles):
        user = User(
            file,
            os.path.join(os.getcwd(), "data", file),
        )
        for k, v in user.make_all_swipes().items():
            # print(k)
            sum += len(v)
        features = []
        a, b = user.divide_swipes(user.make_all_swipes(), sum)

        for swipe in a:
            features.append(Feature_Extractor.extract_all_features_to_list(swipe))

        template_features = make_template(features)
        for swipe in b:
            genuine_scores.append(score_calc(template_features, swipe))

    print("AVG:", sum(genuine_scores) / len(genuine_scores))
    print("Mean:", statistics.mean(genuine_scores))
    print("Median:", statistics.median(genuine_scores))
    print("St. dev:", statistics.stdev(genuine_scores))

    return genuine_scores


def generate_all_genuine_scores():
    p = os.path.join(os.getcwd(), "data")
    onlyfiles = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))]
    for file in tqdm(onlyfiles):
        sum = 0
        user = User(
            file,
            os.path.join(os.getcwd(), "data", file),
        )
        for k, v in user.make_all_swipes().items():
            # print(k)
            sum += len(v)
        # print(sum)
        features = []
        a, b = user.divide_swipes(user.make_all_swipes(), sum)
        for swipe in a:
            features.append(Feature_Extractor.extract_all_features_to_list(swipe))
        # print(features)
        # print(make_template(features))

        # this prints out all the genuine scores
        u = 0
        genuine_scores = []
        template_features = make_template(features)
        for swipe in b:
            genuine_scores.append(score_calc(template_features, swipe))
            u += 1
        genuine_file_path = os.path.join(
            os.getcwd(), "genuine_scores", "genuine_" + file
        )
        # print(file)
        try:
            with open(genuine_file_path, "wb") as f:
                pickle.dump(genuine_scores, f)
        except FileNotFoundError:
            pass


def avg_swipes():
    p = os.path.join(os.getcwd(), "data")
    onlyfiles = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))]
    file_swipes = []
    for file in tqdm(onlyfiles):
        if file == ".DS_Store":
            pass
        print(file)
        s = 0
        if file == ".log":
            return
        else:
            user = User(
                file,
                os.path.join(os.getcwd(), "data", file),
            )
            for swipe in user.make_all_swipes().items():
                s += 1
        file_swipes.append(s)
        # print(file_swipes)
    return sum(file_swipes) / len(file_swipes)

def swipe_length_histogram():
    p = os.path.join(os.getcwd(), "data")
    onlyfiles = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))]
    swipe_lengths = []
    for file in tqdm(onlyfiles):
        user = User(
            file,
            os.path.join(os.getcwd(), "data", file),
        )
        for _,swipe in user.make_all_swipes().items():
                for obj in swipe:
                    swipe_lengths.append(Feature_Extractor.length(obj))
        avg = sum(swipe_lengths)/len(swipe_lengths)
        st_dev = statistics.stdev(swipe_lengths)
    print("Avg:", avg)
    print("st. dev", st_dev) #GET RID OF .DS Store

if __name__ == "__main__":
   swipe_length_histogram()