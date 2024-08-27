import json
import random

import geopandas as gpd
import pandas as pd


class CensusBuiltYear:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.building_path = config['shapefile_path']
        self.buildings_gdf = gpd.read_file(self.building_path)

        # Read periods from configuration file
        self.census_columns = list(config['attributes']['census']['built_year'].keys())
        self.period_mapping = config['attributes']['census']['built_year']

        # Calculate the median year for each period dynamically based on these columns
        self.median_years = self.calculate_median_years()

    def calculate_median_years(self):
        # Function to calculate the median year for each period based on the configuration file
        median_years = {}
        for column, period in self.period_mapping.items():
            try:
                if '-' in period:
                    parts = period.split('-')
                    if parts[0] == '':
                        end = int(parts[1])
                        median_years[column] = end
                    elif parts[1] == '':
                        start = int(parts[0])
                        median_years[column] = start + 5  # assuming a placeholder median for open-ended periods
                    else:
                        start, end = map(int, parts)
                        median_years[column] = (start + end) // 2
                elif period.startswith('-'):
                    end = int(period.replace('-', ''))
                    median_years[column] = end
                elif period.endswith('-'):
                    start = int(period.replace('-', ''))
                    median_years[column] = start + 5  # assuming a placeholder median for open-ended periods
                else:
                    raise ValueError(f"Invalid period format for column {column}: {period}")
            except ValueError:
                raise ValueError(f"Invalid period format for column {column}: {period}")
        return median_years

    def assign_built_year(self):
        # Check data types in census columns and convert to numeric if needed
        for column in self.census_columns:
            self.buildings_gdf[column] = pd.to_numeric(self.buildings_gdf[column], errors='coerce').fillna(0)

        # Debugging: Print a few rows to check data content
        print("Sample data from GeoDataFrame:")
        print(self.buildings_gdf.head())

        # Function to assign a built year based on the percentage distribution in the census section
        def get_random_year(group):
            # Convert strings to integers and ensure values are numeric
            periods = {key: group[key].sum() for key in self.census_columns}

            # Debugging: Check the computed periods
            print(f"Computed periods for group: {periods}")

            total_buildings = sum(periods.values())
            if total_buildings == 0:
                print(f"No buildings found in any period for group.")
                return pd.Series([None] * len(group))  # Return a Series of None if there are no buildings

            # Create a cumulative distribution
            cumulative_distribution = []
            cumulative = 0
            for column, count in periods.items():
                proportion = count / total_buildings
                cumulative += proportion
                cumulative_distribution.append((cumulative, self.median_years[column]))

            # Assign a construction year based on the cumulative distribution
            def choose_year():
                rand_value = random.random()
                for cumulative, year in cumulative_distribution:
                    if rand_value <= cumulative:
                        return year
                return None  # Fallback, should not happen

            # Assign a random year to each building in the group
            return group.apply(lambda _: choose_year(), axis=1)

        # Check if 'SEZ2011' column exists
        if 'SEZ2011' not in self.buildings_gdf.columns:
            print("SEZ2011 column is missing in the data.")
            return

        # Apply the function to each census section (grouped by SEZ2011)
        try:
            self.buildings_gdf['b_year_ces'] = self.buildings_gdf.groupby('SEZ2011').apply(
                get_random_year).reset_index(level=0, drop=True)
        except ValueError as e:
            print(f"Error during groupby operation: {e}")
            return

        # Debugging: Print DataFrame to check if the column is added correctly
        print("DataFrame after adding 'b_year_ces' column:")
        print(self.buildings_gdf.head())

        # Save the updated GeoDataFrame
        self.buildings_gdf.to_file(self.building_path, driver='GeoJSON')
        print(f"GeoJSON with assigned built years successfully saved to {self.building_path}")

        # Reload the GeoJSON file to check if the column exists
        reloaded_gdf = gpd.read_file(self.building_path)
        if 'b_year_ces' in reloaded_gdf.columns:
            print("Column 'b_year_ces' is present in the saved GeoJSON file.")
        else:
            print("Column 'b_year_ces' is NOT present in the saved GeoJSON file.")

        return self.buildings_gdf

