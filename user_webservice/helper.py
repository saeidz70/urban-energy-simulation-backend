# helpers.py

import json
import os

import geojson

from model_extraction.processing.process_main import ProcessMain


class ProjectDataHelper:
    def __init__(self):
        self.base_dir = '/path/to/save/files'  # Directory to save files

    def process_data(self, data):
        # Save GeoJSON file
        self.save_polygon_geojson(data['polygonArray'], data['projectName'])

        # Save BuildingUse GeoJSON
        self.save_building_use_geojson(data['BuildingUse'], data['projectName'])

        # Save config files (Census, Height, etc.)
        self.save_config_files(data)

        # Run the main processing class
        processor = ProcessMain()
        processor.run_all_processing()

    def save_polygon_geojson(self, polygon_array, project_name):
        geojson_data = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon_array]
            },
            "properties": {
                "name": project_name
            }
        }

        file_path = os.path.join(self.base_dir, f"{project_name}_polygon.geojson")
        with open(file_path, 'w') as geojson_file:
            geojson.dump(geojson_data, geojson_file)

    def save_building_use_geojson(self, building_use_data, project_name):
        file_path = os.path.join(self.base_dir, f"{project_name}_building_use.geojson")
        with open(file_path, 'w') as geojson_file:
            geojson.dump(building_use_data['data'], geojson_file)

    def save_config_files(self, data):
        # Save Census Config
        self.save_config(data['Census'], data['projectName'], 'census')

        # Save Height Config
        self.save_config(data['Height'], data['projectName'], 'height')

        # Save other configs as needed

    def save_config(self, config_data, project_name, config_type):
        config_path = os.path.join(self.base_dir, f"{project_name}_{config_type}_config.json")
        with open(config_path, 'w') as config_file:
            json.dump(config_data, config_file)
