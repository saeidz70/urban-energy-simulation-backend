from processing.features_collection.base_feature import BaseFeature

class NetLeasedArea(BaseFeature):

    def calculate(self, gdf, rows):
        """
        Calculate the Net Leased Area (NLA) for specific rows.
        """
        gdf.loc[rows, self.feature_name] = gdf.loc[rows, self.required_features[0]] * 0.8

        # Explicitly apply round function using lambda
        gdf[self.feature_name] = gdf[self.feature_name].apply(lambda x: round(x, 2))

        self.validate_data(gdf, self.feature_name)
        print(f"Net Leased Area calculation completed.")
        return gdf
