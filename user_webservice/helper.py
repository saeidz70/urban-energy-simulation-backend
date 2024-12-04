import json
import os

import geopandas as gpd

from config.config import Config
from scenario.scenario_manager import ScenarioManager
from user_webservice.polygon_from_buildings import BuildingPolygonCreator


class DataHelper(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.user_building_file = self.config["user_building_file"]
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.manager = ScenarioManager()
        self.polygon_creator = BuildingPolygonCreator()
        self.project_id = None

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def process_data(self, feature, data):
        self.project_id = data.get("project_id", "")
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

        self.save_project_info(data)
        self.save_config()
        print("Polygon data saved in config.json.")
        self.polygon_creator.user_polygon(polygon_array)
        self.manager.run_scenarios(self.project_id)

    def process_building_geometry(self, data):
        building_geometry = data.get("buildingGeometry")
        if not building_geometry:
            raise ValueError("No buildingGeometry data provided.")

        try:
            # Load GeoDataFrame from GeoJSON
            buildings_gdf = gpd.GeoDataFrame.from_features(building_geometry['features'])
            print("Building geometry data loaded successfully.")

            # Check and set CRS from input
            input_crs = building_geometry.get("crs", {}).get("properties", {}).get("name")
            if input_crs:
                print(f"CRS provided in data: {input_crs}")
                if buildings_gdf.crs is None or buildings_gdf.crs.to_string() != input_crs:
                    print(f"Setting CRS to input CRS: {input_crs}.")
                    buildings_gdf.set_crs(input_crs, inplace=True, allow_override=True)
            else:
                print(f"No CRS provided in data. Setting default CRS: {self.default_crs}")
                buildings_gdf.set_crs(self.default_crs, inplace=True)

            # Reproject to default CRS
            if buildings_gdf.crs.to_string() != self.default_crs:
                print(f"Reprojecting GeoDataFrame to default CRS: {self.default_crs}.")
                buildings_gdf = buildings_gdf.to_crs(self.default_crs)

            # Ensure the directory for user_building_file exists
            user_file_dir = os.path.dirname(self.user_building_file)
            if not os.path.exists(user_file_dir):
                print(f"Directory {user_file_dir} does not exist. Creating it now.")
                os.makedirs(user_file_dir)

            # Save as GeoJSON file in default CRS
            buildings_gdf.to_file(self.user_building_file, driver="GeoJSON")
            print(f"Building geometry saved to {self.user_building_file} in CRS {self.default_crs}.")

            self.config["user_building_file"] = self.user_building_file
            self.save_project_info(data)  # Save project info
            self.save_config()
            print("Project info saved in config.json.")
            self.polygon_creator.create_polygon_from_buildings()
            self.manager.run_scenarios(self.project_id)

        except Exception as e:
            raise ValueError(f"Error processing building geometry: {e}")

    def save_project_info(self, data):
        project_info = {
            "projectName": data.get("projectName"),
            "mapCenter": data.get("mapCenter"),
            "polygonArray": data.get("polygonArray"),
            "scenarioList": data.get("scenarioList"),
            "scenario_id": data.get("scenario_id"),
            "project_id": data.get("project_id")
        }
        self.config["project_info"] = project_info
        print("Project data saved in project section of config.json.")
