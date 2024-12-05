from Code.model_build.builder import *
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from typing import Type
from abc import ABC, abstractmethod


class Solver(ABC):

    def __init__(self, build_output_path, apply_input_path, apply_output_path, score_timing_path):
        self.build_output_path = build_output_path
        self.apply_input_path = apply_input_path
        self.apply_output_path = apply_output_path
        self.score_timing_path = score_timing_path

    def apply(self):
        start_time = time.time()
        self.model_apply()
        elapsed_time = time.time() - start_time

        print(f'Model Apply Time: {elapsed_time}')
        with open(f"{self.score_timing_path}/model_apply_time.json", 'w') as file:
            file.write(f"""{{"time": {elapsed_time}, "status": "success"}}""")

    @abstractmethod
    def model_apply(self):
        pass


class RandomSolver(Solver):

    def model_apply(self):
        pass


class NaiveTSPSolver(Solver):

    def model_apply(self):
        pass


algorithm_registry: dict[str, tuple[Type[Builder], Type[Solver]]] = {
    "Random": (Builder, RandomSolver),
    "NaiveTSP": (NaiveTSPBuilder, NaiveTSPSolver),
}
