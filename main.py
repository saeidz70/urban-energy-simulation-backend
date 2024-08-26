from model_extraction.prepration.prep_main import PrepMain
from model_extraction.processing.process_main import ProcessMain

if __name__ == '__main__':
    config_path = 'data_source/config/configuration.json'

    # Preparation
    preparation = PrepMain(config_path)
    # preparation.select_census_sections()
    # preparation.getBoundaries()
    # preparation.osm_building_extraction()
    # preparation.data_integration()
    # preparation.clean_data()
    # preparation.filter_area()
    # preparation.process_census_built_year()
    # preparation.process_data()


    # Processing
    processing = ProcessMain(config_path)
    # processing.processing_height()
    # processing.building_kriging_filler()
    processing.process_volume()
    # processing.process_areas()
    # processing.process_floor()
