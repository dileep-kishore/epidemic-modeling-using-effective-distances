#!/usr/bin/env python3
# @Author: Dileep Kishore <dileep>
# @Last modified by:   dileep

import math
from functools import partial
from itertools import starmap
from os import path
import csv
from collections import defaultdict, namedtuple
import numpy as np


CoordXYZ = namedtuple('CoordXYZ', ['x', 'y', 'z'])
CoordLatLon = namedtuple('CoordLatLon', ['lat', 'lon'])

def cnvrt_to_cart(coord):
    """Convert latitude and longitude to cartesian"""
    x = math.cos(coord.lat) * math.cos(coord.lon)
    y = math.cos(coord.lat) * math.sin(coord.lon)
    z = math.sin(coord.lat)
    return CoordXYZ(x=x, y=y, z=z)

def cnvrt_to_latlon(coord):
    """Convert cartesian to latitude and longitude"""
    lon = math.atan2(coord.y, coord.x)
    hyp = math.sqrt(coord.x ** 2 + coord.y ** 2)
    lat = math.atan2(coord.z, hyp)
    return CoordLatLon(lat=lat, lon=lon)

def coord_calc(lat, lon):
    """
        Calculate Catersian coordiantes given latitude and longitude
        Parameters:
        -----------
        lat : float
            Latitude in degrees. South is negative
        lon : float
            Longitude in degrees. West is negative
        Returns:
        --------
        coord_tuple : tuples
            (CoordXYZ, CoordLatLon)
    """
    lat, lon = map(lambda x: math.radians(float(x)), [lat, lon])
    lat_lon = CoordLatLon(lat=lat, lon=lon)
    return lat_lon, cnvrt_to_cart(lat_lon)

def write_file(cntry_locmap, data_fol):
    """
        Write centroid of international airport for each country into a file
        Parameters:
        -----------
        cntry_locmap : map object
            Iterator of tuples (cntry, loc) where loc is np.array
    """
    fname = data_fol('parsed_geolocation.csv')
    with open(fname, 'w') as fid:
        csvwriter = csv.writer(fid)
        for cntry, loc in cntry_locmap:
            row = [cntry, str(loc.lat), str(loc.lon)]
            csvwriter.writerow(row)
    return None

def main(data_fol, data_file):
    """
        Extract geographical airport coordinates
        Parameters:
        -----------
        data_fol : partial path.join function
            Partial path function that links to the data directory
        data_file : str
            File name of the input file
    """
    ind_dict = {'airport': 1, 'country': 3, 'lat': 6, 'lon': 7}
    loc_dict = defaultdict(list)
    fname = data_fol(data_file)
    get_centroid = lambda x: cnvrt_to_latlon(CoordXYZ(*np.mean(x, axis=0)))
    with open(fname, 'r') as fid:
        csvreader = csv.reader(fid, quotechar='"')
        for row in csvreader:
            row_dict = dict([(k, row[v]) for k, v in ind_dict.items()])
            country = row_dict['country']
            latlon, xyz = coord_calc(row_dict['lat'], row_dict['lon'])
            loc_dict[country].append(xyz)
    loc_map = starmap(lambda cntry, locs: (cntry, get_centroid(locs)),
                      loc_dict.items())
    write_file(loc_map, data_fol)
    return loc_map

if __name__ == '__main__':
    DATA_DIR = partial(path.join, path.abspath('../../data/openflights/'))
    INFILE = 'airports.dat.txt'
    main(DATA_DIR, INFILE)
