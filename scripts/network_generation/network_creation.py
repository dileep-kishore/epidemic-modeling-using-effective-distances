#!/usr/bin/env python3
# @Author: Dileep Kishore <dileep>
# @Last modified by:   dileep

import csv
from os import path
from functools import partial
from collections import deque
import matplotlib.pyplot as plt
import networkx as nx

def net_from_elist(erow, graph):
    flow_rate = erow.pop()
    try:
        flow_per_day = round(float(flow_rate)/365)
    except ValueError:
        return None
    if flow_per_day < 1:
        return None
    graph.add_nodes_from(erow)
    graph.add_edge(*erow, f=flow_per_day)
    return None

def update_nodes(nrow, graph):
    node_name, node_key, node_pop = nrow
    if node_key in graph.nodes():
        nx.set_node_attributes(graph, 'name', {node_key: node_name})
        nx.set_node_attributes(graph, 'pop', {node_key: int(node_pop)})
        # graph[node_key]['name'] = node_name
        # graph[node_key]['pop'] = int(node_pop)
    return None

def make_network(edge_list, node_attrb=None, edge_attrb=None):
    """
        Create a network from edgelist and append node and edge attributes
        Parameters:
        -----------
        edge_list : str
            File containing the list of edges in the GMN
        node_attrb : str
            File containing extra attributes for each node
        edge_attrb : str
            File containing extra attributes for each edge
    """
    G = nx.DiGraph()
    net_updater = partial(net_from_elist, graph=G)
    with open(edge_list, 'r') as eid:
        deque(map(net_updater, csv.reader(eid)), maxlen=0)
    if node_attrb:
        node_updater = partial(update_nodes, graph=G)
        with open(node_attrb, 'r') as nid:
            deque(map(node_updater, csv.reader(nid)), maxlen=0)
    if edge_attrb:
        pass
    G = remove_self_loops(G)
    return G

def remove_self_loops(graph):
    """Remove self loops in the network (these constitute local flights)
       Parameters:
       -----------
       graph: Networkx graph object
    """
    for node in graph.nodes_with_selfloops():
        graph.remove_edge(node, node)
    return graph

def get_data():
    data_dir = partial(path.join, path.abspath('../data/EU_data/Europe_air_traffic/'))
    EDGE_LIST, NODE_LIST = map(data_dir,
                               ['airtraffic_el.csv', 'country_population.csv'])
    return EDGE_LIST, NODE_LIST

if __name__ == '__main__':
    edge_list, node_list = get_data()
    network = make_network(edge_list, node_attrb=node_list)
    # nx.write_graphml(network, "network.graphml")
    # nx.draw(network)
    # plt.savefig("network.png")
