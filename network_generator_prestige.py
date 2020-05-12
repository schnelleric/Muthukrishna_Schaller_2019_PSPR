#!/usr/bin/env python3

import networkx as nx
import random
from scipy import stats
from network_data import *
import numpy
from human_social_network_generator34 import *

def human_social_network_mutual_iterations(grid, iterations):
    """
    Returns a network that mimics human social networks where a connection between two people is more likely if they
    have more mutual acquaintances.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to make new edges (connections between individuals)

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
        # optns.append('other') Remove to only appear in mutual case

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

    return G

def human_social_network_pop_iterations(grid, iterations, distance):
    """
    Returns a network that mimics human social networks where people try to connect to people who have more connections.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to make new edges (connections between individuals)
    distance : integer
        Furthest distance to be considered when connecting to someone without mutual acquaintances

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge. The node is more likely to connect to a node
    with many connections.
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
        # Ensures there exists a node to be connected to
        if optns != []:
            a = random.choice(optns)
            G.add_edge(n, a)
        i += 1

    return G

def human_social_network_mutual_pop_iterations(grid, iterations, distance):
    """
    Returns a network that mimics human social networks where a connection between two people is more likely if they
    have more mutual acquaintances. People can also connect to someone with whom they share no mutual connections but
    who have many connections.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to make new edges (connections between individuals)
    distance : integer
        Furthest distance to be considered when connecting to someone without mutual acquaintances

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge. The edge will be more likely to connect two
    individuals if they have many mutual acquaintances. If they connect to someone without a mutual acquaintance then
    they are more likely to connect to someone with a lot of connections.

    Does not scale well. As population gets larger, prestige must be reduced to reach good level of clustering.
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
            new_choices = nx.single_source_shortest_path(G, n, cutoff=distance).keys()
            others = []
            for node in new_choices:
                if node not in rmv and node not in choices:

                    # More popular nodes are more likely to be connected to
                    count = G.degree(node)
                    for j in range(count):
                        others.append(node)
            # Ensures there exists a node to be connected to
            if others == []:
                a = n
            else:
                a = random.choice(others)
        G.add_edge(n, a)
        i += 1

    return G

def human_social_network_prestige_fixed_flat_iterations(grid, iterations, pres_percent):
    """
    Returns a network that mimics human social networks where a connection between two people is more likely if they
    have more mutual acquaintances or are prestigious.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to make new edges (connections between individuals)
    pres_percent : float
        Percent of the population who is prestigious

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge. The edge will be more likely to connect two
    individuals if they have many mutual acquaintances while also allowing the possibility to connect the randomly
    selected node to a prestigious individual.

    Prestige is flat which means individuals are either prestigious or not, there is no in between. Prestige is also
    static.
    """
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)

    # Set default prestige to not prestigious
    nx.set_node_attributes(G, 0, 'prestige')

    # Select x percent (as given in parameters) of the population at random to be prestigious
    num_pres = round((grid[0]*grid[1])*pres_percent)
    pres = random.choices(list(G.nodes), k=num_pres)
    node_to_pres = {}
    for node in pres:
        node_to_pres[node] = 1
    nx.set_node_attributes(G, node_to_pres, 'prestige')

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
        # If meet someone else it would be someone with prestige
        optns += pres

        # Remove friends from list of options
        choices = [c for c in optns if c not in rmv]

        # Select randomly from list and create a new edge with that person (become friends)
        a = random.choice(choices)

        G.add_edge(n, a)
        i += 1

    return G

def human_social_network_prestige_fixed_flat_ext_iterations(grid, iterations, pres_percent, connect_dist, *args):
    """
    Returns a network that mimics human social networks where a connection between two people is more likely if they
    have more mutual acquaintances or are prestigious. People also have an extraversion parameter which dictates how
    likely they are to make new connections.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to make new edges (connections between individuals)
    pres_percent : float
        Percent of the population who is prestigious
    connect_dist : function
        Distribution function from which to draw probability of connection / migration values.
    args : arguments
        Arguments needed for the probability distribution

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge. The edge will be more likely to connect two
    individuals if they have many mutual acquaintances while also allowing the possibility to connect the randomly
    selected node to a prestigious individual.

    Prestige is flat which means individuals are either prestigious or not, there is no in between. Prestige is also
    static.

    Extraversion is included in this model and assigned to individuals from a given distribution. More extraverted
    individuals are more likely to make connections.

    Assume that the most extraverted individuals in the network are the ones who will be prestigious. (MAYBE INCORRECT)

    Have a feeling adding extraversion complicates the model without improving it.
    """
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)
    ext_to_node = {}

    # Give each node an extraversion value from a given distribution
    for node in list(G.nodes):
        nx.set_node_attributes(G, {node:connect_dist(*args)}, 'extraversion')

        # Make dictionary of extraversion value to each node, important for finding k most extraverted people
        ext_value = nx.get_node_attributes(G, 'extraversion')[node]
        if ext_value not in ext_to_node:
            ext_to_node[ext_value] = []
        ext_to_node[ext_value] += [node]

    # Set default prestige to not prestigious
    nx.set_node_attributes(G, 0, 'prestige')

    # Set the top x percent (as provided in parameters) of most extraverted people to being prestigious
    # Assumes extraversion and prestige are related
    # Could change to make extraverted individuals be more likely to be prestigious but not guaranteed to be prestigious
    num_pres = round((grid[0]*grid[1])*pres_percent)
    ext_sorted = sorted(ext_to_node.keys(), reverse=True)
    pres = []
    for j in range(num_pres):
        pres += ext_to_node[ext_sorted[j]]
    node_to_pres = {}
    for node in pres:
        node_to_pres[node] = 1
    nx.set_node_attributes(G, node_to_pres, 'prestige')

    i = 0
    while i < iterations:
        # Select random person
        n = random.choice(list(G.nodes))
        if random.random() < nx.get_node_attributes(G,'extraversion')[n]:
            optns = []
            rmv = [n]

            # List out friends of friends (the more connections to the person the more times they appear on list)
            for nbr in list(G.neighbors(n)):
                for optn in list(G.neighbors(nbr)):
                    optns.append(optn)
                rmv.append(nbr)

            # Add an option to meet someone who is not the friend of a friend
            # If meet someone else it would be someone with prestige
            optns += pres

            # Remove friends from list of options
            choices = [c for c in optns if c not in rmv]

            # Select randomly from list and create a new edge with that person (become friends)
            a = random.choice(choices)

            G.add_edge(n, a)
            i += 1

    return G

if __name__ == '__main__':
    # Example Networks

    # G = human_social_network_mutual_iterations((30, 30), 7000)
    # H = human_social_network_pop_iterations((30, 30), 3000, 3)
    # I = human_social_network_pop_iterations((30, 30), 6000, 2)
    # J = human_social_network_mutual_pop_iterations((30, 30), 7000, 4)
    K = human_social_network_prestige_fixed_flat_iterations((15, 15), 200, 0.1)
    # beta_params = [[4, 4], [2.5, 3.5], [3.5, 2.5]]
    # L = human_social_network_prestige_fixed_flat_ext_iterations((30, 30), 1750, 0.05, numpy.random.beta, *beta_params[0])
    # M = human_social_network_iterations((30, 30), 50, False, random.betavariate, *beta_params[0])

    degree_distribution_plot(K)
    statistics(K)
    # degree_distribution_plot(L)
    # statistics(L)
    # degree_distribution_plot(M)
    # statistics(M)
    plt.show()
