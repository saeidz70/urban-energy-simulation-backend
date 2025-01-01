import json
import uuid

from config.config import Config


class ScenarioId(Config):
    def __init__(self):
        super().__init__()

    def generate_scenario_id(self):
        # Generate a unique scenario ID
        scenario_id = str(uuid.uuid4())

        # Load the config file
        self.load_config()

        # Update the project_info with the new scenario ID
        if "project_info" not in self.config:
            self.config["project_info"] = {}
        self.config["project_info"]["scenario_id"] = scenario_id

        # Save the updated config
        with open(self.config_path, 'w') as file:
            json.dump(self.config, file, indent=4)

        print(f"Generated unique scenario ID: {scenario_id} and saved to config.")
        return scenario_id

    def run(self):
        """Run the scenario ID generation process."""
        try:
            scenario_id = self.generate_scenario_id()
            print("scenario ID generation process completed successfully.")
            return scenario_id
        except Exception as e:
            print(f"Error during scenario ID generation: {e}")
            raise
