import os

import geopandas as gpd


class DataCheck:
    def __init__(self, config):
        self.config = config
        self.user_file = self.config['user_file_path']
        self.translation = self.config.get('translation', {})

        # Load the user file if it exists
        if os.path.exists(self.user_file):
            self.user_gdf = gpd.read_file(self.user_file)
            print(f"User file loaded successfully: {self.user_file}")
            # print("User GeoDataFrame head: ", self.user_gdf.head())
        else:
            print(f"File not found: {self.user_file}")
            self.user_gdf = None

    def get_data_from_user(self, feature, buildings_gdf):
        if self.user_gdf is not None:
            try:
                translated_feature = self.translation.get(feature)
                print(f"Translated feature for '{feature}': {translated_feature}")

                if not translated_feature:
                    print(f"No translation provided for feature '{feature}'. Skipping.")
                    return None

                if translated_feature not in self.user_gdf.columns:
                    print(f"Translated feature '{translated_feature}' not found in the user file columns.")
                    return None

                # Perform spatial join to match geometries
                matched_gdf = gpd.sjoin(
                    buildings_gdf[['geometry']],
                    self.user_gdf,
                    how="inner",
                    predicate="intersects",
                    lsuffix='_left',
                    rsuffix='_right'
                )
                print("Spatial join result: ", matched_gdf.head())

                # Explicitly map the translated feature to the desired feature name
                if translated_feature in matched_gdf.columns:
                    print(f"Feature '{feature}' matched successfully with '{translated_feature}' in user file.")
                    matched_gdf[feature] = matched_gdf[translated_feature]  # Map the values explicitly
                    print(f"returning data from DataCheck '{feature}': ", matched_gdf[[feature]].head())
                    return matched_gdf[['geometry', feature]]
                else:
                    print(f"Feature '{translated_feature}' not found after spatial join.")
                    return None
            except Exception as e:
                print(f"Error during spatial join or data retrieval: {e}")
                return None
        else:
            print("No geographic data frame loaded, skipping data processing.")
            return None
