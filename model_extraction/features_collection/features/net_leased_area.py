from model_extraction.features_collection.base_feature import BaseFeature

class NetLeasedArea(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'net_leased_area'
        self.gross_floor_area_column = 'gross_floor_area'
        # Dynamically retrieve and set feature configuration
        self.get_feature_config(self.feature_name)

    def run(self, gdf):
        """
        Main method to calculate and assign Net Leased Area (NLA) to the GeoDataFrame.
        """
        print(f"Starting the process of {self.feature_name}...")

        # Process feature
        gdf = self.process_feature(gdf, self.feature_name)

        # Handle invalid or missing NLA values
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            self.calculate_nla(gdf, invalid_rows.index)

        print(f"{self.feature_name} assignment completed.")
        return gdf

    def calculate_nla(self, gdf, rows):
        """
        Calculate the Net Leased Area (NLA) for specific rows.
        """
        gdf.loc[rows, self.feature_name] = gdf.loc[rows, self.gross_floor_area_column] * 0.8
        gdf[self.feature_name] = gdf[self.feature_name].round(2).astype(float)
