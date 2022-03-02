
from utils.deepWalk import DeepWalk
import argparse
import networkx as nx








if __name__ == "__main__":


    parser = argparse.ArgumentParser()

    parser.add_argument("inputedge", type=str, help="The input edge file path")
    parser.add_argument("outputdir", type=str, help="The output dir")


    args = parser.parse_args()

    print(args.inputedge)
    graph = nx.read_edgelist(args.inputedge)

    dw = DeepWalk(graph, 5, 10000, walkers=12, verbose=0, random_state=2022, large_data=True)

    dw.generate_train_data(workers=12, verbose=0, output_dir=args.outputdir)


