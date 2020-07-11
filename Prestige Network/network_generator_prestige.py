#!/usr/bin/env python3

import networkx as nx
import random
import math
import time
import itertools
from network_data import *
import statistics as stats
import csv

def human_social_network_prestige(grid, geodesic):
    """
    Returns a network that mimics human social networks where people try to connect to those who have more important
    connections, as calculated using eigenvector centrality. Connections are only possible between nodes a distance of
    k apart. Connections between nodes become exponentially less likely the further apart they are from each other.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    geodesic : float
        Desired average shortest path length / degrees of separation (geodesic)
        This will be treated as an upper bound

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge with a node within a distance of k to them.
    The node is more likely to connect to a node with many important connections and that is nearby.
    """
    # Set up the graph with connections between neighbors
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)
    r = int(round((grid[0] * grid[1]) / 4))
    nodes = list(G.nodes)

    # Probably already built in
    initial_nbrs = {}
    for n in nodes:
        nbrs = [nbr for nbr in G[n]]
        initial_nbrs[n] = nbrs

    while geodesic < nx.average_shortest_path_length(G):
        # Only check for desired geodesic every r iterations as the operation is very time consuming
        for j in range(r):
            # Select random person
            n = random.choice(nodes)
            odds = []
            centrality = nx.eigenvector_centrality_numpy(G)
            nbrs = [nbr for nbr in G[n]]
            nbrs.append(n)

            for optn in nodes:
                if optn in nbrs:
                    odds.append(0)
                else:
                    dist = nx.shortest_path_length(G, n, optn)
                    # Set the odds of being connected to based on eigenvector centrality of the option and its
                    # distance from n
                    w = centrality[optn] * math.exp(-2*dist)
                    odds.append(w)

            # Select at random a new connection for n from the list of options given the assigned odds
            a = random.choices(nodes, weights=odds, k=1)[0]
            G.add_edge(n, a)

    return G, initial_nbrs

