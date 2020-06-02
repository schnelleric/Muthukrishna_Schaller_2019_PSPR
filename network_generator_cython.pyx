#!python
#cython: language_level=3

import math
import networkx as nx
import random

def human_social_network_prestige_cython((int, int) grid, float geodesic):
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
    cdef int j, r
    cdef float dist, w
    cdef object G, n, nbr, a
    cdef list nbrs, nodes, odds
    cdef dict centrality

    # Set up the graph with connections between neighbors
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)
    r = int(round((grid[0] * grid[1]) / 4))

    while geodesic < nx.average_shortest_path_length(G):
        # Only check for desired geodesic every r iterations as the operation is very time consuming
        for j in range(r):
            # Select random person
            nodes = list(G.nodes)
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
            a = random.choices(nodes, cum_weights=odds, k=1)[0]
            G.add_edge(n, a)

    return G
