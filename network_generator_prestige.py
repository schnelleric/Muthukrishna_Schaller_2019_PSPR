#!/usr/bin/env python3

import networkx as nx
import random
from network_data import *

def human_social_network_k_algorithm(grid, geodesic, k):
    """
    Returns a network that mimics human social networks where people try to connect to those who have more connections.
    When a connection is made between person A and person B, there is a chance that person A also connects to one of
    person B's connections.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to make new edges (connections between individuals)
    distance : integer
        Furthest distance to be considered when connecting to someone
    percent : float
        Chance that when you connect to someone you also connect to one of their connections

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge. The node is more likely to connect to a node
    with many connections. Afterwards that node has a chance to connect to one of their new connection's neighbors.
    """
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)

    i = 0
    while geodesic < nx.average_shortest_path_length(G):
        for j in range(100):
            # Select random person
            n = random.choice(list(G.nodes))
            optns = []
            rmv = [n]
            rmv.append(G.neighbors(n))

            # Look at all nodes within a set distance from n
            close_nodes = nx.single_source_shortest_path(G, n, cutoff=k).keys()
            for optn in close_nodes:

                # If a node is not already connected to n then add it to the list of possible options based on how many
                # connections it has (how prestigious it is)
                if optn not in rmv:
                    count = G.degree(optn)
                    for j in range(count):
                        optns.append(optn)
            # Ensures there exists a node to be connected to
            if optns != []:

                # Select at random a new connection for n from the list of options
                a = random.choice(optns)
                G.add_edge(n, a)

            i += 1


    print(i)
    return G

if __name__ == '__main__':
    # Example Networks

    G = human_social_network_k_algorithm((30, 30), 3.4, 3)
    H = nx.powerlaw_cluster_graph(900, 3, 0.25)
    # I = human_social_network_k_algorithm((15, 15), 3.4, 3)
    # J = nx.powerlaw_cluster_graph(225, 2, 0.15)

    degree_distribution_plot(G)
    statistics(G)
    degree_distribution_plot(H)
    statistics(H)
    plt.show()
