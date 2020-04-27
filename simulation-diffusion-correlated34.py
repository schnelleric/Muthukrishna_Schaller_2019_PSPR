#!/usr/bin/env python3
"""
Created on Apr 5, 2018

Converting code to Python 3.4 so it can run on Harvard server.
This version uses correlated values for extraversion and conformity.

@author: Michael Muthukrishna
"""

import pathlib
import argparse
from human_social_network_generator34 import human_social_network_iterations, \
    human_social_network, human_social_network_iterations_correlated
from numpy import random
import math
import csv
import copy as C
from MyNetworkFunctions import *

debug_mode = False
output_json_graphs = False
# Create the folder for storing the output files (if it doesn't exist)
data_folder = "./data_corr/"
# pathlib.Path(data_folder).mkdir(exist_ok=True)

beta_params = [[4, 4], [2.5, 3.5], [3.5, 2.5]]

conversion_threshold = 0.5
ext_conf_corr = -0.3

parser = argparse.ArgumentParser(description="Run DSIT simulation over Muthukrishna-Schaller network")
parser.add_argument('-e', '--extraversion', help='-1=negative skew, 0=approximate normal, 1=positive skew',
                    required=(not debug_mode), default=0)
parser.add_argument('-c', '--conformity', help='-1=negative skew, 0=approximate normal, 1=positive skew',
                    required=(not debug_mode), default=0)
parser.add_argument('-i', '--iterations', help='int - number of iterations', required=(not debug_mode), default=10)
parser.add_argument('-n', '--sim_num', help='int - number of simulation', required=(not debug_mode), default=-1)
parser.add_argument('-d', '--disciples', help='int - number of disciples', required=(not debug_mode), default=0)


#############################################################################
#### Helper functions #######################################################
#############################################################################
def shouldIChange(graph, nodeNum):
    conformity = graph.node[nodeNum]['conformity']
    myValue = graph.node[nodeNum]['value']
    sameTally = 0
    diffTally = 0

    neighbors = graph.neighbors(nodeNum)
    for n in neighbors:
        if graph.node[n]['value'] == myValue:
            sameTally = sameTally + 1
        else:
            diffTally = diffTally + 1

    prob_of_conforming = conformity * diffTally / (sameTally + diffTally)
    if (random.random() < prob_of_conforming):
        return True
    return False


def simulate(graph, fileName, disciples=0, iterations=1):
    random.seed()
    graphSummaryDataFileName = fileName + '.csv'
    f = open(graphSummaryDataFileName, 'w')
    fields = ['iteration', 'gen', 'influenceMoveCount', '0:1 Distribution']
    csvwr = csv.DictWriter(f, fieldnames=fields, delimiter=',')
    csvwr.writeheader()

    for i in range(0, iterations):
        if debug_mode:
            print("Iteration:" + str(i))
        g = C.deepcopy(graph)
        # Set all nodes to 0. While you're doing that, find the most extraverted person (Jesus)
        jesus_ext = 0
        jesus = g.nodes()[0]
        for node in g.nodes():
            if g.node[node]['extraversion'] > jesus_ext:
                jesus_ext = g.node[node]['extraversion']
                jesus = node
            g.add_node(node, value=0)

        # Create the revolutionary - Jesus
        g.add_node(jesus, value=1)
        g.add_node(jesus, conformity=0)

        # Also convert disciples
        if disciples > 0:
            jesus_friends = g.neighbors(jesus)
            if disciples < len(jesus_friends):
                apostles = random.choice(jesus_friends, disciples, False)
                for node in apostles:
                    g.add_node(node, value=1)
            else:
                for node in jesus_friends:
                    g.add_node(node, value=1)

        data = {}
        data['iteration'] = i
        data['gen'] = 0
        data['influenceMoveCount'] = 0
        # =======================================================================
        # data['meanSimilar'] = meanSimilarityCoefficient(g)
        # muthClump = muthukrishnaClumpiness(g)
        # data['meanClumpSize'] = N.mean(muthClump)
        # data['numClumps'] = len(muthClump)
        # valComm = valueCommunities(g)
        # data['meanCommunitySize'] = N.mean(map(len, valComm))
        # data['numCommunities'] = len(valComm)
        # data['influenceMoveCount'] = 0
        # =======================================================================
        converted = zeroToOne(g)
        data['0:1 Distribution'] = converted
        csvwr.writerow(data)
        # Save graph
        if output_json_graphs:
            save_to_jsonfile(fileName + '_iter_' + str(i) + '_gen_' + str(0) + '.json', g)

        # Select random node and apply social influence rules until nNodes generations of no change
        nStayedSame = 0
        count = 0
        numNodes = len(g.nodes())
        while (nStayedSame < 2 * numNodes and converted > conversion_threshold):
            if debug_mode:
                print("Count:" + str(count))
            count = count + 1
            randNode = random.choice(g.nodes())
            # calculate if value should change and change if necessary
            if (shouldIChange(g, randNode)):
                newValue = (g.node[randNode]['value'] + 1) % 2
                g.add_node(randNode, value=newValue)
                nStayedSame = 0
            else:
                nStayedSame = nStayedSame + 1

            converted = zeroToOne(g)

        # If you want to write every generation, indent this under the while loop.
        # Here I'm just outputting at the beginning and end to save space
        data = {}
        data['iteration'] = i
        data['gen'] = count
        data['influenceMoveCount'] = count
        # ===================================================================
        # data['meanSimilar'] = meanSimilarityCoefficient(g)
        # muthClump = muthukrishnaClumpiness(g)
        # data['meanClumpSize'] = N.mean(muthClump)
        # data['numClumps'] = len(muthClump)
        # valComm = valueCommunities(g)
        # data['meanCommunitySize'] = N.mean(map(len, valComm))
        # data['numCommunities'] = len(valComm)
        # data['influenceMoveCount'] = count
        # ===================================================================
        converted = zeroToOne(g)
        data['0:1 Distribution'] = converted
        csvwr.writerow(data)
        if output_json_graphs:
            save_to_jsonfile(fileName + '_iter_' + str(i) + '_gen_' + str(count + 1) + '.json', g)
    f.close()


if __name__ == '__main__':
    args = parser.parse_args()
    Gs = []
    if debug_mode:
        print("Create network")
    params = beta_params[int(args.extraversion)] + beta_params[int(args.conformity)] + [ext_conf_corr, 900]
    G = human_social_network_iterations_correlated((30, 30), 50, False, *params)

    if debug_mode:
        print("Run DSIT")
    simulate(G,
             data_folder + 'graph_corr_ext_' + args.extraversion + '_conf_' + args.conformity + '_simnum_' + args.sim_num + '_disciples_' + args.disciples,
             int(args.disciples), int(args.iterations))
