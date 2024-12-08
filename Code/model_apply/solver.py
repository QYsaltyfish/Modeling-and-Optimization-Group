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

        # Optional if needed
        self.package_data = None
        self.route_data = None
        self.travel_times = None

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


class SolverUtils(Solver, ABC):

    def read_fine_grained_dataset(self):
        self.package_data = json.load(open(f"{self.apply_input_path}/fine_grained_package_data.json"))
        self.route_data = json.load(open(f"{self.apply_input_path}/fine_grained_route_data.json"))
        self.travel_times = json.load(open(f"{self.apply_input_path}/fine_grained_travel_times.json"))

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
        }

        Returns
        -------
        adjacency_matrix: numpy.ndarray
            A 2D numpy array representing the adjacency matrix of travel times.
            The element at [i, j] corresponds to the travel time from the stop
            represented by index `i` to the stop represented by index `j`.
        """

        n = len(route_travel_times)
        adjacency_matrix = np.zeros((n, n), dtype=float)

        for start_idx, end_dict in enumerate(route_travel_times.values()):
            for end_idx, dist in enumerate(end_dict.values()):
                adjacency_matrix[start_idx, end_idx] = dist

        return adjacency_matrix

    @staticmethod
    def find_station(route_stops):
        """
        Parameters
        ----------
        route_stops: dict
        Dictionary containing the stop types for a specific route.

        Data format:
        {
            "<stop-id>": {
                "type": "<stop-type>"
            },
            "..."
        }

        Returns
        -------
        station_info: tuple
            A tuple containing two elements:
            - station_idx (int): The index of the station.
            - station_id (str): The stop ID of the station.
        """
        station_idx = None
        station_id = None

        for i, (stop_id, stop_dict) in enumerate(route_stops.items()):
            if stop_dict["type"] == "Station":
                station_idx = i
                station_id = stop_id

        return station_idx, station_id

    @staticmethod
    def solve_tsp_model(adjacency_matrix, station):
        manager = pywrapcp.RoutingIndexManager(
            len(adjacency_matrix), 1, station
        )
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(adjacency_matrix[from_node, to_node])

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            print('Solution:')
            index = routing.Start(0)
            plan_output = 'Route for vehicle 0:\n'
            route_distance = 0
            while not routing.IsEnd(index):
                plan_output += ' {} ->'.format(manager.IndexToNode(index))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            plan_output += ' {}\n'.format(manager.IndexToNode(index))
            print(plan_output)
            print('Route distance: {}'.format(route_distance))
        else:
            print('No solution found !')

        return solution


class RandomSolver(Solver):

    def model_apply(self):
        proposed_sequences = dict()
        self.route_data = json.load(open(f"{self.apply_input_path}/new_route_data.json", 'r'))
        self.travel_times = json.load(open(f"{self.apply_input_path}/new_travel_times.json", 'r'))

        for route in self.route_data:
            route_solution = self.solve_route(route)
            proposed_sequences[route] = {"proposed": route_solution}

        return proposed_sequences

    def solve_route(self, route):
        res = dict()
        stops = self.route_data[route]["stops"]

        station_idx, station = next((i, stop) for i, stop in enumerate(stops) if stops[stop]["type"] == "Station")
        stops = list(stops)
        stops[0], stops[station_idx] = stops[station_idx], stops[0]
        other_stops = stops[1:]
        np.random.shuffle(other_stops)

        res[station] = 0
        for i, stop in enumerate(other_stops, start=1):
            res[stop] = i
        return res


class NaiveTSPSolver(SolverUtils):

    def model_apply(self):
        self.read_fine_grained_dataset()

        for route in self.route_data:
            self.solve_route(route)

    def solve_route(self, route):
        res = dict()
        stops = self.route_data[route]["stops"]

        station_idx, station = self.find_station(self.route_data[route]["stops"])
        adjacency_matrix = self.build_adjacency_matrix(self.travel_times[route])
        adjacency_matrix = self.process_adjacency_matrix(adjacency_matrix)

    @staticmethod
    def process_adjacency_matrix(adjacency_matrix):
        n = adjacency_matrix.shape[0]

        for row in range(n):
            for col in range(row + 1, n):
                tmp = (adjacency_matrix[row, col] + adjacency_matrix[col, row]) * 0.5
                adjacency_matrix[row, col] = tmp
                adjacency_matrix[col, row] = tmp

        return adjacency_matrix



algorithm_registry: dict[str, tuple[Type[Builder], Type[Solver]]] = {
    "Random": (EmptyBuilder, RandomSolver),
    "NaiveTSP": (NaiveTSPBuilder, NaiveTSPSolver),
}


def main():
    travel_times = {'A': {'A': 0, 'B': 2, 'C': 500},
                    'B': {'A': 500, 'B': 0, 'C': 4},
                    'C': {'A': 2, 'B': 500, 'C': 0}}

    adjacency_matrix = SolverUtils.build_adjacency_matrix(travel_times)
    print(adjacency_matrix)
    adjacency_matrix = NaiveTSPSolver.process_adjacency_matrix(adjacency_matrix)
    print(adjacency_matrix)

    SolverUtils.solve_tsp_model(adjacency_matrix, 2)



if  __name__ == "__main__":
    main()
