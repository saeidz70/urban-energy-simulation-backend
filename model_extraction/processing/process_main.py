from model_extraction.processing.ArchetypeAssigner import TabulaAssigner
from model_extraction.processing.built_year.census_built_year import CensusBuiltYear
from model_extraction.processing.built_year.osm_built_year import OsmBuiltYear
from model_extraction.processing.census_information.building_usage import BuildingUsageProcessor
from model_extraction.processing.census_information.census_id import CensusIdCalculator
from model_extraction.processing.census_information.family_num_calculation import FamilyCalculator
from model_extraction.processing.census_information.population_calculation import PopulationCalculator
from model_extraction.processing.census_information.tot_area_per_cens_id import TotalAreaPerCensusCalculator
from model_extraction.processing.geometry_calculation.area_process import BuildingAreaCalculator
from model_extraction.processing.geometry_calculation.floor_process import FloorProcess
from model_extraction.processing.geometry_calculation.gross_floor_area import GrossFloorAreaCalculator
from model_extraction.processing.geometry_calculation.height_process import HeightProcess
from model_extraction.processing.geometry_calculation.height_processing.building_kriging_filler import \
    BuildingKrigingFiller
from model_extraction.processing.geometry_calculation.net_leased_area import NetLeasedAreaCalculator
from model_extraction.processing.geometry_calculation.volume_calculator import BuildingVolumeCalculator


class ProcessMain:
    def __init__(self, config_path):
        self.config_path = config_path

    def area(self):
        filter_area = BuildingAreaCalculator(self.config_path)
        filter_area.process_buildings()

    def height(self):
        height_process = HeightProcess(self.config_path)
        height_process.process_heights()
        # height_process.calculate_heights_from_dtm_dsm()

    def building_kriging_filler(self):
        building_kriging_filler = BuildingKrigingFiller(self.config_path)
        building_kriging_filler.process_filling()

    def volume(self):
        volume_calculator = BuildingVolumeCalculator(self.config_path)
        volume_calculator.process_volume_calculation()

    def usage(self):
        building_usage = BuildingUsageProcessor(self.config_path)
        building_usage.process()

    def n_floor(self):
        process_floor = FloorProcess(self.config_path)
        process_floor.process_floors()

    def gross_floor_area(self):
        gross_floor_area = GrossFloorAreaCalculator(self.config_path)
        gross_floor_area.calculate_gfa()

    def net_leased_area(self):
        net_leased_area = NetLeasedAreaCalculator(self.config_path)
        net_leased_area.calculate_nla()

    def census_id(self):
        census_id = CensusIdCalculator(self.config_path)
        census_id.calculate_census_id()

    def tot_area_per_cens_id(self):
        area_census_id = TotalAreaPerCensusCalculator(self.config_path)
        area_census_id.calculate_total_area_per_census()

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
        self.area_calculation()
        self.processing_height()
        self.building_kriging_filler()
        self.process_volume()
        self.building_usage()
        self.process_census_built_year()
        self.process_osm_built_year()
        self.process_archetype()
        self.process_floor()
        self.population_calculator()
        self.family_calculator()






    # def process_areas(self):
    #     process_areas = ProcessAreas(self.config_path)
    #     process_areas.calculate_building_areas()
    #

    # def processing_census(self):
    #     census_process = ProcessCensus(self.config_path)
    #     census_process.make_selected_census()
    #     census_process.merge_buildings_census()
    #
