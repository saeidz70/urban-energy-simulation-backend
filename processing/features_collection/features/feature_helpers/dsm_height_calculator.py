import os

import geopandas as gpd
import numpy as np
import rioxarray

from config.config import Config


class DtmDsmHeightCalculator(Config):
    def __init__(self):
        super().__init__()
        self.height_column = 'height'
        self.dtm_path = self.config.get('dtm_path')
        self.dsm_path = self.config.get('dsm_path')
        self.output_path = self.config.get('dsm_output_path')
        self.boundary_path = self.config.get('selected_boundaries')
        self.projected_crs = f"EPSG:{self.config.get('PROJECTED_CRS', 32632)}"
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.dtm_data = None
        self.dsm_data = None

    def read_and_crop_raster(self, path, boundary_gdf):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Raster file not found: {path}")

        # Ensure boundary is in the projected CRS
        if boundary_gdf.crs != self.projected_crs:
            boundary_gdf = boundary_gdf.to_crs(self.projected_crs)

        boundary = boundary_gdf.geometry.unary_union

        # Read and crop raster with rioxarray
        raster = rioxarray.open_rasterio(path, masked=True).squeeze()
        raster = raster.rio.reproject(self.projected_crs)
        cropped_raster = raster.rio.clip([boundary], from_disk=True)
        return cropped_raster

    def load_data(self):
        boundary_gdf = gpd.read_file(self.boundary_path)

        if boundary_gdf.crs is None:
            boundary_gdf.set_crs(epsg=self.projected_crs, inplace=True)

        self.dtm_data = self.read_and_crop_raster(self.dtm_path, boundary_gdf)
        self.dsm_data = self.read_and_crop_raster(self.dsm_path, boundary_gdf)

    def calculate_building_heights(self, buildings_gdf):
        if self.dtm_data is None or self.dsm_data is None:
            raise ValueError("DTM and DSM data must be loaded first.")

        # Reproject buildings to the projected CRS
        if buildings_gdf.crs != self.projected_crs:
            buildings_gdf = buildings_gdf.to_crs(self.projected_crs)

        heights = []
        for geometry in buildings_gdf.geometry:
            try:
                dtm_clip = self.dtm_data.rio.clip([geometry], from_disk=True)
                dsm_clip = self.dsm_data.rio.clip([geometry], from_disk=True)

                dtm_mean = dtm_clip.mean().item()
                dsm_mean = dsm_clip.mean().item()

                if np.isnan(dtm_mean) or np.isnan(dsm_mean):
                    heights.append(np.nan)
                else:
                    height = dsm_mean - dtm_mean
                    heights.append(round(height, 2))  # Round to two decimal places
            except Exception as e:
                print(f"Error processing geometry: {e}")
                heights.append(np.nan)

        buildings_gdf[self.height_column] = heights

        # Reproject back to the default CRS
        if buildings_gdf.crs != self.default_crs:
            buildings_gdf = buildings_gdf.to_crs(self.default_crs)

        return buildings_gdf
