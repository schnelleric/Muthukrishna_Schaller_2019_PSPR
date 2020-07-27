import subprocess
import shutil

if __name__ == "__main__":
    sizes = [10, 13, 15, 20, 50, 100]
    probs = [75, 60, 50, 30, 20, 0]

    for i in range(len(sizes)):
        for d in range(6):
            for j in range(25):
                args = []
                args.append("-n {}".format(sizes[i]))
                args.append("-d {}".format(d))
                args.append("-p 0.{}".format(probs[i]+j))

                python_file = "network_generator_prestige.py"
                print("Ran " + ', '.join(args))
                subprocess.call(["python3", python_file] + args)
                print("Completed " + ', '.join(args))

