from model_extraction.features_collection.base_feature import BaseFeature

class W2W(BaseFeature):
    """
    Assigns and validates W2W values in the GeoDataFrame.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = 'w2w'
        self.get_feature_config(self.feature_name)  # Dynamically retrieve and set feature configuration

    def run(self, gdf):
        """
        Main method to process and assign W2W values.
        """
        print("Starting W2W value assignment...")

        # Step 1: Process and initialize the feature column
        gdf = self.process_feature(gdf, self.feature_name)

        # Step 2: Handle invalid or missing W2W values
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            print(f"Assigning W2W values to {len(invalid_rows)} rows...")
            gdf = self._assign_default_w2w_value(gdf, invalid_rows.index)

        # Step 3: Final validation
        gdf = self.validate_data(gdf, self.feature_name)

        print("W2W value assignment completed.")
        return gdf

    def _assign_default_w2w_value(self, gdf, rows):
        """
        Assign default W2W values to specific rows.
        """
        gdf.loc[rows, self.feature_name] = 0.5
        return gdf