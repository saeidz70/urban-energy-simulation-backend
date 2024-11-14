import geopandas as gpd
import random
from config.config import Config


class TabulaType(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config.get('building_path')
        self.tabula_types = ['mfh', 'sf', 'ab', 'th']  # Possible values for tabula_type

    def run(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Assign a random Tabula type to each building
        buildings_gdf['tabula_type'] = [random.choice(self.tabula_types) for _ in range(len(buildings_gdf))]

        # Save updated data back to the GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"'tabula_type' attribute assigned randomly for all buildings in {self.building_file}")
