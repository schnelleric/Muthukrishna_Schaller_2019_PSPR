#!/usr/bin/env python3

import matplotlib.pyplot as plt
import collections
import networkx as nx
import scipy.stats as stats
import scipy.optimize as optimize
import numpy as np

def degree_distribution_plot(G):
    """
    Makes a plot for the degree distribution of the inputted graph where the y axis corresponds to the fraction of nodes
    in the graph and the x axis corresponds to the degree of a node. Both axes uses a logarithmic scale.

    Parameters
    ----------
    G : Graph
        A graph corresponding to a human social network.

    Notes
    -----
    Values on axes are predetermined and may not be optimal for a given graph.
    """

    # Adapted from https://networkx.github.io/documentation/stable/auto_examples/drawing/plot_degree_histogram.html
    num_nodes = G.number_of_nodes()
    degrees = [G.degree(n) for n in G.nodes]
    degreeCount = collections.Counter(degrees)
    deg, cnt = zip(*degreeCount.items())
    cnt_frac = []
    for i in range(len(cnt)):
        cnt_frac.append(cnt[i] / num_nodes)

    plt.scatter(deg, cnt_frac, s=10)

    plt.title("Degree Distribution")
    plt.ylabel("Fraction")
    plt.yscale("log")
    y_ticks = [1, 0.1, 0.01, 0.001, 0.0001]
    plt.yticks(y_ticks, y_ticks)
    plt.xlabel("Degree")
    plt.xscale("log")
    x_ticks = [3, 30, 300]
    plt.xticks(x_ticks, x_ticks)

    plt.show(block=False)

def double_power_pdf(xs, x_min, alpha1, alpha2, switch):
    vals = []
    for x in xs:
        if x < switch:
            val = ((alpha1 - 1)/x_min) * ((x / x_min) ** (-alpha1))
        else:
            val = ((alpha1 - 1)/x_min) * ((switch / x_min)**(-alpha1)) * ((x / switch) ** (-alpha2))
        vals.append(val)
    return vals

def double_power_cdf(xs, x_min, alpha1, alpha2, switch):
    vals = []
    for x in xs:
        if x < switch:
            val = ((x_min * (x ** alpha1)) - ((x_min ** alpha1) * x)) / (x_min * (x ** alpha1))
        else:
            val = ((x_min * (switch ** alpha1)) - ((x_min ** alpha1) * switch)) / (x_min * (switch ** alpha1))
            val += ((alpha1 - 1) * (x_min ** (alpha1 - 1)) * (switch * (x ** (alpha2)) - ((switch ** alpha2) * x)) *
                    (switch ** (-alpha1)) * (x ** (-alpha2))) / (alpha2 - 1)
        vals.append(val)
    return vals

def ks_test(G):
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
    KS test currently not working properly.
    """
    num_nodes = G.number_of_nodes()
    degrees = [G.degree(n) for n in G.nodes]
    degreeCount = collections.Counter(degrees)
    deg, cnt = zip(*degreeCount.items())
    cnt_frac = []
    for i in range(len(cnt)):
        cnt_frac.append(cnt[i] / num_nodes)

    sort_deg = sorted(deg)
    x_min = sort_deg[0]
    sort_cnt = []
    for degree in sort_deg:
        val = degreeCount[degree] / num_nodes
        sort_cnt.append(val)

    single_pdf = lambda x, alpha: ((alpha - 1)/x_min) * ((x / x_min) ** (-alpha))
    a = optimize.curve_fit(single_pdf, deg, cnt_frac)[0][0]
    single_cdf = lambda x: ((x_min * (x ** a)) - ((x_min ** a) * x)) / (x_min * (x ** a))
    ks1, p1 = stats.kstest(deg, single_cdf)

    double_pdf = lambda xs, a1, a2, switch: double_power_pdf(xs, x_min, a1, a2, switch)
    a1, a2, switch = optimize.curve_fit(double_pdf, deg, cnt_frac, bounds=([-np.inf, -np.inf, x_min], [np.inf, np.inf, np.inf]))[0]
    double_cdf = lambda xs: double_power_cdf(xs, x_min, a1, a2, switch)
    ks2, p2 = stats.kstest(deg, double_cdf)

    return (a, ks1, p1, a1, a2, switch, ks2, p2)