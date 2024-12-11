from model_extraction.features_collection.base_feature import BaseFeature

class GrossFloorArea(BaseFeature):
    """
    Class to calculate and assign Gross Floor Area (GFA) for buildings.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = 'gross_floor_area'
        self.area_column = 'area'
        self.n_floor_column = 'n_floor'
        self.get_feature_config(self.feature_name)  # Dynamically retrieve and set feature configuration

    def run(self, gdf):
        """
        Main method to calculate and assign GFA to the GeoDataFrame.
        """
        print(f"Starting the process of {self.feature_name}...")

        # Process feature
        gdf = self.process_feature(gdf, self.feature_name)

        # Handle invalid or missing GFA values
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            gdf = self.calculate_gfa(gdf, invalid_rows.index)

        gdf = self.validate_data(gdf, self.feature_name)

        print(f"{self.feature_name} assignment completed.")
        return gdf

    def calculate_gfa(self, gdf, rows):
        """
        Calculate the GFA for specific rows without overwriting existing values.
        """
        # Calculate GFA only for the specified rows
        gdf.loc[rows, self.feature_name] = (
                gdf.loc[rows, self.area_column] * gdf.loc[rows, self.n_floor_column]
        ).round(2).astype(float)
        return gdf
