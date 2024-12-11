from model_extraction.features_collection.base_feature import BaseFeature


class Usage(BaseFeature):
    """
    Processes and filters building usage data based on allowed usage types.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = "usage"
        self.census_id_column = "census_id"
        self.default_usage = "residential"  # Default fallback usage
        self.get_feature_config(self.feature_name)  # Dynamically set configuration for the feature

    def run(self, gdf):
        """
        Main method to process and assign usage data.
        """
        print(f"Starting the process to assign '{self.feature_name}'...")

        # Step 1: Process feature
        gdf = self.process_feature(gdf, self.feature_name)

        # Step 2: Handle missing or invalid usage values
        gdf = self._handle_missing_usage(gdf)

        # Step 3: Filter and normalize usage values
        gdf = self._filter_usage_values(gdf)

        print("Usage assignment completed.")
        return gdf

    def _handle_missing_usage(self, gdf):
        """
        Handle invalid or missing usage values by fetching data from OSM and census.
        """
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)

        if not invalid_rows.empty:
            print("Fetching usage data from OSM...")
            osm_data = self._get_osm_data(self.feature_name, gdf)
            gdf = self.update_missing_values(gdf, osm_data, self.feature_name)

        # Replace "yes" values with the default usage type
        gdf.loc[gdf[self.feature_name] == "yes", self.feature_name] = self.default_usage

        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)

        if not invalid_rows.empty:
            print("Calculating usage data from census information...")
            gdf = self._calculate_usage(gdf, invalid_rows.index)

        return gdf

    def _calculate_usage(self, gdf, rows):
        """
        Calculate usage values using census data for specific rows.
        """
        usage_mapping = {}

        # Group by census_id and calculate predominant usage for each group
        for census_id, group in gdf.loc[rows].groupby(self.census_id_column):
            usage_mapping[census_id] = self._calculate_group_usage(group)

        # Assign calculated usage back to the GeoDataFrame
        gdf.loc[rows, self.feature_name] = gdf.loc[rows, self.census_id_column].map(
            usage_mapping).fillna(self.default_usage)

        return gdf

    def _calculate_group_usage(self, group):
        """
        Determine the predominant usage type for a group of buildings based on census data.
        """
        if not all(col in group.columns for col in self.census_usage.keys()):
            return self.default_usage  # Default if required columns are missing

        # Count building types using census columns
        building_counts = {col: group[col].astype(int).sum() for col in self.census_usage.keys()}
        total_count = sum(building_counts.values())

        if total_count == 0:
            return self.default_usage  # Default if no data available

        # Compare counts of residential (E3) and non-residential (E4)
        return "residential" if building_counts.get("E3", 0) >= building_counts.get("E4", 0) else "non residential"

    def _filter_usage_values(self, gdf):
        """
        Filter and normalize usage values to ensure they are within allowed usage types.
        """
        gdf = self.validate_data(gdf, self.feature_name)

        # Retain rows with valid usage types
        valid_gdf = gdf[gdf[self.feature_name].isin(self.allowed_usages)].copy()

        # Log the number of filtered rows
        num_invalid = len(gdf) - len(valid_gdf)
        if num_invalid > 0:
            print(f"Filtered out {num_invalid} rows with invalid '{self.feature_name}' values.")

        return valid_gdf
