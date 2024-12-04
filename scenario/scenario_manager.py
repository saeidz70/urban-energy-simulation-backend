import geopandas as gpd

from config.config import Config
from model_extraction.preparation.data_preparation import PrepMain
from model_extraction.transformation.file_to_db import DBServerUploader
from model_extraction.transformation.output_generator import OutputFileGenerator
from scenario.project_id import ProjectId
from scenario.scenario_id import ScenarioId
from scenario.scenarios import BaselineScenario, GeometryScenario, DemographicScenario, EnergyScenario


class ScenarioManager(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config.get('building_path')
        self.uploader = DBServerUploader()
        self.project_id = ProjectId()
        self.scenario_id = ScenarioId()
        self.scenario_map = {
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

    def prepare(self):
        print("Running preparation steps...")
        preparation = PrepMain()
        preparation.run_all_preparations()
        print("Preparation completed.")

    def generate_output(self, gdf):
        print("Generating output file...")
        generator = OutputFileGenerator()
        json_result = generator.generate_output_file(gdf)
        if json_result:
            self.uploader.upload_geojson(json_result)
        print("Output file generated.")

    def assign_project_and_scenario_id(self, project_id):
        self.scenario_id.run()
        if "baseline" in self.scenario_list and project_id == "":
            self.project_id.run()
        else:
            self.load_config()
            self.config["project_info"]["project_id"] = project_id
            self.save_config()

    def run_scenarios(self, project_id):
        self.reload_config()
        self.prepare()
        self.assign_project_and_scenario_id(project_id)

        gdf = gpd.read_file(self.building_file)
        # print("Original GeoDataFrame:", gdf.head())

        for scenario_name in self.scenario_list:
            scenario_class = self.scenario_map.get(scenario_name.lower())
            if scenario_class:
                print(f"Running scenario: {scenario_name}")
                scenario_instance = scenario_class()
                gdf = scenario_instance.run_scenario(gdf)
            else:
                print(f"Warning: Scenario '{scenario_name}' not found in scenario_map.")

        gdf.to_file(self.building_file, driver='GeoJSON')
        print("Features are updated in the buildings GeoJSON file.")
        self.generate_output(gdf)
