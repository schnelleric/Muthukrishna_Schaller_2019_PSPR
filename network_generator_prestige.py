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

    At each iteration one node is selected at random to receive a new edge. The edge will be more likely to connect two
    individuals if they have many mutual acquaintances.
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
        # optns.append('other') Remove to only appear in prestige case

        # Remove friends from list of options
        choices = [c for c in optns if c not in rmv]

        # Select randomly from list and create a new edge with that person (become friends)
        a = random.choice(choices)

        # If select to meet someone who isn't a friend of a friend then ensure they are a path of only 4 away
        # Can't meet someone too distant from you
        '''
        if a == 'other':
            new_choices = nx.single_source_shortest_path(G, n, cutoff=4).keys()
            others = [b for b in new_choices if b not in rmv and b not in choices]
            a = random.choice(list(set(others)))
        '''

        G.add_edge(n, a)
        i += 1

    curr_geodesic = nx.average_shortest_path_length(G)
    curr_clustering = nx.average_clustering(G)
    degrees = [G.degree(n) for n in G.nodes]
    curr_skew_degree = stats.skew(degrees)

    print("Geodesic: " + str(curr_geodesic) + "; Clustering: " + str(curr_clustering) + "; Skew: " + str(
    curr_skew_degree))

    return G

def human_social_network_prestige_iterations(grid, iterations, distance):
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

    At each iteration one node is selected at random to receive a new edge. The node is more likely to connect to
    another node with many connections.
    """
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)

    i = 0
    while i < iterations:
        # Select random person
        n = random.choice(list(G.nodes))
        optns = []
        rmv = [n]
        rmv.append(G.neighbors(n))

        # Look at all nodes within a set distance from n
        close_nodes = nx.single_source_shortest_path(G, n, cutoff=distance).keys()
        for optn in close_nodes:

            # If a node is not already connected to n then add it to the list of possible options based on how many
            # connections it has (how prestigious it is)
            if optn not in rmv:
                count = G.degree(optn)
                for j in range(count):
                    optns.append(optn)
        a = random.choice(optns)
        G.add_edge(n, a)
        i += 1

    curr_geodesic = nx.average_shortest_path_length(G)
    curr_clustering = nx.average_clustering(G)
    degrees = [G.degree(n) for n in G.nodes]
    curr_skew_degree = stats.skew(degrees)

    print("Geodesic: " + str(curr_geodesic) + "; Clustering: " + str(curr_clustering) + "; Skew: " + str(
    curr_skew_degree))

    return G

def human_social_network_mutual_prestige_iterations(grid, iterations):
    """
    Returns a network that mimics human social networks where people try to connect with others with more connections.

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

    At each iteration one node is selected at random to receive a new edge. The edge will be more likely to connect two
    individuals if they have many mutual acquaintances. If they connect to someone without a mutual acquaintance then
    they are more likely to connect to someone with a lot of connections.
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

        # If select to meet someone who isn't a friend of a friend then ensure they are a path of only 4 away
        # Can't meet someone too distant from you
        if a == 'other':
            new_choices = nx.single_source_shortest_path(G, n, cutoff=4).keys()
            others = []
            for node in new_choices:
                if node not in rmv and node not in choices:

                    # More prestigious nodes are more likely to be connected to
                    count = G.degree(node)
                    for j in range(count):
                        others.append(node)
            a = random.choice(others)
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
H = human_social_network_prestige_iterations((30, 30), 3000, 3)
I = human_social_network_prestige_iterations((30, 30), 6000, 2)
J = human_social_network_mutual_prestige_iterations((30, 30), 7000)