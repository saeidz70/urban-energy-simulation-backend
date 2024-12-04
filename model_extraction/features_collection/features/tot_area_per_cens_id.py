from model_extraction.features_collection.base_feature import BaseFeature


class TotalAreaPerCensusId(BaseFeature):
    """
    Calculates the total building area for each census section.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = "tot_area_per_cens_id"
        self.census_id_column = "census_id"
        self.area_column = "area"
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})
        self.data_type = self.feature_config.get('type', 'float')

    def run(self, gdf):
        print("Starting total area per census ID calculation...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate that the required columns exist in the GeoDataFrame
        if not self._validate_required_columns_exist(gdf, [self.census_id_column, self.area_column]):
            return gdf

        # Check CRS with projected CRS
        self.check_crs_with_projected_crs(gdf)

        # Calculate total area per census ID
        gdf = self.calculate_total_area(gdf)

        print("Total area per census ID calculation completed.")  # Essential print 2
        return gdf

    def calculate_total_area(self, gdf):
        """Calculates total area per census ID and adds it to the GeoDataFrame."""
        # Remove existing total area column to ensure fresh calculation
        if self.feature_name in gdf.columns:
            gdf.drop(columns=[self.feature_name], inplace=True)

        # Group by census ID and sum the area
        total_area = (
            gdf.groupby(self.census_id_column)[self.area_column]
            .sum()
            .reset_index(name=self.feature_name)
        )

        # Merge the calculated total area back to the original GeoDataFrame
        return gdf.merge(total_area, on=self.census_id_column, how='left')
