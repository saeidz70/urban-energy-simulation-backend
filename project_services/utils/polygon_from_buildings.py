import os

import geopandas as gpd
from shapely.geometry import Polygon

from config.config import Config


class BuildingPolygonCreator(Config):
    def __init__(self):
        super().__init__()
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.user_building_file = self.config.get('user_building_file')
        self.output_path = self.config.get('polygon_from_building')

    def user_polygon(self, polygon_coords):
        """Create and save a polygon from the provided coordinates."""
        self._ensure_closed_polygon(polygon_coords)

        polygon = Polygon(polygon_coords)
        polygon_gdf = self._create_geo_dataframe(polygon)
        self._save_geojson(polygon_gdf)
        return polygon_gdf

    def load_buildings(self):
        """Load the user building file as a GeoDataFrame."""
        if not os.path.exists(self.user_building_file):
            raise FileNotFoundError(f"File not found: {self.user_building_file}")

        try:
            buildings_gdf = gpd.read_file(self.user_building_file)
            if buildings_gdf.empty:
                raise ValueError("The building file contains no geometries.")
            print("Buildings loaded successfully.")
            return buildings_gdf
        except Exception as e:
            raise FileNotFoundError(f"Unable to load building file: {e}")

    def create_polygon_from_buildings(self):
        """Create a polygon encompassing all building geometries."""
        self.load_config()
        buildings_gdf = self.load_buildings()

        polygon = self._create_convex_hull(buildings_gdf)
        self._update_map_center(polygon)
        self._save_polygon_in_project_info(polygon)

        polygon_gdf = self._create_geo_dataframe(polygon, crs=buildings_gdf.crs)
        self._save_geojson(polygon_gdf)

        self.save_config()
        print("Configuration updated with mapCenter and polygonArray.")
        return polygon_gdf

    def _ensure_closed_polygon(self, coords):
        """Ensure the polygon coordinates form a closed shape."""
        if coords[0] != coords[-1]:
            coords.append(coords[0])

    def _create_geo_dataframe(self, polygon, crs=None):
        """Create a GeoDataFrame from a Polygon."""
        crs = crs or self.default_crs
        return gpd.GeoDataFrame(geometry=[polygon], crs=crs)

    def _save_geojson(self, gdf):
        """Save a GeoDataFrame as a GeoJSON file."""

        # Ensure the output directory exists
        output_dir = os.path.dirname(self.output_path)
        if not os.path.exists(output_dir):
            print(f"Directory {output_dir} does not exist. Creating it now.")
            os.makedirs(output_dir, exist_ok=True)

        gdf.set_crs(self.default_crs, inplace=True)
        gdf.to_file(self.output_path, driver='GeoJSON')
        print(f"GeoJSON file saved to {self.output_path}")

    def _create_convex_hull(self, gdf):
        """Create a convex hull polygon from building geometries."""
        return gdf.unary_union.convex_hull

    def _update_map_center(self, polygon):
        """Update the map center in the configuration based on the polygon centroid."""
        centroid = polygon.centroid
        self.config["project_info"]["mapCenter"] = {
            "latitude": centroid.y,
            "longitude": centroid.x,
            "zoom": 8
        }
        print(f"Map center updated to latitude: {centroid.y}, longitude: {centroid.x}, zoom: 8")

    def _save_polygon_in_project_info(self, polygon):
        """Save the polygon coordinates to project_info in the configuration."""
        coordinates = list(map(list, polygon.exterior.coords))
        self.config["project_info"]["polygonArray"] = coordinates
        print("PolygonArray added to project_info in the configuration.")