def network_equilibrium(G, initial_nbrs, d, p):
    """
    Given a graph that has properties of human social networks. Continue to apply processes based on prestige, as well
    as an analogue to individuals dying, maintaining the networks human features.

    Parameters
    ----------
    G : Graph
        Inputted graph of already desired parameters
    p : float
        Probability of a node losing most of its edges at a given iteration
    iterations : int
        Number of iterations to apply equilibrium algorithm

    Notes
    -----
    The algorithm works by taking a graph and at each iteration adding an edge between nodes based on prestige
    mechanics. At every iteration there is also a chance that one node gets all but its initial four edges (to its left,
    right, up, and down) removed.
    """
    nodes = list(G.nodes)
    num_nodes = len(nodes)

    # Necessary for graphing change in clustering and geodesic
    i_vals = []
    geos = []
    clustering = []

    # Used for gathering info on behaviour of removal phase
    count_add_e = 0
    count_remove_n = 0
    count_remove_e = 0
    count_keep_e = 0
    degrees = []
    in_a_row = 0
    count = 0

    # Used to measure whether the network is in equilibrium
    prev_geo = nx.average_shortest_path_length(G)
    movement_avg = []
    prev_check = prev_geo

    while in_a_row < 3:
        for i in range(num_nodes):
            count += 1
            count_add_e += 1

            # Select random person
            n = random.choice(nodes)
            odds = []
            centrality = nx.eigenvector_centrality_numpy(G)
            nbrs = [nbr for nbr in G[n]]
            nbrs.append(n)

            for optn in nodes:
                if optn in nbrs:
                    odds.append(0)
                else:
                    dist = nx.shortest_path_length(G, n, optn)
                    # Set the odds of being connected to based on eigenvector centrality of the option and its
                    # distance from n
                    w = centrality[optn] * math.exp(-d*dist)
                    odds.append(w)

            # Select at random a new connection for n from the list of options given the assigned odds
            a = random.choices(nodes, weights=odds, k=1)[0]
            G.add_edge(n, a)

            # Removal only has a p2 probability of occurring
            if random.random() < p:
                count_remove_n += 1
                # Select node for removal
                rmv = random.choice(nodes)
                # List all neighbours of the node being removed
                nbrs = [nbr for nbr in G[rmv]]
                num_nbrs = len(nbrs)
                to_add = []

                for nbr in nbrs:
                    # The 4 initial neighbours always stay connected
                    if nbr in initial_nbrs[rmv]:
                        to_add.append(nbr)
                        count_keep_e += 1
                    else:
                        # Every other connection is given a probability of maintaining their connection
                        mutuals = list(nx.common_neighbors(G, rmv, nbr))
                        odd = ((len(mutuals) + 1) / num_nbrs)
                        if random.random() < odd:
                            to_add.append(nbr)
                            count_keep_e += 1
                        else:
                            count_remove_e += 1

                # Update the connections
                G.remove_node(rmv)
                G.add_node(rmv)
                for choice in to_add:
                    G.add_edge(rmv, choice)

        print(count)
        i_vals.append(count)
        geo = nx.average_shortest_path_length(G)
        geos.append(geo)
        clust = nx.average_clustering(G)
        clustering.append(clust)
        move = geo - prev_geo
        movement_avg.append(move)
        prev_geo = geo
        total_degs = [G.degree(n) for n in nodes]
        degrees.append(stats.mean(total_degs))

        # if len(movement_avg) > 4: # In 70k (4) In 56k (5)
        #     check = stats.mean(movement_avg[4:])
        # else:
        #     check = 10
        check = stats.mean(movement_avg) # This never finished for 30x30
        # curr = stats.mean(geos)
        # check = curr - prev_check
        # prev_check = curr
        if abs(check) < 0.001:
            in_a_row += 1
        else:
            in_a_row = 0
        print(round(check, 4))

    if in_a_row != 3:
        print("You Failed bud")

    # Count averages throughout the life of the network
    cuts = int(round(count_remove_e / (count_remove_e + count_keep_e), 2) * 100)
    m = int(math.sqrt(G.number_of_nodes()))
    node_ratio = round((count_add_e / count_remove_n), 2)
    edge_ratio = round((count_add_e / count_remove_e), 2)
    movement_skip_five = round(stats.mean(movement_avg[5:]), 2)
    movement = round(stats.mean(movement_avg), 2)
    geo_avg = round(stats.mean(geos), 2)
    geo_avg_skip_five = round(stats.mean(geos[5:]), 2)
    clustering_avg = round(stats.mean(clustering), 2)
    clustering_avg_skip_five = round(stats.mean(clustering[5:]), 2)
    degree_avg = round(stats.mean(degrees), 2)
    degree_avg_skip_five = round(stats.mean(degrees[5:]), 2)
    avg_num_removed = round((count_remove_e / count_remove_n), 2)
    avg_num_maintained = round((count_keep_e / count_remove_n), 2)
    total_edges = nx.number_of_edges(G)

    with open('network.csv', 'w', newline='') as file:
        fieldnames = ['size', 'p', 'decay', 'iterations', 'avg_clust', 'avg_clust_skip_5', 'avg_degree',
                      'avg_degree_skip_5', 'total_edges', 'removed_edges', 'avg_geo', 'avg_geo_skip_5',
                      'avg_geo_move', 'avg_geo_move_skip_5']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'size': '{0}x{0}'.format(m), 'p': str(p), 'decay': str(d), 'iterations': str(count),
                         'avg_clust': str(clustering_avg), 'avg_clust_skip_5': str(clustering_avg_skip_five),
                         'avg_degree': str(degree_avg), 'avg_degree_skip_5': str(degree_avg_skip_five),
                         'total_edges': str(total_edges), 'removed_edges': str(count_remove_e), 'avg_geo': str(geo_avg),
                         'avg_geo_skip_5': str(geo_avg_skip_five), 'avg_geo_move': str(movement),
                         'avg_geo_move_skip_5': str(movement_skip_five)})

    # print("Average clustering coefficient: {}".format(clustering_avg))
    # print("Average clustering coefficient ignoring first 5 data points: {}".format(clustering_avg_skip_five))
    # print("Average degree: {}".format(degree_avg))
    # print("Average degree ignoring first 5 data points: {}".format(degree_avg_skip_five))
    # print("Removed on average {}% of edges".format(cuts))
    # print("Removed 1 node for every {} edges added".format(node_ratio))
    # print("Removed 1 edge for every {} edges added".format(edge_ratio))
    # print("On average remove {} edges when a node is removed".format(avg_num_removed))
    # print("On average keep {} edges when a node is removed".format(avg_num_maintained))
    # print("On average geodesic moves by {}".format(movement))
    # print("If we ignore the first 5 data point, on average geodesic moves by {}".format(movement_skip_five))
    # print("Average geodesic: {}".format(geo_avg))
    # print("Average geodesic ignoring first 5 data points: {}".format(geo_avg_skip_five))

    # plt.scatter(i_vals, geos, s=10)
    # plt.title("Geodesic Equilibrium")
    # plt.xlabel("# of Iterations")
    # plt.ylabel("Average Geodesic")
    # plt.axhline(3.4, c='black', lw=1)
    # plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Dist -{}\Geo equilibrium small with p of {} {}x{}.png'.format(d, p, m, m))
    # plt.close()
    #
    # plt.scatter(i_vals, clustering, s=10)
    # plt.title("Clustering Equilibrium")
    # plt.xlabel("# of Iterations")
    # plt.ylabel("Clustering Coefficient")
    # plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    # plt.axhline(0.1, c='black', lw=1)
    # plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Dist -{}\Clust equilibrium small with p of {} {}x{}.png'.format(d, p, m, m))
    # plt.close()

    return G

