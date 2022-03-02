
import gensim
from gensim.models import doc2vec
from gensim.test.utils import get_tmpfile
import smart_open
import numpy as np
import re
import os
import random


def read_corpus(fname, base, token_only=False):

    with smart_open.open(fname, encoding='utf8') as f:

        for i, line in enumerate(f):
            line = re.sub('\n', '', line)
            bbids = np.unique(line.split(' '))
            if token_only:
                yield bbids
            else:
                yield doc2vec.TaggedDocument(bbids, [base*100000000+i])



def train(train, model_dir):


    train_corpus = list(read_corpus(train, 0))



    model = doc2vec.Doc2Vec(vector_size=50, min_count=0, epochs=40)
    model.build_vocab(train_corpus)

    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)

    model_path = os.path.join(model_dir, 'doc2vec.model')

    model.save(model_path)



def test(test, model_dir):

    model = doc2vec.Doc2Vec(vector_size=50, min_count=0, epochs=40)

    model_path = os.path.join(model_dir, 'doc2vec.model')

    model.load(model_path)


    train_corpus = list(read_corpus(train, 0))
    test_corpus = list(read_corpus(test, 0, token_only=True))

    doc_id = random.randint(0, len(test_corpus) -1)

    inferred_vector = model.infer_vector(test_corpus[doc_id])

    sims = model.dv.most_similar([inferred_vector], topn=len(model.dv))

    # Compare and print the most/median/least similar documents from the train corpus
    print('Test Document ({}): «{}»\n'.format(doc_id, ' '.join(test_corpus[doc_id])))
    print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
    for label, index in [('MOST', 0), ('MEDIAN', len(sims)//2), ('LEAST', len(sims) - 1)]:
        print(u'%s %s: «%s»\n' % (label, sims[index], ' '.join(train_corpus[sims[index][0]].words)))


