import json
import os


class PopulationCalculator:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.input_file = self.config["input_params"]["population"]["input"]
        self.output_file = self.config["input_params"]["population"]["output"]
        self.population_column = self.config["input_params"]["population"]["population"]
        self.volume_column = self.config["input_params"]["population"]["volume"]
        self.sez_column = self.config["input_params"]["population"]["censusID"]
        self.input_data = {}
        self.buildings = []

    def load_config(self, config_path: str):
        with open(config_path, 'r') as file:
            return json.load(file)

    def read_input_data(self):
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Input file '{self.input_file}' not found.")
        with open(self.input_file, 'r') as file:
            self.input_data = json.load(file)
            self.buildings = self.input_data.get('features', [])

    def calculate_population_distribution(self):
        census_volumes = {}
        census_population = {}

        # First pass: Calculate census volumes and census population
        for building in self.buildings:
            properties = building.get('properties', {})
            census_id = properties.get(self.sez_column)
            volume = properties.get(self.volume_column, 0)
            population = int(properties.get(self.population_column, 0))

            if census_id not in census_volumes:
                census_volumes[census_id] = 0
            census_volumes[census_id] += volume

            census_population[census_id] = population

        # Second pass: Calculate allocated population and rearrange properties
        for building in self.buildings:
            properties = building.get('properties', {})
            census_id = properties.get(self.sez_column)
            volume = properties.get(self.volume_column, 0)

            if census_id in census_volumes and census_volumes[census_id] > 0:
                population_ratio = volume / census_volumes[census_id]
                allocated_population = population_ratio * census_population[census_id]
                properties['population'] = round(allocated_population)
            else:
                properties['population'] = 0

            # Create an ordered dictionary to ensure 'allocated_population' comes after 'volume'
            ordered_properties = {}
            for key in properties:
                ordered_properties[key] = properties[key]
                if key == self.volume_column and 'population' in properties:
                    ordered_properties['population'] = properties['population']

            # Update properties with ordered_properties
            building['properties'] = ordered_properties

    def output_results(self):
        self.input_data['features'] = self.buildings
        with open(self.output_file, 'w') as file:
            json.dump(self.input_data, file, indent=2)

    def run(self):
        self.read_input_data()
        self.calculate_population_distribution()
        self.output_results()
