import math

def latlon_to_webmercator(lon, lat):
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180
    return x, y

def convert_geom_to_3857(geom):
    converted_geom = []
    for ring in geom:
        converted_ring = []
        for poly in ring:
            converted_poly = []
            for coord in poly:
                x, y = latlon_to_webmercator(coord[0], coord[1])
                converted_poly.append([x, y])
            converted_ring.append(converted_poly)
        converted_geom.append(converted_ring)
    return converted_geom
