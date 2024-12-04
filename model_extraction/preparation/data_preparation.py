from config.config import Config
from model_extraction.preparation.data_cleaning.clean_null import CleanGeoData
from model_extraction.preparation.read_data.building_extractor import BuildingExtractor
from model_extraction.preparation.read_data.census_selector import CensusSelector
from model_extraction.preparation.read_data.data_integration import DataIntegration
from model_extraction.preparation.read_data.db_census_fetcher import DbCensusFetcher
from model_extraction.preparation.read_data.get_selected_boundries import GetSelectedBoundaries


class PrepMain(Config):
    def __init__(self):
        super().__init__()

    def fetch_census_data(self):
        census_fetcher = DbCensusFetcher()
        print("Fetching census data")
        census_fetcher.run()

    def select_census_sections(self):
        census_selector = CensusSelector()
        print("Selecting census sections")
        census_selector.run()

    def getBoundaries(self):
        extractor = GetSelectedBoundaries()
        print("Processing boundaries")
        extractor.process_boundaries()

    def building_extraction(self):
        building_extractor = BuildingExtractor()
        print("Extracting buildings")
        building_extractor.extract_and_save_buildings()

    def data_integration(self):
        integrator = DataIntegration()
        print("Integrating data")
        integrator.integrate_buildings()

    def clean_data(self):
        clean_data = CleanGeoData()
        print("Cleaning data")
        clean_data.clean_data()


    def run_all_preparations(self):
        self.fetch_census_data()
        # self.select_census_sections()
        self.getBoundaries()
        self.building_extraction()
        self.data_integration()
        self.clean_data()
