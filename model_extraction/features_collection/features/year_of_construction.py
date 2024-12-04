import pandas as pd

from model_extraction.features_collection.base_feature import BaseFeature


class YearOfConstruction(BaseFeature):
    """
    Assigns year of construction to buildings based on census data.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = 'year_of_construction'
        self.census_id_column = 'census_id'
        year_config = self.config.get('features', {}).get(self.feature_name, {})
        self.census_columns = list(year_config.get("census_built_year", {}).keys())
        self.year_mapping = year_config.get("census_built_year", {})
        self.median_years = self._calculate_median_years()

    def run(self, gdf):
        print(f"Starting the process to assign {self.feature_name}...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate required columns using BaseFeature method
        if not self._validate_required_columns_exist(gdf, [self.census_id_column]):
            return gdf

        # Retrieve year_of_construction if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Convert census-related columns to numeric
        self._convert_to_numeric(gdf)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self._assign_years(gdf)
        else:
            # Check for null or invalid values in the year_of_construction column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, int))

            # Assign years for invalid rows
            gdf = self._assign_years(gdf, invalid_rows)

        print("Year of construction assignment completed.")  # Essential print 2
        return gdf

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

    def _assign_years(self, gdf, invalid_rows=None):
        """
        Assign year_of_construction to buildings by grouping by census_id.
        """
        year_mapping = {}

        for census_id, group in gdf.groupby(self.census_id_column):
            year_mapping[census_id] = self._calculate_group_year(group)

        if invalid_rows is None:
            gdf[self.feature_name] = gdf[self.census_id_column].map(year_mapping).fillna(1900).astype(int)
        else:
            gdf.loc[invalid_rows, self.feature_name] = gdf.loc[invalid_rows, self.census_id_column].map(
                year_mapping).fillna(1900).astype(int)
        return gdf