import json


class Config:
    def __init__(self, config_path=None):
        self.config_path = config_path or '/Users/saeidzolfaghari/PycharmProjects/Automatic_Scenario_creation/config/configuration.json'
        self.config = {}
        self.load_config()  # Load configuration at initialization

    def load_config(self):
        """Reloads the configuration from the JSON file specified by config_path."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Failed to reload configuration: {str(e)}")
