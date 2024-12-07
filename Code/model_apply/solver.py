from Code.model_build.builder import *
import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from typing import Type


class Solver(ABC):

    def __init__(self, build_output_path, apply_input_path, apply_output_path, score_timing_path):
        self.build_output_path = build_output_path
        self.apply_input_path = apply_input_path
        self.apply_output_path = apply_output_path
        self.score_timing_path = score_timing_path

        self.new_package_data = None
        self.new_route_data = None
        self.new_travel_times = None

    def apply(self):
        start_time = time.time()
        proposed_sequences = self.model_apply()
        elapsed_time = int(time.time() - start_time)

        print(f'Model Apply Time: {elapsed_time}')

        # noinspection PyTypeChecker
        json.dump(proposed_sequences, open(f"{self.apply_output_path}/proposed_sequences.json", 'w'))
        with open(f"{self.score_timing_path}/model_apply_time.json", 'w') as file:
            file.write(f"""{{"time": {elapsed_time}, "status": "success"}}""")

    @abstractmethod
    def model_apply(self) -> dict:
        """
        Returns
        -------
        proposed_sequences: dict
        Dictionary containing proposed sequences.

        Data format:
        {
            "RouteID_<hex-hash>": {
                "proposed": {
                    "<stop-id>": 0,
                    "<stop-id>": 1,
                    "<stop-id>": 2,
                    "<stop-id>": 3,
                    "..."
                },
                "..."
            }
        }
        """
        pass


class RandomSolver(Solver):

    def model_apply(self):
        proposed_sequences = dict()
        self.new_route_data = json.load(open(f"{self.apply_input_path}/new_route_data.json", 'r'))
        self.new_travel_times = json.load(open(f"{self.apply_input_path}/new_travel_times.json", 'r'))

        for route in self.new_route_data:
            route_solution = self.solve_route(route)
            proposed_sequences[route] = {"proposed": route_solution}

        return proposed_sequences

    def solve_route(self, route):
        res = dict()
        stops = self.new_route_data[route]["stops"]

        station_idx, station = next((i, stop) for i, stop in enumerate(stops) if stops[stop]["type"] == "Station")
        stops = list(stops)
        stops[0], stops[station_idx] = stops[station_idx], stops[0]
        other_stops = stops[1:]
        np.random.shuffle(other_stops)

        res[station] = 0
        for i, stop in enumerate(other_stops, start=1):
            res[stop] = i
        return res


class NaiveTSPSolver(Solver):

    def model_apply(self):
        pass


algorithm_registry: dict[str, tuple[Type[Builder], Type[Solver]]] = {
    "Random": (EmptyBuilder, RandomSolver),
    "NaiveTSP": (NaiveTSPBuilder, NaiveTSPSolver),
}
