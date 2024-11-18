import os

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import box

from config.config import Config


class DtmDsmHeightCalculator(Config):
    def __init__(self):
        super().__init__()
        self.dtm_path = self.config.get('dtm_path')
        self.dsm_path = self.config.get('dsm_path')
        self.output_path = self.config.get('dsm_output_path')
        self.boundary_path = self.config.get('selected_boundaries')
        self.default_epsg = self.config.get("DEFAULT_EPSG_CODE")  # EPSG:32632 for projected operations
        self.standard_epsg = 4326  # EPSG:4326 as standard output format
        self.dtm_data = None
        self.dsm_data = None
        self.dtm_profile = None
        self.dsm_profile = None

    def read_and_crop_raster(self, path, boundary_gdf):
        print(f"Attempting to read and crop raster file: {path}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Raster file not found: {path}")

        # Ensure boundary is in projected CRS for accurate spatial operations
        if boundary_gdf.crs != f"EPSG:{self.default_epsg}":
            print(f"Reprojecting boundary from {boundary_gdf.crs} to EPSG:{self.default_epsg}")
            boundary_gdf = boundary_gdf.to_crs(epsg=self.default_epsg)
        boundary = boundary_gdf.geometry.unary_union

        with rasterio.open(path) as src:
            if src.crs.to_string() != f"EPSG:{self.default_epsg}":
                print(f"Reprojecting raster from {src.crs} to EPSG:{self.default_epsg}")
                transform, width, height = calculate_default_transform(
                    src.crs, f"EPSG:{self.default_epsg}", src.width, src.height, *src.bounds)

                reprojected_data = np.empty((height, width), dtype=np.float32)
                reproject(
                    source=rasterio.band(src, 1),
                    destination=reprojected_data,
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=f"EPSG:{self.default_epsg}",
                    resampling=Resampling.nearest
                )
                out_meta = src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": height,
                    "width": width,
                    "transform": transform,
                    "crs": f"EPSG:{self.default_epsg}"
                })
            else:
                reprojected_data, transform = mask(src, [boundary], crop=True)
                out_meta = src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": reprojected_data.shape[1],
                    "width": reprojected_data.shape[2],
                    "transform": transform,
                    "crs": f"EPSG:{self.default_epsg}"
                })
            print(f"Raster {path} processed successfully with CRS set to EPSG:{self.default_epsg}.")
        return reprojected_data[0], out_meta

    def load_data(self):
        print("Loading and cropping DTM and DSM data with enforced CRS.")
        boundary_gdf = gpd.read_file(self.boundary_path)
        if boundary_gdf.crs is not None and boundary_gdf.crs.to_string() != f"EPSG:{self.default_epsg}":
            boundary_gdf = boundary_gdf.to_crs(epsg=self.default_epsg)
        elif boundary_gdf.crs is None:
            boundary_gdf.set_crs(epsg=self.default_epsg, inplace=True, allow_override=True)

        self.dtm_data, self.dtm_profile = self.read_and_crop_raster(self.dtm_path, boundary_gdf)
        self.dsm_data, self.dsm_profile = self.read_and_crop_raster(self.dsm_path, boundary_gdf)

    def calculate_building_heights(self, buildings_gdf):
        if self.dtm_data is None or self.dsm_data is None:
            raise ValueError("DTM and DSM data must be loaded first.")
        print("Calculating building heights by masking DTM and DSM.")

        # Temporarily reproject user_building_file to EPSG:32632
        if buildings_gdf.crs != f"EPSG:{self.default_epsg}":
            print(f"Reprojecting buildings_gdf from {buildings_gdf.crs} to EPSG:{self.default_epsg}")
            buildings_gdf = buildings_gdf.to_crs(epsg=self.default_epsg)

        heights = []
        with rasterio.open(self.dtm_path) as dtm_src, rasterio.open(self.dsm_path) as dsm_src:
            dtm_bounds = box(*dtm_src.bounds)
            dsm_bounds = box(*dsm_src.bounds)

            for geometry in buildings_gdf.geometry:
                # Check for overlap with DTM/DSM bounds
                if not geometry.intersects(dtm_bounds):
                    print(
                        f"Geometry does not overlap with DTM raster extent. Skipping geometry with bounds: {geometry.bounds}")
                    heights.append(np.nan)
                    continue
                try:
                    dtm_masked, _ = mask(dtm_src, [geometry], crop=True)
                    dsm_masked, _ = mask(dsm_src, [geometry], crop=True)

                    dtm_mean = np.mean(dtm_masked[dtm_masked != dtm_src.nodata])
                    dsm_mean = np.mean(dsm_masked[dsm_masked != dsm_src.nodata])

                    if np.isnan(dtm_mean) or np.isnan(dsm_mean):
                        print("Warning: No valid data in the footprint, setting height to NaN.")
                        height = np.nan
                    else:
                        height = dsm_mean - dtm_mean
                        print(f"Calculated height for building footprint: {height}")
                    heights.append(height)
                except ValueError:
                    print("ValueError encountered during masking: setting height to NaN.")
                    heights.append(np.nan)

        buildings_gdf['height'] = heights

        # Reproject back to EPSG:4326 before returning
        if buildings_gdf.crs != f"EPSG:{self.standard_epsg}":
            print(f"Reprojecting buildings_gdf back to EPSG:{self.standard_epsg}")
            buildings_gdf = buildings_gdf.to_crs(epsg=self.standard_epsg)

        return buildings_gdf
