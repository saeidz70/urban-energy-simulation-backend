import os

import geopandas as gpd
import osmnx as ox
from shapely.geometry import Polygon


class OSMBuildingExtractor:
    def __init__(self, config):
        self.boundary_geojson_path = config['selected_boundaries']
        self.output_file_path = config['osm_building_path']
        self.default_crs = f"EPSG:{config.get('DEFAULT_CRS', 4326)}"
        self.boundary_polygon = self.load_boundary()

    def load_boundary(self):
        """Load the boundary GeoJSON and combine geometries into a single polygon."""
        try:
            gdf = gpd.read_file(self.boundary_geojson_path)
            if gdf.empty:
                raise ValueError("Boundary GeoJSON file is empty.")
            gdf = gdf[gdf.geometry.is_valid]  # Filter invalid geometries
            combined_boundary = gdf.unary_union
            if not isinstance(combined_boundary, Polygon):
                raise ValueError("Combined boundary is not a valid polygon.")
            print("Boundary loaded and combined successfully.")
            return combined_boundary
        except Exception as e:
            raise RuntimeError(f"Error loading boundary file: {e}")

    def extract_buildings(self):
        """Extract buildings from OSM using the boundary polygon."""
        try:
            print("Extracting buildings from OSM...")
            buildings = ox.features_from_polygon(self.boundary_polygon, tags={'building': True})
            if buildings.empty:
                raise ValueError("No buildings found in the specified boundary.")
            print(f"Extracted {len(buildings)} buildings from OSM.")
            return buildings
        except Exception as e:
            raise RuntimeError(f"Error extracting buildings from OSM: {e}")

    def filter_columns(self, buildings):
        """Filter columns to include only required fields."""
        try:
            # Required columns
            required_columns = ['nodes', 'building', 'geometry']
            available_columns = [col for col in required_columns if col in buildings.columns]
            if 'geometry' not in available_columns:
                raise ValueError("The 'geometry' column is missing in the buildings data.")
            filtered_buildings = buildings[available_columns].copy()
            print("Filtered columns in the buildings data.")
            return filtered_buildings
        except Exception as e:
            raise RuntimeError(f"Error filtering building columns: {e}")

    def save_buildings(self, buildings):
        """Save the filtered buildings GeoDataFrame to a GeoJSON file."""
        try:
            output_dir = os.path.dirname(self.output_file_path)
            os.makedirs(output_dir, exist_ok=True)

            print("Sanitizing data before saving...")
            filtered_buildings = self.filter_columns(buildings)

            # Sanitize data: convert unsupported types to strings
            for column in filtered_buildings.columns:
                if filtered_buildings[column].dtype == 'object':
                    filtered_buildings[column] = filtered_buildings[column].apply(
                        lambda x: str(x) if isinstance(x, (list, dict)) else x
                    )

            # Ensure CRS consistency
            if filtered_buildings.crs is None or filtered_buildings.crs.to_string() != self.default_crs:
                print(f"Reprojecting data to {self.default_crs}.")
                filtered_buildings = filtered_buildings.to_crs(self.default_crs)

            # Save to GeoJSON
            filtered_buildings.to_file(self.output_file_path, driver='GeoJSON')
            print(f"Building data saved to {self.output_file_path}.")
        except Exception as e:
            raise RuntimeError(f"Error saving building data: {e}")
