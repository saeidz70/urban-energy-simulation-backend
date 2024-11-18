import geopandas as gpd
from shapely.geometry.polygon import Polygon

from config.config import Config


class BuildingPolygonCreator(Config):
    def __init__(self):
        super().__init__()
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.user_building_file = self.config.get('user_building_file')
        self.output_path = self.config.get('polygon_from_building')

    def user_polygon(self, polygon_coords):

        if polygon_coords[0] != polygon_coords[-1]:
            polygon_coords.append(polygon_coords[0])

        # Create a Polygon from the coordinates
        polygon = Polygon(polygon_coords)

        # Create a GeoDataFrame with the Polygon
        polygon_gdf = gpd.GeoDataFrame(geometry=[polygon], crs=self.default_crs)

        self.save_geojson(polygon_gdf)
        return polygon_gdf

    def load_buildings(self):
        """Load user_building_file from a GeoJSON file."""
        try:
            self.user_building_file = gpd.read_file(self.user_building_file)
            print("Buildings loaded successfully.")
        except Exception as e:
            raise FileNotFoundError(f"Unable to load building file: {e}")

    def create_polygon_from_buildings(self):
        self.load_buildings()
        """Create a polygon that surrounds all user_building_file."""
        if self.user_building_file.empty:
            raise ValueError("No building data available to create an polygon.")

        # Combine all geometries to a single polygon
        polygon = self.user_building_file.unary_union.convex_hull
        print("Polygon created from user_building_file foot-prints successfully.")

        # Create a GeoDataFrame to handle the polygon
        polygon_gdf = gpd.GeoDataFrame(geometry=[polygon], crs=self.user_building_file.crs)

        self.save_geojson(polygon_gdf)
        return polygon_gdf

    def save_geojson(self, gdf):
        gdf.set_crs(self.default_crs, inplace=True)

        # Save to GeoJSON
        gdf.to_file(self.output_path, driver='GeoJSON')
        print(f"GeoJSON file has been saved to {self.output_path}")
