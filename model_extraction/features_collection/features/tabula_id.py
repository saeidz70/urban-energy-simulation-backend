from model_extraction.features_collection.base_feature import BaseFeature


class TabulaID(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = "tabula_id"
        self.year_of_construction_column = "year_of_construction"
        self.tabula_type_column = "tabula_type"
        self.feature_config = self.config.get("features", {}).get(self.feature_name, {})
        self.tabula_mapping = self.feature_config.get("tabula_mapping", {})

    def run(self, gdf):
        print("Starting Tabula ID assignment...")  # Essential print 1

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate that the required columns exist in the GeoDataFrame
        if not self._validate_required_columns_exist(gdf, [self.year_of_construction_column, self.tabula_type_column]):
            return gdf

        # Retrieve tabula_id if it is null, some rows are null, or data type is wrong
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Validate the data type of the feature in the DataFrame
        gdf = self.validate_data(gdf, self.feature_name)

        # Check if data returned is None or null
        if gdf[self.feature_name].isnull().all():
            gdf = self.assign_tabula_ids(gdf)

        else:
            # Check for null or invalid values in the tabula_id column
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, str))

            # Assign Tabula IDs for invalid rows
            gdf = self.assign_tabula_ids(gdf, invalid_rows)

        print("Tabula ID assignment completed.")  # Essential print 2
        return gdf

    def determine_tabula_id(self, year, tabula_type):
        """Determine the Tabula ID based on year and tabula type."""
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

    def assign_tabula_ids(self, gdf, invalid_rows=None):
        """Assign Tabula IDs to buildings based on year and type."""
        if invalid_rows is None:
            gdf[self.feature_name] = gdf.apply(
                lambda row: self.determine_tabula_id(
                    row[self.year_of_construction_column],
                    row[self.tabula_type_column]
                ),
                axis=1
            )
        else:
            gdf.loc[invalid_rows, self.feature_name] = gdf.loc[invalid_rows].apply(
                lambda row: self.determine_tabula_id(
                    row[self.year_of_construction_column],
                    row[self.tabula_type_column]
                ),
                axis=1
            )
        return gdf
