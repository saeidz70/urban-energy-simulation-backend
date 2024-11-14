import geopandas as gpd
import random
from config.config import Config


class ConstructionType(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config.get('building_path')
        self.construction_types = ['high', 'med', 'low']

    def run(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Set random construction type for each building
        buildings_gdf['construction_type'] = [random.choice(self.construction_types) for _ in range(len(buildings_gdf))]

        # Save updated data back to the GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"'construction_type' attribute assigned randomly for all buildings in {self.building_file}")
