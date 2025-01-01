from processing.features_collection.base_feature import BaseFeature

class NetLeasedArea(BaseFeature):

    def calculate(self, gdf, rows):
        """
        Calculate the Net Leased Area (NLA) for specific rows.
        """
        gdf.loc[rows, self.feature_name] = gdf.loc[rows, self.required_features[0]] * 0.8
        gdf[self.feature_name] = gdf[self.feature_name].round(2).astype(float)

        self.validate_data(gdf, self.feature_name)
        return gdf
