import geopandas as gpd

from config.config import Config
from model_extraction.features_collection.feature_factory import FeatureFactory

if __name__ == '__main__':
    config_path = 'config/configuration.json'
    config = Config()
    building_file = config.config['building_path']
    gdf = gpd.read_file(building_file)
    print("Original GeoDataFrame:")
    print(gdf.head())
    ########### PREPARATION:
    # preparation = PrepMain()
    # preparation.shapefile_to_geojson()
    # preparation.select_census_sections()
    # preparation.getBoundaries()
    # preparation.building_extraction()
    # preparation.data_integration()
    # preparation.clean_data()
    # preparation.run_all_preparations()

    # area_calculator = BuildingAreaCalculator()
    # gdf = area_calculator.run(gdf)
    #
    # print("GeoDataFrame after calculating building areas:")
    # print(gdf.head())


    ########## PROCESSING:
    processing = FeatureFactory()
    #
    gdf = processing.run_feature('neighbours_ids', gdf)
    print(gdf[['neighbours_ids']].head())
    gdf.to_file(building_file, driver='GeoJSON')
    print(f"Data saved to {building_file}.")

    # processing.building_id()
    # processing.census_id()
    # processing.area()
    # processing.height()
    # processing.volume()
    # processing.n_floor()
    # processing.gross_floor_area()
    # processing.net_leased_area()
    # processing.tot_area_per_cens_id()
    # processing.usage()
    # processing.n_family()
    # processing.year_of_construction()
    # processing.construction_type()
    # processing.heating()
    # processing.cooling()
    # processing.hvac_type()
    # processing.tabula_type()
    # processing.tabula_id()



    # manager = ScenarioManager()
    # manager.run_scenarios()

    # output_generator = OutputFileGenerator()
    # output_generator.generate_output_file()

    # fetcher = DbCensusFetcher()
    # fetcher.run()

    # polygon_creator = BuildingPolygonCreator()
    # polygon_creator.create_polygon()
    #
    # census_selector = CensusSelector()
    # census_selector.run()

