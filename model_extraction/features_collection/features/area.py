from model_extraction.features_collection.base_feature import BaseFeature


class Area(BaseFeature):
    # Dynamically retrieve and set feature configuration

    def run(self, gdf, feature_name):
        """
        Main method to calculate and validate the area feature.
        """
        self.feature_name = feature_name
        self.get_feature_config(self.feature_name)

        print(f"Calculating '{self.feature_name}' feature started...")

        # Initialize the feature column if not present
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Ensure GeoDataFrame uses the projected CRS for accurate area calculations
        gdf = self.check_crs_with_projected_crs(gdf)

        # Handle invalid or missing
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        print(f"Invalid rows count: {len(invalid_rows)} for {self.feature_name}")
        if not invalid_rows.empty:
            gdf = self.calculate(gdf, invalid_rows.index)

        # Validate and filter the feature data
        gdf = self.validate_data(gdf, self.feature_name)

        gdf = self.filter_data(
            gdf, self.feature_name, min_value=self.min, max_value=self.max, data_type=self.type
        )

        print(f"'{self.feature_name}' calculation completed.")
        return gdf

    def calculate(self, gdf, rows):
        """
        Calculate areas for rows with missing values based on geometry.
        """
        # Identify rows with missing values in the area column
        missing_area_rows = rows

        # Calculate and assign area only for those rows
        gdf.loc[missing_area_rows, self.feature_name] = gdf.loc[missing_area_rows].geometry.area.round(2)
        return gdf
