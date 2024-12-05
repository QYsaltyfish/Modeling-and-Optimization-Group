from model_apply.solver import *
from model_score import model_score


def model_test(model: str):
    builder = algorithm_registry[model][0]
    solver = algorithm_registry[model][1]

    builder = builder(
        "../Training dataset/model_build_inputs",
        "../Training dataset/model_build_outputs",
        "../Training dataset/model_score_timings"
    )
    builder.build()

    solver = solver(
        "../Training dataset/model_build_outputs",
        "../Training dataset/model_apply_inputs",
        "../Training dataset/model_apply_outputs",
        "../Training dataset/model_score_timings"
    )
    solver.apply()


if __name__ == '__main__':
    model_test("Random")
