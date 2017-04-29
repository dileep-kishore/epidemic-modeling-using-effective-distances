#!/usr/bin/env python3
# @Author: Dileep Kishore <dileep>
# @Last modified by:   dileep

from functools import partial
from collections import defaultdict
from os import path
import numpy as np
from toolz import compose
from toolz.curried import map as cmap, filter as cfilter


def write_file(air_traffic, data_fol):
    """Write air_traffic dictionary to edgelist file
       Parameters:
       -----------
       air_traffic: Dict
           Dictionary containing key: (source, dest) and value: flow_rate
    """
    fname = data_fol('airtraffic_el.csv')
    with open(fname, 'w') as fid:
        for (source, dest), traffic in air_traffic.items():
            fid.write(','.join([source, dest, str(traffic)]))
            fid.write('\n')
    return None

def catch_int_except(x):
    """Fuction used in int filter returns None if string cannot be converted to int"""
    try:
        int(x)
    except ValueError:
        return None
    else:
        return int(x)

def main(data_fol, data_file):
    """Extract and write air traffic information between countries
       Parameters:
       -----------
       data_fol : partial path.join function
            Partial path function that links to the data directory
        data_file : str
            File name of the input file
    """
    yr_range = tuple(map(str, range(2006, 2016)))
    fname = data_fol(data_file)
    air_traffic = defaultdict(float)
    mean_func = compose(np.mean, list, cfilter(lambda x: x is not None), cmap(catch_int_except))
    with open(fname, 'r') as fid:
        header_finfo, *header_tinfo = next(fid).split('\t')
        header_tinfo = [d.strip() for d in header_tinfo]
        yr_inds = tuple(filter(lambda x: header_tinfo[x] in yr_range, range(len(header_tinfo))))
        for row in fid:
            location, *flow_rate = row.split('\t')
            flow_rate = [d.strip() for d in flow_rate]
            unit, code, source, dest = location.split(',')
            if unit != 'PAS' or code != 'PAS_CRD' or \
            any(map(lambda x: 'EU' in x or 'EA' in x, (source, dest))):
                continue
            air_traffic[(source, dest)] += mean_func(flow_rate[i] for i in yr_inds)
            print(source, dest, air_traffic[(source, dest)])
    write_file(air_traffic, data_fol)
    return air_traffic

if __name__ == '__main__':
    data_dir = partial(path.join, path.abspath('../../data/EU_data/Europe_air_traffic/raw/'))
    infile = 'avia_paocc.tsv'
    traffic_dict = main(data_dir, infile)
