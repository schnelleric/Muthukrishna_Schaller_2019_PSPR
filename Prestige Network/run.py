import time
from network_generator_prestige import *
import pyximport; pyximport.install()
from network_generator_cython import *
import networkx as nx
import statistics

start = time.time()
human_social_network_prestige_cython((30, 30), 3.4)
print(time.time() - start)

start = time.time()
human_social_network_prestige((30, 30), 3.4)
print(time.time() - start)

# cython_geos = []
# cython_clusts = []
# for i in range(10):
#     G = human_social_network_prestige_cython((30, 30), 3.4)
#     cython_geos.append(nx.average_shortest_path_length(G))
#     cython_clusts.append(nx.average_clustering(G))
# cython_geo = round(statistics.mean(cython_geos), 2)
# cython_clust = round(statistics.mean(cython_clusts), 2)
#
# normal_geos = []
# normal_clusts = []
# for i in range(10):
#     G = human_social_network_prestige((30, 30), 3.4)
#     normal_geos.append(nx.average_shortest_path_length(G))
#     normal_clusts.append(nx.average_clustering(G))
# normal_geo = round(statistics.mean(normal_geos), 2)
# normal_clust = round(statistics.mean(normal_clusts), 2)
#
# print("Normal geodesic: {}; Cython geodesic: {}".format(normal_geo, cython_geo))
# print("Normal clustering: {}; Cython clustering: {}".format(normal_clust, cython_clust))
