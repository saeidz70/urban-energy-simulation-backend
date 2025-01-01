import pandas as pd

from processing.features_collection.base_feature import BaseFeature


class YearOfConstruction(BaseFeature):
    """
    Assigns year of construction to buildings based on census data.
    """

    def calculate(self, gdf, rows=None):
        self.median_years = self._calculate_median_years()
        self._convert_to_numeric(gdf)
        """
        Assign year_of_construction to buildings by grouping by census_id.
        """
        year_mapping = {
            census_id: self._calculate_group_year(group)
            for census_id, group in gdf.groupby(self.required_features[0])
        }

        if rows is None:
            # Assign to all rows if no specific rows are specified
            gdf[self.feature_name] = gdf[self.required_features[0]].map(year_mapping).fillna(1900).astype(int)
        else:
            # Assign only to invalid rows
            gdf.loc[rows, self.feature_name] = gdf.loc[rows, self.required_features[0]].map(
                year_mapping).fillna(1900).astype(int)

        gdf = self.validate_data(gdf, self.feature_name)

        print("Year of construction assignment completed.")
        return gdf

    def _calculate_median_years(self):
        """
        Calculate median years for each census period.
        """
        median_years = {}
        for key, period in self.census_built_year.items():
            try:
                start, end = map(int, period.split('-'))
                median_years[key] = (start + end) // 2
            except ValueError:
                median_years[key] = None  # Assign None for invalid or unexpected formats
        return median_years

    def _calculate_group_year(self, group):
        """
        Calculate the weighted average year for a group of buildings.
        """
        # Convert relevant columns to numeric to handle mixed types
        building_counts = {
            col: pd.to_numeric(group[col], errors='coerce').sum()
            for col in self.census_built_year.keys() if col in group.columns
        }
        total_count = sum(building_counts.values())

        if total_count == 0:
            return 1900  # Default year for groups with no data

        # Weighted average year calculation
        weighted_year = sum(
            self.median_years[col] * count / total_count
            for col, count in building_counts.items() if self.median_years.get(col) is not None
        )

        return int(round(weighted_year))

    def _convert_to_numeric(self, gdf):
        """
        Convert census-related columns to numeric values, handling errors gracefully.
        """
        for col in self.census_built_year.keys():
            if col in gdf.columns:
                gdf[col] = pd.to_numeric(gdf[col], errors='coerce').fillna(0).astype(int)
