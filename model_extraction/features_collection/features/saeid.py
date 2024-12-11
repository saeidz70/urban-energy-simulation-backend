from random import random

from model_extraction.features_collection.base_feature import BaseFeature


class Saeid(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'saeid'
        self.n_family_column = 'n_family'
        self.saeid_config = self.config.get("features", {}).get(self.feature_name, {})
        self.min_saeid = self.saeid_config.get("min", 0)
        self.max_saeid = self.saeid_config.get("max", 100)
        self.data_type = self.saeid_config.get("type", "int")

    def run(self, gdf):
        # Starting the saeid calculation
        print(f"Calculating {self.feature_name} feature started...")

        # Initialize the feature column
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        if not self.validate_required_columns_exist(gdf, self.n_family_column):
            return gdf

        gdf = self.retrieve_data_from_sources(gdf, self.feature_name)

        gdf = self.validate_data(gdf, self.feature_name)

        if gdf[self.feature_name].isnull().any() or not gdf[self.feature_name].dtype == self.data_type:
            gdf = self._calculate_saeid(gdf)

        gdf = self.filter_data(gdf, self.feature_name, self.min_saeid, self.max_saeid, self.data_type)
        return gdf

    def _calculate_saeid(self, gdf):
        gdf[self.feature_name] = random(self.min_saeid, self.max_saeid)
        return gdf
