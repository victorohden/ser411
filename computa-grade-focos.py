# encoding: utf-8
import sys
# Carrega a biblioteca OS que fornece funcionalidades
# associadas ao Sistema Operacional
import os
# Carrega a biblioteca NumPy para criação de matrizes
import numpy as np

try:
    from osgeo import gdal, ogr, osr
except:
    sys.exit("Erro: a biblioteca GDAL não foi encontrada!")

from utils import *

gdal.UseExceptions()
ogr.UseExceptions()
osr.UseExceptions()

# Definição de constantes globais do programa
# vector_file = "/home/labgeo4/Dados/Queimadas/focos/focos-2016.shp"
vector_file = r"F:\Materias\python\2016\focos\focos-2016.shp"
vector_file_base_name = os.path.basename(vector_file)
layer_name = os.path.splitext(vector_file_base_name)[0]

spatial_extent = {'xmin': -89.975, 'ymin': -59.975, 'xmax': -29.975, 'ymax': 10.025}
spatial_resolution = {'x': 0.05, 'y': 0.05}
grid_dimensions = {'cols': 1200, 'rows': 1400}

file_format = "GTiff"
# caminho onde serão salvas as imagens
outup_file_path = "F:/Materias/python/2016/focos/"
shp_focos = ogr.Open(vector_file)

# Abrindo arquivo vetorial com focos de queimada
if shp_focos is None:
    sys.exit("Erro: não foi possivel abrir o arquivo '{0}'.".format(vector_file))

layer_focos = shp_focos.GetLayer(layer_name)
if layer_focos is None:
    sys.exit("Erro: não foi possivel abrir o arquivo '{0}' no arquivo {1}!".format(layer_name, vector_file))

sensor = {"TERRA_M-M", "AQUA_M-M", "TERRA_M-T", "AQUA_M-T"}
mes = {1,2,3,4,5,6,7,8,9,10,11,12,13}
#mes = {"01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"}
for x in sensor:  # cada um dos sensores
    for y in mes:  # cada um dos meses
        if mes == 9:
            condicao = "satelite = '%s' and timestamp > '2016/0%s' and timestamp < '2016/%s'" % (x, y, y +1)
        elif mes > 9:
            condicao = "satelite = '%s' and timestamp > '2016/%s' and timestamp < '2016/%s'" % (x, y, y +1)
        else:
            condicao = "satelite = '%s' and timestamp > '2016/0%s' and timestamp < '2016/0%s'" % (x, y, y + 1)
        print (condicao)
        layer_focos.SetAttributeFilter(condicao)
        num_focos = layer_focos.GetFeatureCount()  # contagem do numero de focos
        print("Satélite: {0}; Mês: {1}; Número de focos:{2}".format(x, y, num_focos))

        # Criando uma matriz numérica
        matriz = np.zeros((grid_dimensions['rows'], grid_dimensions['cols']), np.int16)

        # Calculando o número de focos associado a cada celula
        for foco in layer_focos:
            location = foco.GetGeometryRef()  # localização
            col, row = Geo2Grid(location, grid_dimensions, spatial_resolution, spatial_extent)
            matriz[row, col] += 1

        # Criando o raster de saida
        driver = gdal.GetDriverByName(file_format)
        if driver is None:
            sys.exit("Erro: não foi possivel identificar o driver '{0}'.".format(file_format))
        output_file_name = outup_file_path + x + "_mes" + str(y) + "_focos" + ".tiff"
        raster = driver.Create(output_file_name, grid_dimensions['cols'], grid_dimensions['rows'], 1, gdal.GDT_UInt16)

        if raster is None:
            sys.exit("Erro: não foi possivel criar o arquivo '{0}'.".format(outup_file_name))
        raster.SetGeoTransform(
            (spatial_extent['xmin'], spatial_resolution['x'], 0, spatial_extent['ymax'], 0, -spatial_resolution['y']))

        srs_focos = layer_focos.GetSpatialRef()
        raster.SetProjection(srs_focos.ExportToWkt())

        band = raster.GetRasterBand(1)
        band.WriteArray(matriz, 0, 0)

        band.FlushCache()

        raster = None
del raster, band