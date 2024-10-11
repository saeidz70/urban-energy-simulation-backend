import json

import geopandas as gpd

from data_check import DataCheck
from data_validation import DataValidation
from db_check import DatabaseCheck
from osm_check import OSMCheck


class UtilityProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.data_check = DataCheck(self.config)
        self.db_check = DatabaseCheck(self.config)
        self.osm_check = OSMCheck(self.config)
        self.data_validation = DataValidation()

    def process_feature(self, feature, buildings_gdf):
        # Try to get the data from user files filtered by polygon
        data = self.data_check.get_data_from_user(feature, buildings_gdf)

        # If no data from user, check the database
        if data is None:
            data = self.db_check.get_data_from_db(feature, buildings_gdf)

        # If still no data, check OSM
        if buildings_gdf[feature].isnull().all():
            osm_data = self.osm_check.get_data_from_osm(feature)

            if osm_data:
                # Convert OSM data to GeoDataFrame
                osm_gdf = gpd.GeoDataFrame.from_features(osm_data["features"])

                # Perform spatial join to match OSM data with buildings_gdf by geometry
                buildings_gdf = gpd.sjoin(buildings_gdf, osm_gdf, how='left', op='intersects')

                # Assuming osm_gdf has 'feature' as a column, assign the feature from OSM
                buildings_gdf[feature] = buildings_gdf[feature].fillna(buildings_gdf[f'{feature}_right'])

                # Drop unnecessary right-side columns if created
                buildings_gdf = buildings_gdf.drop(columns=[f'{feature}_right'], errors='ignore')

            return buildings_gdf

        # Validate the data
        if data and self.data_validation.validate(data):
            return data
        else:
            return None
