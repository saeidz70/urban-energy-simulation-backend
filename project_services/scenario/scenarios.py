from processing.features_collection.feature_factory import FeatureFactory

class BaseScenario(FeatureFactory):
    def __init__(self):
        super().__init__()
        self.feature_list = None

    def run_scenario(self, gdf):
        """Execute each feature method based on the scenario's feature list and return the modified GeoDataFrame."""
        for feature_name in self.feature_list:
            print(f"Executing feature: {feature_name}")
            gdf = self.run_feature(feature_name, gdf)
        return gdf

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
