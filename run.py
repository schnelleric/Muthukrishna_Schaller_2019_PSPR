from network_generator_prestige import *

if __name__ == "__main__":
    sizes = [10, 13, 15, 20, 50, 100]
    probs = [75, 60, 50, 30, 20, 0]

    for i in range(len(sizes)):
        for d in range(6):
            for j in range(25):
                network_equilibrium(sizes[i], d, probs[i] + j)
