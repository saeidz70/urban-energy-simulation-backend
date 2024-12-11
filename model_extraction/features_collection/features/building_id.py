import uuid

from model_extraction.features_collection.base_feature import BaseFeature


class BuildingID(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'building_id'
        # Dynamically retrieve and set feature configuration
        self.get_feature_config(self.feature_name)

    def run(self, gdf):
        if gdf is None:
            raise ValueError("The input GeoDataFrame (gdf) is None.")

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        initial_id_count = gdf[self.feature_name].notnull().sum()
        print(f"Number of building IDs before: {initial_id_count}")

        # Assign unique IDs to buildings that do not have one
        gdf = self.assign_unique_id(gdf)

        # Print the number of IDs added
        final_id_count = gdf[self.feature_name].notnull().sum()
        ids_added = final_id_count - initial_id_count
        print(f"Number of building IDs added: {ids_added}")

        return gdf

    def assign_unique_id(self, gdf):
        # Assign UUIDs only to rows where building_id is NaN
        gdf.loc[gdf[self.feature_name].isnull(), self.feature_name] = [
            str(uuid.uuid4()) for _ in range(gdf[self.feature_name].isnull().sum())]

        return gdf
