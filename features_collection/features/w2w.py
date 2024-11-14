import geopandas as gpd
from config.config import Config


class W2W(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config.get('building_path')  # Path to the building data file

    def run(self):
        # Load the building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Check if 'w2w' column exists; if not, add it with default values of 0.5
        buildings_gdf['w2w'] = 0.5

        # Save the updated data back to the GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"'w2w' attribute set to 0.5 for all buildings in {self.building_file}")
