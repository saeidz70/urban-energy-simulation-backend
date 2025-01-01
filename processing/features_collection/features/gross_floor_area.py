from processing.features_collection.base_feature import BaseFeature

class GrossFloorArea(BaseFeature):
    """
    Class to calculate and assign Gross Floor Area (GFA) for buildings.
    """

    def calculate(self, gdf, rows):
        """
        Calculate the GFA for specific rows without overwriting existing values.
        """
        gdf.loc[rows, self.feature_name] = (
                gdf.loc[rows, self.required_features[0]] * gdf.loc[rows, self.required_features[1]]
        ).round(2).astype(float)
        return gdf
