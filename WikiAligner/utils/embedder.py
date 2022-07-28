import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))  # BASE_DIR: WikiTrans base directory.
sys.path.append(BASE_DIR)

import pickle
import numpy as np
# import gensim
from utils import _global


class Embedder:
    def __init__(self) -> None:
        pass

    def embed(self, *docs, method: 'str' = 'labse'):
        """Embed docs into vectors with user-defined method (model).
        """
        if method == 'labse':
            model = self._load_labse()
            for doc in docs:
                embed = np.array(model.encode(doc))
                print('Embedding finished!')
                yield embed

    def save(self, **kwargs):
        """Save embedding vectors as numpy (.npy) files.

        Parameters
        ----------
        **kwargs : 
            Make the format is <filename>(don't make them str) = <embed_vector>
        """
        for filename in kwargs:
            filepath = os.path.join(_global.EMBEDPATH, filename + '.npy')
            np.save(filepath, kwargs[filename])
            print('Embedding vector saved!')
        return None

    def load(self, *filenames):
        """Load embedding vectors from numpy (.npy) files.
        """
        for filename in filenames:
            path = os.path.join(_global.EMBEDPATH, filename + '.npy')
            embed = np.load(path)
            print('Embedding vector loaded!')
            yield embed

    def _embed_check(self):
        """Check if a doc's embedding exists already.
        """
        pass

    def _load_labse(self):
        labse_path = os.path.join(_global.MODEL_PATH, 'labse_model.pkl')
        print('Loading LaBSE model...')
        with open(labse_path, 'rb') as f:
            labse_model = pickle.load(f)
        print('LaBSE model has been loaded!')
        return labse_model

    def embed_with_doc2vec(self, text):
        pass


if __name__ == '__main__':
    # Test
    from embedder import Embedder
    embedder = Embedder()
    doc1 = ['Hello there!', 'What\'s up?']
    doc2 = ['你好啊！', '最近怎么样？']
    embed_list = []
    for embed in embedder.embed(doc1, doc2):
        embed_list.append(embed)
    embed1 = embed_list[0]
    embed2 = embed_list[1]
    print('embed1 shape: ', embed1.shape)
    print('embed1 head: ')
    print(embed1[0][:5])
    print('embed2 shape: ', embed2.shape)
    print('embed2 head: ')
    print(embed2[0][:5])
    embedder.save(embed1_test=embed1, embed2_test=embed2)
    [e1, e2] = [eb for eb in embedder.load('embed1_test', 'embed2_test')]
    print(e1 == embed1)
