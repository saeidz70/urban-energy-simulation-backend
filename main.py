from model_extraction.prepration.prep_main import PrepMain
from model_extraction.processing.census_process import ProcessCensus
from model_extraction.processing.height_process import HeightProcess

if __name__ == '__main__':
    config_path = 'data_source/config/configuration.json'

    # Preparation
    # preparation = PrepMain(config_path)
    # final_gdf = preparation.process_data()
    # preparation.plot_and_save(final_gdf)
    #
    # # Processing Census
    # census_process = ProcessCensus(config_path)
    # census_process.make_selected_census()
    # census_process.merge_buildings_census()

    # Processing Height
    height_process = HeightProcess(config_path)
    height_process.process_height()
