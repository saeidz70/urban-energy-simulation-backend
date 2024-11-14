import json
from config.config import Config
from model_extraction.preparation.data_preparation import PrepMain
from model_extraction.transformation.file_to_db import DBServerUploader
from model_extraction.transformation.output_generator import OutputFileGenerator
from scenario.scenarios import BaselineScenario, GeometryScenario, DemographicScenario, EnergyScenario


class ScenarioManager(Config):
    def __init__(self):
        super().__init__()
        self.uploader = DBServerUploader()
        self.scenario_map = {
            "baseline": BaselineScenario,
            "geometry": GeometryScenario,
            "demographic": DemographicScenario,
            "energy": EnergyScenario
        }

    def reload_config(self):
        # Method to reload configuration if needed
        self.load_config()  # Assuming there's a method in Config to reload config file
        self.get_project_info()

    def get_project_info(self):
        # This method now just fetches the project info from the loaded config
        self.project_info = self.config.get("project_info", {})
        self.scenario_list = self.project_info.get("scenarioList", [])
        print(f"Scenario to be run: {self.scenario_list}")

    def prepare(self):
        print("Running preparation steps...")
        preparation = PrepMain()
        preparation.run_all_preparations()
        print("Preparation completed.")

    def output(self):
        print("Generating output file...")
        generator = OutputFileGenerator()
        generator.generate_output_file()
        self.uploader.upload_geojson()
        print("Output file generated.")

    def run_scenarios(self):
        self.reload_config()  # Ensure config is reloaded and updated each time
        self.prepare()
        for scenario_name in self.scenario_list:
            scenario_class = self.scenario_map.get(scenario_name.lower())
            if scenario_class:
                print(f"Running scenario: {scenario_name}")
                scenario_instance = scenario_class()
                scenario_instance.run_scenario()
            else:
                print(f"Warning: Scenario '{scenario_name}' not found in scenario_map.")
        self.output()
