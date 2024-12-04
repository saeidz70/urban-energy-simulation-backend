from model_extraction.features_collection.base_feature import BaseFeature


class CensusId(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'census_id'
        self.census_config = self.config.get('features', {}).get(self.feature_name, {})
        self.census_id_column = self.census_config.get('census_id_column', 'SEZ2011')

    def run(self, gdf):
        # Validate that the required census_id_column exists in the GeoDataFrame
        self._validate_required_columns_exist(gdf, [self.census_id_column])

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Assign the values from the census_id_column to the feature column
        gdf[self.feature_name] = gdf[self.census_id_column]

        return gdf
