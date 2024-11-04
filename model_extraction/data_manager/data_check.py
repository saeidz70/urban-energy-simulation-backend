import os

import geopandas as gpd


class DataCheck:
    def __init__(self, config):
        self.config = config
        self.user_file = self.config['user_file_path']

        # Check if the file exists before reading it
        if os.path.exists(self.user_file):
            self.user_gdf = gpd.read_file(self.user_file)
        else:
            print(f"File not found: {self.user_file}")
            self.user_gdf = None  # Initialize as None if file doesn't exist

    def get_data_from_user(self, feature, buildings_gdf):
        # Check if user_gdf was successfully loaded
        if self.user_gdf is not None:
            try:
                matched_gdf = gpd.sjoin(buildings_gdf[['geometry']], self.user_gdf, how="inner", predicate="intersects",
                                        lsuffix='_left', rsuffix='_right')
                if feature in matched_gdf.columns:
                    return matched_gdf[['geometry', feature]]
                else:
                    print(f"Feature '{feature}' not found in the dataset.")
                    return None
            except Exception as e:
                print(f"Error during spatial join or data retrieval: {e}")
                return None
        else:
            print("No geographic data frame loaded, skipping data processing.")
            return None
