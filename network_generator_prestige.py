#!/usr/bin/env python3

import networkx as nx
import random
from network_data import *

def human_social_network_k_algorithm(grid, geodesic, k):
    """
    Returns a network that mimics human social networks where people try to connect to those who have more connections.
    Connections are only possible between nodes a distance of k apart.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions
        Number of nodes in network is grid[0]*grid[1]
    geodesic : float
        Desired average shortest path length / degrees of separation (geodesic)
        This will be treated as an upper bound
    k : integer
        Furthest distance to be considered when connecting to someone

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge with a node within a distance of k to them.
    The node is more likely to connect to a node with many connections.
    """
    # Set up the graph with connections between neighbors
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)
    r = int(round((grid[0] * grid[1]) / 10))

    i = 0
    while geodesic < nx.average_shortest_path_length(G):
        # Only check for desired geodesic every r iterations as the operation is very time consuming
        for j in range(r):
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

def human_social_network_decay(grid, geodesic, k, decay_type):
    """
    Returns a network that mimics human social networks where people try to connect to those who have more connections.
    Connections are only possible between nodes a distance of k apart. Connections between nearby nodes are more likely.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    geodesic : float
        Desired average shortest path length / degrees of separation (geodesic)
        This will be treated as an upper bound
    k : integer
        Furthest distance to be considered when connecting to someone
    decay_type : ['linear', 'square', 'exponential']
        Type of decay function to be used when considering nodes further away from ego

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge with a node within a distance of k to them.
    The node is more likely to connect to a node with many connections and that is nearby.
    """
    # Set up the graph with connections between neighbors
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)
    r = int(round((grid[0] * grid[1]) / 10))

    i = 0
    while geodesic < nx.average_shortest_path_length(G):
        # Only check for desired geodesic every r iterations as the operation is very time consuming
        for j in range(r):
            # Select random person
            n = random.choice(list(G.nodes))

            # List out all nodes close enough to connect to
            close_nodes = list(nx.single_source_shortest_path(G, n, cutoff=k).keys())
            odds = []

            for optn in close_nodes:
                if optn == n:
                    odds.append(0)
                else:
                    dist = nx.shortest_path_length(G, n, optn)
                    # If the option is a neighbor of n then it cannot be connected to again
                    if dist == 1:
                        odds.append(0)
                    else:
                        # Set the odds of being connected to based on the distance from n and the decay function chosen
                        if decay_type == 'linear':
                            w = G.degree(optn) / (dist)
                        elif decay_type == 'square':
                            w = G.degree(optn) / (dist ** 2)
                        elif decay_type == 'exponential':
                            w = G.degree(optn) / (dist ** dist)
                        else:
                            w = G.degree(optn)
                        odds.append(w)

            # Select at random a new connection for n from the list of options given the assigned odds
            a = random.choices(close_nodes, weights=odds, k=1)[0]
            G.add_edge(n, a)
            i += 1

    print(i)
    return G

def human_social_network_exp_decay(grid, geodesic, l):
    """
    Returns a network that mimics human social networks where people try to connect to those who have more connections.
    Connections are only possible between nodes a distance of k apart. Connections between nodes become exponentially
    less likely the further apart they are from each other.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    geodesic : float
        Desired average shortest path length / degrees of separation (geodesic)
        This will be treated as an upper bound
    l : [0, 1]
        Modifier for exponential function
        If 1, the clustering coefficient of the graph will be slightly lower

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge with a node within a distance of k to them.
    The node is more likely to connect to a node with many connections and that is nearby.
    """
    # Set up the graph with connections between neighbors
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)
    r = int(round((grid[0] * grid[1]) / 10))

    i = 0
    while geodesic < nx.average_shortest_path_length(G):
        # Only check for desired geodesic every r iterations as the operation is very time consuming
        for j in range(r):
            # Select random person
            nodes = list(G.nodes)
            n = random.choice(nodes)
            odds = []

            for optn in nodes:
                if optn == n:
                    odds.append(0)
                else:
                    dist = nx.shortest_path_length(G, n, optn)
                    # If the option is a neighbor of n then it cannot be connected to again
                    if dist == 1:
                        odds.append(0)
                    else:
                        # Set the odds of being connected to based on the distance from n and an exponential decay
                        # function
                        # If l is 1, then further nodes will be slightly favoured and thus clustering will slightly
                        # decrease
                        w = G.degree(optn) / ((dist - l) ** (dist - l))
                        odds.append(w)

            # Select at random a new connection for n from the list of options given the assigned odds
            a = random.choices(nodes, weights=odds, k=1)[0]
            G.add_edge(n, a)
            i += 1

    print(i)
    return G

if __name__ == '__main__':
    # Example Networks

    # G = human_social_network_k_algorithm((30, 30), 3.4, 4)
    # H = human_social_network_decay((30, 30), 3.4, 4, "normal")
    # I = human_social_network_decay((30, 30), 3.4, 4, "square")
    # J = human_social_network_decay((30, 30), 3.4, 4, "exponential")
    # K = human_social_network_exp_decay((30, 30), 3.4, 0)
    # L = human_social_network_exp_decay((30, 30), 3.4, 1)
    # M = nx.powerlaw_cluster_graph(900, 3, 0.25)
    N = human_social_network_exp_decay((15, 15), 3.4, 0)
    O = human_social_network_exp_decay((15, 15), 3.4, 1)
    # P = nx.powerlaw_cluster_graph(225, 2, 0.15)

    degree_distribution_plot(N)
    statistics(N)
    degree_distribution_plot(O)
    statistics(O)
    plt.show()
