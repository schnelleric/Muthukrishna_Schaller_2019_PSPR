#!python
#cython: language_level=3

import math
import networkx as nx
import random
import itertools

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
            a = random.choices(nodes, weights=odds, k=1)[0]
            G.add_edge(n, a)

    return G

def network_equilibrium_cython(object G, float p1, float p2, int iterations):
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
    cdef int i, r, ind
    cdef float dist, w
    cdef object n, nbr, a, optn, rmv, selection, choice, chunk, el, edges
    cdef list nbrs, nodes, odds, mutuals, selections, places_to_connect
    cdef dict centrality
    cdef float initial_clustering, initial_geodesic, final_clustering, final_geodesic


    initial_geodesic = nx.average_shortest_path_length(G)
    initial_clustering = nx.average_clustering(G)

    for i in range(iterations):
        nodes = list(G.nodes)
        if random.random() < p1:
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
                    w = centrality[optn] * math.exp(-2 * dist)
                    odds.append(w)

            # Select at random a new connection for n from the list of options given the assigned odds
            a = random.choices(nodes, weights=odds, k=1)[0]
            G.add_edge(n, a)

        if random.random() < p2:
            rmv = random.choice(nodes)
            nbrs = [nbr for nbr in G[rmv]]
            odds = []

            for nbr in nbrs:
                mutuals = list(nx.common_neighbors(G, rmv, nbr))
                odds.append(len(mutuals) + 1)

            G.remove_node(rmv)
            G.add_node(rmv)

            selections = []
            if len(nbrs) <= 3:
                selections = nbrs
            else:
                for j in range(3):
                    selection = random.choices(nbrs, weights=odds)[0]
                    ind = nbrs.index(selection)
                    nbrs.pop(ind)
                    odds.pop(ind)
                    selections.append(selection)

            for choice in selections:
                G.add_edge(rmv, choice)

            if nx.is_connected(G) == False:
                places_to_connect = []
                for chunk in list(nx.connected_components(G)):
                    el = random.choice(list(chunk))
                    places_to_connect.append(el)
                edges = itertools.combinations(places_to_connect, 2)
                G.add_edges_from(edges)


    final_geodesic = nx.average_shortest_path_length(G)
    final_clustering = nx.average_clustering(G)
    print("Inputted Geodesic: {}; Outputted Geodesic: {}".format(initial_geodesic, final_geodesic))
    print("Geodesic Difference: {}".format(initial_geodesic-final_geodesic))
    print("Inputted Clustering: {}; Outputted Clustering: {}".format(initial_clustering, final_clustering))
    print("Clustering Difference: {}".format(initial_clustering-final_clustering))

    # return G
