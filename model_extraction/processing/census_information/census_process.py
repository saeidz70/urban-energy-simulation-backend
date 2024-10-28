import json

import geopandas as gpd
import pandas as pd


class ProcessCensus:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.census_path = config['census_path']
        self.building_path = config['input_file']
        self.output_selected_census_path = config['output_selected_census_path']
        self.output_buildings_census_path = config['output_buildings_census_path']
        self.census_df = pd.read_csv(self.census_path, encoding='ISO-8859-1', delimiter=',')
        self.buildings_gdf = gpd.read_file(self.building_path)

    def make_selected_census(self):

        # print("Census columns:", self.census_df.columns)
        # print("Building columns:", self.buildings_gdf.columns)
        if 'SEZ2011' not in self.census_df.columns or 'SEZ2011' not in self.buildings_gdf.columns:
            raise ValueError("SEZ2011 is not available in one of the datasets")
        elif 'SEZ2011' in self.census_df.columns and 'SEZ2011' in self.buildings_gdf.columns:
            sez2011_ids = self.buildings_gdf['SEZ2011'].unique()
            filtered_census_df = self.census_df[self.census_df['SEZ2011'].isin(sez2011_ids)]
            filtered_census_df.to_csv(self.output_selected_census_path, index=False)
            print(f"Filtered census data successfully saved to {self.output_selected_census_path}")

            return filtered_census_df

    def merge_buildings_census(self):
        if 'SEZ2011' not in self.census_df.columns or 'SEZ2011' not in self.buildings_gdf.columns:
            raise ValueError("SEZ2011 is not available in one of the datasets")
        elif 'SEZ2011' in self.census_df.columns and 'SEZ2011' in self.buildings_gdf.columns:
            merged_gdf = self.buildings_gdf.merge(self.census_df, on='SEZ2011', how='inner')
            merged_gdf.to_file(self.output_buildings_census_path, driver='GeoJSON')
            print(f"Data successfully merged and saved to {self.output_buildings_census_path}")

            return merged_gdf
        