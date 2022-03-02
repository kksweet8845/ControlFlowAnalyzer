import networkx as nx
import sklearn
import gensim
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.manifold import TSNE
from joblib import Parallel, delayed
from gensim.models import Word2Vec
import numpy as np
import itertools
import random
import os


class DeepWalk(object):
    def __init__(self, graph, walk_length, num_walks, walkers=1, verbose=0, random_state=None, large_data=False):
        self.G = graph
        self.walk_length = walk_length
        self.num_walks = num_walks
        self.walkers = walkers
        self.verbose = verbose
        self.w2v = None
        self.embeddings = None
        self.random_state = random_state if random_state else 2022
        if large_data:
            print("This large data flow should be generate separated")
        else:
            self.dataset = self.get_train_data(walk_length, num_walks, workers=walkers)


    def fit(self, embed_size=128, window=5, n_jobs=3, epochs=5, **kwargs):
        kwargs['sentences'] = self.dataset
        kwargs['min_count'] = kwargs.get('min_count', 0)
        kwargs['size'] = embed_size
        kwargs['sg'] = 1
        kwargs['hs'] = 1
        kwargs['workers'] = n_jobs
        kwargs['window'] = window
        kwargs['iter'] = epochs
        kwargs['seed'] = self.random_state

        self.w2v = Word2Vec(**kwargs)

    def generate_train_data(self, workers=1, verbose=0, output_dir=None):
        assert(output_dir != None, "The output_dir should not be None")
        self.get_train_data(self.walk_length, self.num_walks, workers=workers, verbose=verbose, output_dir=output_dir)


    def get_train_data(self, walk_length, num_walks, workers=1, verbose=0, output_dir=None):

        if num_walks % workers == 0:
            num_walks = [num_walks // workers] * workers
        else:
            num_walks = [num_walks // workers] * workers + [num_walks % workers]

        nodes = list(self.G.nodes())

        results = Parallel(n_jobs=workers, verbose=verbose)(
            delayed(self.simulate_walks)(i, nodes, num, walk_length, output_dir) for i, num in enumerate(num_walks)
        )

        dataset = list(itertools.chain(*results))
        return dataset

    def simulate_walks(self, index, nodes, num_walks, walk_length, output_dir):
        walks = []

        file = output_dir
        if output_dir != None:
            file =  open(os.path.join(os.path.join(output_dir, f"{index}.seq")), 'w')
        for _ in range(num_walks):
            random.shuffle(nodes)
            for v in nodes:
                if file:
                    seq = self.deep_walk(walk_length=walk_length, start_node=v)
                    file.write(' '.join(seq)+'\n')
                else:
                    walks.append(self.deep_walk(walk_length=walk_length, start_node=v))

        if file:
            file.close()

        return walks

    def deep_walk(self, walk_length, start_node):
        G = self.G

        walk = [start_node]

        while len(walk) < walk_length:
            current_node = walk[-1]
            current_neighbors = list(G.neighbors(current_node))
            if len(current_neighbors) > 0:
                walk.append(random.choice(current_neighbors))
            else:
                break
        return walk

    def get_embeddings(self):
        if self.w2v:
            self.embeddings = {}
            for node in self.G.nodes():
                self.embeddings[node] = self.w2v.wv[node]
            return self.embeddings
        else:
            print("Please train the model first")
            return None



if __name__ == "__main__":
    pass





















    