if __name__ == '__main__':
    # Example Networks
    # G, initial_nbrs_G = human_social_network_prestige((30, 30), 3.4)
    # G1 = nx.grid_2d_graph(13, 13, True)
    # G1 = nx.convert_node_labels_to_integers(G1)
    #
    # # Probably already built in
    # initial_nbrs_G1 = {}
    # for n in list(G1.nodes):
    #     nbrs = [nbr for nbr in G1[n]]
    #     initial_nbrs_G1[n] = nbrs
    #
    # G1 = network_equilibrium(G1, initial_nbrs_G1, 4, 0.77)
    # ks(G1)
    #
    # G4 = nx.grid_2d_graph(15, 15, True)
    # G4 = nx.convert_node_labels_to_integers(G4)
    #
    # # Probably already built in
    # initial_nbrs_G4 = {}
    # for n in list(G4.nodes):
    #     nbrs = [nbr for nbr in G4[n]]
    #     initial_nbrs_G4[n] = nbrs
    #
    # G4 = network_equilibrium(G4, initial_nbrs_G4, 4, 0.67)
    # ks(G4)

    G5 = nx.grid_2d_graph(30, 30, True)
    G5 = nx.convert_node_labels_to_integers(G5)

    # Probably already built in
    initial_nbrs_G5 = {}
    for n in list(G5.nodes):
        nbrs = [nbr for nbr in G5[n]]
        initial_nbrs_G5[n] = nbrs

    G5 = network_equilibrium(G5, initial_nbrs_G5, 4, 0.33)
    ks(G5)

    #
    #
    # G2 = nx.grid_2d_graph(40, 40, True)
    # G2 = nx.convert_node_labels_to_integers(G2)
    #
    # # Probably already built in
    # initial_nbrs_G2 = {}
    # for n in list(G2.nodes):
    #     nbrs = [nbr for nbr in G2[n]]
    #     initial_nbrs_G2[n] = nbrs
    #
    # G2 = network_equilibrium(G2, initial_nbrs_G2, 0.25, 50000)

    # G3 = nx.grid_2d_graph(5, 5, True)
    # G3 = nx.convert_node_labels_to_integers(G3)
    #
    # # Probably already built in
    # initial_nbrs_G3 = {}
    # for n in list(G3.nodes):
    #     nbrs = [nbr for nbr in G3[n]]
    #     initial_nbrs_G3[n] = nbrs
    #
    # G3 = network_equilibrium(G3, initial_nbrs_G3, 1, 50000)
    # degree_distribution_plot(G3)

    # degree_distribution_plot(G1)
    # degree_distribution_plot(G4)
    degree_distribution_plot(G5)
    # degree_distribution_plot(G2)
    # degree_distribution_plot(G3)

    plt.show()