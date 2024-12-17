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
        self.project_id_generator = ProjectId()
        self.scenario_id_generator = ScenarioId()
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

    def assign_project_and_scenario_id(self, project_id, scenario_id):
        """Assign or generate project and scenario IDs as needed."""
        if not project_id:
            print("No project_id provided; generating a new Project ID...")
            project_id = self.project_id_generator.run()

        if not scenario_id:
            print("No scenario_id provided; generating a new Scenario ID...")
            scenario_id = self.scenario_id_generator.run()

        return project_id, scenario_id  # Return the updated IDs

    def run_scenarios(self, project_id, scenario_id, polygon_gdf, gdf=None):
        self.reload_config()

        # Assign or generate project and scenario IDs and capture the updated values
        project_id, scenario_id = self.assign_project_and_scenario_id(project_id, scenario_id)

        # Update the config file to reflect the updated IDs
        self.config["project_info"]["project_id"] = project_id
        self.config["project_info"]["scenario_id"] = scenario_id
        self.save_config()

        print(f"Project ID: {project_id}, Scenario ID: {scenario_id} saved successfully.")

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

        gdf.to_file(self.building_file, driver='GeoJSON')
        print("Features are updated in the buildings GeoJSON file.")
        self.generate_output(gdf)
