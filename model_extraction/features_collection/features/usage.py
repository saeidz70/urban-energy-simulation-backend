from model_extraction.features_collection.base_feature import BaseFeature


class Usage(BaseFeature):
    """
    Processes and filters building usage data based on allowed usage types.
    """
    def __init__(self):
        super().__init__()
        self.feature_name = 'usage'
        self.census_id_column = 'census_id'
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})
        self.allowed_usages = {
            usage.lower() for usage in self.feature_config.get('allowed_values', ["residential", "non residential"])
        }
        self.census_usage = self.feature_config.get('census_usage', {"E3": "residential", "E4": "non residential"})
        self.census_columns = list(self.census_usage.keys())

    def run(self, gdf):
        print(f"Starting the process to assign {self.feature_name}...")

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate required columns
        if not self._validate_required_columns_exist(gdf, [self.census_id_column]):
            return gdf

        # Retrieve usage data if null or invalid
        gdf = self.retrieve_data_from_sources(self.feature_name, gdf)

        # Handle missing or invalid usage values
        if gdf[self.feature_name].isnull().all():
            gdf = self._get_osm_data(self.feature_name, gdf)
            if gdf[self.feature_name].isnull().all():
                gdf = self._calculate_usage(gdf)
        else:
            invalid_rows = gdf[self.feature_name].isnull() | gdf[self.feature_name].apply(
                lambda x: not isinstance(x, str))
            gdf = self._calculate_usage(gdf, invalid_rows)

        # Filter usage values based on allowed types
        gdf = self._filter_usage_values(gdf)

        print("Usage assignment completed.")
        return gdf

    def _calculate_usage(self, gdf, invalid_rows=None):
        """
        Calculate usage values using census data for missing or invalid rows.
        """
        if invalid_rows is None:
            invalid_rows = gdf[self.feature_name].isnull()

        if invalid_rows.any():
            print(f"Calculating {self.feature_name} values from census data.")
            usage_mapping = {
                census_id: self._calculate_group_usage(group)
                for census_id, group in gdf.groupby(self.census_id_column)
            }

            # Assign calculated usage to invalid rows
            gdf.loc[invalid_rows, self.feature_name] = gdf.loc[invalid_rows, self.census_id_column].map(
                usage_mapping).fillna('residential')

        return gdf

    def _calculate_group_usage(self, group):
        """
        Determine the predominant usage type for a group of buildings.
        """
        building_counts = {col: group[col].sum() for col in self.census_columns if col in group.columns}
        total_count = sum(building_counts.values())

        if total_count == 0:
            return 'residential'  # Default usage if no census data available

        # Compare residential and non-residential counts
        if building_counts.get('E3', 0) >= building_counts.get('E4', 0):
            return 'residential'
        return 'non residential'

    def _filter_usage_values(self, gdf):
        """
        Ensure usage values are within the allowed usage types.
        """
        print(f"Filtering {self.feature_name} values based on allowed usage types.")

        # Normalize usage values
        gdf.loc[:, self.feature_name] = gdf[self.feature_name].apply(
            lambda x: x.strip().lower() if isinstance(x, str) else None
        )

        # Filter by allowed usage and create a copy to avoid warnings
        gdf = gdf[gdf[self.feature_name].isin(self.allowed_usages)].copy()
        return gdf
