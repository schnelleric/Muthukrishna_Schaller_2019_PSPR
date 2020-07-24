from network_generator_prestige import *

if __name__ == "__main__":
    sizes = [10, 13, 15, 20, 50, 100]
    probs = [75, 60, 50, 30, 20, 0]

    for i in range(len(sizes)):
        G = nx.grid_2d_graph(sizes[i], sizes[i], True)
        G = nx.convert_node_labels_to_integers(G)

        initial_nbrs_G = {}
        for n in list(G.nodes):
            nbrs = [nbr for nbr in G[n]]
            initial_nbrs_G[n] = nbrs

        for d in range(6):
            for j in range(25):
                G1 = G.copy()
                network_equilibrium(G1, initial_nbrs_G, d, probs[i] + j)
