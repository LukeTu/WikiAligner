import pickle
import os
import gensim

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR: WikiTrans base directory.


class Embedder:
    def __init__(self) -> None:
        self.model_path = os.path.join(BASE_DIR, 'models')

    # def embed_auto(self, method='labse'):
    #     if method == 'labse':
    #         self.load_labse()
    #         self.embed_with_labse()

    # def load_labse(self):
    #     labse_path = os.path.join(self.model_path, 'labse_model.pkl')
    #     print('Loading LaBSE model...')
    #     with open(labse_path, 'rb') as f:
    #         labse_model = pickle.load(f)
    #     print('LaBSE model has been loaded!')
    #     return labse_model

    def embed_with_labse(self, text, labse_model):
        labse_path = os.path.join(self.model_path, 'labse_model.pkl')
        print('Loading LaBSE model...')
        with open(labse_path, 'rb') as f:
            labse_model = pickle.load(f)
        print('LaBSE model has been loaded!')
        print('Creating embedding with LaBSE...')
        return labse_model.encode(text)

    def embed_with_doc2vec(self, text):
        pass