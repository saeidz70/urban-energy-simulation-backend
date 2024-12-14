import os
import warnings
from abc import ABC, abstractmethod

import geopandas as gpd
import pandas as pd

from model_extraction.data_manager.utility import UtilityProcess


class BaseFeature(UtilityProcess, ABC):
    def __init__(self):
        # Initialize default and projected CRS from configuration
        super().__init__()
        self.feature_name = None
        self.projected_crs = self.config.get('PROJECTED_CRS', 'EPSG:32632')
        self.default_crs = self.config.get('DEFAULT_CRS', 4326)

    # --- CRS Management ---
    def set_crs(self, gdf, target_crs, crs_type="default"):
        """
        Ensure the GeoDataFrame has the correct CRS, reprojecting if necessary.
        """
        if gdf.crs is None:
            print(f"No CRS found; setting to {crs_type} CRS (EPSG:{target_crs}).")
            gdf.set_crs(epsg=target_crs, inplace=True)
        elif gdf.crs.to_string() != f"EPSG:{target_crs}":
            print(f"CRS mismatch. Reprojecting to {crs_type} CRS (EPSG:{target_crs}).")
            gdf = gdf.to_crs(epsg=target_crs)
        return gdf

    def check_crs_with_default_crs(self, gdf):
        return self.set_crs(gdf, self.default_crs, crs_type="default")

    def check_crs_with_projected_crs(self, gdf):
        return self.set_crs(gdf, self.projected_crs, crs_type="projected")

    # --- File Operations ---
    def load_geojson(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"GeoJSON file not found: {file_path}")
        gdf = gpd.read_file(file_path)
        if 'geometry' not in gdf.columns or gdf.empty:
            raise ValueError("The input GeoJSON file does not contain valid geometry data.")
        return gdf

    def save_geojson(self, gdf, file_path):
        gdf.to_file(file_path, driver='GeoJSON')
        print(f"Data saved to {file_path}.")

    # --- Feature Management ---
    def initialize_feature_column(self, gdf, feature_name):
        if feature_name not in gdf.columns:
            print(f"Initializing {feature_name} column.")
            gdf[feature_name] = None
        return gdf

    def validate_required_columns_exist(self, gdf, feature_name):
        required_features = self.config.get('features', {}).get(feature_name, {}).get('required_features', [])
        missing_columns = [col for col in required_features if col not in gdf.columns]
        if missing_columns:
            warnings.warn(f"Missing required columns for feature '{feature_name}': {', '.join(missing_columns)}")
            return False
        return True

    def update_missing_values(self, gdf, new_data, feature_name):
        """
        Update missing values in the feature column of the GeoDataFrame using values from new data.
        """
        if new_data is not None and feature_name in new_data.columns:
            # Align indices between gdf and new_data
            new_data = new_data.set_index(gdf.index)  # Ensure the indices match

            # Assign only the missing values
            missing_mask = gdf[feature_name].isnull()
            gdf.loc[missing_mask, feature_name] = new_data.loc[missing_mask, feature_name]
        return gdf

    def process_feature(self, gdf, feature_name):
        gdf = self.initialize_feature_column(gdf, feature_name)
        if not self.validate_required_columns_exist(gdf, feature_name):
            return gdf
        gdf = self.retrieve_data_from_sources(feature_name, gdf)
        return gdf

    def check_invalid_rows(self, gdf, feature_name):
        if not gdf[feature_name].isnull().all():
            gdf = self.validate_data(gdf, feature_name)
        invalid_rows = gdf[gdf[feature_name].isnull()]
        if not invalid_rows.empty:
            print(f"Found {len(invalid_rows)} invalid rows in feature '{feature_name}'.")
        else:
            print(f"No invalid rows found for feature '{feature_name}'.")
        return invalid_rows

    def filter_data(self, gdf, feature_name, min_value, max_value, data_type):
        """
        Validate and filter the feature column in the GeoDataFrame.
        Replace values outside the specified range with default min/max values.
        """
        if feature_name not in gdf.columns:
            print(f"Feature '{feature_name}' does not exist in the GeoDataFrame.")
            return gdf

        # Replace invalid values with min_value or max_value
        gdf[feature_name] = gdf[feature_name].apply(
            lambda x: x if pd.notnull(x) and min_value <= x <= max_value else min_value
        )

        # Ensure data type is consistent
        gdf[feature_name] = gdf[feature_name].astype(data_type)
        return gdf

    def get_feature_config(self, feature_name):
        """
        Retrieve and set configuration attributes for a feature dynamically.
        """
        # Retrieve the feature's configuration
        feature_config = self.config.get('features', {}).get(feature_name, {})

        if not feature_config:
            raise KeyError(f"Feature '{feature_name}' configuration not found in the config file.")

        # Dynamically assign configuration attributes to the instance
        for key, value in feature_config.items():
            setattr(self, key, value)
        return feature_config

    def run(self, gdf, feature_name):
        """
        Main method to assign feature values to the GeoDataFrame.
        """
        self.feature_name = feature_name
        self.get_feature_config(self.feature_name)  # Dynamically retrieve and set feature configuration
        self.dep = self.config.get('required_features', [])
        print(f"Starting {self.feature_name} assignment...")

        # Process feature and initialize column
        gdf = self.process_feature(gdf, self.feature_name)

        # Handle invalid or missing Tabula IDs
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        print(f"Invalid rows count: {len(invalid_rows)} for {self.feature_name}")
        if not invalid_rows.empty:
            gdf = self.calculate(gdf, invalid_rows.index)

        # Validate and filter the feature data
        gdf = self.validate_data(gdf, self.feature_name)

        print(f"{self.feature_name} assignment completed.")
        return gdf

    @abstractmethod
    def calculate(self, gdf, rows):
        """
        Default calculation method: Assigns a 'not defined' value.
        """
        print(f"No specific calculation defined for {self.feature_name}. Assigning 'not defined' to rows.")
        gdf.loc[rows, self.feature_name] = "not defined"
        return gdf
