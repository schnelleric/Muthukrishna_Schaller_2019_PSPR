#!/usr/bin/env python3
"""
Created on Apr 5, 2018

Changed to handle networkx1.9.1 on the Harvard server
@author: Michael Muthukrishna
"""

import networkx as nx
from scipy import stats
import random
import subprocess


def _migrate(location, grid, torus):
    """
    Parameters
    ----------
    location : dict
        Dictionary of nodes and current position
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    torus : boolean
        If True, nodes can migrate from one edge to another
        (e.g. from (0,0) to (10,0) for a size 10 grid)
        If False, edges are imposed. There are arguments for doing both

    Notes
    -----
    Nodes can migrate to adjacent nodes to the North, South, East, or West
    """
    location = (location[0] + random.choice([-1, 0, 1]), location[1] + random.choice([-1, 0, 1]))

    if torus:
        location0 = location[0]
        location1 = location[1]
        if location[0] < 0:
            location0 = grid[0] - 1
        elif location[0] >= grid[0]:
            location0 = 0

        if location[1] < 0:
            location1 = grid[1] - 1
        elif location[1] >= grid[1]:
            location1 = 0

        location = (location0, location1)
    else:
        location = (max(min(grid[0], location[0]), 0), max(min(grid[1], location[1]), 0))

    return location


def _run_sim(G, locations, grid):
    """
    Gives each person the opportunity to move based on extraversion probability
    """
    overlaps = {}
    for person in range(0, len(G.nodes())):
        if random.random() < G.node[person]['extraversion']:
            current_location = locations[person]
            new_location = _migrate(current_location, grid, True)
            if new_location in overlaps:
                for friend in overlaps[new_location]:
                    G.add_edge(person, friend)
                temp_location_list = overlaps[new_location]
                temp_location_list.append(person)
                overlaps[new_location] = temp_location_list
            else:
                overlaps[new_location] = [person]
            locations[person] = new_location

    return (G, locations)


def human_social_network(grid, geodesic, connect_dist, *args):
    """
    Returns a network of a specified degree distribution where clustering
    and geodesic are close to realistic values in comparable sized ground-truth
    human social network

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    geodesic : float
        Desired average shortest path length / degrees of separation (geodesic).
        This will be treated as an upper bound.
    connect_dist : function
        Distribution function from which to draw probability of connection / migration values.
    args : arguments
        Arguments needed for the probability distribution

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.
    Each node has a probability of 'migrating', referred to as 'extraversion'
    (which is one source of this probability), drawn from the connect_dist
    distribution.
    If two nodes are at the same grid position, an edge is created between
    these two nodes.
    This typically results in realistic network parameters. The process can continue until the desired
    geodesic value is reached.

    """

    G = nx.grid_2d_graph(grid[0], grid[1], True)
    node_count = 0
    grid_locations = {}

    # Set up grid
    # print("Stage1")
    for i in range(0, grid[0]):
        for j in range(0, grid[1]):
            grid_locations[node_count] = (i, j)
            G.add_node((i, j), extraversion=connect_dist(*args))
            node_count = node_count + 1
    G = nx.convert_node_labels_to_integers(G)

    # Continue movement process until network required geodesic is reached
    i = 0
    curr_geodesic = nx.average_shortest_path_length(G)
    while (geodesic < curr_geodesic):
        G, grid_locations = _run_sim(G, grid_locations, grid)
        curr_geodesic = nx.average_shortest_path_length(G)
        i = i + 1
        # print("Stage2:" + str(i) + "," + str(curr_geodesic))

    return G


