import random
import networkx as nx
import math
import matplotlib.pyplot as plt
import stats

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

def human_social_network_pop_triad_iterations(grid, iterations, distance, percent):
    """
    Returns a network that mimics human social networks where people try to connect to those who have more connections.
    When a connection is made between person A and person B, there is a chance that person A also connects to one of
    person B's connections.

    Parameters
    ----------
    grid : (int, int)
        Tuple of grid dimensions. Number of nodes in network is grid[0]*grid[1]
    iterations : integer
        Number of iterations to make new edges (connections between individuals)
    distance : integer
        Furthest distance to be considered when connecting to someone
    percent : float
        Chance that when you connect to someone you also connect to one of their connections

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge. The node is more likely to connect to a node
    with many connections. Afterwards that node has a chance to connect to one of their new connection's neighbors.
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

            # Select at random a new connection for n from the list of options
            a = random.choice(optns)
            G.add_edge(n, a)

            # There is a chance that n also connects to a neighbor of its new connection a
            if random.random() < percent:
                more = G.neighbors(n)
                again = []
                # Could also make this process sensitive to prestige
                for node in more:
                    if node not in G.neighbors(a):
                        again.append(node)
                if again != []:
                    b = random.choice(again)
                    G.add_edge(a, b)

                # Alternate direction where a connects to one of n's friends
                # more = []
                # for extra in G.neighbors(a):
                #     if extra not in rmv:
                #         more.append(extra)
                # if more != []:
                #     b = random.choice(more)
                #     G.add_edge(n, b)
        i += 1

    return G

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

def human_social_network_exp_decay(grid, geodesic, l=1):
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
    l : [0, 1, 2]
        Modifier for exponential function
        Higher values lower the clustering coefficient of the graph

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

def human_social_network_exp_decay_all_involve(grid, geodesic):
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

    Notes
    -----
    The algorithm works by creating a grid where nodes are connected to their neighbors
    to the North, South, East, and West. The top and bottom of the grid and left and right
    are connected to form a torus, ensuring all nodes have the same number of edges initially.

    At each iteration one node is selected at random to receive a new edge with a node within a distance of k to them.
    The node is more likely to connect to a node with many connections and that is nearby. Force all nodes to be
    selected for a new connection at some point.
    """
    # Set up the graph with connections between neighbors
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)
    r = int(round((grid[0] * grid[1]) / 10))
    to_use = []

    i = 0
    while geodesic < nx.average_shortest_path_length(G):
        # Only check for desired geodesic every r iterations as the operation is very time consuming
        for j in range(r):
            # Select random person
            if to_use == []:
                to_use = list(G.nodes)
            nodes = list(G.nodes)
            n = random.choice(to_use)
            to_use.remove(n)

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
                        w = G.degree(optn) / ((dist - 1) ** (dist - 1))
                        odds.append(w)

            # Select at random a new connection for n from the list of options given the assigned odds
            a = random.choices(nodes, weights=odds, k=1)[0]
            G.add_edge(n, a)
            i += 1

    print(i)
    return G

def human_social_network_exp_decay_eigen(grid, geodesic, l=1):
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
    l : [0, 1, 2]
        Modifier for exponential function
        Higher values lower the clustering coefficient of the graph

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
    r = int(round((grid[0] * grid[1]) / 10))

    i = 0
    while geodesic < nx.average_shortest_path_length(G):
        # Only check for desired geodesic every r iterations as the operation is very time consuming
        for j in range(r):
            # Select random person
            nodes = list(G.nodes)
            n = random.choice(nodes)
            odds = []
            centrality = nx.eigenvector_centrality_numpy(G)

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
                        w = centrality[optn] / ((dist) ** (dist - l))
                        odds.append(w)

            # Select at random a new connection for n from the list of options given the assigned odds
            a = random.choices(nodes, weights=odds, k=1)[0]
            G.add_edge(n, a)
            i += 1

    print(i)
    return G

