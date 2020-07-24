#!/usr/bin/env python3

import networkx as nx
import random
import math
from network_data import *
import scipy.stats as stats
import csv
import argparse

parser = argparse.ArgumentParser(description="Run prestige network generator")
parser.add_argument('-n', '--size', help='int - network size is nxn', default=15)
parser.add_argument('-d', '--decay', help='float - distance decay strength', default=4)
parser.add_argument('-p', '--birth_death_rate', help='int - frequency of birth-death process', default=0.5)

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

def network_equilibrium(n, d, p, graph=False):
    """
    Returns a network with the same properties as a human social network, namely high clustering, low average shortest
    distance and a skewed degree distribution. This is achieved by applying an algorithm that makes new connections
    using prestige and distance. The algorithm includes a birth-death process which prevents the network from reaching
    completness.

    Parameters
    ----------
    n : int
        Size of network, where the network has nxn nodes
    d : float
        Strength of the distance decay function
    p : float
        Probability of a node losing most of its edges at a given iteration
    graph : bool
        Whether or not the a graph for the geodesics value at each round is printed

    Notes
    -----
    The algorithm works by taking a graph and at each iteration adding an edge between nodes based on prestige
    mechanics. At every iteration there is also a chance that one node gets all but its initial four edges (to its left,
    right, up, and down) removed.
    """
    G = nx.grid_2d_graph(n, n, True)
    G = nx.convert_node_labels_to_integers(G)

    initial_nbrs = {}
    for n in list(G.nodes):
        nbrs = [nbr for nbr in G[n]]
        initial_nbrs[n] = nbrs

    nodes = list(G.nodes)
    num_nodes = len(nodes)

    with open(r'data\{0}x{0} p={1} d={2}.csv'.format(n, p, d), 'w', newline='') as file:

        fields = ['iterations', 'edges', 'geodesic', 'clustering', 'movement', 'avg_degree', 'degree_skew',
                  'alpha', 'KS', 'p_KS', 'alpha1', 'alpha2', 'switch', 'KS_double', 'p_KS_double']
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        start = {}
        start['iterations'] = 0
        start['edges'] = nx.number_of_edges(G)
        geo = nx.average_shortest_path_length(G)
        start['geodesic'] = geo
        start['clustering'] = nx.average_clustering(G)
        start['movement'] = 'N/A'
        degrees = [G.degree(n) for n in nodes]
        start['avg_degree'] = np.mean(degrees)
        start['degree_skew'] = stats.skew(degrees)

        alpha, ks, p_ks, alpha1, alpha2, switch, ks2, p_ks2 = ks_test(G)
        start['alpha'] = alpha
        start['KS'] = ks
        start['p_KS'] = p_ks
        start['alpha1'] = alpha1
        start['alpha2'] = alpha2
        start['switch'] = switch
        start['KS_double'] = ks2
        start['p_KS_double'] = p_ks2

        writer.writerow(start)

        # Necessary for graphing change in clustering and geodesic
        movement = []
        x_vals = [0]
        geos = [geo]

        # Used for gathering info on behaviour of removal phase
        in_a_row = 0
        iterations = 0

        # Used to measure whether the network is in equilibrium
        prev_geo = nx.average_shortest_path_length(G)

        while in_a_row < 3:
            for i in range(num_nodes):
                iterations += 1

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

                # Removal only has a p probability of occurring
                if random.random() < p:
                    # count_remove_n += 1

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
                            # count_keep_e += 1
                        else:
                            # Every other connection is given a probability of maintaining their connection
                            mutuals = list(nx.common_neighbors(G, rmv, nbr))
                            odd = ((len(mutuals) + 1) / num_nbrs)
                            if random.random() < odd:
                                to_add.append(nbr)

                    # Update the connections
                    G.remove_node(rmv)
                    G.add_node(rmv)
                    for choice in to_add:
                        G.add_edge(rmv, choice)

            end_of_round = {}
            end_of_round['iterations'] = iterations
            geo = nx.average_shortest_path_length(G)
            end_of_round['edges'] = nx.number_of_edges(G)
            end_of_round['geodesic'] = geo
            end_of_round['clustering'] = nx.average_clustering(G)
            move = geo - prev_geo
            prev_geo = geo
            end_of_round['movement'] = move
            degrees = [G.degree(n) for n in nodes]
            end_of_round['avg_degree'] = np.mean(degrees)
            end_of_round['degree_skew'] = stats.skew(degrees)

            alpha, ks, p_ks, alpha1, alpha2, switch, ks2, p_ks2 = ks_test(G)
            end_of_round['alpha'] = alpha
            end_of_round['KS'] = ks
            end_of_round['p_KS'] = p_ks
            end_of_round['alpha1'] = alpha1
            end_of_round['alpha2'] = alpha2
            end_of_round['switch'] = switch
            end_of_round['KS_double'] = ks2
            end_of_round['p_KS_double'] = p_ks2

            writer.writerow(end_of_round)

            x_vals.append(iterations)
            geos.append(geo)

            movement.append(move)
            check = np.mean(movement)
            if abs(check) < 0.001:
                in_a_row += 1
            else:
                in_a_row = 0

    if graph:
        plt.scatter(x_vals, geos, s=10)
        plt.title("Geodesic Equilibrium")
        plt.xlabel("# of Iterations")
        plt.ylabel("Average Geodesic")
        plt.axhline(3.4, c='black', lw=1)
        plt.savefig(r'graphs\{0}x{0} p={1} d={2} geodesic.csv'.format(n, p, d))
        plt.close()

    return G


if __name__ == '__main__':
    network_equilibrium(13, 4, 0.75)
