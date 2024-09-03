import json

import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


class BuildingHeightCalculator:
    def __init__(self, config_path, expected_crs='epsg:4326'):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.dtm_path = config['dtm_path']
        self.dsm_path = config['dsm_path']
        self.output_path = config['dsm_output_path']
        self.expected_crs = expected_crs
        self.dtm_data = None
        self.dsm_data = None
        self.dtm_profile = None
        self.dsm_profile = None

    def read_raster(self, path):
        with rasterio.open(path) as src:
            data = src.read(1)
            profile = src.profile
        return data, profile

    def check_crs(self, profile):
        return profile['crs'].to_string() == self.expected_crs

    def transform_crs(self, data, profile):
        if 'gcps' in profile:
            gcps, gcp_crs = profile['gcps']
            transform, width, height = calculate_default_transform(
                gcp_crs, self.expected_crs, width=profile['width'], height=profile['height'], gcps=gcps)
            src_transform = transform
            src_crs = gcp_crs
        else:
            transform, width, height = calculate_default_transform(
                profile['crs'], self.expected_crs, profile['width'], profile['height'], *profile['transform'][:6])
            src_transform = profile['transform']
            src_crs = profile['crs']

        new_profile = profile.copy()
        new_profile.update({
            'crs': self.expected_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        reprojected_data = np.empty((height, width), dtype=np.float32)
        reproject(
            source=data,
            destination=reprojected_data,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=transform,
            dst_crs=self.expected_crs,
            resampling=Resampling.nearest
        )

        return reprojected_data, new_profile

    def load_data(self):
        self.dtm_data, self.dtm_profile = self.read_raster(self.dtm_path)
        self.dsm_data, self.dsm_profile = self.read_raster(self.dsm_path)

        if not self.check_crs(self.dtm_profile):
            self.dtm_data, self.dtm_profile = self.transform_crs(self.dtm_data, self.dtm_profile)
        if not self.check_crs(self.dsm_profile):
            self.dsm_data, self.dsm_profile = self.transform_crs(self.dsm_data, self.dsm_profile)

    def calculate_building_heights(self):
        if self.dtm_data is None or self.dsm_data is None:
            raise ValueError("DTM and DSM data must be loaded first.")

        building_heights = self.dsm_data - self.dtm_data
        return building_heights

    def save_building_heights(self, building_heights):
        new_profile = self.dtm_profile.copy()
        new_profile.update(dtype=rasterio.float32, count=1, compress='lzw')

        with rasterio.open(self.output_path, 'w', **new_profile) as dst:
            dst.write(building_heights.astype(rasterio.float32), 1)
