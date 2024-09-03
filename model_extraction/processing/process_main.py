from model_extraction.processing.ArchetypeAssigner import TabulaAssigner
from model_extraction.processing.built_year.census_built_year import CensusBuiltYear
from model_extraction.processing.built_year.osm_built_year import OsmBuiltYear
from model_extraction.processing.census_information.building_usage import BuildingUsageProcessor
from model_extraction.processing.census_information.family_num_calculation import FamilyCalculator
from model_extraction.processing.census_information.population_calculation import PopulationCalculator
from model_extraction.processing.geometry_calculation.floor_process import FloorProcess
from model_extraction.processing.geometry_calculation.height_processing.building_kriging_filler import \
    BuildingKrigingFiller
from model_extraction.processing.geometry_calculation.height_processing.height_process import HeightProcess
from model_extraction.processing.geometry_calculation.volume_calculator import BuildingVolumeCalculator


class ProcessMain:
    def __init__(self, config_path):
        self.config_path = config_path

    def processing_height(self):
        height_process = HeightProcess(self.config_path)
        height_process.process_height()
        # height_process.calculate_heights_from_dtm_dsm()

    def building_kriging_filler(self):
        building_kriging_filler = BuildingKrigingFiller(self.config_path)
        building_kriging_filler.process_filling()

    def process_volume(self):
        volume_calculator = BuildingVolumeCalculator(self.config_path)
        volume_calculator.process_volume_calculation()

    def building_usage(self):
        building_usage = BuildingUsageProcessor(self.config_path)
        building_usage.process()

    def process_floor(self):
        process_floor = FloorProcess(self.config_path)
        process_floor.process_floors()

    def population_calculator(self):
        population_calculation = PopulationCalculator(self.config_path)
        population_calculation.run()

    def family_calculator(self):
        family_calculation = FamilyCalculator(self.config_path)
        family_calculation.run()

    def process_census_built_year(self):
        process_census_built_year = CensusBuiltYear(self.config_path)
        process_census_built_year.run()

    def process_osm_built_year(self):
        osm_built_year = OsmBuiltYear(self.config_path)
        osm_built_year.run()

    def process_archetype(self):
        archetype_assigner = TabulaAssigner(self.config_path)
        archetype_assigner.run()

    def run_all_processing(self):
        self.processing_height()
        self.building_kriging_filler()
        self.process_volume()
        self.building_usage()
        self.process_census_built_year()
        self.process_osm_built_year()
        self.process_archetype()

    # def process_areas(self):
    #     process_areas = ProcessAreas(self.config_path)
    #     process_areas.calculate_building_areas()
    #

    # def processing_census(self):
    #     census_process = ProcessCensus(self.config_path)
    #     census_process.make_selected_census()
    #     census_process.merge_buildings_census()
    #
