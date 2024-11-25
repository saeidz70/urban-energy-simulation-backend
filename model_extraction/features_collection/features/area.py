import os

import geopandas as gpd

from config.config import Config


class BuildingAreaCalculator(Config):
    """Class to calculate and filter building areas from a GeoJSON file."""

    def __init__(self):
        super().__init__()
        self.buildings_geojson_path = self.config['building_path']
        self.projected_crs = self.config.get('PROJECTED_CRS', 'EPSG:32632')  # Default CRS for area calculations
        self.feature_name = 'area'
        self.area_config = self.config.get("features", {}).get(self.feature_name, {})
        self.min_area = self.area_config.get("min", 50)  # Default minimum area (m²)
        self.max_area = self.area_config.get("max", 1000000)  # Default maximum area (m²)
        self.data_type = self.area_config.get("type", "float")  # Default data type for 'area' column
        self.buildings_gdf = self._load_geojson(self.buildings_geojson_path)

    def _load_geojson(self, file_path):
        """Load GeoJSON file and check validity."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"GeoJSON file not found: {file_path}")
        gdf = gpd.read_file(file_path)
        if 'geometry' not in gdf.columns or gdf.empty:
            raise ValueError("The input GeoJSON file does not contain valid geometry data.")
        return gdf

    def _calculate_areas(self, gdf):
        """Calculate the area of buildings after projecting to the configured CRS."""
        gdf_projected = gdf.to_crs(self.projected_crs)
        gdf_projected[self.feature_name] = gdf_projected.geometry.area.round(
            2)  # Calculate area and round to 2 decimals
        return gdf_projected

    def _filter_buildings(self, gdf):
        """Filter buildings based on area limits."""
        filtered_gdf = gdf.loc[
            (gdf[self.feature_name] >= self.min_area) & (gdf[self.feature_name] <= self.max_area)
            ].copy()  # Create an explicit copy to avoid SettingWithCopyWarning
        filtered_gdf[self.feature_name] = filtered_gdf[self.feature_name].astype(self.data_type)
        return filtered_gdf

    def _save_geojson(self, gdf):
        """Save the filtered GeoDataFrame to the same file as input."""
        gdf.to_file(self.buildings_geojson_path, driver='GeoJSON')
        print(f"Filtered building data saved to {self.buildings_geojson_path}.")

    def process_buildings(self):
        """Run the full processing pipeline."""
        print("Calculating building areas...")
        buildings_with_area = self._calculate_areas(self.buildings_gdf)

        print(f"Filtering buildings within area limits: {self.min_area} - {self.max_area} m²...")
        filtered_buildings = self._filter_buildings(buildings_with_area)

        print("Saving filtered buildings...")
        self._save_geojson(filtered_buildings)
        return filtered_buildings
