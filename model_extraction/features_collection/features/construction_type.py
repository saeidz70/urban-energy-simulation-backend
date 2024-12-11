from model_extraction.features_collection.base_feature import BaseFeature

class ConstructionType(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = "construction_type"
        self.year_of_construction_column = "year_of_construction"
        # Dynamically retrieve and set feature configuration
        self.get_feature_config(self.feature_name)

    def run(self, gdf):
        """
        Main method to assign construction types to the GeoDataFrame.
        """
        print("Starting construction type assignment...")

        # Process feature
        gdf = self.process_feature(gdf, self.feature_name)

        # Handle invalid or missing construction types
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            self.assign_construction_types(gdf, invalid_rows.index)

        print("Construction type assignment completed.")
        return gdf

    def assign_construction_types(self, gdf, rows):
        """
        Assign construction types to specific rows based on year of construction.
        """
        gdf.loc[rows, self.feature_name] = gdf.loc[rows].apply(
            lambda row: self.determine_construction_type(
                row.get(self.year_of_construction_column)
            ),
            axis=1
        )

    def determine_construction_type(self, year):
        """
        Determine the construction type based on the year of construction.
        """
        try:
            year = int(year)
            for period, construction_type in self.construction_period.items():
                start_year, end_year = map(int, period.split('-'))
                if start_year <= year <= end_year:
                    return construction_type
        except (ValueError, TypeError):
            return None
