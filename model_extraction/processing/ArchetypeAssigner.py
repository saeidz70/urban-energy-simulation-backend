import json
import pandas as pd
import geopandas as gpd


class BuildingArchetypeAssigner:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.tab_match_path = config['tabula']
        self.building_path = config['building_path']
        self.output_path = config['output_archetypes_path']

        self.tab_match_df = pd.read_csv(self.tab_match_path)
        self.tab_match_df['YEAR'] = self.tab_match_df['YEAR'].str.strip()
        self.buildings_gdf = gpd.read_file(self.building_path)

        # Print the columns to debug
        print("Columns in buildings_gdf:", self.buildings_gdf.columns)

    def get_year_slot(self, year):
        for i, string_slot in enumerate(self.tab_match_df['YEAR']):
            string_slot = string_slot.strip()
            if string_slot.startswith('...'):
                slot = [0, int(string_slot.split('...')[1].strip())]
            elif string_slot.endswith('...'):
                slot = [int(string_slot.split('...')[0].strip()), 1000000]
            else:
                slot = [int(string_slot.split('...')[0].strip()), int(string_slot.split('...')[1].strip())]

            if slot[0] <= year <= slot[1]:
                return i
        return None

    def assign_archetype(self, row):
        if row['tab_type'] == 'unknown' or row['usage'] != 'residenziale':
            return 'unknown'
        try:
            return self.tab_match_df.iloc[int(row['tabula_year_slot'])][row['tab_type']]
        except Exception as e:
            print(f"Error assigning archetype: {e}")
            return 'unknown'

    def assign_tab_type(self, row):
        if row['usage'] != 'residenziale':
            return 'unknown'
        if row['n_families'] == 1 and row['number_of_floors'] <= 2:
            return 'SFH'
        elif row['n_families'] > 1 and row['number_of_floors'] >= 4:
            return 'AB'
        elif row['n_families'] > 1 and row['number_of_floors'] < 4:
            return 'MFH'
        elif row['n_families'] == 1 and row['number_of_floors'] == 3:
            return 'TH'
        elif 1 < row['n_families'] <= 3 and row['number_of_floors'] < 3:
            return 'TH'
        else:
            return 'unknown'

    def process_buildings(self):
        # Debug: Check if 'year' column exists
        if 'year' not in self.buildings_gdf.columns:
            raise KeyError("The 'year' column is missing from the buildings GeoDataFrame.")

        self.buildings_gdf['tabula_year_slot'] = self.buildings_gdf['year'].apply(self.get_year_slot)
        self.buildings_gdf['tab_type'] = self.buildings_gdf.apply(self.assign_tab_type, axis=1)
        self.buildings_gdf['archetype_code'] = self.buildings_gdf.apply(self.assign_archetype, axis=1)
        self.buildings_gdf.to_file(self.output_path, driver='GeoJSON')
        print(f"Processed buildings data successfully saved to {self.output_path}")
        return self.buildings_gdf
