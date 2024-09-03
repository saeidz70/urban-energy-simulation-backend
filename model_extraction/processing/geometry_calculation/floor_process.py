import json

import geopandas as gpd
import pandas as pd


class FloorProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.building_path = self.config['Building_usage_path']
        self.avg_floor_height = self.config["limits"]['avg_floor_height']
        self.buildings_gdf = gpd.read_file(self.building_path)

    def process_floors(self):
        if 'height' not in self.buildings_gdf.columns:
            raise ValueError("'height' column must be present in the dataset.")

        if 'building:levels' in self.buildings_gdf.columns:
            self.buildings_gdf['building:levels'] = pd.to_numeric(self.buildings_gdf['building:levels'],
                                                                  errors='coerce')
            self.buildings_gdf['n_floor'] = self.buildings_gdf['building:levels']
            missing_levels_mask = self.buildings_gdf['n_floor'].isnull()
            self.buildings_gdf.loc[missing_levels_mask, 'n_floor'] = (
                        self.buildings_gdf.loc[missing_levels_mask, 'height'] / self.avg_floor_height).round().astype(
                int)
        else:
            self.buildings_gdf['n_floor'] = (self.buildings_gdf['height'] / self.avg_floor_height).round().astype(int)

        if 'building:levels' in self.buildings_gdf.columns:
            self.buildings_gdf = self.buildings_gdf.drop(columns=['building:levels'])

        if 'height' not in self.buildings_gdf.columns:
            raise ValueError("'height' column must be present in the dataset.")

        columns = list(self.buildings_gdf.columns)
        height_index = columns.index('height')
        columns.insert(height_index + 1, columns.pop(columns.index('n_floor')))
        self.buildings_gdf = self.buildings_gdf[columns]

        self.buildings_gdf.to_file(self.building_path, driver='GeoJSON')
        return self.buildings_gdf
