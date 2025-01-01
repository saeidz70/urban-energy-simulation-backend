from processing.features_collection.base_feature import BaseFeature


class CensusId(BaseFeature):

    def run(self, gdf, feature_name):
        print("Starting Census ID assignment...")

        self.feature_name = feature_name
        # Dynamically retrieve and set feature configuration
        self.get_feature_config(self.feature_name)

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate that the required census_id_column exists in the GeoDataFrame
        self.validate_required_columns_exist(gdf, self.feature_name)

        # Handle invalid or missing Tabula IDs
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        print(f"Invalid rows count: {len(invalid_rows)} for {self.feature_name}")
        if not invalid_rows.empty:
            gdf = self.calculate(gdf, invalid_rows.index)

        print("Census ID assignment completed.")
        return gdf

    def calculate(self, gdf, rows):
        if self.feature_name not in gdf.columns or gdf[self.feature_name].isnull().any():
            # Assign the values from the census_id_column to the feature column
            gdf[self.feature_name] = gdf[self.census_id_column]
        return gdf
