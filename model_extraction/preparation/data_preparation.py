import geopandas as gpd

from config.config import Config
from model_extraction.preparation.data_cleaning.clean_null import CleanGeoData
from model_extraction.preparation.read_data.building_manager import BuildingManager
from model_extraction.preparation.read_data.census_selector import CensusSelector
from model_extraction.preparation.read_data.data_integration import DataIntegration
from model_extraction.preparation.read_data.db_census_fetcher import DbCensusFetcher
from model_extraction.preparation.read_data.get_selected_boundries import GetSelectedBoundaries


class PrepMain(Config):
    def __init__(self):
        super().__init__()

    def fetch_census_data(self, polygon_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        print("Fetching census data")
        return DbCensusFetcher().run(polygon_gdf)

    def select_census_sections(self, polygon_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        print("Selecting census sections")
        return CensusSelector().run(polygon_gdf)

    def get_boundaries(self, selected_census_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        print("Processing boundaries")
        return GetSelectedBoundaries().run(selected_census_gdf)

    def extract_buildings(self, boundaries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        print("Extracting buildings")
        return BuildingManager().run(boundaries)

    # def extract_buildings(self, boundaries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    #     print("Extracting buildings")
    #     return BuildingExtractor().run(boundaries)

    def integrate_data(self, buildings_gdf: gpd.GeoDataFrame,
                       selected_census_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        print("Integrating data")
        return DataIntegration().run(buildings_gdf, selected_census_gdf)

    def clean_data(self, integrated_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        print("Cleaning data")
        return CleanGeoData().run(integrated_gdf)

    def run(self, polygon_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        #  selected_census_gdf = self.fetch_census_data(polygon_gdf)
        selected_census_gdf = self.select_census_sections(polygon_gdf)
        boundaries = self.get_boundaries(selected_census_gdf)
        buildings_gdf = self.extract_buildings(boundaries)
        integrated_gdf = self.integrate_data(buildings_gdf, selected_census_gdf)
        return self.clean_data(integrated_gdf)
