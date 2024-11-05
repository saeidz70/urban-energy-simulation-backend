import json

import pandas as pd

from model_extraction.data_manager.data_check import DataCheck
from model_extraction.data_manager.data_validation import DataValidation
from model_extraction.data_manager.db_check import DatabaseCheck
from model_extraction.data_manager.osm_check import OSMCheck


class UtilityProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.data_check = DataCheck(self.config)
        self.db_check = DatabaseCheck(self.config)
        self.osm_check = OSMCheck(self.config)
        self.data_validation = DataValidation()

    def process_feature(self, feature, buildings_gdf):
        if feature not in buildings_gdf.columns:
            buildings_gdf[feature] = None

        data = self._get_feature_data(feature, buildings_gdf)

        if data is not None and feature in data.columns and self.data_validation.validate(data):
            data = data.drop_duplicates(subset='geometry')
            buildings_gdf = buildings_gdf.merge(data[['geometry', feature]], on='geometry', how='left',
                                                suffixes=('', '_new'))

            new_feature_col = f"{feature}_new"
            if new_feature_col in buildings_gdf.columns:
                # Convert new feature column to the appropriate type before fillna to ensure consistency
                buildings_gdf[new_feature_col] = pd.to_numeric(buildings_gdf[new_feature_col], errors='coerce')
                buildings_gdf[feature] = buildings_gdf[feature].fillna(buildings_gdf[new_feature_col])
                if feature == 'n_floor':
                    buildings_gdf[feature] = buildings_gdf[feature].astype('Int64')
                buildings_gdf = buildings_gdf.drop(columns=[new_feature_col])

        return buildings_gdf[['geometry', feature]]

    def _get_feature_data(self, feature, buildings_gdf):
        try:
            data = self.data_check.get_data_from_user(feature, buildings_gdf)
            if data is not None:
                print(data, "data got from user file", data.head())
            else:
                print("No data returned from user file.")
        except Exception as e:
            print(f"Error retrieving user data: {e}")
            data = None

        if data is None:
            try:
                data = self.db_check.get_data_from_db(feature, buildings_gdf)
                if data is not None:
                    print(data, "data got from db")
                else:
                    print("No data returned from database.")
            except Exception as e:
                print(f"Error retrieving database data: {e}")
                data = None

        if data is None:
            try:
                data = self.osm_check.get_data_from_osm(feature, buildings_gdf)
                if data is not None:
                    print(data, "data got from osm")
                else:
                    print("No data returned from OSM.")
            except Exception as e:
                print(f"Error retrieving OSM data: {e}")
                data = None

        return data
