from model_extraction.prepration.prep_main import PrepMain
from model_extraction.processing.process_main import ProcessMain

if __name__ == '__main__':
    config_path = 'data_source/config/configuration.json'


    def baseline():
        pass


    def geometry():
        pass


    def demographic():
        pass


    def energy():
        pass



    ########### PREPARATION:
    preparation = PrepMain(config_path)
    preparation.shapefile_to_geojson()
    preparation.select_census_sections()
    preparation.getBoundaries()
    preparation.building_extraction()
    preparation.data_integration()
    preparation.clean_data()
    # preparation.run_all_preparations()



    ########## PROCESSING:
    processing = ProcessMain(config_path)
    processing.area_calculation()
    processing.processing_height()
    processing.process_volume()
    processing.process_floor()
    # processing.building_usage()
    # processing.population_calculator()
    # processing.family_calculator()
    # processing.process_census_built_year()
    # processing.process_osm_built_year()
    # processing.process_archetype()
    # processing.run_all_processing()
