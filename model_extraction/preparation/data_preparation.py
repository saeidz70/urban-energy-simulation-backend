from config.config import Config
from model_extraction.preparation.data_cleaning.clean_null import CleanGeoData
from model_extraction.preparation.read_data.census_selector import CensusSelector
from model_extraction.preparation.read_data.building_extractor import BuildingExtractor
from model_extraction.preparation.read_data.convert import Convertor
from model_extraction.preparation.read_data.data_integration import DataIntegration
from model_extraction.preparation.read_data.get_selected_boundries import GetSelectedBoundaries


class PrepMain(Config):
    def __init__(self):
        super().__init__()

    # def shapefile_to_geojson(self):
    #     convertor = Convertor(self.config_path)
    #     convertor.convert_file_format("user_file")

    def select_census_sections(self):
        census_selector = CensusSelector()
        census_selector.get_selected_sections()

    def getBoundaries(self):
        extractor = GetSelectedBoundaries()
        extractor.process_boundaries()

    def building_extraction(self):
        building_extractor = BuildingExtractor()
        building_extractor.extract_and_save_buildings()

    def data_integration(self):
        integrator = DataIntegration()
        integrated_gdf = integrator.integrate_buildings()
        integrator.save_integrated(integrated_gdf)

    def clean_data(self):
        clean_data = CleanGeoData()
        clean_data.clean_data()


    def run_all_preparations(self):
        self.select_census_sections()
        self.getBoundaries()
        self.building_extraction()
        self.data_integration()
        self.clean_data()
