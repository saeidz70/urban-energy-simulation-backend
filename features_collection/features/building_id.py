import geopandas as gpd
import uuid
from config.config import Config


class BuildingIDAssigner(Config):
    def __init__(self):
        super().__init__()
        self.building_file_path = self.config['building_path']

    def assign_unique_id(self):
        buildings_gdf = gpd.read_file(self.building_file_path)

        # Ensure a unique ID column exists
        if 'building_id' not in buildings_gdf.columns:
            # Assign a truncated UUID (8 characters) for each building
            buildings_gdf['building_id'] = [str(uuid.uuid4()) for _ in range(len(buildings_gdf))]

        # Correctly reorder columns to make 'census_id' the first column
        columns = ['building_id'] + [col for col in buildings_gdf.columns if col != 'building_id']
        buildings_gdf = buildings_gdf.reindex(columns=columns)

        # Save the updated data back to file
        buildings_gdf.to_file(self.building_file_path, driver='GeoJSON')
        print("IDs have been assigned to each building.")

        return buildings_gdf
