#!/usr/bin/env python3
"""
Created on Apr 5, 2018

Converting code to Python 3.4 so it can run on the Harvard server.
This is code for consolidation.

@author: Michael Muthukrishna
"""

import argparse
from human_social_network_generator34 import human_social_network_iterations_correlated
from numpy import random
import csv
import copy as C
from MyNetworkFunctions import *

debug_mode = False
output_json_graphs = False
# Create the folder for storing the output files (if it doesn't exist)
data_folder = "./data_consol_corr/"
# pathlib.Path(data_folder).mkdir(exist_ok=True)

beta_params = [[4, 4], [2.5, 3.5], [3.5, 2.5]]

ext_conf_corr = -0.3

parser = argparse.ArgumentParser(description="Run DSIT simulation over Muthukrishna-Schaller network")
parser.add_argument('-e', '--extraversion', help='-1=negative skew, 0=approximate normal, 1=positive skew',
                    required=(not debug_mode), default=0)
parser.add_argument('-c', '--conformity', help='-1=negative skew, 0=approximate normal, 1=positive skew',
                    required=(not debug_mode), default=0)
parser.add_argument('-i', '--iterations', help='int - number of iterations', required=(not debug_mode), default=10)
parser.add_argument('-n', '--sim_num', help='int - number of simulation', required=(not debug_mode), default=-1)
parser.add_argument('-p', '--power', help='float - power to raise learning to', required=(not debug_mode), default=-1)


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

    p = float(args.power)
    prob_of_conforming = conformity * diffTally ** p / (sameTally ** p + diffTally ** p)
    if (random.random() < prob_of_conforming):
        return True
    return False


def simulate(graph, fileName, iterations=1):
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
        # Randomize values on nodes
        for node in g.nodes():
            temp = random.randint(2)
            g.add_node(node, value=temp)

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
        zero_one = zeroToOne(g)
        data['0:1 Distribution'] = zero_one
        csvwr.writerow(data)
        # Save graph
        save_to_jsonfile(fileName + '_iter_' + str(i) + '_gen_' + str(0) + '.json', g)

        # Select random node and apply social influence rules until nNodes generations of no change
        nStayedSame = 0
        count = 0
        numNodes = len(g.nodes())
        while (nStayedSame < 2 * numNodes):
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

            if count % numNodes == 0:
                # If you want to write every generation, indent this under the while loop.
                # Here I'm just outputting at the beginning and end to save space
                data = {}
                data['iteration'] = i
                data['gen'] = count / numNodes
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
                data['0:1 Distribution'] = zeroToOne(g)
                csvwr.writerow(data)
                # Save graph
                if output_json_graphs and count % numNodes == 0:
                    save_to_jsonfile(fileName + '_iter_' + str(i) + '_gen_' + str(count) + '.json', g)
    f.close()


if __name__ == '__main__':
    args = parser.parse_args()
    Gs = []
    if debug_mode:
        print("Create network")
    params = beta_params[int(args.extraversion)] + beta_params[int(args.conformity)] + [ext_conf_corr, 900]
    G = human_social_network_iterations_correlated((30, 30), 50, False, *params)
    if debug_mode:
        print("Save iterations of the graph")

    if debug_mode:
        print("Run DSIT")
    simulate(G,
             data_folder + 'graph_ext_' + args.extraversion + '_conf_' + args.conformity + '_simnum_' + args.sim_num + '_power_' + args.power,
             int(args.iterations))
