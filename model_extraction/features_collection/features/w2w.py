from model_extraction.features_collection.base_feature import BaseFeature


class W2W(BaseFeature):
    """
    A class to assign W2W values to buildings.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = 'w2w'
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})

    def run(self, gdf):
        print("Starting W2W assignment...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Retrieve W2W data if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self.assign_default_w2w_value(gdf)

        print("W2W assignment completed.")  # Essential print 2
        return gdf

    def assign_default_w2w_value(self, gdf):
        """Assigns a default W2W value to the feature column."""
        gdf[self.feature_name] = 0.5
        return gdf
