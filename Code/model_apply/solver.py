from Code.model_build.builder import *
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


class NaiveTSPSolver:

    def __init__(self):
        pass


algorithm_registry = {
    "NaiveTSP": (NaiveTSPBuilder, NaiveTSPSolver),
}
