#!/usr/bin/env python3

import networkx as nx
import random
import math
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
    Returns a network with the same properties as a human social network, namely high clustering, low average shortest
    distance and a skewed degree distribution. This is achieved by applying an algorithm that makes new connections
    using prestige and distance. The algorithm includes a birth-death process which prevents the network from reaching
    completness.

    Parameters
    ----------
    G : Graph
        Inputted graph of already desired parameters
    initial_nbrs: dict
        Lists the initial neighbours for each node
    d : float
        Strength of the distance decay function
    p : float
        Probability of a node losing most of its edges at a given iteration

    Notes
    -----
    The algorithm works by taking a graph and at each iteration adding an edge between nodes based on prestige
    mechanics. At every iteration there is also a chance that one node gets all but its initial four edges (to its left,
    right, up, and down) removed.
    """
    nodes = list(G.nodes)
    num_nodes = len(nodes)

    # Necessary for graphing change in clustering and geodesic
    x_vals = []
    geos = []
    clustering = []
    degrees = []
    moves_csv = []
    movement = []

    # Used for gathering info on behaviour of removal phase
    starting_edges = nx.number_of_edges(G)
    # count_remove_n = 0
    # count_remove_e = 0
    # count_keep_e = 0
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
                        #     count_keep_e += 1
                        # else:
                        #     count_remove_e += 1

                # Update the connections
                G.remove_node(rmv)
                G.add_node(rmv)
                for choice in to_add:
                    G.add_edge(rmv, choice)

        # Update end of round values
        x_vals.append(iterations)
        geo = nx.average_shortest_path_length(G)
        geos.append(geo)
        clust = nx.average_clustering(G)
        clustering.append(clust)
        move = geo - prev_geo
        movement.append(move)
        prev_geo = geo
        total_degs = [G.degree(n) for n in nodes]
        degrees.append(stats.mean(total_degs))

        check = stats.mean(movement)
        if abs(check) < 0.001:
            in_a_row += 1
        else:
            in_a_row = 0
        moves_csv.append(check)

    # Count averages throughout the life of the network
    m = int(math.sqrt(G.number_of_nodes()))
    degree_avg = stats.mean(degrees)
    degree_std = stats.stdev(degrees)
    movement_avg = stats.mean(movement)
    movement_std = stats.stdev(movement)
    geo_avg = stats.mean(geos)
    geo_std = stats.stdev(geos)
    clustering_avg = stats.mean(clustering)
    clustering_std = stats.stdev(clustering)
    total_edges = nx.number_of_edges(G)

    a, ks_val, ks_p, a1, a2, switch, ks_val2, ks_p2 = ks(G)

    with open('network data.csv', 'a', newline='') as file:

        fields = ['size', 'p', 'decay', 'iterations', 'starting_edges', 'total_edges', 'avg_clust', 'std_clust',
                  'avg_degree', 'std_degree', 'avg_geo', 'std_geo', 'avg_geo_move', 'std_geo_move',
                  'alpha', 'KS', 'p_KS', 'alpha1', 'alpha2', 'x_switch', 'KS_double', 'KS_p_double']
        writer = csv.DictWriter(file, fieldnames=fields)

        row = {}
        row['size'] = '{0}x{0}'.format(m)
        row['p'] = str(p)
        row['decay'] = str(d)
        row['iterations'] = str(iterations)
        row['starting_edges'] = str(starting_edges)
        row['total_edges'] = str(total_edges)
        row['avg_clust'] = str(clustering_avg)
        row['std_clust'] = str(clustering_std)
        row['avg_degree'] = str(degree_avg)
        row['std_degree'] = str(degree_std)
        row['avg_geo'] = str(geo_avg)
        row['std_geo'] = str(geo_std)
        row['avg_geo_move'] = str(movement_avg)
        row['std_geo_move'] = str(movement_std)
        row['alpha'] = str(a)
        row['KS'] = str(ks_val)
        row['p_KS'] = str(ks_p)
        row['alpha1'] = str(a1)
        row['alpha2'] = str(a2)
        row['x_switch'] = str(switch)
        row['KS_double'] = str(ks_val2)
        row['KS_p_double'] = str(ks_p2)

        writer.writerow(row)

    with open('movement.csv', 'a', newline='') as file:

        writer = csv.writer(file)
        writer.writerow(moves_csv)


    # plt.scatter(x_vals, geos, s=10)
    # plt.title("Geodesic Equilibrium")
    # plt.xlabel("# of Iterations")
    # plt.ylabel("Average Geodesic")
    # plt.axhline(3.4, c='black', lw=1)
    # plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Dist -{}\Geo equilibrium small with p of {} {}x{}.png'.format(d, p, m, m))
    # plt.close()
    #
    # plt.scatter(x_vals, clustering, s=10)
    # plt.title("Clustering Equilibrium")
    # plt.xlabel("# of Iterations")
    # plt.ylabel("Clustering Coefficient")
    # plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    # plt.axhline(0.1, c='black', lw=1)
    # plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Dist -{}\Clust equilibrium small with p of {} {}x{}.png'.format(d, p, m, m))
    # plt.close()

    return G

if __name__ == '__main__':
    with open('network data.csv', 'w', newline='') as file:

        fields = ['size', 'p', 'decay', 'iterations', 'starting_edges', 'total_edges', 'avg_clust', 'std_clust',
                  'avg_degree', 'std_degree', 'avg_geo', 'std_geo', 'avg_geo_move', 'std_geo_move',
                  'alpha', 'KS', 'p_KS', 'alpha1', 'alpha2', 'x_switch', 'KS_double', 'KS_p_double']
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

    G1 = nx.grid_2d_graph(16, 16, True)
    G1 = nx.convert_node_labels_to_integers(G1)

    initial_nbrs_G1 = {}
    for n in list(G1.nodes):
        nbrs = [nbr for nbr in G1[n]]
        initial_nbrs_G1[n] = nbrs

    for i in range(51):
        G = G1.copy()
        network_equilibrium(G, initial_nbrs_G1, 4, 0.35 + i/100)
