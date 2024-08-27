from model_extraction.prepration.data_cleaning.clean_null import CleanGeoData
from model_extraction.prepration.data_cleaning.filter_area import BuildingAreaCalculator
from model_extraction.prepration.read_data.area_selection import CensusSelector
from model_extraction.prepration.read_data.data_integration import DataIntegration
from model_extraction.prepration.read_data.get_selected_boundries import GetSelectedBoundaries
from model_extraction.prepration.read_data.osm_building_extractor import OSMBuildingExtractor


class PrepMain:
    def __init__(self, config_path):
        self.config_path = config_path

    def select_census_sections(self):
        census_selector = CensusSelector(self.config_path)
        census_selector.get_selected_sections()

    def getBoundaries(self):
        extractor = GetSelectedBoundaries(self.config_path)
        extractor.process_boundaries()

    def osm_building_extraction(self):
        osm_building_extractor = OSMBuildingExtractor(self.config_path)
        buildings = osm_building_extractor.extract_buildings()
        osm_building_extractor.save_buildings(buildings)

    def data_integration(self):
        integrator = DataIntegration(self.config_path)
        integrated_gdf = integrator.integrate_buildings()
        integrator.save_integrated(integrated_gdf)

    def clean_data(self):
        clean_data = CleanGeoData(self.config_path)
        clean_data.clean_data()

    def filter_area(self):
        filter_area = BuildingAreaCalculator(self.config_path)
        filter_area.process_buildings()

    def run_all_preparations(self):
        self.select_census_sections()
        self.getBoundaries()
        self.osm_building_extraction()
        self.data_integration()
        self.clean_data()
        self.filter_area()
