import json
import geopandas as gpd
import pandas as pd
from model_extraction.processing.dsm_height_calculator import BuildingHeightCalculator


class HeightProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.building_path = config['building_path']
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

    def process_height(self):
        if 'height' in self.buildings_gdf.columns:
            try:
                self.buildings_gdf['height'] = self.buildings_gdf['height'].astype(int)
            except ValueError:
                self.buildings_gdf['height'] = pd.to_numeric(self.buildings_gdf['height'], errors='coerce')

        elif 'building:levels' in self.buildings_gdf.columns:
            self.buildings_gdf['height'] = self.buildings_gdf['building:levels'].astype(int) * 3

        else:
            # Calculate height from DTM & DSM
            self.calculate_heights_from_dtm_dsm()

        self.buildings_gdf.to_file(self.building_path, driver='GeoJSON')
        return self.buildings_gdf
