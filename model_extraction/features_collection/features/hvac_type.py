import random

import geopandas as gpd

from config.config import Config


class HVACType(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'hvac_type'
        self.building_file = self.config.get('building_path')
        self.hvac_types_config = self.config.get('features', {}).get(self.feature_name, {})
        self.hvac_types = self.hvac_types_config.get("values", ["gb", "hp"])

    def run(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Assign random HVAC type to each building
        buildings_gdf[self.feature_name] = [random.choice(self.hvac_types) for _ in range(len(buildings_gdf))]

        # Save updated data back to the GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f" {self.feature_name} attribute assigned randomly for all buildings in {self.building_file}")
