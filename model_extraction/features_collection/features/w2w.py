from model_extraction.features_collection.base_feature import BaseFeature

class W2W(BaseFeature):
    """
    Assigns and validates W2W values in the GeoDataFrame.
    """

    def calculate(self, gdf, rows):
        """
        Assign default W2W values to specific rows.
        """
        gdf.loc[rows, self.feature_name] = 0.5

        gdf = self.validate_data(gdf, self.feature_name)

        print("W2W value assignment completed.")
        return gdf