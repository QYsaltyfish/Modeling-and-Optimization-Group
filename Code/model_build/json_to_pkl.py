import json
import pickle

train_data_path = '../../Training dataset/model_build_inputs'
actual_sequences = json.load(open(f"{train_data_path}/actual_sequences.json"))
package_data = json.load(open(f"{train_data_path}/package_data.json"))
route_data = json.load(open(f"{train_data_path}/route_data.json"))
travel_times = json.load(open(f"{train_data_path}/travel_times.json"))

pickle.dump(actual_sequences, open(f"./pkl/actual_sequences.pkl", "wb"))
pickle.dump(package_data, open(f"./pkl/package_data.pkl", "wb"))
pickle.dump(route_data, open(f"./pkl/route_data.pkl", "wb"))
pickle.dump(travel_times, open(f"./pkl/travel_times.pkl", "wb"))
