import json
import os
from typing import Dict, Any

import geopandas as gpd
import numpy as np
from pykrige.ok import OrdinaryKriging


class BuildingKrigingFiller:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.input_file_path = self.config["input_params"]["height"]["input"]
        self.output_file_path = self.config["input_params"]["height"]["output"]
        self.projected_crs = self.config.get('DEFAULT_EPSG_CODE', 'EPSG:32632')
        self.target_column = self.config["input_params"]["height"]['kriging_target_column']
        self.buildings_gdf = self.load_geojson(self.input_file_path)

    def load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found.")
            raise
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the configuration file {config_path}.")
            raise

    def load_geojson(self, file_path: str) -> gpd.GeoDataFrame:
        try:
            return gpd.read_file(file_path)
        except FileNotFoundError:
            print(f"GeoJSON file {file_path} not found.")
            raise
        except Exception as e:
            print(f"Error loading GeoJSON file {file_path}: {e}")
            raise

    def fill_missing_values_kriging(self) -> None:
        self.buildings_gdf = self.buildings_gdf.to_crs(self.projected_crs)
        known_points = self.buildings_gdf.dropna(subset=[self.target_column])
        missing_points = self.buildings_gdf[self.buildings_gdf[self.target_column].isnull()]

        if known_points.empty or missing_points.empty:
            print(f"No available data for Kriging on column {self.target_column}.")
            return

        known_coords = self.extract_coordinates(known_points)
        missing_coords = self.extract_coordinates(missing_points)
        known_values = known_points[self.target_column].values

        filled_values = self.perform_kriging(known_coords, known_values, missing_coords)
        self.buildings_gdf.loc[self.buildings_gdf[self.target_column].isnull(), self.target_column] = filled_values

    def extract_coordinates(self, gdf: gpd.GeoDataFrame) -> np.ndarray:
        return np.array([(geom.centroid.x, geom.centroid.y) for geom in gdf.geometry])

    def perform_kriging(self, known_coords: np.ndarray, known_values: np.ndarray,
                        missing_coords: np.ndarray) -> np.ndarray:
        krige = OrdinaryKriging(
            known_coords[:, 0], known_coords[:, 1], known_values,
            variogram_model='linear',
            verbose=False,
            enable_plotting=False
        )
        z, _ = krige.execute('points', missing_coords[:, 0], missing_coords[:, 1])
        return z

    def save_filled(self) -> None:
        os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
        self.buildings_gdf.to_file(self.output_file_path, driver='GeoJSON')
        print(f"Building data with filled values saved to {self.output_file_path}.")

    def process_filling(self) -> None:
        self.fill_missing_values_kriging()
        self.buildings_gdf[self.target_column] = self.buildings_gdf[self.target_column].astype(float).round(1)
        self.save_filled()

