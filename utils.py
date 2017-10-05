import sys

def Geo2Grid (location, dimensions, resolution, extent):

    x = location.GetX()
    y = location.GetY()

    col = int((x - extent['xmin'])/resolution['x'])

    row = int (dimensions['rows']-(y - extent['ymin'])/resolution['y'])

    return col, row