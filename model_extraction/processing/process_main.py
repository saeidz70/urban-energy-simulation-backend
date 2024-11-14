from features_collection.features.building_id import BuildingIDAssigner
from features_collection.features.tabula_id import TabulaAssigner
from features_collection.features.year_of_construction import CensusBuiltYear
from model_extraction.processing.osm_built_year import OsmBuiltYear
from features_collection.features.usage import BuildingUsageProcessor
from features_collection.features.census_id import CensusIdCalculator
from features_collection.features.n_family import FamilyCalculator
from features_collection.features.feature_helpers.population import PopulationCalculator
from features_collection.features.tot_area_per_cens_id import TotalAreaPerCensusCalculator
from features_collection.features.area import BuildingAreaCalculator
from features_collection.features.n_floor import FloorProcess
from features_collection.features.gross_floor_area import GrossFloorAreaCalculator
from features_collection.features.height import HeightProcess
from model_extraction.processing.building_kriging_filler import \
    BuildingKrigingFiller
from features_collection.features.net_leased_area import NetLeasedAreaCalculator
from features_collection.features.feature_helpers.volume import BuildingVolumeCalculator


class ProcessMain:
    def __init__(self, config_path):
        self.config_path = config_path

    def building_id(self):
        id_assigner = BuildingIDAssigner(self.config_path)
        id_assigner.assign_unique_id()

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
