import geopandas as gpd
import random
from config.config import Config


class Cooling(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config.get('building_path')

    def run(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Set random True/False values for the 'cooling' column
        buildings_gdf['cooling'] = [random.choice([True, False]) for _ in range(len(buildings_gdf))]

        # Save updated data back to the GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"'cooling' attribute assigned randomly for all buildings in {self.building_file}")
