import os
import pickle
from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR: WikiTrans base directory.


class Compresser:
    """Compress big models in advance. Don't have to run online.
    """
    def __init__(self) -> None:
        self.model_path = os.path.join(BASE_DIR, 'models')
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

    def compress_labse(self):
        model = SentenceTransformer('sentence-transformers/LaBSE')
        labse_path = os.path.join(self.model_path, 'labse_model.pkl')
        with open(labse_path, 'wb') as f:
            pickle.dump(model, f)
        print(f'LaBSE model have been compressed at {labse_path}')


if __name__ == '__main__':
    compresser = Compresser()
    compresser.compress_labse()