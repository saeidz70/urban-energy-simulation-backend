import json
import geopandas as gpd


class FloorProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.building_path = self.config['building_path']
        self.avg_floor_height = self.config['limits']['avg_floor_height']
        self.buildings_gdf = gpd.read_file(self.building_path)

    def process_floors(self):
        if 'building:levels' in self.buildings_gdf.columns:
            self.buildings_gdf['n_floor'] = self.buildings_gdf['building:levels'].astype(int)
            self.buildings_gdf = self.buildings_gdf.drop(columns=['building:levels'])
        elif 'height' in self.buildings_gdf.columns:
            self.buildings_gdf['n_floor'] = (self.buildings_gdf['height'] / self.avg_floor_height).round().astype(int)
        else:
            raise ValueError("Neither 'building:levels' nor 'height' columns are present in the dataset.")

        # Ensure 'area' column exists
        if 'area' not in self.buildings_gdf.columns:
            raise ValueError("'area' column must be present in the dataset.")

        # Reorder columns to place 'n_floor' next to 'area'
        columns = list(self.buildings_gdf.columns)
        area_index = columns.index('area')
        columns.insert(area_index + 1, columns.pop(columns.index('n_floor')))
        self.buildings_gdf = self.buildings_gdf[columns]

        self.buildings_gdf.to_file(self.building_path, driver='GeoJSON')
        return self.buildings_gdf
