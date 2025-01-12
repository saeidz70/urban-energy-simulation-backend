import os

import geopandas as gpd

from config.config import Config
from project_services.scenario.scenario_manager import ScenarioManager
from project_services.utils.polygon_from_buildings import BuildingPolygonCreator
from project_services.utils.project_id import ProjectId
from project_services.utils.scenario_id import ScenarioId


class DataHelper(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.user_building_file = self.config["user_building_file"]
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.manager = ScenarioManager()
        self.polygon_creator = BuildingPolygonCreator()
        self.project_id_generator = ProjectId()
        self.scenario_id_generator = ScenarioId()

    def process_polygon_array(self, data):
        self._save_project_info(data)
        polygon_array = data.get("polygonArray")
        if not polygon_array:
            raise ValueError("No polygonArray data provided.")
        polygon_gdf = self.polygon_creator.user_polygon(polygon_array)
        self.manager.run_scenarios(polygon_gdf)

    def process_building_geometry(self, data):
        self._save_project_info(data)
        building_geometry = data.get("buildingGeometry")
        if not building_geometry:
            raise ValueError("No buildingGeometry data provided.")
        buildings_gdf = self._load_building_geometry(building_geometry)
        self._save_building_geometry(buildings_gdf)
        polygon_gdf = self.polygon_creator.create_polygon_from_buildings()
        self.manager.run_scenarios(polygon_gdf)

    def update_buildings_gdf(self, data):
        self._save_project_info(data)
        building_geometry = data.get("buildingGeometry")
        if not building_geometry:
            raise ValueError("No buildingGeometry data provided.")
        buildings_gdf = self._load_building_geometry(building_geometry)
        self._save_building_geometry(buildings_gdf)
        polygon_gdf = self.polygon_creator.create_polygon_from_buildings()
        self.manager.run_scenarios(polygon_gdf, buildings_gdf)

    def _save_project_info(self, data):
        self.load_config()
        self.project_id = data.get("project_id", "")
        self.scenario_id = data.get("scenario_id", "")

        if not self.project_id or not isinstance(self.project_id, str) or not self.project_id.strip():
            self.project_id = self.project_id_generator.run()
        elif not self.scenario_id or not isinstance(self.scenario_id, str) or not self.scenario_id.strip():
            self.scenario_id = self.scenario_id_generator.run()

        print(f"Project ID: {self.project_id}")
        print(f"Scenario ID: {self.scenario_id}")

        # Check if scenarioList contains "baseline"
        if data.get("scenarioList") and "baseline" in data["scenarioList"]:
            print('ScenarioList contains "baseline"; setting scenario_id to match project_id.')
            self.scenario_id = self.project_id

        project_info = {
            "project_id": self.project_id,
            "scenario_id": self.scenario_id,
            "projectName": data.get("projectName", ""),
            "scenario_name": data.get("scenario_name", ""),
            "scenarioList": data.get("scenarioList", []),
            "translation": data.get("translation", {}),
            "mapCenter": data.get("mapCenter", {}),
            "polygonArray": data.get("polygonArray", []),
        }
        self.config["project_info"] = project_info
        print("Project data saved in project section of config.json.")
        print(f"project_info: {project_info}")
        self.save_config()

    def _load_building_geometry(self, building_geometry):
        try:
            buildings_gdf = gpd.GeoDataFrame.from_features(building_geometry['features'])
            print("Building geometry data loaded successfully.")
            input_crs = building_geometry.get("crs", {}).get("properties", {}).get("name")
            if input_crs:
                print(f"CRS provided in data: {input_crs}")
                if buildings_gdf.crs is None or buildings_gdf.crs.to_string() != input_crs:
                    print(f"Setting CRS to input CRS: {input_crs}.")
                    buildings_gdf.set_crs(input_crs, inplace=True, allow_override=True)
            else:
                print(f"No CRS provided in data. Setting default CRS: {self.default_crs}")
                buildings_gdf.set_crs(self.default_crs, inplace=True)
            return self._check_crs(buildings_gdf)
        except Exception as e:
            raise ValueError(f"Error processing building geometry: {e}")

    def _save_building_geometry(self, buildings_gdf):
        user_file_dir = os.path.dirname(self.user_building_file)
        if not os.path.exists(user_file_dir):
            print(f"Directory {user_file_dir} does not exist. Creating it now.")
            os.makedirs(user_file_dir)
        buildings_gdf.to_file(self.user_building_file, driver="GeoJSON")
        print(f"Building geometry saved to {self.user_building_file} in CRS {self.default_crs}.")
        self.config["user_building_file"] = self.user_building_file
        print("Project info saved in config.json.")

    def _check_crs(self, gdf):
        if gdf.crs is None:
            print(f"No CRS found; setting to {self.default_crs}.")
            gdf.set_crs(self.default_crs, inplace=True)
        elif gdf.crs.to_string() != f"EPSG:{self.default_crs}":
            print(f"CRS mismatch. projecting to {self.default_crs} CRS (EPSG:{self.default_crs}).")
            gdf = gdf.to_crs(self.default_crs)
        return gdf