def human_social_network_prestige_types(grid, geodesic, decay_type, alpha, beta):
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

    BEST PRESTIGE MODEL AT THE MOMENT
    """
    # Set up the graph with connections between neighbors
    G = nx.grid_2d_graph(grid[0], grid[1], True)
    G = nx.convert_node_labels_to_integers(G)
    r = int(round((grid[0] * grid[1]) / 10))

    if decay_type == "power":
        decay = lambda x: alpha * (x**beta)
    elif decay_type == "exponential":
        decay = lambda x: math.exp(alpha * (x**beta))
    elif decay_type == "exponential log":
        decay = lambda x: math.exp(alpha * (math.log(x)**beta))
    else:
        decay = lambda x: x
    while geodesic < nx.average_shortest_path_length(G):
        # Only check for desired geodesic every r iterations as the operation is very time consuming
        for j in range(r):
            # Select random person
            nodes = list(G.nodes)
            n = random.choice(nodes)
            odds = []
            centrality = nx.eigenvector_centrality_numpy(G)

            for optn in nodes:
                if optn == n:
                    odds.append(0)
                else:
                    dist = nx.shortest_path_length(G, n, optn)
                    # If the option is a neighbor of n then it cannot be connected to again
                    if dist == 1:
                        odds.append(0)
                    else:
                        # Set the odds of being connected to based on eigenvector centrality of the option and its
                        # distance from n
                        w = centrality[optn] / decay(dist)
                        odds.append(w)

            # Select at random a new connection for n from the list of options given the assigned odds
            a = random.choices(nodes, weights=odds, k=1)[0]
            G.add_edge(n, a)
    return G

def network_equilibrium_mult(G, initial_nbrs, p2, val, iterations):
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

    percent_cut = []
    tot_edges = []
    odds_on_cuts = []

    i_vals = []
    geos = []
    count_add_e = 0
    count_remove_n = 0
    clustering = []

    prev_geo = None
    movement_avg = []

    for i in range(iterations):
        count_add_e += 1
        if (i % 500) == 0:
            print(i)
            i_vals.append(i)
            geo = nx.average_shortest_path_length(G)
            geos.append(geo)
            clust = nx.average_clustering(G)
            clustering.append(clust)
            if prev_geo:
                # if geo <= prev_geo:
                #     drops.append(prev_geo - geo)
                # else:
                #     rises.append(geo - prev_geo)
                #     num_rises += 1
                movement_avg.append(geo - prev_geo)
            prev_geo = geo

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

        if random.random() < p2:
            count_remove_n += 1
            rmv = random.choice(nodes)
            nbrs = [nbr for nbr in G[rmv]]
            num_nbrs = len(nbrs)
            to_add = []

            for nbr in nbrs:
                # if nbr in initial_nbrs[rmv]:
                #     to_add.append(nbr)
                # else:
                mutuals = list(nx.common_neighbors(G, rmv, nbr))
                odd = ((len(mutuals) + 1) / num_nbrs)
                if random.random() < odd:
                    to_add.append(nbr)
                    odds_on_cuts.append(odd)

            G.remove_node(rmv)
            G.add_node(rmv)

            percent_cut.append((num_nbrs - len(to_add))/num_nbrs)
            tot_edges.append(num_nbrs)

            for choice in to_add:
                G.add_edge(rmv, choice)

            while nx.is_connected(G) == False:
                added = 0
                smallest_chunk = None
                smallest_value = None
                for chunk in list(nx.connected_components(G)):
                    if smallest_value == None or len(chunk) < smallest_value:
                        smallest_value = len(chunk)
                        smallest_chunk = chunk
                el = random.choice(list(smallest_chunk))
                el_nbrs = [nbr for nbr in G[el]]
                unconnected_original = []
                for or_nbr in initial_nbrs[el]:
                    if or_nbr not in el_nbrs:
                        unconnected_original.append(or_nbr)
                while unconnected_original != [] and added != val:
                    added += 1
                    next = random.choice(unconnected_original)
                    unconnected_original.remove(next)
                    G.add_edge(el, next)
                    count_add_e += 1

                # places_to_connect = []
                # for chunk in list(nx.connected_components(G)):
                #     el = random.choice(list(chunk))
                #     places_to_connect.append(el)
                # edges = itertools.combinations(places_to_connect, 2)
                # G.add_edges_from(edges)

    i_vals.append(iterations)
    geos.append(nx.average_shortest_path_length(G))
    clustering.append(nx.average_clustering(G))

    cuts = int(round(stats.mean(percent_cut), 2) * 100)
    num_nodes = int(math.sqrt(G.number_of_nodes()))
    ratio = round((count_add_e / count_remove_n), 2)
    # rise_avg = round(stats.mean(rises), 2)
    # drop_avg = round(stats.mean(drops), 2)
    movement = round(stats.mean(movement_avg), 2)
    movement_skip_five = round(stats.mean(movement_avg[5:]), 2)
    geo_avg = round(stats.mean(geos), 2)
    geo_avg_skip_five = round(stats.mean(geos[5:]), 2)
    clustering_avg = round(stats.mean(clustering), 2)
    clustering_avg_skip_five = round(stats.mean(clustering[5:]), 2)

    # print("Inputted Geodesic: {}; Outputted Geodesic: {}".format(initial_geodesic, final_geodesic))
    # print("Geodesic Difference: {}".format(final_geodesic - initial_geodesic))
    # print("Inputted Clustering: {}; Outputted Clustering: {}".format(initial_clustering, final_clustering))
    # print("Clustering Difference: {}".format(final_clustering - initial_clustering))
    print("Average clustering coefficient: {}".format(clustering_avg))
    print("Average clustering coefficient ignoring first 5 data points: {}".format(clustering_avg_skip_five))
    print("Removed on average {}% of edges".format(cuts))
    # print("Started with {} edges, added {} edges, removed {} nodes".format(num_edges0, count_add_e, count_remove_n))
    print("Removed 1 node for every {} edges added".format(ratio))
    print("On average geodesic moves by {}".format(movement))
    print("If we ignore the first 5 data point, on average geodesic moves by {}".format(movement_skip_five))
    print("Average geodesic: {}".format(geo_avg))
    print("Average geodesic ignoring first 5 data points: {}".format(geo_avg_skip_five))

    plt.scatter(i_vals, geos, s=10)
    plt.title("Geodesic Equilibrium")
    plt.xlabel("# of Iterations")
    plt.ylabel("Average Geodesic")
    plt.axhline(3.4, c='black', lw=1)
    plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Geo connect {} {} iterations with p of {} {}x{}.png'.format(val, iterations, p2, num_nodes, num_nodes))
    plt.close()

    plt.scatter(i_vals, clustering, s=10)
    plt.title("Clustering Equilibrium")
    plt.xlabel("# of Iterations")
    plt.ylabel("Clustering Coefficient")
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    plt.axhline(0.1, c='black', lw=1)
    plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Clust connect {} {} iterations with p of {} {}x{}.png'.format(val, iterations, p2, num_nodes, num_nodes))
    plt.close()
    return G

def network_equilibrium(G, initial_nbrs, p2, iterations):
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

    percent_cut = []
    tot_edges = []
    odds_on_cuts = []

    i_vals = []
    geos = []
    count_add_e = 0
    count_remove_n = 0
    clustering = []

    prev_geo = None
    movement_avg = []

    for i in range(iterations):
        count_add_e += 1
        if (i % 500) == 0:
            print(i)
            i_vals.append(i)
            geo = nx.average_shortest_path_length(G)
            geos.append(geo)
            clust = nx.average_clustering(G)
            clustering.append(clust)
            if prev_geo:
                # if geo <= prev_geo:
                #     drops.append(prev_geo - geo)
                # else:
                #     rises.append(geo - prev_geo)
                #     num_rises += 1
                movement_avg.append(geo - prev_geo)
            prev_geo = geo

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

        if random.random() < p2:
            count_remove_n += 1
            rmv = random.choice(nodes)
            nbrs = [nbr for nbr in G[rmv]]
            num_nbrs = len(nbrs)
            to_add = []

            for nbr in nbrs:
                # if nbr in initial_nbrs[rmv]:
                #     to_add.append(nbr)
                # else:
                mutuals = list(nx.common_neighbors(G, rmv, nbr))
                odd = ((len(mutuals) + 1) / num_nbrs)
                if random.random() < odd:
                    to_add.append(nbr)
                    odds_on_cuts.append(odd)

            G.remove_node(rmv)
            G.add_node(rmv)

            percent_cut.append((num_nbrs - len(to_add))/num_nbrs)
            tot_edges.append(num_nbrs)

            for choice in to_add:
                G.add_edge(rmv, choice)

            while nx.is_connected(G) == False:
                smallest_chunk = None
                smallest_value = None
                for chunk in list(nx.connected_components(G)):
                    if smallest_value == None or len(chunk) < smallest_value:
                        smallest_value = len(chunk)
                        smallest_chunk = chunk
                el = random.choice(list(smallest_chunk))
                el_nbrs = [nbr for nbr in G[el]]
                unconnected_original = []
                for or_nbr in initial_nbrs[el]:
                    if or_nbr not in el_nbrs:
                        unconnected_original.append(or_nbr)
                if unconnected_original != []:
                    next = random.choice(unconnected_original)
                    G.add_edge(el, next)
                    count_add_e += 1

                # places_to_connect = []
                # for chunk in list(nx.connected_components(G)):
                #     el = random.choice(list(chunk))
                #     places_to_connect.append(el)
                # edges = itertools.combinations(places_to_connect, 2)
                # G.add_edges_from(edges)

    i_vals.append(iterations)
    geos.append(nx.average_shortest_path_length(G))
    clustering.append(nx.average_clustering(G))

    cuts = int(round(stats.mean(percent_cut), 2) * 100)
    num_nodes = int(math.sqrt(G.number_of_nodes()))
    ratio = round((count_add_e / count_remove_n), 2)
    # rise_avg = round(stats.mean(rises), 2)
    # drop_avg = round(stats.mean(drops), 2)
    movement = round(stats.mean(movement_avg), 2)
    movement_skip_five = round(stats.mean(movement_avg[5:]), 2)
    geo_avg = round(stats.mean(geos), 2)
    geo_avg_skip_five = round(stats.mean(geos[5:]), 2)
    clustering_avg = round(stats.mean(clustering), 2)
    clustering_avg_skip_five = round(stats.mean(clustering[5:]), 2)

    # print("Inputted Geodesic: {}; Outputted Geodesic: {}".format(initial_geodesic, final_geodesic))
    # print("Geodesic Difference: {}".format(final_geodesic - initial_geodesic))
    # print("Inputted Clustering: {}; Outputted Clustering: {}".format(initial_clustering, final_clustering))
    # print("Clustering Difference: {}".format(final_clustering - initial_clustering))
    print("Average clustering coefficient: {}".format(clustering_avg))
    print("Average clustering coefficient ignoring first 5 data points: {}".format(clustering_avg_skip_five))
    print("Removed on average {}% of edges".format(cuts))
    # print("Started with {} edges, added {} edges, removed {} nodes".format(num_edges0, count_add_e, count_remove_n))
    print("Removed 1 node for every {} edges added".format(ratio))
    print("On average geodesic moves by {}".format(movement))
    print("If we ignore the first 5 data point, on average geodesic moves by {}".format(movement_skip_five))
    print("Average geodesic: {}".format(geo_avg))
    print("Average geodesic ignoring first 5 data points: {}".format(geo_avg_skip_five))

    plt.scatter(i_vals, geos, s=10)
    plt.title("Geodesic Equilibrium")
    plt.xlabel("# of Iterations")
    plt.ylabel("Average Geodesic")
    plt.axhline(3.4, c='black', lw=1)
    plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Geo {} iterations with p of {} {}x{}.png'.format(iterations, p2, num_nodes, num_nodes))
    plt.close()

    plt.scatter(i_vals, clustering, s=10)
    plt.title("Clustering Equilibrium")
    plt.xlabel("# of Iterations")
    plt.ylabel("Clustering Coefficient")
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    plt.axhline(0.1, c='black', lw=1)
    plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Clust {} iterations with p of {} {}x{}.png'.format(iterations, p2, num_nodes, num_nodes))
    plt.close()
    return G

def network_equilibrium_iterations(G, initial_nbrs, d, p, iterations):
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

    # Used to measure whether the network is in equilibrium
    prev_geo = None
    movement_avg = []

    for i in range(iterations):
        count_add_e += 1
        if (i % 500) == 0:
            # Track stats about the network every 500 iterations
            print(i)
            i_vals.append(i)
            geo = nx.average_shortest_path_length(G)
            geos.append(geo)
            clust = nx.average_clustering(G)
            clustering.append(clust)
            if prev_geo:
                movement_avg.append(geo - prev_geo)
            prev_geo = geo
            total_degs = [G.degree(n) for n in nodes]
            degrees.append(stats.mean(total_degs))

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

    # Track final statistics
    i_vals.append(iterations)
    geo = nx.average_shortest_path_length(G)
    geos.append(geo)
    clust = nx.average_clustering(G)
    clustering.append(clust)
    if prev_geo:
        movement_avg.append(geo - prev_geo)
    total_degs = [G.degree(n) for n in nodes]
    degrees.append(stats.mean(total_degs))

    # Count averages throughout the life of the network
    cuts = int(round(count_remove_e / (count_remove_e + count_keep_e), 2) * 100)
    num_nodes = int(math.sqrt(G.number_of_nodes()))
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

    print("Average clustering coefficient: {}".format(clustering_avg))
    print("Average clustering coefficient ignoring first 5 data points: {}".format(clustering_avg_skip_five))
    print("Average degree: {}".format(degree_avg))
    print("Average degree ignoring first 5 data points: {}".format(degree_avg_skip_five))
    print("Removed on average {}% of edges".format(cuts))
    print("Removed 1 node for every {} edges added".format(node_ratio))
    print("Removed 1 edge for every {} edges added".format(edge_ratio))
    print("On average remove {} edges when a node is removed".format(avg_num_removed))
    print("On average keep {} edges when a node is removed".format(avg_num_maintained))
    print("On average geodesic moves by {}".format(movement))
    print("If we ignore the first 5 data point, on average geodesic moves by {}".format(movement_skip_five))
    print("Average geodesic: {}".format(geo_avg))
    print("Average geodesic ignoring first 5 data points: {}".format(geo_avg_skip_five))

    # plt.scatter(i_vals, geos, s=10)
    # plt.title("Geodesic Equilibrium")
    # plt.xlabel("# of Iterations")
    # plt.ylabel("Average Geodesic")
    # plt.axhline(3.4, c='black', lw=1)
    # plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Dist -{}\Geo {} iterations with p of {} {}x{}.png'.format(d, iterations, p2, num_nodes, num_nodes))
    # plt.close()
    #
    # plt.scatter(i_vals, clustering, s=10)
    # plt.title("Clustering Equilibrium")
    # plt.xlabel("# of Iterations")
    # plt.ylabel("Clustering Coefficient")
    # plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    # plt.axhline(0.1, c='black', lw=1)
    # plt.savefig(r'C:\Users\Eric\Desktop\Equilibrium Graphs\Important\Dist -{}\Clust {} iterations with p of {} {}x{}.png'.format(d, iterations, p2, num_nodes, num_nodes))
    # plt.close()

    return G