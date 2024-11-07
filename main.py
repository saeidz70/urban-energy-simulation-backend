from model_extraction.prepration.prep_main import PrepMain
from model_extraction.processing.process_main import ProcessMain

if __name__ == '__main__':
    config_path = 'data_source/config/configuration.json'

    ########### PREPARATION:
    preparation = PrepMain(config_path)
    # preparation.shapefile_to_geojson()
    # preparation.select_census_sections()
    # preparation.getBoundaries()
    # preparation.building_extraction()
    # preparation.data_integration()
    # preparation.clean_data()
    preparation.websevice()
    # preparation.run_all_preparations()



    ########## PROCESSING:
    processing = ProcessMain(config_path)


    # processing.area()
    # processing.height()
    # processing.volume()
    # processing.n_floor()
    # processing.gross_floor_area()
    # processing.net_leased_area()
    # processing.census_id()
    # processing.tot_area_per_cens_id()
    # processing.building_usage()
    # processing.population_calculator()
    # processing.family_calculator()
    # processing.process_census_built_year()
    # processing.process_osm_built_year()
    # processing.process_archetype()
    # processing.run_all_processing()

    def baseline():
        pass


    def geometry():
        pass


    def demographic():
        pass


    def energy():
        pass
