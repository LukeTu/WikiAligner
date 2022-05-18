import pickle
import os
import gensim

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR: WikiTrans base directory.


class Embedder:
    def __init__(self) -> None:
        self.model_path = os.path.join(BASE_DIR, 'models')
        if not os.path.exists(self.model_path):
            raise ValueError(
                f'Invalid model path at \n{self.model_path}. Please compress the model first.'
            )

    def embed_auto(self,
                   text1: 'list[str]',
                   text2: 'list[str]',
                   method: 'str' = 'labse'):
        if method == 'labse':
            model = self.load_labse()
            embedding1 = model.encode(text1)
            embedding2 = model.encode(text2)
        print('Embedding finished!')
        return embedding1, embedding2

    def load_labse(self):
        labse_path = os.path.join(self.model_path, 'labse_model.pkl')
        print('Loading LaBSE model...')
        with open(labse_path, 'rb') as f:
            labse_model = pickle.load(f)
        print('LaBSE model has been loaded!')
        return labse_model

    def embed_with_doc2vec(self, text):
        pass

    # def embed_with_labse(self, text):  #, labse_model
    #     labse_path = os.path.join(self.model_path, 'labse_model.pkl')
    #     print('Loading LaBSE model...')
    #     with open(labse_path, 'rb') as f:
    #         labse_model = pickle.load(f)
    #     print('LaBSE model has been loaded!')
    #     print('Creating embedding with LaBSE...')
    #     return labse_model.encode(text, show_progress_bar=True)