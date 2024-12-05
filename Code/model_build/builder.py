import time
from abc import ABC, abstractmethod


class Builder(ABC):

    def __init__(self, build_input_path, build_output_path, score_timing_path):
        self.build_input_path = build_input_path
        self.build_output_path = build_output_path
        self.score_timing_path = score_timing_path

    def build(self):
        start_time = time.time()
        self.model_build()
        elapsed_time = time.time() - start_time

        print(f'Model Build Time: {elapsed_time}')
        with open(f"{self.score_timing_path}/model_build_time.json", 'w') as file:
            file.write(f"""{{"time": {elapsed_time}, "status": "success"}}""")

    @abstractmethod
    def model_build(self):
        pass


class NaiveTSPBuilder(Builder):

    def model_build(self):
        pass
