import geojson
import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import shape, Polygon

from config.config import Config


class GetSelectedBoundaries(Config):
    def __init__(self):
        super().__init__()
        self.input_file_path = self.config['db_census_sections']
        self.output_file_path = self.config['selected_boundaries']
        self.geo_data = self.load_geojson()
        self.polygons = []
        self.combined_polygon = None

    def load_geojson(self):
        with open(self.input_file_path) as f:
            geojson_data = geojson.load(f)
        return geojson_data

    def extract_polygons(self, geojson_data):
        for feature in geojson_data['features']:
            geom = feature['geometry']
            if geom['type'] == 'Polygon':
                self.polygons.append(shape(geom))
            elif geom['type'] == 'MultiPolygon':
                for poly in geom['coordinates']:
                    self.polygons.append(Polygon(poly[0]))

    def combine_polygons(self):
        self.combined_polygon = gpd.GeoSeries(self.polygons).unary_union

    def plot_boundary(self):
        if self.combined_polygon is None:
            print("No combined polygon to plot. Please run combine_polygons() first.")
            return

        fig, ax = plt.subplots()
        gpd.GeoSeries(self.combined_polygon).plot(ax=ax, color='blue', edgecolor='black')
        plt.title("Polygon Boundary of the GeoJSON Area")
        plt.show()

    def save_boundary(self):
        if self.combined_polygon is None:
            print("No combined polygon to save. Please run combine_polygons() first.")
            return

        combined_gdf = gpd.GeoDataFrame(geometry=[self.combined_polygon])
        combined_gdf.to_file(self.output_file_path, driver="GeoJSON")
        print(f"Polygon boundary extracted and saved to {self.output_file_path}.")

    def process_boundaries(self):
        self.extract_polygons(self.geo_data)
        self.combine_polygons()
        # self.plot_boundary()
        self.save_boundary()
