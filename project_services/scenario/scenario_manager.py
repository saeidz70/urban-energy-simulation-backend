import os

from config.config import Config
from processing.output_generator.file_to_db import DBServerUploader
from processing.output_generator.output_generator import OutputFileGenerator
from processing.preparation.data_preparation import PrepMain
from project_services.scenario.scenarios import BaselineScenario, GeometryScenario, DemographicScenario, EnergyScenario


class ScenarioManager(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config.get('building_path')
        self.uploader = DBServerUploader()
        self.scenario_map = {
            "update": BaselineScenario,
            "baseline": BaselineScenario,
            "geometry": GeometryScenario,
            "demographic": DemographicScenario,
            "energy": EnergyScenario
        }
        self.project_info = {}
        self.scenario_list = []

    def reload_config(self):
        self.load_config()
        self.get_project_info()

    def get_project_info(self):
        self.project_info = self.config.get("project_info", {})
        self.scenario_list = self.project_info.get("scenarioList", [])
        print(f"Scenarios to be run: {self.scenario_list}")

    def prepare(self, polygon_gdf):
        print("Running preparation steps...")
        preparation = PrepMain()
        building_gdf = preparation.run(polygon_gdf)
        print("Preparation completed.")
        return building_gdf

    def generate_output(self, gdf):
        print("Generating output file...")
        generator = OutputFileGenerator()
        json_result = generator.generate_output_file(gdf)
        if json_result:
            self.uploader.upload_geojson(json_result)
        print("Output file generated.")

    def run_scenarios(self, polygon_gdf, gdf=None):
        self.reload_config()

        if "update" in self.scenario_list:
            gdf = gdf
            self.prepare(polygon_gdf)
        else:
            gdf = self.prepare(polygon_gdf)

        for scenario_name in self.scenario_list:
            scenario_class = self.scenario_map.get(scenario_name.lower())
            if scenario_class:
                print(f"Running scenario: {scenario_name}")
                scenario_instance = scenario_class()
                gdf = scenario_instance.run_scenario(gdf)
            else:
                print(f"Warning: Scenario '{scenario_name}' not found in scenario_map.")

        self.save_building_file(gdf)
        self.generate_output(gdf)

    def save_building_file(self, gdf):
        if not os.path.exists(os.path.dirname(self.building_file)):
            os.makedirs(os.path.dirname(self.building_file))
        gdf.to_file(self.building_file, driver='GeoJSON')
        print("Features are updated in the buildings GeoJSON file.")