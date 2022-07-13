from cmath import sqrt
from swipe import Swipe
import numpy as np


def split_into_sized_chunks(lst, size: int):
    return np.array_split(lst, size)


def pairwise_length_vector(swipe: Swipe): #This function creates an array of the length of from point to point 
    length_vector = []
    times = swipe.swipe_timestamps()
    print("Times: ", times)
    x_coords = []
    y_coords = []
    for time in times:
        x_coords.append(int(swipe.x_pos(time)))
        y_coords.append(int(swipe.y_pos(time)))
    # print("X positions: ", (x_coords))
    # print("Y positions: ", (y_coords))
    for i in range(0, len(x_coords) - 1):
        x1 = x_coords[i]
        x2 = x_coords[i + 1]
        y1 = y_coords[i]
        y2 = y_coords[i + 1]
        length_vector.append(pow(pow((y2 - y1), 2) + pow((x2 - x1), 2), 0.5))
    return length_vector


class Feature_Extractor:
    def __init__(self):
        pass

    @staticmethod
    def length(swipe: Swipe):
        #! FIXME: We need to figure out which file is giving us a divide by zero error and why
        pairwise_lengths = pairwise_length_vector(swipe)
        return sum(pairwise_lengths)

    @staticmethod
    def time_delta(swipe: Swipe):
        timestamps = swipe.swipe_timestamps()
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



    @staticmethod
    def calculate_velocity(swipe: Swipe):
        length = pairwise_length_vector(swipe)
        velocities = []
        

    @staticmethod
    def calculate_acceleration(initial_swipe: Swipe):
        velocity = Feature_Extractor.calculate_velocity(initial_swipe)
        time = Feature_Extractor.time_delta(initial_swipe)

        return float(velocity / time)

    @staticmethod
    def percentile_velocity(initial_swipe: Swipe, percentile: float):
        if percentile >= 1.0 or percentile <= 0.0:
            raise ValueError("Percentile should be between 0 and 1 non-inclusive")
        velocity = Feature_Extractor.calculate_velocity(initial_swipe)
        return float(velocity * percentile)

    @staticmethod
    def extract_all_features(swipe: Swipe):
        feature_values = {}
        feature_values["length"] = Feature_Extractor.length(swipe)
        feature_values["velocity"] = Feature_Extractor.calculate_velocity(swipe)
        feature_values["acceleration"] = Feature_Extractor.calculate_acceleration(swipe)
        feature_values["percentile"] = Feature_Extractor.percentile_velocity(swipe, 0.3)
        return feature_values
