import geopandas as gpd

from config.config import Config


class GetSelectedBoundaries(Config):
    def __init__(self):
        super().__init__()
        self.output_file_path = self.config['selected_boundaries']
        self.polygons = []
        self.boundary_polygon = None

    def _extract_polygons(self, selected_census_gdf):
        """Extract polygons from the selected census GeoDataFrame."""
        if selected_census_gdf.empty:
            raise ValueError("Selected census GeoDataFrame is empty.")

        for geom in selected_census_gdf.geometry:
            if geom.geom_type == 'Polygon':
                self.polygons.append(geom)
            elif geom.geom_type == 'MultiPolygon':
                self.polygons.extend(geom.geoms)

    def _combine_polygons(self):
        """Combine all extracted polygons into a single polygon."""
        if not self.polygons:
            raise ValueError("No polygons to combine.")
        self.boundary_polygon = gpd.GeoSeries(self.polygons).unary_union

    def _save_boundary(self):
        """Save the combined polygon boundary to the output file."""
        if self.boundary_polygon is None:
            raise ValueError("No combined polygon to save. Please run _combine_polygons() first.")

        boundary_polygon = gpd.GeoDataFrame(geometry=[self.boundary_polygon], crs="EPSG:4326")
        boundary_polygon.to_file(self.output_file_path, driver="GeoJSON")
        print(f"Polygon boundary extracted and saved to {self.output_file_path}.")
        return boundary_polygon

    def run(self, selected_census_gdf):
        """Run the process to extract, combine, and save polygon boundaries."""
        self._extract_polygons(selected_census_gdf)
        self._combine_polygons()
        boundary_polygon = self._save_boundary()
        return boundary_polygon
