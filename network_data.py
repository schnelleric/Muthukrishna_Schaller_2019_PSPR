#!/usr/bin/env python3

import matplotlib.pyplot as plt
import collections
import networkx as nx
from scipy import stats

def degree_distribution_plot(G):
    """
    Makes a plot for the degree distribution of the inputted graph where the y axis corresponds to the fraction of nodes
    in the graph and the x axis corresponds to the degree of a node. The y axis uses a logarithmic scale.

    Parameters
    ----------
    G : Graph
        A graph corresponding to a human social network.

    Notes
    -----
    Currently there exists an issue where if the fraction of nodes with a given degree is too small it is omitted from
    the plot.
    """

    # Adapted from https://networkx.github.io/documentation/stable/auto_examples/drawing/plot_degree_histogram.html
    degrees = [G.degree(n) for n in G.nodes]
    degreeCount = collections.Counter(degrees)
    deg, cnt = zip(*degreeCount.items())
    cnt_frac = []
    for i in range(len(cnt)):
        cnt_frac.append(cnt[i] / G.number_of_nodes())

    plt.scatter(deg, cnt_frac, s=10)

    plt.title("Degree Distribution")
    plt.ylabel("Fraction")
    # Have issue where if a fraction is too close to zero it will not appear on the plot
    plt.yscale("log")
    # Need to ensure only uses whole numbers on the x axis
    plt.xlabel("Degree")
    plt.xscale("linear")

    plt.show()

def statistics(G):
    """
    Prints the characteristic path length (geodesic) of the inputted network, the clustering coefficient of the inputted
    network, and Kolmogorov-Smirnov test results for the similarity of the degree distribution with a power law
    distribution of the inputted network.

    Parameters
    ----------
    G : Graph
        A graph corresponding to a human social network.

    Notes
    -----
    I believe the KS test is working correctly however there are currently no networks that pass it so it is unclear if
    it is actually working.
    """

    curr_geodesic = nx.average_shortest_path_length(G)
    curr_clustering = nx.average_clustering(G)
    degrees = [G.degree(n) for n in G.nodes]
    alphas = []
    alpha = 0.1
    while alpha < 5:
        alphas.append(round(alpha, 1))
        alpha += 0.1
    best_alpha = None
    best_ks = None
    best_p = None
    for a in alphas:
        ks, p = stats.kstest(rvs=degrees, cdf='powerlaw', args=(a,))
        if best_p == None or p > best_p:
            best_alpha, best_ks, best_p = a, ks, p

    print("Geodesic: " + str(curr_geodesic) + "; Clustering: " + str(curr_clustering) +
          "; Degree Distribution: alpha = " + str(best_alpha) + ", KS = " + str(best_ks) + ", p = " + str(best_p))

    return (curr_geodesic, curr_clustering, best_alpha, best_ks, best_p)
