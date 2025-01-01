import numpy as np
import pandas as pd

from config.config import Config


class CleanGeoData(Config):
    def __init__(self):
        super().__init__()
        self.buildings_file_path = self.config['building_path']
        self.geo_data = None

    def run(self, integrated_gdf):
        self.geo_data = integrated_gdf
        
        # Replace empty strings, NaNs, etc., with None
        self.geo_data = self.geo_data.replace({pd.NA: None, np.nan: None, '': None})

        # Drop rows with too many None values
        threshold = len(self.geo_data.columns) * 0.5  # Define a threshold for None values

        self.geo_data = self.geo_data.dropna(thresh=threshold)

        self.geo_data.to_file(self.buildings_file_path, driver='GeoJSON')
        print(f"Cleaned GeoJSON successfully saved to {self.buildings_file_path}")

        return self.geo_data
