from abc import ABC, abstractmethod
import json
import numpy as np
import time


class Builder(ABC):

    def __init__(self, build_input_path, build_output_path, score_timing_path):
        self.build_input_path = build_input_path
        self.build_output_path = build_output_path
        self.score_timing_path = score_timing_path

        # Optional if needed
        self.actual_sequences = None
        self.invalid_sequence_scores = None
        self.package_data = None
        self.route_data = None
        self.travel_times = None

    def build(self):
        start_time = time.time()
        self.model_build()
        elapsed_time = int(time.time() - start_time)

        print(f'Model Build Time: {elapsed_time}')
        with open(f"{self.score_timing_path}/model_build_time.json", 'w') as file:
            file.write(f"""{{"time": {elapsed_time}, "status": "success"}}""")

    @abstractmethod
    def model_build(self):
        pass


class BuilderUtils(Builder, ABC):

    def read_fine_grained_dataset(self):
        self.actual_sequences = json.load(
            open(f"{self.build_input_path}/fine_grained_actual_sequences.json")
        )
        self.invalid_sequence_scores = json.load(
            open(f"{self.build_input_path}/fine_grained_invalid_sequence_scores.json")
        )
        self.package_data = json.load(
            open(f"{self.build_input_path}/fine_grained_package_data.json")
        )
        self.route_data = json.load(
            open(f"{self.build_input_path}/fine_grained_route_data.json")
        )
        self.travel_times = json.load(
            open(f"{self.build_input_path}/fine_grained_travel_times.json")
        )

    @staticmethod
    def build_adjacency_matrix(route_travel_times):
        """
        Parameters
        ----------
        route_travel_times: dict
        Dictionary containing the travel times for a specific route.

        Data format:
        {
            "<stop-id*>": {
              "<stop-id*>": 0,
              "<stop-id>": "<float-number>",
              "<stop-id>": "<float-number>",
              "..."
            },
            "<stop-id*>": {
              "<stop-id>": "<float-number>",
              "<stop-id*>": 0,
              "<stop-id>": "<float-number>",
              "..."
            },
            "..."
        },
        """

        n = len(route_travel_times)
        adjacency_matrix = np.zeros((n, n))

        for start, start_dict in route_travel_times.items():
            for stop, dist in start_dict.items():
                adjacency_matrix[start, stop] = dist

        return adjacency_matrix


class EmptyBuilder(Builder):

    def model_build(self):
        pass


class NaiveTSPBuilder(BuilderUtils):

    def model_build(self):
        self.read_fine_grained_dataset()


