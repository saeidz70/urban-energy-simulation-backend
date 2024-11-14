import geopandas as gpd
import random
from config.config import Config


class HVACType(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config.get('building_path')
        self.hvac_types = ['gb', 'hp']

    def run(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Assign random HVAC type to each building
        buildings_gdf['hvac_type'] = [random.choice(self.hvac_types) for _ in range(len(buildings_gdf))]

        # Save updated data back to the GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"'hvac_type' attribute assigned randomly for all buildings in {self.building_file}")
