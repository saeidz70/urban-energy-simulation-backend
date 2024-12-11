from model_extraction.features_collection.base_feature import BaseFeature


class CensusId(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'census_id'
        # Dynamically retrieve and set feature configuration
        self.get_feature_config(self.feature_name)

    def run(self, gdf):
        print("Starting Census ID assignment...")

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        # Validate that the required census_id_column exists in the GeoDataFrame
        self.validate_required_columns_exist(gdf, self.feature_name)

        # Assign census IDs
        gdf = self.assign_census_id(gdf)

        print("Census ID assignment completed.")
        return gdf

    def assign_census_id(self, gdf):
        if self.feature_name not in gdf.columns or gdf[self.feature_name].isnull().any():
            # Assign the values from the census_id_column to the feature column
            gdf[self.feature_name] = gdf[self.census_id_column]
        return gdf
