import json
import geopandas as gpd
import pandas as pd


class HeightProcess:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.building_path = config['building_path']
        self.buildings_gdf = gpd.read_file(self.building_path)

    def process_height(self):
        if 'height' in self.buildings_gdf.columns:
            try:
                self.buildings_gdf['height'] = self.buildings_gdf['height'].astype(int)
            except ValueError:
                self.buildings_gdf['height'] = pd.to_numeric(self.buildings_gdf['height'], errors='coerce')
                if 'building:levels' in self.buildings_gdf.columns:
                    self.buildings_gdf['height'].fillna(self.buildings_gdf['building:levels'].astype(int) * 3,
                                                        inplace=True)
                else:
                    print("No 'building:levels' data available to calculate missing heights.")
        else:
            if 'building:levels' in self.buildings_gdf.columns:
                self.buildings_gdf['height'] = self.buildings_gdf['building:levels'].astype(int) * 3
            else:
                print("Neither 'height' nor 'building:levels' are available in the dataset.")

        self.buildings_gdf.to_file(self.building_path, driver='GeoJSON')
        return self.buildings_gdf
