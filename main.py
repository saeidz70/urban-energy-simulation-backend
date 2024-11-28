from model_extraction.features_collection.feature_factory import FeatureFactory

if __name__ == '__main__':
    # config_path = 'config/configuration.json'

    ########### PREPARATION:
    # preparation = PrepMain()
    # preparation.shapefile_to_geojson()
    # preparation.select_census_sections()
    # preparation.getBoundaries()
    # preparation.building_extraction()
    # preparation.data_integration()
    # preparation.clean_data()
    # preparation.run_all_preparations()



    ########## PROCESSING:
    processing = FeatureFactory()
    #
    # processing.building_id()
    # processing.census_id()
    # processing.area()
    processing.height()
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

