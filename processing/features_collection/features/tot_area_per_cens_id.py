from processing.features_collection.base_feature import BaseFeature


class TotalAreaPerCensusId(BaseFeature):
    """
    Calculates the total building area for each census section.
    """

    def run(self, gdf, feature_name):
        self.feature_name = feature_name
        self.get_feature_config(self.feature_name)  # Dynamically retrieve and set feature configuration
        print("Starting total area per census ID calculation...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate required columns
        if not self.validate_required_columns_exist(gdf, self.feature_name):
            return gdf

        # Check CRS with projected CRS
        self.check_crs_with_projected_crs(gdf)

        # Handle invalid or missing neighbour IDs
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            # Calculate total area per census ID
            gdf = self.calculate(gdf, invalid_rows.index)

        gdf = self.validate_data(gdf, self.feature_name)

        print("Total area per census ID calculation completed.")  # Essential print 2
        return gdf

    def calculate(self, gdf, rows):
        """Calculates total area per census ID and adds it to the GeoDataFrame."""
        # Remove existing total area column to ensure fresh calculation
        if self.feature_name in gdf.columns:
            gdf.drop(columns=[self.feature_name], inplace=True)

        # Group by census ID and sum the area
        total_area = (
            gdf.groupby(self.required_features[0])[self.required_features[1]]
            .sum()
            .reset_index(name=self.feature_name)
        )

        # Merge the calculated total area back to the original GeoDataFrame
        return gdf.merge(total_area, on=self.required_features[0], how='left')
