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
        self.scenario_id = None

    def process_polygon_array(self, data):
        self.save_project_info(data)

        polygon_array = data.get("polygonArray")
        if not polygon_array:
            raise ValueError("No polygonArray data provided.")
        print("Polygon data saved in config.json.")

        polygon_gdf = self.polygon_creator.user_polygon(polygon_array)
        self.manager.run_scenarios(self.project_id, self.scenario_id, polygon_gdf)

    def process_building_geometry(self, data):
        self.save_project_info(data)  # Save project info
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
            buildings_gdf = self.check_crs(buildings_gdf)

            # Ensure the directory for user_building_file exists
            user_file_dir = os.path.dirname(self.user_building_file)
            if not os.path.exists(user_file_dir):
                print(f"Directory {user_file_dir} does not exist. Creating it now.")
                os.makedirs(user_file_dir)

            # Save as GeoJSON file in default CRS
            buildings_gdf.to_file(self.user_building_file, driver="GeoJSON")
            print(f"Building geometry saved to {self.user_building_file} in CRS {self.default_crs}.")

            self.config["user_building_file"] = self.user_building_file
            print("Project info saved in config.json.")
            polygon_gdf = self.polygon_creator.create_polygon_from_buildings()
            self.manager.run_scenarios(self.project_id, self.scenario_id, polygon_gdf)

        except Exception as e:
            raise ValueError(f"Error processing building geometry: {e}")

    def update_buildings_gdf(self, data):
        self.save_project_info(data)  # Save project info
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
            buildings_gdf = self.check_crs(buildings_gdf)

            # Ensure the directory for user_building_file exists
            user_file_dir = os.path.dirname(self.user_building_file)
            if not os.path.exists(user_file_dir):
                print(f"Directory {user_file_dir} does not exist. Creating it now.")
                os.makedirs(user_file_dir)

            # Save as GeoJSON file in default CRS
            buildings_gdf.to_file(self.user_building_file, driver="GeoJSON")
            print(f"Building geometry saved to {self.user_building_file} in CRS {self.default_crs}.")

            self.config["user_building_file"] = self.user_building_file
            print("Project info saved in config.json.")
            polygon_gdf = self.polygon_creator.create_polygon_from_buildings()

            self.manager.run_scenarios(self.project_id, self.scenario_id, polygon_gdf, buildings_gdf)

        except Exception as e:
            raise ValueError(f"Error processing building geometry: {e}")

    def save_project_info(self, data):
        self.project_id = data.get("project_id", "")
        self.scenario_id = data.get("scenario_id", "")

        if not self.project_id or not self.scenario_id:
            self.project_id, self.scenario_id = self.manager.assign_project_and_scenario_id(self.project_id,
                                                                                            self.scenario_id)

        project_info = {
            "projectName": data.get("projectName"),
            "mapCenter": data.get("mapCenter"),
            "polygonArray": data.get("polygonArray"),
            "scenarioList": data.get("scenarioList"),
            "project_id": self.project_id,
            "scenario_id": self.scenario_id,
        }
        self.config["project_info"] = project_info
        print("Project data saved in project section of config.json.")
        self.save_config()

    def check_crs(self, gdf):
        """
        Ensure the GeoDataFrame has the correct CRS, projecting if necessary.
        """
        if gdf.crs is None:
            print(f"No CRS found; setting to {self.default_crs}.")
            gdf.set_crs(self.default_crs, inplace=True)
        elif gdf.crs.to_string() != f"EPSG:{self.default_crs}":
            print(f"CRS mismatch. projecting to {self.default_crs} CRS (EPSG:{self.default_crs}).")
            gdf = gdf.to_crs(self.default_crs)
        return gdf
