import os

import geopandas as gpd

from config.config import Config


class DataCheck(Config):
    def __init__(self):
        super().__init__()
        self.user_file = self.config.get('user_building_file', '')
        self.project_info = self.config.get('project_info', {})
        self.translation = self.project_info.get('translation', {})
        self.user_gdf = None

    def _is_translation_valid(self, feature):
        """
        Check if a valid translation exists for the specified feature.
        """
        if not self.translation or not isinstance(self.translation, dict):
            print("No valid 'translation' found in the project info.")
            return False

        feature_translation = self.translation.get(feature)
        if not feature_translation or not isinstance(feature_translation, str):
            print(f"No valid translation for feature '{feature}'.")
            return False

        return True

    def _load_user_file(self):
        """
        Load the user GeoDataFrame if the file exists.
        """
        if os.path.exists(self.user_file):
            try:
                print(f"Loading user file: {self.user_file}")
                return gpd.read_file(self.user_file)
            except Exception as e:
                print(f"Error loading user file: {e}")
        else:
            print(f"User file not found: {self.user_file}")
        return None

    def get_data_from_user(self, feature, buildings_gdf):
        """
        Retrieve data for a specific feature by checking user GeoDataFrame.
        """

        # Validate translation for the specified feature
        if not self._is_translation_valid(feature):
            print(f"Skipping process for feature '{feature}' due to invalid or missing translation.")
            return None

        # Load the user GeoDataFrame if not already loaded
        if self.user_gdf is None:
            self.user_gdf = self._load_user_file()

        if self.user_gdf is None:
            print("User GeoDataFrame not loaded. Skipping data processing.")
            return None

        feature_translation = self.translation[feature]

        # Ensure the translated feature exists in the user GeoDataFrame
        if feature_translation not in self.user_gdf.columns:
            print(f"Translated feature '{feature_translation}' not found in the user file columns.")
            return None

        try:
            print(f"Performing spatial join for feature '{feature}' using '{feature_translation}'.")
            # Perform spatial join to match geometries
            matched_gdf = gpd.sjoin(
                buildings_gdf[['geometry']],
                self.user_gdf,
                how="inner",
                predicate="intersects",
                lsuffix='_left',
                rsuffix='_right'
            )

            # Map the translated feature to the desired feature name
            if feature_translation in matched_gdf.columns:
                matched_gdf[feature] = matched_gdf[feature_translation]
                print(f"Feature '{feature}' successfully retrieved from user data.")
                return matched_gdf[['geometry', feature]]
            else:
                print(f"Feature '{feature_translation}' not found after spatial join.")
                return None

        except Exception as e:
            print(f"Error during spatial join or data retrieval for feature '{feature}': {e}")
            return None
