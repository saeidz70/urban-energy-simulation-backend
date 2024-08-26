import json

import geopandas as gpd


class ProcessAreas:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.building_path = config['building_path']
        self.buildings_gdf = gpd.read_file(self.building_path)

    def calculate_building_areas(self):
        self.buildings_gdf['area'] = self.buildings_gdf['geometry'].area.round(2)

        # Reorder columns to place 'area' next to 'height'
        columns = list(self.buildings_gdf.columns)
        if 'height' in columns:
            height_index = columns.index('height')
            columns.insert(height_index + 1, columns.pop(columns.index('area')))
        self.buildings_gdf = self.buildings_gdf[columns]

        self.buildings_gdf.to_file(self.building_path, driver='GeoJSON')
        print(f"Building areas GeoJSON successfully saved to {self.building_path}")

        return self.buildings_gdf
