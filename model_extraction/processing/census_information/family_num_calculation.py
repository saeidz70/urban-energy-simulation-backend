import json
import os


class FamilyCalculator:
    def __init__(self, config_path):
        # Initialize from configuration dictionary
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.input_file = config["input_params"]["family"]["input"]
        self.output_file = config["input_params"]["family"]["output"]
        self.family_column = config["input_params"]["family"]["family"]
        self.volume_column = config["input_params"]["family"]["volume"]
        self.sez_column = config["input_params"]["family"]["censusID"]
        self.input_data = {}
        self.buildings = []

    def read_input_data(self):
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Input file '{self.input_file}' not found.")
        with open(self.input_file, 'r') as file:
            self.input_data = json.load(file)
            self.buildings = self.input_data.get('features', [])

    def calculate_family_distribution(self):
        census_volumes = {}
        census_families = {}

        # First pass: Calculate census volumes and census families
        for building in self.buildings:
            properties = building.get('properties', {})
            census_id = properties.get(self.sez_column)
            volume = properties.get(self.volume_column, 0)
            families = int(properties.get(self.family_column, 0))

            if census_id not in census_volumes:
                census_volumes[census_id] = 0
            census_volumes[census_id] += volume

            census_families[census_id] = families

        # Second pass: Calculate allocated families and rearrange properties
        for building in self.buildings:
            properties = building.get('properties', {})
            census_id = properties.get(self.sez_column)
            volume = properties.get(self.volume_column, 0)

            if census_id in census_volumes and census_volumes[census_id] > 0:
                family_ratio = volume / census_volumes[census_id]
                allocated_families = family_ratio * census_families[census_id]
                properties['families'] = round(allocated_families)
            else:
                properties['families'] = 0

            # Create an ordered dictionary to ensure 'allocated_families' comes after 'volume'
            ordered_properties = {}
            for key in properties:
                ordered_properties[key] = properties[key]
                if key == self.volume_column and 'families' in properties:
                    ordered_properties['families'] = properties['families']

            # Update properties with ordered_properties
            building['properties'] = ordered_properties

    def output_results(self):
        self.input_data['features'] = self.buildings
        with open(self.output_file, 'w') as file:
            json.dump(self.input_data, file, indent=2)

    def run(self):
        self.read_input_data()
        self.calculate_family_distribution()
        self.output_results()
