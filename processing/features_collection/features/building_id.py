import uuid

from processing.features_collection.base_feature import BaseFeature


class BuildingID(BaseFeature):

    def run(self, gdf, feature_name):
        self.feature_name = feature_name
        # Dynamically retrieve and set feature configuration
        self.get_feature_config(self.feature_name)

        if gdf is None:
            raise ValueError("The input GeoDataFrame (gdf) is None.")

        # Initialize the feature column if it does not exist
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        initial_id_count = gdf[self.feature_name].notnull().sum()
        print(f"Number of building IDs before: {initial_id_count}")

        # Handle invalid or missing Tabula IDs
        invalid_rows = self.check_invalid_rows(gdf, self.feature_name)
        print(f"Invalid rows count: {len(invalid_rows)} for {self.feature_name}")
        if not invalid_rows.empty:
            gdf = self.calculate(gdf, invalid_rows.index)

        # Print the number of IDs added
        final_id_count = gdf[self.feature_name].notnull().sum()
        ids_added = final_id_count - initial_id_count
        print(f"Number of building IDs added: {ids_added}")

        return gdf

    def calculate(self, gdf, rows):
        # Assign UUIDs only to rows where building_id is NaN
        gdf.loc[gdf[self.feature_name].isnull(), self.feature_name] = [
            str(uuid.uuid4()) for _ in range(gdf[self.feature_name].isnull().sum())]

        return gdf
