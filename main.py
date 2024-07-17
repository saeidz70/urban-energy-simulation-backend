from model_extraction.prepration.prep_main import PrepMain
from model_extraction.processing.process_main import ProcessMain


if __name__ == '__main__':
    config_path = 'data_source/config/configuration.json'

    # Preparation
    # preparation = PrepMain(config_path)
    # final_gdf = preparation.process_data()
    # preparation.plot_and_save(final_gdf)


    # Processing
    processing = ProcessMain(config_path)
    # processing.processing_height()
    # processing.process_areas()
    processing.process_floor()
