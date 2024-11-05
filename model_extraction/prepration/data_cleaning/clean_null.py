import json

import geopandas as gpd
import numpy as np
import pandas as pd


class CleanGeoData:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.buildings_file_path = config['building_path']
        self.geo_data = gpd.read_file(self.buildings_file_path)

    def clean_data(self):
        # Replace empty strings, NaNs, etc., with None
        self.geo_data = self.geo_data.replace({pd.NA: None, np.nan: None, '': None})

        # Drop rows with too many None values
        threshold = len(self.geo_data.columns) * 0.5  # Define a threshold for None values
        self.geo_data = self.geo_data.dropna(thresh=threshold)

        self.geo_data.to_file(self.buildings_file_path, driver='GeoJSON')
        print(f"Cleaned GeoJSON successfully saved to {self.buildings_file_path}")

        return self.geo_data
