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

    output = model_score.evaluate(
        "../Training dataset/model_score_inputs/new_actual_sequences.json",
        "../Training dataset/model_apply_outputs/proposed_sequences.json",
        "../Training dataset/model_apply_inputs/new_travel_times.json",
        "../Training dataset/model_score_inputs/new_invalid_sequence_scores.json"
    )

    if all(output["route_feasibility"].values()):
        print(f"""Submission score: {output["submission_score"]}""")
    else:
        print(f"""Submission error:\n{output["route_feasibility"]}""")


if __name__ == '__main__':
    model_test("Random")
