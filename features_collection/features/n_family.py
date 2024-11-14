import json
import geopandas as gpd
import pandas as pd

from config.config import Config
from features_collection.features.feature_helpers.volume import BuildingVolumeCalculator


class FamilyCalculator(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config['building_path']
        self.family_column = self.config["census"]["population_columns"]["n_family"]
        self.buildings = None  # To store the buildings GeoDataFrame

    def calculate_volume(self):
        volume_calculator = BuildingVolumeCalculator()
        volume_calculator.calculate_volume()

    def calculate_family_distribution(self):
        # Read buildings data if not already loaded
        if self.buildings is None:
            self.buildings = gpd.read_file(self.building_file)

        # Ensure the family column exists and convert to numeric, handling errors
        if self.family_column not in self.buildings.columns:
            self.buildings[self.family_column] = 0
        else:
            self.buildings[self.family_column] = pd.to_numeric(self.buildings[self.family_column],
                                                               errors='coerce').fillna(0)

        # Aggregate census volumes and families
        census_volumes = self.buildings.groupby('census_id')['volume'].sum()
        census_families = self.buildings.groupby('census_id')[self.family_column].sum()

        # Calculate family distribution based on volume ratios
        self.buildings['families'] = self.buildings.apply(
            lambda row: round((row['volume'] / census_volumes[row['census_id']]) * census_families[row['census_id']])
            if row['census_id'] in census_volumes and census_volumes[row['census_id']] > 0 else 0, axis=1
        )
        print("Family distribution calculated and added to buildings data.")

    def output_results(self):
        # Save the updated GeoJSON file with families data
        try:
            self.buildings.to_file(self.building_file, driver='GeoJSON')
            print(f"Updated data saved to {self.building_file}.")
        except Exception as e:
            print(f"Error saving data: {e}")
            raise

    def run(self):
        # Run the full family calculation process
        try:
            self.calculate_volume()
            self.calculate_family_distribution()
            self.output_results()
        except Exception as e:
            print(f"Error during processing: {e}")
