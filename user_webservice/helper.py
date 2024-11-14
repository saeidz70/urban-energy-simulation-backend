import json
import os

import geopandas as gpd

from scenario.scenario_manager import ScenarioManager


class DataHelper:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()
        self.user_file_path = "/Users/saeidzolfaghari/PycharmProjects/Automatic_Scenario_creation/data_source/input_files/shp/my_user_file.geojson"
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.manager = ScenarioManager()

    def load_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def process_data(self, feature, data):
        if feature == "polygonArray":
            self.process_polygon_array(data)
        elif feature == "buildingGeometry":
            print("Processing building geometry data in helper")
            self.process_building_geometry(data)
        else:
            raise ValueError(f"Unknown feature: {feature}")

    def process_polygon_array(self, data):
        polygon_array = data.get("polygonArray")
        if not polygon_array:
            raise ValueError("No polygonArray data provided.")

        # Save polygonArray data into the config file under "study_case"
        self.save_project_info(data)
        self.config["study_case"] = polygon_array
        self.save_config()
        print("Polygon data saved in study_case of config.json.")
        self.manager.run_scenarios()

    def process_building_geometry(self, data):
        building_geometry = data.get("buildingGeometry")
        if not building_geometry:
            raise ValueError("No buildingGeometry data provided.")

        # Validate and convert to GeoDataFrame
        try:
            buildings_gdf = gpd.GeoDataFrame.from_features(building_geometry['features_collection'])
            print("Building geometry data loaded successfully.")
            if buildings_gdf.crs is None:
                print("No CRS found in the GeoJSON data. Setting to default.")
                buildings_gdf.set_crs(self.default_crs, inplace=True)
        except Exception as e:
            raise ValueError(f"Invalid GeoJSON format for building geometry: {e}")

        # Reproject to the default EPSG code if needed
        print(f"Reprojecting to EPSG:{self.default_crs}")
        buildings_gdf = buildings_gdf.to_crs(epsg=self.default_crs)

        # Ensure the directory for user_file_path exists
        user_file_dir = os.path.dirname(self.user_file_path)
        if not os.path.exists(user_file_dir):
            print(f"Directory {user_file_dir} does not exist. Creating it now.")
            os.makedirs(user_file_dir)

        # Save as GeoJSON file
        buildings_gdf.to_file(self.user_file_path, driver="GeoJSON")
        print(f"Building geometry saved to {self.user_file_path}.")

        # Empty study_case in the config file
        self.config["study_case"] = []
        self.config["user_file_path"] = self.user_file_path
        self.save_project_info(data)  # Save project info
        self.save_config()
        print("Project info saved in config.json.")
        self.manager.run_scenarios()

    def save_project_info(self, data):
        project_info = {
            "projectName": data.get("projectName"),
            "mapCenter": data.get("mapCenter"),
            "polygonArray": data.get("polygonArray"),
            "scenarioList": data.get("scenarioList")
        }
        self.config["project_info"] = project_info
        print("Project data saved in project section of config.json.")

    def run_baseline(self):
        print("Running Baseline processing...")
        # baseline_processor = Baseline()
        # baseline_processor.run()
        print("Baseline processing completed.")
