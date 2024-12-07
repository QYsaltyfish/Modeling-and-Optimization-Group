import json


def no_undelivered(route):
    for stop_dict in package_data[route].values():
        for package in stop_dict.values():
            if package["scan_status"] != "DELIVERED":
                return False
    return True


train_data_path = '../../Training dataset/model_build_inputs'
actual_sequences = json.load(open(f"{train_data_path}/actual_sequences.json"))
invalid_sequence_scores = json.load(open(f"{train_data_path}/invalid_sequence_scores.json"))
package_data = json.load(open(f"{train_data_path}/package_data.json"))
route_data = json.load(open(f"{train_data_path}/route_data.json"))
travel_times = json.load(open(f"{train_data_path}/travel_times.json"))

fine_grained_routes = [
    route
    for route in route_data
    if route_data[route]["route_score"] == "High" and
       no_undelivered(route)
]

actual_sequences = {route: actual_sequences[route] for route in fine_grained_routes}
invalid_sequence_scores = {route: invalid_sequence_scores[route] for route in fine_grained_routes}
package_data = {route: package_data[route] for route in fine_grained_routes}
route_data = {route: route_data[route] for route in fine_grained_routes}
travel_times = {route: travel_times[route] for route in fine_grained_routes}

json.dump(actual_sequences, open(f"{train_data_path}/fine_grained_actual_sequences.json", "w"))
json.dump(invalid_sequence_scores, open(f"{train_data_path}/fine_grained_invalid_sequence_scores.json", "w"))
json.dump(package_data, open(f"{train_data_path}/fine_grained_package_data.json", "w"))
json.dump(route_data, open(f"{train_data_path}/fine_grained_route_data.json", "w"))
json.dump(travel_times, open(f"{train_data_path}/fine_grained_travel_times.json", "w"))
