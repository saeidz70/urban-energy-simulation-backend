import pandas as pd
import geopandas as gpd
from config.config import Config
from model_extraction.data_manager.data_check import DataCheck
from model_extraction.data_manager.data_validation import DataValidation
from model_extraction.data_manager.db_check import DatabaseCheck
from model_extraction.data_manager.osm_check import OSMCheck


class UtilityProcess(Config):
    def __init__(self):
        super().__init__()
        self.data_check = DataCheck(self.config)
        self.db_check = DatabaseCheck(self.config)
        self.osm_check = OSMCheck(self.config)
        self.data_validation = DataValidation()

    def process_feature(self, feature, buildings_gdf):
        # Ensure feature column exists in buildings_gdf
        if feature not in buildings_gdf.columns:
            buildings_gdf[feature] = None
        print(f"Starting to process feature: '{feature}'")

        # Retrieve feature data from different sources
        data = self._get_feature_data(feature, buildings_gdf)
        print("Retrieved data from sources:", data.head() if data is not None else "No data retrieved")

        # Proceed if data is valid and has expected columns
        if data is not None and feature in data.columns and self.data_validation.validate(data):
            data = data.drop_duplicates(subset='geometry')
            print("Data after removing duplicates:", data.head())

            # Perform the merge and handle missing values
            buildings_gdf = buildings_gdf.merge(data[['geometry', feature]], on='geometry', how='left',
                                                suffixes=('', '_new'))
            new_feature_col = f"{feature}_new"
            print(f"After merge, buildings_gdf columns: {buildings_gdf.columns}")

            # Handle different data types for the feature
            if buildings_gdf[new_feature_col].dtype == 'str':
                buildings_gdf[feature] = buildings_gdf[feature].fillna(buildings_gdf[new_feature_col])
            else:
                # Convert to numeric, treating errors by setting invalid parsing as NaN
                buildings_gdf[new_feature_col] = pd.to_numeric(buildings_gdf[new_feature_col], errors='coerce')
                buildings_gdf[feature] = buildings_gdf[feature].fillna(buildings_gdf[new_feature_col])

            if feature == 'n_floor':
                # Convert 'n_floor' to integer type; use 'Int64' to accommodate NaNs as integers
                buildings_gdf[feature] = buildings_gdf[feature].astype('Int64')

            # Drop the temporary column
            buildings_gdf.drop(columns=[new_feature_col], inplace=True)

        print("Final buildings_gdf head after processing feature:", buildings_gdf.head())
        return buildings_gdf[['geometry', feature]]

    def _get_feature_data(self, feature, buildings_gdf):
        data = None
        self.load_config()
        scenario_list = self.config.get("project_info", {}).get("scenarioList", [])

        if "baseline" in scenario_list:
            try:
                data = self.osm_check.get_data_from_osm(feature, buildings_gdf)
                if data is not None:
                    print("Data retrieved from OSM:", data.head())
            except Exception as e:
                print(f"Error retrieving OSM data: {e}")
        else:
            try:
                data = self.data_check.get_data_from_user(feature, buildings_gdf)
                if data is not None:
                    print("Data retrieved from user file:", data.head())
            except Exception as e:
                print(f"Error retrieving user data: {e}")

            if data is None:
                try:
                    data = self.db_check.get_data_from_db(feature, buildings_gdf)
                    if data is not None:
                        print("Data retrieved from database:", data.head())
                except Exception as e:
                    print(f"Error retrieving database data: {e}")

        # Confirm final data for the feature before returning
        if data is None or data.empty:
            print(f"No data retrieved for feature '{feature}' from any source.")
        else:
            print(f"Final data retrieved for '{feature}':", data.head())

        return data
