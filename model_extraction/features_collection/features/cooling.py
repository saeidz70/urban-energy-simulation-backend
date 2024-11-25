import random

import geopandas as gpd

from config.config import Config


class Cooling(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'cooling'
        self.building_file = self.config.get('building_path')
        self.cooling_config = self.config.get('features', {}).get('cooling', {})
        self.cooling_value = self.cooling_config.get('values', None)

    def run(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Set random True/False values for the 'cooling' column
        buildings_gdf[self.feature_name] = [random.choice(self.cooling_value) for _ in range(len(buildings_gdf))]

        # Save updated data back to the GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"{self.feature_name} attribute assigned randomly for all buildings in {self.building_file}")
