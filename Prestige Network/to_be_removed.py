import random
import networkx as nx
import math

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