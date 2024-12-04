from model_extraction.features_collection.base_feature import BaseFeature


class GrossFloorArea(BaseFeature):
    """
    A class to calculate the Gross Floor Area (GFA) for buildings based on their area and number of floors.
    """

    def __init__(self):
        super().__init__()
        self.feature_name = 'gross_floor_area'
        self.area_column = 'area'
        self.n_floor_column = 'n_floor'
        self.gross_floor_area_config = self.config.get('features', {}).get(self.feature_name, {})
        self.data_type = self.gross_floor_area_config.get("type", "float")

    def run(self, gdf):
        print(f"Starting the process of {self.feature_name}...")

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate that the required columns exist in the GeoDataFrame
        if not self._validate_required_columns_exist(gdf, [self.area_column, self.n_floor_column]):
            return gdf

        # Retrieve gross_floor_area if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self.calculate_gfa(gdf)

        else:
            # Check for null or invalid values in the gross_floor_area column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, (int, float)))

            # Calculate GFA for invalid rows
            gdf = self.calculate_gfa(gdf, invalid_rows)

        # Format the GFA column
        gdf = self.format_gfa_column(gdf)

        return gdf

    def calculate_gfa(self, gdf, invalid_rows=None):
        """
        Calculates the Gross Floor Area (GFA) based on area and number of floors.
        Ensures the calculation is added to the data as a new column.
        """
        if invalid_rows is None:
            gdf[self.feature_name] = gdf[self.area_column] * gdf[self.n_floor_column]
        else:
            gdf.loc[invalid_rows, self.feature_name] = gdf.loc[invalid_rows, self.area_column] * gdf.loc[
                invalid_rows, self.n_floor_column]
        return gdf

    def format_gfa_column(self, gdf):
        """
        Rounds and ensures the data type of the GFA column is consistent with configuration.
        Helps maintain data integrity.
        """
        gdf[self.feature_name] = (
            gdf[self.feature_name].round(2).astype(self.data_type)
        )
        return gdf
