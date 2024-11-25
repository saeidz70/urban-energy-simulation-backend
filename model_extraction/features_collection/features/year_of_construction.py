import geopandas as gpd
import pandas as pd

from config.config import Config


class YearOfConstruction(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'year_of_construction'
        self.census_id_column = 'census_id'
        # Load configuration for building path and year_of_construction details
        self.building_path = self.config.get("building_path")
        year_config = self.config.get('features', {}).get('year_of_construction', {})
        self.census_columns = list(year_config.get("census_built_year", {}).keys())
        self.year_mapping = year_config.get("census_built_year", {})
        self.median_years = self._calculate_median_years()

    def _calculate_median_years(self):
        """
        Calculate median years for each census period.
        """
        median_years = {}
        for key, period in self.year_mapping.items():
            try:
                start, end = map(int, period.split('-'))
                median_years[key] = (start + end) // 2
            except ValueError:
                median_years[key] = None  # Assign None for invalid or unexpected formats
        return median_years

    def _validate_columns(self, gdf, required_columns):
        """
        Validate that the required columns exist in the GeoDataFrame.
        """
        missing_columns = [col for col in required_columns if col not in gdf.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    def _convert_to_numeric(self, gdf):
        """
        Convert census-related columns to numeric values, handling errors gracefully.
        """
        for col in self.census_columns:
            if col in gdf.columns:
                gdf[col] = pd.to_numeric(gdf[col], errors='coerce').fillna(0).astype(int)

    def _calculate_group_year(self, group):
        """
        Calculate the weighted average year for a group of buildings.
        """
        building_counts = {
            col: group[col].sum() for col in self.census_columns if col in group.columns
        }
        total_count = sum(building_counts.values())

        if total_count == 0:
            return 1900  # Default year for groups with no data

        # Weighted average year calculation
        weighted_year = sum(
            self.median_years[col] * count / total_count
            for col, count in building_counts.items() if self.median_years.get(col) is not None
        )

        return int(round(weighted_year))  # Ensure the result is an integer

    def _assign_years(self, gdf):
        """
        Assign year_of_construction to buildings by grouping by census_id.
        """
        year_mapping = {}

        for census_id, group in gdf.groupby(self.census_id_column):
            year_mapping[census_id] = self._calculate_group_year(group)

        gdf[self.feature_name] = gdf[self.census_id_column].map(year_mapping).fillna(1900).astype(int)
        return gdf

    def _save_to_file(self, gdf):
        """
        Save the updated GeoDataFrame to the configured GeoJSON file.
        """
        gdf.to_file(self.building_path, driver='GeoJSON')
        print(f"Updated building data saved to {self.building_path}.")

    def run(self):
        """
        Execute the full process to assign construction years.
        """
        print(f"Starting the process to assign {self.feature_name}...")

        # Load the building data
        buildings_gdf = gpd.read_file(self.building_path)

        # Validate required columns
        self._validate_columns(buildings_gdf, required_columns=[self.census_id_column])

        # Convert census-related columns to numeric
        self._convert_to_numeric(buildings_gdf)

        # Assign construction years
        updated_gdf = self._assign_years(buildings_gdf)

        # Save the updated GeoDataFrame
        self._save_to_file(updated_gdf)

        print("Year of construction assignment completed.")
        return updated_gdf
