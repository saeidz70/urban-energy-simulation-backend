import json
import re

import geopandas as gpd
import pandas as pd

from model_extraction.processing.geometry_calculation.height_processing.dsm_height_calculator import \
    BuildingHeightCalculator


class HeightProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.building_path = config['filtered_area_path']
        self.config_path = config_path
        self.buildings_gdf = gpd.read_file(self.building_path)

    def calculate_heights_from_dtm_dsm(self):
        calculator = BuildingHeightCalculator(self.config_path)
        calculator.load_data()
        building_heights = calculator.calculate_building_heights()

        # Extract heights for building centroids
        heights = []
        for geom in self.buildings_gdf.geometry:
            centroid = geom.centroid
            row, col = ~calculator.dtm_profile['transform'] * (centroid.x, centroid.y)
            row, col = int(row), int(col)
            heights.append(building_heights[row, col])

        self.buildings_gdf['height_dsm'] = heights
        return heights

    def clean_height(self, height):
        if height is None or pd.isna(height):  # Check for None or NaN
            return None
        if isinstance(height, str):
            height = re.sub(r'[^\d.]+', '', height)
        try:
            return float(height)
        except ValueError:
            return None

    def process_height(self):
        if 'height' in self.buildings_gdf.columns and 'building:levels' in self.buildings_gdf.columns:
            # Clean height values and convert to float
            self.buildings_gdf['height'] = self.buildings_gdf['height'].apply(self.clean_height)

            # Convert 'building:levels' to numeric, forcing errors to NaN
            self.buildings_gdf['building:levels'] = pd.to_numeric(self.buildings_gdf['building:levels'],
                                                                  errors='coerce')

            # Calculate missing 'building:levels' based on 'height'
            self.buildings_gdf.loc[
                self.buildings_gdf['height'].notnull() & self.buildings_gdf[
                    'building:levels'].isnull(), 'building:levels'
            ] = (self.buildings_gdf['height'] / 3.5).round()

            # Calculate missing 'height' based on 'building:levels'
            self.buildings_gdf.loc[
                self.buildings_gdf['height'].isnull() & self.buildings_gdf['building:levels'].notnull(), 'height'
            ] = self.buildings_gdf['building:levels'] * 3.5

        elif 'height' in self.buildings_gdf.columns:
            # Clean height values and convert to float
            self.buildings_gdf['height'] = self.buildings_gdf['height'].apply(self.clean_height)

            # Calculate 'building:levels' from 'height'
            self.buildings_gdf['building:levels'] = self.buildings_gdf['height'] / 3.5

        elif 'building:levels' in self.buildings_gdf.columns:
            # Convert 'building:levels' to numeric, forcing errors to NaN
            self.buildings_gdf['building:levels'] = pd.to_numeric(self.buildings_gdf['building:levels'],
                                                                  errors='coerce')

            # Calculate 'height' from 'building:levels'
            self.buildings_gdf['height'] = self.buildings_gdf['building:levels'] * 3.5

        else:
            # If neither column exists, calculate heights from DSM/DTM
            self.calculate_heights_from_dtm_dsm()

        self.buildings_gdf.to_file(self.building_path, driver='GeoJSON')
        return self.buildings_gdf
