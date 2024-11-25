import geopandas as gpd

from config.config import Config


class W2W(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'w2w'
        self.building_file = self.config.get('building_path')  # Path to the building data file
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})

    def run(self):
        # Load the building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Check if 'w2w' column exists; if not, add it with default values of 0.5
        buildings_gdf[self.feature_name] = 0.5

        # Save the updated data back to the GeoJSON file
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"{self.feature_name} attribute set to 0.5 for all buildings in {self.building_file}")
