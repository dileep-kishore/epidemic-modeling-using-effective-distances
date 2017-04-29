#!/usr/bin/env python3
# @Author: Dileep Kishore <dileep>
# @Last modified by:   dileep

from itertools import starmap
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from network_generation.network_creation import get_data, make_network


def calc_eff_dist(graph):
    """
       Calculate effective distances between countries
       Parameters:
       -----------
       graph : Networkx graph object
           Air traffic network in the EU
       Returns:
       --------
       graph : Networkx grpah object
           Air traffic network with edge_attrb 'd' storing effective distance
       phi : int
           Total flow rate in the network
       omega : int
           Total population of all nodes in the network
       fn : list
           Exit rate at each node
    """
    for node1, node2 in graph.edges_iter():
        try:
            flow = (graph[node1][node2]['f'] + graph[node2][node1]['f']) // 2
        except KeyError:
            flow = graph[node1][node2]['f']
            graph[node2][node1] = {'f': flow}
        graph[node1][node2]['f'] = graph[node2][node1]['f'] = flow
    phi = sum(starmap(lambda n1, n2: graph[n1][n2]['f'], graph.edges_iter()))
    print(f"phi={phi}")
    # FIXME: equation S21 says that fn=cn
    fn = defaultdict(int)
    for node in graph.nodes_iter():
        fn[node] = sum(map(lambda x: x['f'], graph[node].values()))
    omega = sum(map(lambda x: x['pop'], graph.node.values()))
    print(f"omega={omega}")
    for node1, node2 in graph.edges_iter():
        prob = graph[node1][node2]['f'] / fn[node2]
        graph[node1][node2]['d'] = 1 - np.log(prob)
    return graph, phi, omega, fn

def net_with_effdist():
    edge_list, node_list = get_data()
    network = make_network(edge_list, node_attrb=node_list)
    network, phi, omega, fn = calc_eff_dist(network)
    return network, phi, omega, fn

if __name__ == '__main__':
    network, phi, omega, fn = net_with_effdist()
    # nx.write_graphml(network, "network.graphml")
    nx.draw(network)
    plt.savefig("network.png")
