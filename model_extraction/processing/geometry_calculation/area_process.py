import json
import os

import geopandas as gpd


class BuildingAreaCalculator:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.buildings_geojson_path = config['building_path']
        self.projected_crs = config.get('DEFAULT_EPSG_CODE', 'EPSG:32632')  # Default to Turin UTM zone 32N

        # Load GeoJSON file during initialization
        self.buildings_gdf = self.load_geojson(self.buildings_geojson_path)

    def load_geojson(self, file_path):
        return gpd.read_file(file_path)

    def calculate_areas(self):
        # Reproject to projected CRS for accurate area calculation
        gdf_projected = self.buildings_gdf.to_crs(self.projected_crs)
        gdf_projected['area'] = gdf_projected.geometry.area.round(2)  # Calculate area and round to 2 decimals

        # Correctly reorder columns to make 'area' the first column
        columns = ['area'] + [col for col in gdf_projected.columns if col != 'area']
        gdf_projected = gdf_projected.reindex(columns=columns)
        return gdf_projected

    def filter_buildings(self, gdf, min_area=50):
        filtered_gdf = gdf[gdf['area'] >= min_area]
        return filtered_gdf

    def save_filtered(self, filtered_gdf):
        output_dir = os.path.dirname(self.buildings_geojson_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filtered_gdf.to_file(self.buildings_geojson_path, driver='GeoJSON')
        print(f"Filtered building data saved to {self.buildings_geojson_path}.")

    def process_buildings(self):
        buildings_with_area = self.calculate_areas()
        filtered_buildings = self.filter_buildings(buildings_with_area)
        self.save_filtered(filtered_buildings)
