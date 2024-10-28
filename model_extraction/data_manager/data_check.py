import json

import geopandas as gpd


class DataCheck:
    def __init__(self, config_path):
        # Load the config from the given path
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.user_file = self.config['user_file_path']
        self.user_gdf = gpd.read_file(self.user_file)

    def get_data_from_user(self, feature, buildings_gdf):
        # Spatial join to filter user data based on buildings in buildings_gdf
        matched_gdf = gpd.sjoin(buildings_gdf[['geometry']], self.user_gdf, how="inner", predicate="intersects")

        # Check if the feature exists in matched_gdf
        if feature in matched_gdf.columns:
            # Select only geometry and the feature
            filtered_gdf = matched_gdf[['geometry', feature]]
            # Return the filtered data
            return filtered_gdf

        # Return None if the feature isn't found in the filtered buildings
        return None
