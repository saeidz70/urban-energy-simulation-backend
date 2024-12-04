from model_extraction.features_collection.base_feature import BaseFeature


class Area(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'area'
        self.area_config = self.config.get("features", {}).get(self.feature_name, {})
        self.min_area = self.area_config.get("min", 50)
        self.max_area = self.area_config.get("max", 1000000)
        self.data_type = self.area_config.get("type", "float")

    def run(self, gdf):
        # Starting the area calculation
        print(f"Calculating {self.feature_name} feature started...")

        # Initialize the feature column
        gdf = self.initialize_feature_column(gdf, self.feature_name)

        gdf = self.check_crs_with_projected_crs(gdf)

        if gdf[self.feature_name].isnull().any() or not gdf[self.feature_name].dtype == self.data_type:
            gdf = self._calculate_areas(gdf)

        gdf = self.filter_data(gdf, self.feature_name, self.min_area, self.max_area, self.data_type)
        return gdf

    def _calculate_areas(self, gdf):
        gdf[self.feature_name] = gdf.geometry.area.round(2)
        return gdf
