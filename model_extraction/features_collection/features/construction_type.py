from model_extraction.features_collection.base_feature import BaseFeature


class ConstructionType(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'construction_type'
        self.year_of_construction_column = 'year_of_construction'
        self.construction_config = self.config.get('features', {}).get(self.feature_name, {})
        self.construction_periods = self.construction_config.get('construction_period', {})

    def run(self, gdf):
        """Run the construction type feature collection process."""
        print(f"Running {self.feature_name} feature process...")

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate that the required year_of_construction_column exists in the GeoDataFrame
        if not self._validate_required_columns_exist(gdf, [self.year_of_construction_column]):
            return gdf

        # Retrieve construction_type if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf[self.feature_name] = gdf[self.year_of_construction_column].apply(self._get_construction_type)

        else:
            # Check for null or invalid values in the construction_type column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, str))

            # Assign construction type based on year_of_construction for invalid rows
            gdf.loc[invalid_rows, self.feature_name] = gdf.loc[invalid_rows, self.year_of_construction_column].apply(
                self._get_construction_type)

        print(f"Completed {self.feature_name} feature process.")
        return gdf

    def _get_construction_type(self, year):
        """Determines the construction type based on the year of construction."""
        for period, construction_type in self.construction_periods.items():
            start_year, end_year = map(int, period.split('-'))
            if start_year <= year <= end_year:
                return construction_type
        return None  # Return None if no matching period is found