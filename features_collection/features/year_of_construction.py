import geopandas as gpd
import pandas as pd

from config.config import Config


class YearOfConstruction(Config):
    def __init__(self):
        super().__init__()
        self.building_path = self.config["building_path"]
        self.census_columns = list(self.config["census"]["built_year"].keys())
        self.year_mapping = self.config["census"]["built_year"]
        self.median_years = self.calculate_median_years()

    def calculate_median_years(self):
        """
        Calculate median years for each census period based on the config mapping.
        """
        median_years = {}
        for key, period in self.year_mapping.items():
            if "-" in period:
                start, end = map(int, period.split('-'))
                median_years[key] = (start + end) // 2
            else:
                median_years[key] = None  # Handle unexpected formats
        return median_years

    def assign_construction_year(self):
        """
        Assign 'year_of_construction' to buildings based on census data and proportion of buildings.
        """
        # Load the building GeoDataFrame
        buildings_gdf = gpd.read_file(self.building_path)

        # Ensure 'census_id' column exists
        if 'census_id' not in buildings_gdf.columns:
            raise ValueError("The 'census_id' column is missing in the building data.")

        # Convert census columns to integers (handle non-numeric values as zeros)
        for col in self.census_columns:
            if col in buildings_gdf.columns:
                buildings_gdf[col] = pd.to_numeric(buildings_gdf[col], errors='coerce').fillna(0).astype(int)

        # Create a new column to store the assigned construction years
        buildings_gdf['year_of_construction'] = None

        # Group buildings by census_id
        for census_id, group in buildings_gdf.groupby("census_id"):
            # Sum the building counts for each census period
            building_counts = {key: group[key].sum() for key in self.census_columns if key in group.columns}
            total_census_buildings = sum(building_counts.values())

            if total_census_buildings > 0:
                # Calculate the weighted average year of construction for the group
                weighted_year = sum(
                    self.median_years[key] * (building_counts[key] / total_census_buildings)
                    for key in self.census_columns if self.median_years[key] is not None
                )
                # Assign the weighted year to all buildings in the group
                weighted_year = min(max(round(weighted_year), 1900), 2022)  # Clamp between 1900 and 2022
                buildings_gdf.loc[group.index, 'year_of_construction'] = weighted_year

        # Fill any remaining None values with a default year
        buildings_gdf['year_of_construction'].fillna(1900, inplace=True)

        # Save the output
        self.save_output(buildings_gdf)
        return buildings_gdf

    def save_output(self, buildings_gdf):
        """
        Save the updated GeoDataFrame to a GeoJSON file.
        """
        buildings_gdf.to_file(self.building_path, driver='GeoJSON')
        print(f"Updated building data saved to {self.building_path}.")

    def run(self):
        """
        Run the process to assign construction years to buildings.
        """
        print("Starting the process to assign year_of_construction...")
        buildings_gdf = self.assign_construction_year()
        print("year_of_construction process completed.")
        return buildings_gdf
