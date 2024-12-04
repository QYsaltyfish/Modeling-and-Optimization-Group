from model_build.builder import *
from model_apply.solver import *
from model_score import model_score


def model_test(model: str):
    builder = algorithm_registry["model"][0]
    solver = algorithm_registry["model"][1]

