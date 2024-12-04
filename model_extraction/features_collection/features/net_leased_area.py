from model_extraction.features_collection.base_feature import BaseFeature


class NetLeasedArea(BaseFeature):
    """
    Calculates Net Leased Area (NLA) for buildings.
    """

    def __init__(self):
        super().__init__()
        self.feature_name = 'net_leased_area'
        self.gross_floor_area_column = 'gross_floor_area'
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})
        self.data_type = self.feature_config.get("type", "float")

    def run(self, gdf):
        print("Running NetLeasedAreaCalculator feature calculation...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate that the required columns exist in the GeoDataFrame
        if not self._validate_required_columns_exist(gdf, [self.gross_floor_area_column]):
            return gdf

        # Retrieve net_leased_area if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self.calculate_nla(gdf)

        else:
            # Check for null or invalid values in the net_leased_area column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, (int, float)))

            # Calculate NLA for invalid rows
            gdf = self.calculate_nla(gdf, invalid_rows)

        # Format the NLA column
        gdf = self.format_nla_column(gdf)

        print("NetLeasedAreaCalculator feature calculation completed.")  # Essential print 2
        return gdf

    def calculate_nla(self, gdf, invalid_rows=None):
        """
        Calculates the Net Leased Area (NLA) based on Gross Floor Area (GFA).
        Ensures the calculation is added to the data as a new column.
        """
        if invalid_rows is None:
            gdf[self.feature_name] = gdf[self.gross_floor_area_column] * 0.8
        else:
            gdf.loc[invalid_rows, self.feature_name] = gdf.loc[invalid_rows, self.gross_floor_area_column] * 0.8
        return gdf

    def format_nla_column(self, gdf):
        """
        Rounds and ensures the data type of the NLA column is consistent with configuration.
        Helps maintain data integrity.
        """
        gdf[self.feature_name] = (
            gdf[self.feature_name].round(2).astype(self.data_type)
        )
        return gdf
