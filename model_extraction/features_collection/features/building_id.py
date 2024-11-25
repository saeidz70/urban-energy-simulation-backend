import uuid

import geopandas as gpd

from config.config import Config


class BuildingIDAssigner(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'building_id'
        self.building_file_path = self.config['building_path']
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})

    def assign_unique_id(self):
        buildings_gdf = gpd.read_file(self.building_file_path)

        # Ensure a unique ID column exists
        if self.feature_name not in buildings_gdf.columns:
            # Assign a truncated UUID (8 characters) for each building
            buildings_gdf[self.feature_name] = [str(uuid.uuid4()) for _ in range(len(buildings_gdf))]

        # Correctly reorder columns to make 'census_id' the first column
        columns = [self.feature_name] + [col for col in buildings_gdf.columns if col != self.feature_name]
        buildings_gdf = buildings_gdf.reindex(columns=columns)

        # Save the updated data back to file
        buildings_gdf.to_file(self.building_file_path, driver='GeoJSON')
        print("IDs have been assigned to each building.")

        return buildings_gdf
