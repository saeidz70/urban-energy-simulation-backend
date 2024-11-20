import pandas as pd

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
        """
        Process a specific feature and merge it into the buildings GeoDataFrame.
        """
        if feature not in buildings_gdf.columns:
            buildings_gdf[feature] = None  # Softly initialize if missing
        print(f"Processing feature: '{feature}'")

        # Retrieve feature data from various sources
        data = self._get_feature_data(feature, buildings_gdf)
        if data is None or data.empty:
            print(f"No valid data found for feature '{feature}'. Skipping processing.")
            return buildings_gdf

        # Ensure feature column exists and is merged correctly
        buildings_gdf = self._merge_feature_data(buildings_gdf, data, feature)
        print(f"Feature '{feature}' processed successfully.")
        return buildings_gdf

    def _merge_feature_data(self, buildings_gdf, data, feature):
        """
        Merge the retrieved feature data into the buildings GeoDataFrame.
        """
        try:
            # Ensure data has the necessary columns
            if 'geometry' not in data.columns or feature not in data.columns:
                print(f"Data for '{feature}' lacks required columns. Skipping merge.")
                return buildings_gdf

            # Drop duplicates based on geometry
            data = data.drop_duplicates(subset='geometry')

            # Merge feature data into buildings_gdf
            buildings_gdf = buildings_gdf.merge(
                data[['geometry', feature]],
                on='geometry',
                how='left',
                suffixes=('', '_new')
            )

            # Fill missing values
            if feature in buildings_gdf.columns:
                buildings_gdf[feature] = buildings_gdf[feature].fillna(buildings_gdf[f"{feature}_new"])

            # Drop temporary '_new' column
            if f"{feature}_new" in buildings_gdf.columns:
                buildings_gdf.drop(columns=[f"{feature}_new"], inplace=True)

            # Convert feature column to appropriate type
            if feature == 'n_floor':
                buildings_gdf[feature] = buildings_gdf[feature].astype('Int64', errors='ignore')
            elif feature != "usage":
                buildings_gdf[feature] = pd.to_numeric(buildings_gdf[feature], errors='coerce')

            return buildings_gdf
        except Exception as e:
            print(f"Error merging feature '{feature}' into buildings GeoDataFrame: {e}")
            return buildings_gdf

    def _get_feature_data(self, feature, buildings_gdf):
        """
        Retrieve feature data from OSM, user file, or database.
        """
        data = None
        self.load_config()
        scenario_list = self.config.get("project_info", {}).get("scenarioList", [])

        if "baseline" in scenario_list:
            try:
                print(f"Retrieving '{feature}' data from OSM...")
                data = self.osm_check.get_data_from_osm(feature, buildings_gdf)
            except Exception as e:
                print(f"Error retrieving OSM data for '{feature}': {e}")
        else:
            try:
                print(f"Retrieving '{feature}' data from user files...")
                data = self.data_check.get_data_from_user(feature, buildings_gdf)
            except Exception as e:
                print(f"Error retrieving user data for '{feature}': {e}")

            if data is None or data.empty:
                try:
                    print(f"Retrieving '{feature}' data from database...")
                    data = self.db_check.get_data_from_db(feature, buildings_gdf)
                except Exception as e:
                    print(f"Error retrieving database data for '{feature}': {e}")

        if data is not None and not data.empty:
            print(f"Successfully retrieved '{feature}' data with columns: {data.columns}")
        else:
            print(f"No data available for '{feature}' from any source.")
        return data
