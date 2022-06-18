import os
import pickle
from sentence_transformers import SentenceTransformer
import _global


class Compresser:
    """Compress big models in advance. Don't have to run online.
    """
    def __init__(self) -> None:
        pass

    def compress_labse(self):
        model = SentenceTransformer('sentence-transformers/LaBSE')
        labse_path = os.path.join(_global.MODEL_PATH, 'labse_model.pkl')
        with open(labse_path, 'wb') as f:
            pickle.dump(model, f)
        print(f'LaBSE model have been compressed at {labse_path}')


def main():
    compresser = Compresser()
    compresser.compress_labse()


if __name__ == '__main__':
    main()