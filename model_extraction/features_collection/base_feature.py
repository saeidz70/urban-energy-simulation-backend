import os
import warnings

import geopandas as gpd

from model_extraction.data_manager.utility import UtilityProcess


class BaseFeature(UtilityProcess):
    def __init__(self):
        super().__init__()
        self.projected_crs = self.config.get('PROJECTED_CRS', 'EPSG:32632')
        self.default_crs = self.config.get('DEFAULT_CRS', 4326)

    def check_crs_with_default_crs(self, gdf):
        if gdf.crs is None:
            print("No CRS found in building data; setting to default CRS.")
            gdf.set_crs(epsg=self.default_crs, inplace=True)
        elif gdf.crs.to_string() != f"EPSG:{self.default_crs}":
            print(f"CRS mismatch. Reprojecting to EPSG:{self.default_crs}.")
            gdf = gdf.to_crs(epsg=self.default_crs)
        return gdf

    def check_crs_with_projected_crs(self, gdf):
        if gdf.crs is None:
            print("No CRS found in building data; setting to projected CRS.")
            gdf.set_crs(epsg=self.projected_crs, inplace=True)
        elif gdf.crs.to_string() != f"EPSG:{self.projected_crs}":
            print(f"CRS mismatch. Reprojecting to EPSG:{self.projected_crs}.")
            gdf = gdf.to_crs(epsg=self.projected_crs)
        return gdf

    def change_crs_to_default(self, gdf):
        print(f"Changing CRS to default CRS: EPSG:{self.default_crs}.")
        return gdf.to_crs(epsg=self.default_crs)

    def change_crs_to_projection(self, gdf):
        print(f"Changing CRS to projected CRS: EPSG:{self.projected_crs}.")
        return gdf.to_crs(epsg=self.projected_crs)

    def load_geojson(self, file_path):
        """Load GeoJSON file and check validity."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"GeoJSON file not found: {file_path}")
        gdf = gpd.read_file(file_path)
        if 'geometry' not in gdf.columns or gdf.empty:
            raise ValueError("The input GeoJSON file does not contain valid geometry data.")
        return gdf

    def save_geojson(self, gdf, file_path):
        """Save the GeoDataFrame to a GeoJSON file."""
        gdf.to_file(file_path, driver='GeoJSON')
        print(f"Data saved to {file_path}.")

    def initialize_feature_column(self, gdf, feature_name):
        """Initialize a feature column if it does not exist."""
        if feature_name not in gdf.columns:
            print(f"Initializing {feature_name} column.")
            gdf[feature_name] = None
        return gdf

    def filter_data(self, gdf, feature_name, min_value, max_value, data_type):
        """Filter data based on feature-specific criteria."""
        filtered_gdf = gdf.loc[
            (gdf[feature_name] >= min_value) & (gdf[feature_name] <= max_value)
            ].copy()
        filtered_gdf[feature_name] = filtered_gdf[feature_name].astype(data_type)
        return filtered_gdf

    def _validate_required_columns_exist(self, gdf, columns):
        """Ensure the specified columns exist in the GeoDataFrame."""
        missing_columns = [col for col in columns if col not in gdf.columns]
        if missing_columns:
            warnings.warn(f"Missing required columns: {', '.join(missing_columns)}")
            return False
        return True
