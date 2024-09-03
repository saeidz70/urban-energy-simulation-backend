import json
from typing import Dict, Any


class BuildingUsageProcessor:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.input_file = self.config["input_params"]["building_use"]["input"]
        self.output_file = self.config["input_params"]["building_use"]["output"]
        self.old_column_name = self.config["input_params"]["building_use"]["old_column_name"]
        self.new_column_name = self.config["input_params"]["building_use"]["new_column_name"]
        self.allowed_buildings = self.config["input_params"]["building_use"]["allowed_buildings"]
        self.data = None

    def load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found.")
            raise
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the configuration file {config_path}.")
            raise

    def load_data(self) -> None:
        try:
            with open(self.input_file, 'r') as file:
                self.data = json.load(file)
            print(f"Data loaded from {self.input_file}")
        except FileNotFoundError:
            print(f"Input file {self.input_file} not found.")
            raise
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the input file {self.input_file}.")
            raise

    def save_data(self) -> None:
        try:
            with open(self.output_file, 'w') as file:
                json.dump(self.data, file, indent=4)
            print(f"Data saved to {self.output_file}")
        except IOError:
            print(f"Error writing to the output file {self.output_file}.")
            raise

    def change_column_name(self) -> None:
        for feature in self.data['features']:
            if self.old_column_name in feature['properties']:
                # Create a new dictionary with the modified column name but preserve order
                new_properties = {}
                for key, value in feature['properties'].items():
                    if key == self.old_column_name:
                        new_properties[self.new_column_name] = value
                    else:
                        new_properties[key] = value
                feature['properties'] = new_properties

    def filter_buildings(self) -> None:
        self.data['features'] = [
            feature for feature in self.data['features']
            if feature['properties'].get(self.new_column_name) in self.allowed_buildings
        ]
        print(f"Buildings filtered to include only: {self.allowed_buildings}")

    def process(self) -> None:
        self.load_data()
        self.change_column_name()
        self.filter_buildings()
        self.save_data()
