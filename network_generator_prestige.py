#!/usr/bin/env python3

import networkx as nx
import random
from scipy import stats


def human_social_network_mutual_iterations(grid, iterations):
    """
    Returns a network that mimics human social networks where a connection between two people is more likely if they
    have more mutual acquaintances.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to run movement function (i.e. how many opportunities
        should each node have to move)

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge. The edge can only connect the node with one
    of its neighbour's neighbours. The more of these mutual acquaintances exist, the more likely these two nodes are to
    be connected.
    """

    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)

    i = 0
    while i < iterations:
        # Select random person
        n = random.choice(list(G.nodes))
        optns = []
        rmv = [n]

        # List out friends of friends (the more connections to the person the more times they appear on list)
        for nbr in list(G.neighbors(n)):
            for optn in list(G.neighbors(nbr)):
                optns.append(optn)
            rmv.append(nbr)

        # Add an option to meet someone who is not the friend of a friend
        optns.append('other')

        # Remove friends from list of options
        choices = [c for c in optns if c not in rmv]

        # Select randomly from list and create a new edge with that person (become friends)
        a = random.choice(choices)

        # If select to meet someone who isn't a friend of a friend then ensure they are a path of only 3 or 4 away
        # Can't meet someone too distant from you
        if a == 'other':
            new_choices = nx.single_source_shortest_path(G, n, cutoff=4).keys()
            others = [b for b in new_choices if b not in rmv and b not in choices]
            a = random.choice(list(set(others)))
        G.add_edge(n, a)
        i += 1

    curr_geodesic = nx.average_shortest_path_length(G)
    curr_clustering = nx.average_clustering(G)
    degrees = [G.degree(n) for n in G.nodes]
    curr_skew_degree = stats.skew(degrees)

    print("Geodesic: " + str(curr_geodesic) + "; Clustering: " + str(curr_clustering) + "; Skew: " + str(
    curr_skew_degree))

    return G

G = human_social_network_mutual_iterations((30, 30), 7000)