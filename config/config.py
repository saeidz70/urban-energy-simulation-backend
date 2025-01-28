import json


class Config:
    def __init__(self, config_path=None):
        self.config_path = config_path or './config/configuration.json'
        self.config = {}
        self.load_config()  # Load configuration at initialization

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Config file {self.config_path} not found. Using default config.")
            self.config = {}

    def save_config(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Config saved to {self.config_path}.")
        except Exception as e:
            print(f"Error saving config: {e}")
