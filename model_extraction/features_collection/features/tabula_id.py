from model_extraction.features_collection.base_feature import BaseFeature


class TabulaID(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = "tabula_id"
        self.year_of_construction_column = "year_of_construction"
        self.tabula_type_column = "tabula_type"
        # Dynamically retrieve and set feature configuration
        self.get_feature_config(self.feature_name)

    def run(self, gdf):
        """
        Main method to assign Tabula IDs to the GeoDataFrame.
        """
        print("Starting Tabula ID assignment...")

        # Process feature
        gdf = self.process_feature(gdf, self.feature_name)

        # Handle invalid or missing Tabula IDs
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        if not invalid_rows.empty:
            gdf = self.assign_tabula_ids(gdf, invalid_rows.index)

        gdf = self.validate_data(gdf, self.feature_name)

        print("Tabula ID assignment completed.")
        return gdf

    def assign_tabula_ids(self, gdf, rows):
        """
        Assign Tabula IDs to specific rows based on year and type.
        """
        gdf.loc[rows, self.feature_name] = gdf.loc[rows].apply(
            lambda row: self.determine_tabula_id(
                row.get(self.year_of_construction_column),
                row.get(self.tabula_type_column)
            ),
            axis=1
        )
        return gdf

    def determine_tabula_id(self, year, tabula_type):
        """
        Determine the Tabula ID based on year and tabula type.
        """
        try:
            year = int(year)
            for period, mapping in self.tabula_mapping.items():
                if "+" in period and year >= int(period.split("+")[0]):
                    return mapping.get(tabula_type)
                elif "-" in period:
                    start, end = map(int, period.split("-"))
                    if start <= year <= end:
                        return mapping.get(tabula_type)
        except (ValueError, TypeError):
            return None