from config.config import Config
from processing.utility.data_check import DataCheck
from processing.utility.data_validation import DataValidation
from processing.utility.db_check import DatabaseCheck
from processing.utility.osm_check import OSMCheck

class UtilityProcess(Config):
    def __init__(self):
        super().__init__()
        self.data_check = None
        self.db_check = None
        self.osm_check = None
        self.data_validation = None

    def initialize_helpers(self):
        """Initialize helper classes for data checking."""
        self.data_check = DataCheck()
        self.db_check = DatabaseCheck()

    def retrieve_data_from_sources(self, feature, buildings_gdf):
        """
        Retrieve and process a specific feature and merge it into the buildings GeoDataFrame.
        """
        if feature not in buildings_gdf.columns:
            buildings_gdf[feature] = None  # Initialize column if missing

        self.load_config()
        scenario_list = self.config.get("project_info", {}).get("scenarioList", [])

        if "baseline" not in scenario_list and "update" not in scenario_list:

            print(f"Attempting to retrieve data for feature: '{feature}'")
            # Retrieve feature data from various sources
            data = self._get_feature_data(feature, buildings_gdf)
            if data is None or data.empty:
                print(f"No valid data found for feature '{feature}'. Skipping processing.")
                return buildings_gdf

            # Merge the retrieved feature data into the buildings GeoDataFrame
            buildings_gdf = self._merge_feature_data(buildings_gdf, data, feature)
            print(f"Feature '{feature}' successfully processed.")
            return buildings_gdf
        else:
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

            return buildings_gdf
        except Exception as e:
            print(f"Error merging feature '{feature}' into buildings GeoDataFrame: {e}")
            return buildings_gdf

    def _get_feature_data(self, feature, buildings_gdf):
        """
        Retrieve feature data from user file, database, or OSM.
        """
        data = None

        self.initialize_helpers()
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
        else:
            try:
                print(f"Filling null values for '{feature}' using database data...")
                db_data = self.db_check.get_data_from_db(feature, buildings_gdf)
                if db_data is not None and not db_data.empty:
                    data = data.combine_first(db_data)
                print(f"Successfully retrieved '{feature}' data with columns: {data.columns}")
            except Exception as e:
                print(f"Error retrieving database data for '{feature}': {e}")

        if data is not None and not data.empty:
            print(f"Successfully retrieved '{feature}' data with columns: {data.columns}")
        else:
            print(f"No data available for '{feature}' from any source.")
        return data

    def _get_osm_data(self, feature, buildings_gdf):
        """
        Retrieve feature data from OSM.
        """
        self.osm_check = OSMCheck(self.config)
        if feature not in buildings_gdf.columns:
            buildings_gdf[feature] = None  # Initialize column if missing
        try:
            print(f"Retrieving '{feature}' data from OSM...")
            data = self.osm_check.get_data_from_osm(feature, buildings_gdf)

            if data is None or data.empty:
                print(f"No valid data found for feature '{feature}'. Skipping processing.")
                return buildings_gdf

            # Merge the retrieved feature data into the buildings GeoDataFrame
            buildings_gdf = self._merge_feature_data(buildings_gdf, data, feature)
            print(f"Feature '{feature}' successfully processed.")
            return buildings_gdf

        except Exception as e:
            print(f"Error retrieving OSM data for '{feature}': {e}")
            return buildings_gdf

    def validate_data(self, df, feature_name):
        """
        Validate and correct data for a specific feature using DataValidation class.
        """
        self.data_validation = DataValidation()

        df = self.data_validation.validate_and_correct(df, feature_name)
        return df
