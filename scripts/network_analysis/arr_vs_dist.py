#!/usr/bin/env python3
# @Author: Dileep Kishore <dileep>
# @Last modified by:   dileep

import csv
from math import sin, cos, atan2, sqrt
from os import path
from functools import partial
from collections import defaultdict, namedtuple
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import networkx as nx
from network_generation.short_eff_paths import net_with_effdist


def yr_to_num(year):
    yyyy, week = year.split('-')
    return int(yyyy) + (float(week[1:]) - 1) /53

def make_plot(disease_dict):
    curr_palette = sns.color_palette("hls", len(disease_dict))
    sns.set_palette(curr_palette)
    fig = plt.figure()
    ax = plt.subplot(111)
    for k, v in disease_dict.items():
        x, y = zip(*v)
        ax.plot(x, y, label=k)
    ax.legend(bbox_to_anchor=(0.75, 1.05), loc='upper center', ncol=2)
    plt.xlabel('Time')
    plt.ylabel('Number of infections')
    fig.savefig('plot.png')

def plt_time_series(graph, data_file):
    """
        Plot time series data of influenza infections in the EU
    """
    node_set = set(map(lambda x: x['name'], graph.node.values()))
    dis_prog = defaultdict(list)
    with open(data_file, 'r') as fid:
        csvreader = csv.reader(fid, delimiter=',')
        for yr, country, h1n1, total_dis in csvreader:
            # if yr_to_num(yr) < 2009 or yr_to_num(yr) > 2010.5:
            if yr_to_num(yr) < 2009:
                continue
            if not h1n1:
                h1n1 = '0'
            if country in node_set:
                dis_prog[country].append((yr_to_num(yr), int(h1n1)))
    make_plot(dis_prog)

def  calc_arr_times(graph, data_file, thres=5):
    """
        Calculate arrival times of H1N1 for each node in the network
        Parameters:
        -----------
        graph : Networkx.graph
            Air-traffic network with edge_attrb 'd' having effective distance
        data_file : str
            File containing infection data at various time-points
        Returns:
        --------
        arr_dict : Dict
            Dictionary that contains the arrival times (float_year) for every country
    """
    node_set = set(map(lambda x: x['name'], graph.node.values()))
    first_obs = 0
    arr_dict = dict()
    with open(data_file, 'r') as fid:
        csvreader = csv.reader(fid, delimiter=',')
        for yr, country, h1n1, total_dis in csvreader:
            if h1n1:
                if first_obs == 0 and int(h1n1) > thres and country in node_set:
                    first_obs = yr_to_num(yr)
                    first_outbreak = country
                if int(h1n1) > thres and country in node_set:
                    arr_dict[country] = yr_to_num(yr)-first_obs
                    node_set.remove(country)
            if not node_set:
                break
    return arr_dict, first_outbreak

def get_shortest_paths(graph, source):
    name_dict = {v['name']: k for k, v in graph.node.items()}
    sp_dict = nx.shortest_path_length(graph, source=name_dict[source], weight='d')
    dist_dict = dict()
    for cntry, eff_dist in sp_dict.items():
        dist_dict[graph.node[cntry]['name']] = eff_dist
    return dist_dict

CoordXYZ = namedtuple('CoordXYZ', ['x', 'y', 'z'])
CoordLatLon = namedtuple('CoordLatLon', ['lat', 'lon'])

def get_geo_dists(graph, source, geofile):
    """
        Calculate the geographical distance from source node to all other countries
    """
    def great_circle_dist(p1, p2, alt=12.192):
        lat1, lon1 = p1.lat, p1.lon
        lat2, lon2 = p2.lat, p2.lon
        dlat, dlon = lat2-lat1, lon2-lon1
        a = sin(dlat/2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon/2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        R = 6371 + alt
        return R * c

    node_set = set(map(lambda x: x['name'], graph.node.values()))
    geo_pos = dict()
    with open(geofile, 'r') as fid:
        csvreader = csv.reader(fid)
        for cntry, *loc in csvreader:
            if cntry in node_set:
                lat, lon = map(float, loc)
                lat_lon = CoordLatLon(lat=lat, lon=lon)
                geo_pos[cntry] = lat_lon
    geo_dict = dict()
    for k, v in geo_pos.items():
        geo_dict[k] = great_circle_dist(v, geo_pos[source])
    return geo_dict

def plot_shortest_path(dist_dict, arr_dict, source_country, thres):
    x, y = [], []
    for k in arr_dict:
        x.append(dist_dict[k])
        y.append(arr_dict[k])
    fig = plt.figure()
    df = pd.DataFrame(data={'Arrival time': y, 'Effective distance': x})
    g = sns.jointplot(x='Effective distance', y='Arrival time', data=df, kind='reg')
    plt.title(f'Source={source_country},Threshold={thres}', y=0.08)
    plt.xlim(xmin=0)
    g.savefig(f'{source_country}_arr_vs_effdist.png')
    return None

def plot_geo_dist(geo_dict, arr_dict, source_country, thres):
    x, y = [], []
    print(f"{geo_dict}")
    for k in arr_dict:
        x.append(geo_dict[k])
        y.append(arr_dict[k])
    df = pd.DataFrame(data={'Arrival time': y, 'Geographical distance': x})
    g = sns.jointplot(x='Geographical distance', y='Arrival time', data=df, kind='reg', color='green')
    plt.title(f'Source={source_country},Threshold={thres}', y=0.08)
    plt.xlim(xmin=0)
    g.savefig(f'{source_country}_arr_vs_geodist.png')
    return None

if __name__ == '__main__':
    # PROCESS: Network generation
    network, phi, omega, fn = net_with_effdist()
    # INPUT: Flu data
    data_dir = partial(path.join, path.abspath('../data/flu_data/'))
    disease_data = data_dir('h1n1_data.csv')
    # INPUT: Geo locations
    geo_data = '../data/openflights/parsed_geolocation.csv'
    # PARAMETER: Flu threshold
    threshold = 100
    # PROCESS: Get Arrival times
    arrival_dict, first_country = calc_arr_times(network, disease_data, thres=threshold)
    # plt_time_series(network, disease_data)
    fig = plt.figure()
    # PROCESS: Shortest paths
    dist_dict = get_shortest_paths(network, first_country)
    plot_shortest_path(dist_dict, arrival_dict, first_country, threshold)
    # PROCESS: Geographical distances
    geo_dict = get_geo_dists(network, first_country, geo_data)
    plot_geo_dist(geo_dict, arrival_dict, first_country, threshold)
    nx.write_gml(network, 'final_network.gml')
