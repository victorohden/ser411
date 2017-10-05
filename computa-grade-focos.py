# encoding: utf-8

import sys

import os

import numpy as np

try:
    from osgeo import gdal, ogr, osr
except:
    sys.exit ("Erro: a biblioteca GDAL não foi encontrada!")

from utils import *

gdal.UseExceptions()
ogr.UseExceptions()
osr.UseExceptions()

vector_file = "/home/labgeo4/Dados/Queimadas/focos/focos-2016.shp"
vector_file_base_name = os.path.basename(vector_file)
layer_name = os.path.splitext(vector_file_base_name)[0]
spatial_extent = {'xmin':-89.975, 'ymin':-59.975,'xmax':-29.975, 'ymax':10.025}
spatial_resolution = {'x':0.05, 'y':0.05}
grid_dimensions = {'cols': 1200, 'rows': 1400}

file_format = "GTiff"
outup_file_name = "/home/labgeo4/Dados/Queimadas/focos/grade-2016.tif"
shp_focos = ogr.Open(vector_file)

if shp_focos is None:
    sys.exit("Erro: não foi possivel abrir o arquivo '{0}'.".format(vector_file))
layer_focos = shp_focos.GetLayer(layer_name)

if layer_focos is None:
    sys.exit("Erro: não foi possivel abrir o arquivo '{0}' no arquivo {1}!.".format(layer_name, vector_file))

matriz = np.zeros((grid_dimensions['rows'], grid_dimensions['cols']), np.int16)

for foco in layer_focos:
    location = foco.GetGeometryRef()

    col, row = Geo2Grid(location, grid_dimensions, spatial_resolution, spatial_extent)

    matriz[row, col] += 1

driver = gdal.GetDriverByName(file_format)

if driver is None:
    sys.exit("Erro: não foi possivel identificar o driver '{0}'.".format(file_format))

raster = driver.Create(outup_file_name, grid_dimensions['cols'], grid_dimensions['rows'], 1, gdal.GDT_UInt16)

if raster is None:
    sys.exit("Erro: não foi possivel criar o arquivo '{0}'.".format(outup_file_name))

raster.SetGeoTransform((spatial_extent['xmin'], spatial_resolution['x'], 0, spatial_extent['ymax'], 0, -spatial_resolution['y']))

srs_focos = layer_focos.GetSpatialRef()
raster.SetProjection(srs_focos.ExportToWkt())

band = raster.GetRasterBand(1)
band.WriteArray(matriz,0,0)

band.FlushCache()