import geopandas as gpd


class ProcessShapefile(object):
    def __init__(self):
        pass

    def process_shapefile(self, shape_file, bounding_box):
        gdf = gpd.read_file(shape_file)

        if not shape_file.endswith('.geojson'):
            shape_file = shape_file.replace('.shp', '.geojson')
            gdf.to_file(shape_file, driver='GeoJSON')

        gdf.to_crs(epsg=4326, inplace=True)

        # Clip with the bounding box
        bbox_gdf = gpd.GeoDataFrame([1], geometry=[bounding_box], crs='epsg:4326')
        clipped_gdf = gpd.clip(gdf, bbox_gdf)

        return clipped_gdf
