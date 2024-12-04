import uuid

from model_extraction.features_collection.base_feature import BaseFeature


class BuildingID(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'building_id'
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})

    def run(self, gdf):
        if gdf is None:
            raise ValueError("The input GeoDataFrame (gdf) is None.")

        initial_id_count = gdf[self.feature_name].notnull().sum() if self.feature_name in gdf.columns else 0
        print(f"Number of building IDs before: {initial_id_count}")

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)
        # Assign unique IDs to buildings that do not have one
        gdf = self.assign_unique_id(gdf)

        # Print the number of IDs added
        final_id_count = gdf[self.feature_name].notnull().sum()
        ids_added = final_id_count - initial_id_count
        print(f"Number of building IDs added: {ids_added}")

        return gdf

    def assign_unique_id(self, gdf):
        if self.feature_name not in gdf.columns or gdf[self.feature_name].isnull().any():
            gdf[self.feature_name] = [str(uuid.uuid4()) for _ in range(len(gdf))]
        return gdf
