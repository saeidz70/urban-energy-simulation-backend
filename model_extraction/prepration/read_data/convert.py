import json
import os

import geopandas as gpd


class Convertor:
    def __init__(self, config_path):
        # Load and parse configuration
        with open(config_path, 'r') as file:
            self.config = json.load(file)

        # Paths and boundary loading
        self.user_file_path = self.config['user_file_path']
        self.my_data = gpd.read_file(self.user_file_path)

    def convert_file_format(self, new_name):
        # Ensure the directory exists
        output_directory = "data_source/input_files/shp/"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Save the file in GeoJSON format
        self.my_data.to_file(f"{output_directory}{new_name}.geojson", driver="GeoJSON")
        return "Converted to GeoJson"
