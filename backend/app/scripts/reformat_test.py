import json
from collections import defaultdict
import os

# Get current script dir and construct json file path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder_path = os.path.join(script_dir, '..', 'app/data')
json_file_path = os.path.join(data_folder_path, 'test_mode.json')
output_file_path = os.path.join(data_folder_path, 'test_mode_grouped.json')

with open(json_file_path, 'r') as f:
    data = json.load(f)

grouped_data = defaultdict(list)
for item in data:
    mode_num = item['extra']['mode_num']
    grouped_data[mode_num].append(item)

result = [{'mode_num': key, 'questions': value, 'is_test': True} for key, value in grouped_data.items()]

with open(output_file_path, 'w') as f:
    json.dump(result, f, indent=4)
