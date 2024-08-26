import json
import os

import geopandas as gpd
import numpy as np
from pykrige.ok import OrdinaryKriging


class BuildingKrigingFiller:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.buildings_geojson_path = config['filtered_area_path']
        self.output_file_path = config['kriging_output_path']
        self.projected_crs = config.get('DEFAULT_EPSG_CODE', 'EPSG:32632')  # Default to Turin UTM zone 32N

        # Load GeoJSON file during initialization
        self.buildings_gdf = self.load_geojson(self.buildings_geojson_path)

    def load_geojson(self, file_path):
        return gpd.read_file(file_path)

    def fill_missing_values_kriging(self, column_name):
        # Ensure the GeoDataFrame is projected
        self.buildings_gdf = self.buildings_gdf.to_crs(self.projected_crs)

        # Extract coordinates and values for known points
        known_points = self.buildings_gdf.dropna(subset=[column_name])
        missing_points = self.buildings_gdf[self.buildings_gdf[column_name].isnull()]

        if known_points.empty or missing_points.empty:
            print(f"No available data for Kriging on column {column_name}.")
            return

        # Get coordinates and values
        known_coords = np.array([(geom.centroid.x, geom.centroid.y) for geom in known_points.geometry])
        missing_coords = np.array([(geom.centroid.x, geom.centroid.y) for geom in missing_points.geometry])
        known_values = known_points[column_name].values

        # Perform Kriging
        krige = OrdinaryKriging(
            known_coords[:, 0], known_coords[:, 1], known_values,
            variogram_model='linear',
            verbose=False,
            enable_plotting=False
        )
        z, ss = krige.execute('points', missing_coords[:, 0], missing_coords[:, 1])

        # Fill in the missing values
        self.buildings_gdf.loc[self.buildings_gdf[column_name].isnull(), column_name] = z

    def save_filled(self):
        output_dir = os.path.dirname(self.output_file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.buildings_gdf.to_file(self.output_file_path, driver='GeoJSON')
        print(f"Building data with filled values saved to {self.output_file_path}.")

    def process_filling(self):
        # Fill missing values for 'height' using Kriging
        self.fill_missing_values_kriging('height')
        # Round 'height' to 1 decimal place and convert to float
        self.buildings_gdf['height'] = self.buildings_gdf['height'].astype(float).round(1)

        # Fill missing values for 'building:levels' using Kriging
        self.fill_missing_values_kriging('building:levels')
        # Round 'building:levels' and convert to integer
        self.buildings_gdf['building:levels'] = self.buildings_gdf['building:levels'].round().astype(int)

        self.save_filled()
