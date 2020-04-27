import json
from networkx.readwrite import json_graph

def save_to_jsonfile(filename, graph):
    g = graph
    g_json = json_graph.node_link_data(g)
    json.dump(g_json, open(filename, 'w'))
    
def zeroToOne(graph):
    """Assumes binary values"""
    zeros = 0
    ones = 0
    for n in graph.nodes():
        if graph.node[n]['value'] == 0:
            zeros = zeros + 1
        else:
            ones = ones + 1
    
    return float(zeros)/float(zeros + ones)