def human_social_network_iterations(grid, iterations, output_geodesic, connect_dist, *args):
    """
    Returns a network of a specified degree distribution where clustering
    and geodesic are close to realistic values in comparable sized ground-truth
    human social network

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to run movement function (i.e. how many opportunities
        should each node have to move)
    output_geodesic : boolean
        If True, outputs the geodesic on each iteration (takes longer)
    connect_dist : function
        Distribution function from which to draw probaility of connection / migration values.
    args : arguments
        Arguments needed for the probability distribution

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.
    Each node has a probability of 'migrating', referred to as 'extraversion'
    (which is one source of this probability), drawn from the connect_dist
    distribution.
    If two nodes are at the same grid position, an edge is created between
    these two nodes.
    This typically results in realistic network parameters. The process
    can continue for the specified number of iterations.

    """

    G = nx.grid_2d_graph(grid[0], grid[1], True)
    node_count = 0
    grid_locations = {}

    # Set up grid
    if output_geodesic:
        print("Stage1")
    for i in range(0, grid[0]):
        for j in range(0, grid[1]):
            grid_locations[node_count] = (i, j)
            G.add_node((i, j), extraversion=connect_dist(*args))
            node_count = node_count + 1
    G = nx.convert_node_labels_to_integers(G)

    # Continue movement process for specified number of iterations
    i = 0
    curr_geodesic = nx.average_shortest_path_length(G)
    while (i < iterations):
        G, grid_locations = _run_sim(G, grid_locations, grid)
        i = i + 1
        if output_geodesic:
            curr_geodesic = nx.average_shortest_path_length(G)
            print("Stage2:" + str(i) + "," + str(curr_geodesic))
        # else:
        #     print("Stage2:" + str(i))
    # curr_geodesic = nx.average_shortest_path_length(G)
    # curr_clustering = nx.average_clustering(G)
    # degrees = [d for n, d in G.degree_iter()]
    # curr_skew_degree = stats.skew(degrees)

    # print("Geodesic:" + str(curr_geodesic) + ";Clustering: " + str(curr_clustering) + ";Skew:" + str(
    # curr_skew_degree))
    return G


def human_social_network_iterations_correlated(grid, iterations, output_geodesic, *args):
    """
    Returns a network of a specified degree distribution where clustering
    and geodesic are close to realistic values in comparable sized ground-truth
    human social network. Assigns a second variable based on correlated values
    generated by the generate_corr_beta.R script.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to run movement function (i.e. how many opportunities
        should each node have to move)
    output_geodesic : boolean
        If True, outputs the geodesic on each iteration (takes longer)
    args : arguments
        Arguments needed for R script

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.
    Each node has a probability of 'migrating', referred to as 'extraversion'
    (which is one source of this probability), drawn from the connect_dist
    distribution.
    If two nodes are at the same grid position, an edge is created between
    these two nodes.
    This typically results in realistic network parameters. The process
    can continue for the specified number of iterations.

    """

    G = nx.grid_2d_graph(grid[0], grid[1], True)
    node_count = 0
    grid_locations = {}

    # Get correlated values
    raw_df_string = subprocess.check_output(['Rscript', 'generate_corr_beta.R'] + [str(n) for n in args])
    df = raw_df_string.decode().splitlines()

    # Set up grid
    if output_geodesic:
        print("Stage1")
    for i in range(0, grid[0]):
        for j in range(0, grid[1]):
            grid_locations[node_count] = (i, j)

            ext_conf_vals = df[node_count + 1].split()
            G.add_node((i, j), extraversion=float(ext_conf_vals[1]))
            G.add_node((i, j), conformity=float(ext_conf_vals[2]))

            node_count = node_count + 1
    G = nx.convert_node_labels_to_integers(G)

    # Continue movement process for specified number of iterations
    i = 0
    curr_geodesic = nx.average_shortest_path_length(G)
    while (i < iterations):
        G, grid_locations = _run_sim(G, grid_locations, grid)
        i = i + 1
        if output_geodesic:
            curr_geodesic = nx.average_shortest_path_length(G)
            print("Stage2:" + str(i) + "," + str(curr_geodesic))
        # else:
        #     print("Stage2:" + str(i))
    # curr_geodesic = nx.average_shortest_path_length(G)
    # curr_clustering = nx.average_clustering(G)
    # degrees = [d for n, d in G.degree_iter()]
    # curr_skew_degree = stats.skew(degrees)

    # print("Geodesic:" + str(curr_geodesic) + ";Clustering: " + str(curr_clustering) + ";Skew:" + str(
    # curr_skew_degree))
    return G
