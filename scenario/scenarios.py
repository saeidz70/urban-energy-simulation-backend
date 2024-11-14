import json
from features_collection.feature_factory import FeatureFactory


class BaseScenario(FeatureFactory):
    def __init__(self):
        super().__init__()

    def run_scenario(self):
        """Execute each feature method based on the scenario's feature list."""
        for feature_name in self.feature_list:
            feature_method = getattr(self, feature_name, None)
            if callable(feature_method):
                print(f"Executing feature: {feature_name}")
                feature_method()
            else:
                print(f"Warning: Method for '{feature_name}' not found in FeatureFactory.")


# Scenario classes inheriting from BaseScenario
class BaselineScenario(BaseScenario):
    def __init__(self):
        super().__init__()
        self.feature_list = self.config["scenarios"]["baseline_scenario"]


class GeometryScenario(BaseScenario):
    def __init__(self):
        super().__init__()
        self.feature_list = self.config["scenarios"]["geometry_scenario"]


class DemographicScenario(BaseScenario):
    def __init__(self):
        super().__init__()
        self.feature_list = self.config["scenarios"]["demographic_scenario"]


class EnergyScenario(BaseScenario):
    def __init__(self):
        super().__init__()
        self.feature_list = self.config["scenarios"]["energy_scenario"]
